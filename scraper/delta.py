"""Bandingkan snapshot analitik (parquet) dengan hasil crawl live → laporan delta (delta.json).

    python -m scraper.delta --live data/live/2026-11-11
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_GLOB = (ROOT / "output" / "chunks" / "*.parquet").as_posix()


def compute_delta(live_dir: Path) -> dict:
    live_glob = (live_dir / "leaf_*.jsonl.gz").as_posix()
    c = duckdb.connect()
    c.execute(f"CREATE VIEW snap AS SELECT id, paket, pagu, metode, lembaga FROM read_parquet('{SNAPSHOT_GLOB}')")
    c.execute(
        f"""CREATE VIEW live AS SELECT CAST(id AS BIGINT) id, paket, CAST(pagu AS DOUBLE) pagu, metode, kldi
            FROM read_json_auto('{live_glob}', format='newline_delimited')"""
    )
    one = lambda q: c.execute(q).fetchone()[0]  # noqa: E731
    d = {
        "computed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "live_dir": live_dir.name,
        "snapshot_rows": one("SELECT COUNT(*) FROM snap"),
        "live_rows": one("SELECT COUNT(DISTINCT id) FROM live"),
        "new_in_live": one("SELECT COUNT(*) FROM live l WHERE NOT EXISTS (SELECT 1 FROM snap s WHERE s.id=l.id)"),
        "removed_from_live": one("SELECT COUNT(*) FROM snap s WHERE NOT EXISTS (SELECT 1 FROM live l WHERE s.id=l.id)"),
        "pagu_changed": one("SELECT COUNT(*) FROM snap s JOIN live l USING(id) WHERE s.pagu <> l.pagu"),
        "metode_changed": one("SELECT COUNT(*) FROM snap s JOIN live l USING(id) WHERE s.metode IS DISTINCT FROM l.metode"),
        "paket_renamed": one("SELECT COUNT(*) FROM snap s JOIN live l USING(id) WHERE s.paket IS DISTINCT FROM l.paket"),
        "live_pagu_total": one("SELECT SUM(pagu) FROM live"),
        "snapshot_pagu_total": one("SELECT SUM(pagu) FROM snap"),
    }
    d["new_pagu_total"] = one(
        "SELECT COALESCE(SUM(l.pagu),0) FROM live l WHERE NOT EXISTS (SELECT 1 FROM snap s WHERE s.id=l.id)"
    )
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", required=True)
    a = ap.parse_args()
    live = Path(a.live)
    delta = compute_delta(live)
    (live / "delta.json").write_text(json.dumps(delta, indent=2))
    print(json.dumps(delta, indent=2))


if __name__ == "__main__":
    main()
