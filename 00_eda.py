"""
Auditra - Step 0: Exploratory Data Analysis (EDA)
Analisis eksploratif data mentah SIRUP sebelum preprocessing.

Output:
  output/reports/eda_report.md   — ringkasan teks
  output/reports/eda_stats.json  — statistik terstruktur
  output/reports/eda_charts.html — visualisasi interaktif (Plotly)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from pipeline.config import load_config, reports_dir

SIRUP_COLS = [
    "id", "paket", "jenisPengadaan", "metode", "lembaga", "satker",
    "lokasi", "pagu", "pemilihanDate", "sumberDana", "isUMKM",
    "volumePekerjaan", "uraianPekerjaan", "spesifikasiPekerjaan",
    "ownerType", "dalamNegeri",
]


def iqr_outliers(series: pd.Series) -> dict:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    mask = (series < lower) | (series > upper)
    return {
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_fence": float(lower),
        "upper_fence": float(upper),
        "n_outliers": int(mask.sum()),
        "pct_outliers": round(mask.mean() * 100, 2),
    }


def main() -> None:
    cfg = load_config()
    input_path = Path(cfg["paths"]["raw"])
    seed = cfg["eda"]["random_seed"]
    sample_n = cfg["eda"]["sample_size"]

    if not input_path.exists():
        raise FileNotFoundError(f"Data mentah tidak ditemukan: {input_path}")

    print("=" * 60)
    print("AUDITRA — EXPLORATORY DATA ANALYSIS")
    print("=" * 60)
    print(f"Input : {input_path}")
    print(f"Sample: {sample_n:,} baris (seed={seed}) untuk visualisasi")

    t0 = datetime.now(timezone.utc)
    df_full = pd.read_csv(input_path, low_memory=False)
    n_rows, n_cols = df_full.shape

    # ── Profil dataset ────────────────────────────────────────────────
    dtypes = {c: str(t) for c, t in df_full.dtypes.items()}
    null_counts = df_full.isnull().sum()
    null_pct = (null_counts / n_rows * 100).round(2)
    null_report = {
        c: {"count": int(null_counts[c]), "pct": float(null_pct[c])}
        for c in null_counts.index if null_counts[c] > 0
    }

    dup_id = int(df_full["id"].duplicated().sum()) if "id" in df_full.columns else -1
    pagu_stats = df_full["pagu"].describe().to_dict() if "pagu" in df_full.columns else {}
    pagu_outliers = iqr_outliers(df_full["pagu"].dropna()) if "pagu" in df_full.columns else {}

    cat_cols = ["metode", "jenisPengadaan", "lembaga", "sumberDana"]
    distributions = {}
    for col in cat_cols:
        if col in df_full.columns:
            vc = df_full[col].value_counts().head(15)
            distributions[col] = {str(k): int(v) for k, v in vc.items()}

