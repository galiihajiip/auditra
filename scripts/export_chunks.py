import math
import os
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = ROOT / "output" / "data_network.parquet"
OUTPUT_DIR = ROOT / "output" / "chunks"

def export_chunks(chunks_count: int = 10):
    """
    Split the massive parquet dataset into smaller chunks (< 25MB).
    This allows deployment via GitHub without hitting the 100MB file size limit.
    """
    if not INPUT_FILE.exists():
        print(f"File not found: {INPUT_FILE}")
        return

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

