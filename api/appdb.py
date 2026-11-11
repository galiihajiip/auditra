"""Application database (SQLite): users, audit cases, notes, evidence, immutable event log.

Dipisah dari DuckDB (analitik read-only atas 3 juta baris). SQLite cukup untuk data
transaksional skala tim audit; skema memakai foreign key + CHECK constraint sehingga
integritas dijaga di level database, bukan hanya di UI.
"""

from __future__ import annotations

import os
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path

from api.config import ROOT

APP_DB_PATH = Path(os.getenv("AUDITRA_APP_DB", ROOT / "output" / "auditra_app.sqlite"))
UPLOAD_DIR = Path(os.getenv("AUDITRA_UPLOAD_DIR", ROOT / "output" / "uploads"))

SCHEMA_VERSION = 2

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name          TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('auditor','reviewer')),
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Penugasan audit atas satu paket. phase mengikuti siklus penugasan (docs/RISET_PROSES_AUDIT.md §3, §8).
CREATE TABLE IF NOT EXISTS cases (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id       INTEGER NOT NULL,
    title            TEXT NOT NULL,
    lembaga          TEXT,
    rpi              REAL,
    risk_label       TEXT,
    pagu             REAL,
    jenis_pengadaan  TEXT,
    metode           TEXT,
    phase            TEXT NOT NULL DEFAULT 'seleksi'
                     CHECK (phase IN ('seleksi','perencanaan','pelaksanaan','reviu','komunikasi','selesai','dihentikan')),
    selection_reason TEXT,
    objective        TEXT,
    scope_stages     TEXT,
    criteria_note    TEXT,
    materiality_note TEXT,
    risk_note        TEXT,
    conclusion       TEXT,
    outcome          TEXT CHECK (outcome IS NULL OR outcome IN ('tanpa_temuan','dengan_temuan')),
    stop_reason      TEXT,
    created_by       INTEGER NOT NULL REFERENCES users(id),
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
-- satu penugasan aktif per paket
CREATE UNIQUE INDEX IF NOT EXISTS ux_cases_active_package
    ON cases(package_id) WHERE phase NOT IN ('selesai','dihentikan');
CREATE INDEX IF NOT EXISTS ix_cases_phase ON cases(phase);

-- Program audit: prosedur, kriteria, bukti diharapkan, hasil pengujian.
CREATE TABLE IF NOT EXISTS procedures (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id         INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    code            TEXT NOT NULL,
    stage           TEXT NOT NULL,
    title           TEXT NOT NULL,
    objective       TEXT,
    criteria        TEXT NOT NULL DEFAULT '[]',
    evidence_expected TEXT NOT NULL DEFAULT '[]',
    techniques      TEXT NOT NULL DEFAULT '[]',
    caution         TEXT,
    custom          INTEGER NOT NULL DEFAULT 0,
    status          TEXT NOT NULL DEFAULT 'belum'
                    CHECK (status IN ('belum','sesuai','tidak_sesuai','tidak_dapat_diuji')),
    result_note     TEXT,
    tested_by       INTEGER REFERENCES users(id),
    tested_at       TEXT
);
CREATE INDEX IF NOT EXISTS ix_proc_case ON procedures(case_id);

CREATE TABLE IF NOT EXISTS evidence (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id       INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    procedure_id  INTEGER REFERENCES procedures(id) ON DELETE SET NULL,
    kind          TEXT NOT NULL CHECK (kind IN ('link','file')),
    title         TEXT NOT NULL,
    url           TEXT,
    filename      TEXT,
    stored_name   TEXT,
    mime          TEXT,
    size_bytes    INTEGER,
    sha256        TEXT,
    form          TEXT NOT NULL CHECK (form IN ('catatan_transaksi','komunikasi_pihak_luar','hasil_observasi','keterangan_entitas')),
    technique     TEXT NOT NULL,
    origin        TEXT NOT NULL CHECK (origin IN ('entitas','pihak_ketiga','pemeriksa')),
    doc_date      TEXT,
    relevan       INTEGER NOT NULL DEFAULT 0,
    valid         INTEGER NOT NULL DEFAULT 0,
    andal         INTEGER NOT NULL DEFAULT 0,
    authenticity_concern INTEGER NOT NULL DEFAULT 0,
    authenticity_note TEXT,
    added_by      INTEGER NOT NULL REFERENCES users(id),
    added_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    review_status TEXT NOT NULL DEFAULT 'pending'
                  CHECK (review_status IN ('pending','verified','rejected')),
    reviewed_by   INTEGER REFERENCES users(id),
    reviewed_at   TEXT,
    review_note   TEXT
);
CREATE INDEX IF NOT EXISTS ix_evidence_case ON evidence(case_id);

-- Temuan: kondisi, kriteria (+sumber), sebab, akibat, rekomendasi; tanggapan; tindak lanjut.
CREATE TABLE IF NOT EXISTS findings (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id          INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    procedure_id     INTEGER REFERENCES procedures(id) ON DELETE SET NULL,
    title            TEXT NOT NULL,
    kondisi          TEXT NOT NULL,
    kriteria         TEXT NOT NULL,
    kriteria_sumber  TEXT NOT NULL,
    sebab            TEXT,
    akibat           TEXT,
    nilai_potensi    REAL,
    rekomendasi      TEXT,
    rekomendasi_kepada TEXT,
    indikasi_kecurangan INTEGER NOT NULL DEFAULT 0,
    created_by       INTEGER NOT NULL REFERENCES users(id),
    created_at       TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    tanggapan_status TEXT NOT NULL DEFAULT 'belum'
                     CHECK (tanggapan_status IN ('belum','diterima','diterima_sebagian','ditolak','tidak_ada_tanggapan')),
    tanggapan        TEXT,
    tanggapan_by     INTEGER REFERENCES users(id),
    tanggapan_at     TEXT,
    tl_status        TEXT NOT NULL DEFAULT 'belum'
                     CHECK (tl_status IN ('belum','dalam_proses','sesuai','tidak_sesuai','tidak_dapat_ditindaklanjuti')),
    tl_note          TEXT,
    tl_by            INTEGER REFERENCES users(id),
    tl_at            TEXT
);
CREATE INDEX IF NOT EXISTS ix_findings_case ON findings(case_id);

-- bukti yang mendukung temuan (SPKN Umum par. 72)
CREATE TABLE IF NOT EXISTS finding_evidence (
    finding_id  INTEGER NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    evidence_id INTEGER NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    PRIMARY KEY (finding_id, evidence_id)
);

-- jejak audit: hanya INSERT (tidak ada endpoint update/delete)
CREATE TABLE IF NOT EXISTS case_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id    INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    type       TEXT NOT NULL,
    from_status TEXT,
    to_status   TEXT,
    body        TEXT,
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);
CREATE INDEX IF NOT EXISTS ix_events_case ON case_events(case_id, id);
"""

_lock = threading.RLock()
_ready_for: str | None = None


def _connect() -> sqlite3.Connection:
    APP_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(APP_DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def _existing_version(path: Path) -> int | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    c = sqlite3.connect(path)
    try:
        return int(c.execute("PRAGMA user_version").fetchone()[0])
    finally:
        c.close()


def init_db() -> None:
    """Buat skema; bila berkas lama berskema <v2 (alur kasus versi awal) → cadangkan, tidak dihapus."""
    global _ready_for
    with _lock:
        if _ready_for == str(APP_DB_PATH):
            return
        ver = _existing_version(APP_DB_PATH)
        if ver is not None and ver < SCHEMA_VERSION:
            backup = APP_DB_PATH.with_suffix(f".v{ver}.bak")
            n = 1
            while backup.exists():
                backup = APP_DB_PATH.with_suffix(f".v{ver}.{n}.bak")
                n += 1
            for ext in ("", "-wal", "-shm"):
                f = Path(str(APP_DB_PATH) + ext)
                if f.exists():
                    f.rename(Path(str(backup) + ext))
        conn = _connect()
        try:
            conn.executescript(SCHEMA)
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
            conn.commit()
        finally:
            conn.close()
        _ready_for = str(APP_DB_PATH)


@contextmanager
def db():
    """Transaksi: commit jika sukses, rollback jika error."""
    init_db()
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
