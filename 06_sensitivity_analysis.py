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

    # ── 1. Perturbasi ±10% per sinyal (renormalize) ─────────────────
    perturb_results = []
    delta = 0.10

    for signal in SIGNAL_COLS:
        for direction in (+1, -1):
            w = dict(base_weights)
            w[signal] = w[signal] * (1 + direction * delta)
            total = sum(w.values())
            w = {k: v / total for k, v in w.items()}
            new_rpi = compute_rpi(df, w)
            new_rank = new_rpi.sort_values(ascending=False)
            for top_n in [50, 100, 500]:
                overlap = rank_overlap(base_rank, new_rank, top_n)
                perturb_results.append({
                    "perturbation": f"{signal} {'+' if direction > 0 else '-'}{int(delta*100)}%",
                    "top_n": top_n,
                    "overlap": round(overlap, 4),
                    "spearman": round(base_rpi.corr(new_rpi, method="spearman"), 4),
                })

