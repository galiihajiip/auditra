"""DuckDB data layer — materialized cache for fast repeated queries."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import duckdb
import pandas as pd

from api.cache import TTLCache
from api.config import (
    DASHBOARD_CACHE_SIZE,
    DATA_CHUNKS_DIR,
    DATA_CHUNKS_GLOB,
    DATA_NETWORK_CSV,
    DATA_NETWORK_PARQUET,
    DUCKDB_CACHE,
    GEO_LOOKUP_CSV,
    GEOJSON_PATH,
    KG_EDGES_CSV,
    KG_NODES_CSV,
)
from api.filters import build_where
from api.owner_category import MAP_MODES, OWNER_CATEGORY_EXPR


class DataStoreNotReady(Exception):
    """Raised while the singleton is still initializing (background warm-up)."""


_init_state = "pending"  # pending | loading | ready | error
_init_error: str | None = None


def _use_parquet_views() -> bool:
    """Query parquet in-place (low RAM). Default on Railway; off locally unless set."""
    explicit = os.getenv("AUDITRA_USE_PARQUET_VIEWS", "").lower()
    if explicit in ("1", "true", "yes"):
        return True
    if explicit in ("0", "false", "no"):
        return False
    return bool(os.getenv("RAILWAY_ENVIRONMENT"))


class DataStore:
    """Singleton DuckDB over a materialized local cache (auditra.duckdb)."""

    _instance: "DataStore | None" = None
    _init_lock = threading.Lock()

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._dashboard_cache = TTLCache(maxsize=DASHBOARD_CACHE_SIZE, ttl_seconds=600)
        self._packages_cache = TTLCache(maxsize=128, ttl_seconds=120)
        self._filter_options_cache: dict | None = None
        self._meta_cache: dict | None = None
        self._geo_coverage_cache: dict | None = None
        self._geojson_cache: dict | None = None
        self._kg_nodes: pd.DataFrame | None = None
        self._kg_edges: pd.DataFrame | None = None
        self.source_path = ""
        self.source_kind = ""

        t0 = time.perf_counter()
        self._ensure_database()
        if _use_parquet_views():
            self.conn = duckdb.connect(":memory:")
            self._configure_session()
            self._setup_parquet_views(self.conn)
        else:
            self.conn = duckdb.connect(str(DUCKDB_CACHE), read_only=False)
            self._configure_session()
            self._ensure_packages_geo(self.conn)
        self._warm_static_caches()
        elapsed = time.perf_counter() - t0
        print(f"[Auditra] Database ready in {elapsed:.1f}s ({self._meta_cache['total_rows']:,} rows)")

    @classmethod
    def _ensure_built(cls) -> None:
        global _init_state, _init_error
        if cls._instance is not None:
            return
        with cls._init_lock:
            if cls._instance is not None:
                return
            if _init_state == "error":
                raise RuntimeError(_init_error or "Database gagal diinisialisasi.")
            _init_state = "loading"
        try:
            instance = cls()
        except Exception as exc:
            with cls._init_lock:
                _init_state = "error"
                _init_error = str(exc)
            raise
        with cls._init_lock:
            cls._instance = instance
            _init_state = "ready"

    @classmethod
    def get(cls) -> "DataStore":
        if _init_state == "loading":
            raise DataStoreNotReady(
                "Database sedang disiapkan. Tunggu 30–90 detik lalu muat ulang halaman."
            )
        if _init_state == "error":
            raise RuntimeError(_init_error or "Database gagal diinisialisasi.")
        if cls._instance is None:
            cls._ensure_built()
        return cls._instance

    @classmethod
    def is_ready(cls) -> bool:
        return _init_state == "ready" and cls._instance is not None

    @classmethod
    def begin_background_init(cls) -> None:
        """Start DataStore warm-up on a worker thread (non-blocking startup)."""
        if cls.is_ready() or _init_state in ("loading", "ready"):
            return

        def _run() -> None:
            try:
                cls._ensure_built()
                print("[Auditra] Background database init complete.")
            except Exception as exc:
                print(f"[Auditra] Background init failed: {exc}")

        threading.Thread(target=_run, name="auditra-db-init", daemon=True).start()

    def _configure_session(self) -> None:
        threads = min(8, max(2, __import__("os").cpu_count() or 4))
        self.conn.execute(f"SET threads TO {threads}")
        self.conn.execute("SET enable_object_cache TO true")

    def _source_mtime(self) -> float:
        chunks = list(DATA_CHUNKS_DIR.glob("*.parquet")) if DATA_CHUNKS_DIR.exists() else []
        if chunks:
            return max(f.stat().st_mtime for f in chunks)
        if DATA_NETWORK_PARQUET.exists():
            return DATA_NETWORK_PARQUET.stat().st_mtime
        if DATA_NETWORK_CSV.exists():
            return DATA_NETWORK_CSV.stat().st_mtime
        return 0

    def _table_exists(self, conn: duckdb.DuckDBPyConnection, name: str) -> bool:
        row = conn.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = ?",
            [name],
        ).fetchone()
        return int(row[0]) > 0

    def _cache_is_usable(self) -> bool:
        """Cache exists, is newer than sources, and has the packages table."""
        if not DUCKDB_CACHE.exists():
            return False
        try:
            if DUCKDB_CACHE.stat().st_mtime < self._source_mtime():
                return False
            test_con = duckdb.connect(str(DUCKDB_CACHE), read_only=True)
            ok = self._table_exists(test_con, "packages")
            test_con.close()
            return ok
        except Exception:
            return False

