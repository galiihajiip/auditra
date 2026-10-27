"""
Auditra - Step 2: Risk Scoring
Menghitung Risk Priority Index (RPI) dari 7 sinyal risiko berbasis data SIRUP murni.

Sinyal:
  S1 - Metode pemilihan (rule-based)
  S2 - Pagu anomali vs median kategori sejenis (z-score)
  S3 - Fragmentasi paket / split contract (TF-IDF similarity)
  S4 - Konsentrasi metode berisiko per satker
  S5 - Ketidaksesuaian UMKM vs nilai paket
  S6 - Kombinasi sumber dana APBN + metode berisiko
  S7 - Reputasi risiko lembaga (Knowledge Graph node weight)

RPI = weighted sum, skala 0–100
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
import warnings
warnings.filterwarnings('ignore')

# ── Config ────────────────────────────────────────────────────────────────────
INPUT_PATH  = 'data/data_clean.csv'   # ganti path sesuai lokasimu
OUTPUT_PATH = 'output/data_scored.csv'

# Bobot RPI (total = 1.0)
WEIGHTS = {
    's1_metode':        0.20,
    's2_pagu_anomali':  0.20,
    's3_fragmentasi':   0.15,
    's4_konsentrasi':   0.15,
    's5_umkm':          0.10,
    's6_dana_metode':   0.10,
    's7_reputasi':      0.10,
}

# Threshold fragmentasi: satker + uraian mirip dalam window pagu
FRAG_PAGU_THRESHOLD = 200_000_000   # 200 juta (batas Pengadaan Langsung)
FRAG_SIMILARITY_THRESHOLD = 0.6     # cosine similarity minimum

