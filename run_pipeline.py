"""
Auditra — Pipeline Orchestrator
Menjalankan seluruh lifecycle: EDA → cleaning → scoring → network → geo → validation.

Usage:
  python run_pipeline.py              # full pipeline
  python run_pipeline.py --from 02    # mulai dari step 02_scoring
  python run_pipeline.py --skip-eda   # lewati EDA
  python run_pipeline.py --validate-only
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

STEPS = [
    ("00", "00_eda.py", "Exploratory Data Analysis"),
    ("01", "01_cleaning.py", "Data Cleaning"),
    ("01b", "01b_patch_lembaga_provinsi.py", "Patch Lembaga/Provinsi"),
    ("02", "02_scoring.py", "Risk Scoring (RPI)"),
    ("03", "03_network_analysis.py", "Knowledge Graph & Network"),
    ("03b", "03b_geo_matching.py", "Geo Matching"),
    ("05", "05_validate.py", "Data Validation"),
    ("06", "06_sensitivity_analysis.py", "Sensitivity Analysis"),
]

