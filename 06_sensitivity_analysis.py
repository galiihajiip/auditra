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

    # ── 2. Equal weights scenario ───────────────────────────────────
    equal_w = {col: 1 / len(SIGNAL_COLS) for col in SIGNAL_COLS}
    equal_rpi = compute_rpi(df, equal_w)
    equal_rank = equal_rpi.sort_values(ascending=False)

    # ── 3. Drop-one-signal analysis ─────────────────────────────────
    dropone = []
    for drop_col in SIGNAL_COLS:
        w = {k: (0.0 if k == drop_col else v) for k, v in base_weights.items()}
        total = sum(w.values())
        w = {k: v / total for k, v in w.items()}
        new_rpi = compute_rpi(df, w)
        new_rank = new_rpi.sort_values(ascending=False)
        dropone.append({
            "dropped": drop_col,
            "spearman_vs_base": round(base_rpi.corr(new_rpi, method="spearman"), 4),
            "top100_overlap": round(rank_overlap(base_rank, new_rank, 100), 4),
        })

    # ── 4. Label stability under equal weights ──────────────────────
    def label(score):
        if score >= 70: return "KRITIS"
        if score >= 50: return "TINGGI"
        if score >= 30: return "SEDANG"
        return "RENDAH"

    base_labels = base_rpi.apply(label)
    equal_labels = equal_rpi.apply(label)
    label_agree = (base_labels == equal_labels).mean()

    stats = {
        "base_weights": base_weights,
        "perturbation_pm10pct": perturb_results,
        "equal_weights": {
            "top100_overlap": round(rank_overlap(base_rank, equal_rank, 100), 4),
            "spearman": round(base_rpi.corr(equal_rpi, method="spearman"), 4),
            "label_agreement_pct": round(label_agree * 100, 2),
        },
        "drop_one_signal": dropone,
    }

