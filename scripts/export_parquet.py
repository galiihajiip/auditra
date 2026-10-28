"""
Convert data_network.csv → parquet (same rows/columns, faster queries).
Run after 03_network_analysis.py.
"""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "output" / "data_network.csv"
PARQUET = ROOT / "output" / "data_network.parquet"


def main() -> None:
    if not CSV.exists():
        raise SystemExit(f"Missing {CSV} — run pipeline first.")

    con = duckdb.connect()
    before = con.execute(
        f"SELECT COUNT(*) FROM read_csv_auto('{CSV.as_posix()}', header=true)"
    ).fetchone()[0]
