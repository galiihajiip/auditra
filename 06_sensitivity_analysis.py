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


