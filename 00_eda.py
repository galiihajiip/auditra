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

