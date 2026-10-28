"""
Auditra - Step 6: Sensitivity Analysis (Robustness RPI Weights)
Menguji stabilitas ranking paket prioritas terhadap perturbasi bobot.

Output:
  output/reports/sensitivity_report.md
  output/reports/sensitivity_stats.json
"""

from __future__ import annotations

import json
from itertools import product

import numpy as np
import pandas as pd

from pipeline.config import load_config, reports_dir

SIGNAL_COLS = [
    "s1_metode", "s2_pagu_anomali", "s3_fragmentasi",
    "s4_konsentrasi", "s5_umkm", "s6_dana_metode", "s7_reputasi",
]


def compute_rpi(df: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    total = sum(df[col] * weights[col] for col in SIGNAL_COLS)
    return (total * 100).round(2)


def rank_overlap(base_rank: pd.Series, new_rank: pd.Series, top_n: int) -> float:
    base_top = set(base_rank.head(top_n).index)
    new_top = set(new_rank.head(top_n).index)
    return len(base_top & new_top) / top_n


def main() -> None:
    cfg = load_config()
    path = cfg["paths"]["network"]
    base_weights = cfg["scoring"]["weights"]

    print("=" * 60)
    print("AUDITRA — SENSITIVITY ANALYSIS")
    print("=" * 60)

    df = pd.read_csv(path, usecols=["id", "paket", "lembaga", "RPI"] + SIGNAL_COLS, low_memory=False)
    print(f"Loaded {len(df):,} rows")

    base_rpi = compute_rpi(df, base_weights)
    base_rank = base_rpi.sort_values(ascending=False)

