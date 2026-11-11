"""Kesegaran data: bandingkan snapshot analitik dengan SIRUP saat ini (live, di-cache, fail-soft)."""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from api.config import ROOT

SNAPSHOT_META = ROOT / "data" / "snapshot.json"  # opsional: {"exported_at": "2026-..", "note": ".."}
LIVE_DIR = ROOT / "data" / "live"
LIVE_TTL = 600  # detik

_lock = threading.Lock()
_cache: dict = {"at": 0.0, "value": None}


def _live_total() -> dict:
    from scraper.sirup import Client, total_records

    now = time.time()
    try:
        total = total_records(Client(delay=0, timeout=6, retries=1))
        return {"total": total, "checked_at": now, "error": None}
    except Exception as exc:  # situs mati / jaringan / struktur berubah
        return {"total": None, "checked_at": now, "error": f"{type(exc).__name__}: {exc}"[:160]}


def live_status(force: bool = False) -> dict:
    with _lock:
        if not force and _cache["value"] and time.time() - _cache["at"] < LIVE_TTL:
            return _cache["value"]
    value = _live_total()
    with _lock:
        # jangan menimpa hasil sukses lama dengan kegagalan sesaat
        if value["total"] is None and _cache["value"] and _cache["value"]["total"] is not None:
            value = {**_cache["value"], "stale": True, "error": value["error"]}
        _cache.update(at=time.time(), value=value)
    return value


def latest_delta() -> dict | None:
    if not LIVE_DIR.exists():
        return None
    for d in sorted(LIVE_DIR.iterdir(), reverse=True):
        f = d / "delta.json"
        if f.exists():
            try:
                return json.loads(f.read_text())
            except Exception:
                return None
    return None


def snapshot_meta() -> dict:
    if SNAPSHOT_META.exists():
        try:
            return json.loads(SNAPSHOT_META.read_text())
        except Exception:
            pass
    return {}


def build(snapshot_rows: int) -> dict:
    live = live_status()
    behind = None if live["total"] is None else live["total"] - snapshot_rows
    snap = snapshot_meta()
    return {
        "snapshot": {
            "rows": snapshot_rows,
            "exported_at": snap.get("exported_at"),  # None = tidak tercatat
            "note": snap.get("note"),
        },
        "live": live,
        "behind_rows": behind,
        "behind_pct": None if behind is None or not live["total"] else round(100 * behind / live["total"], 1),
        "delta": latest_delta(),
        "source_url": "https://sirup.inaproc.id/sirup/caripaketctr/index",
    }
