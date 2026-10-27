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

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading cleaned data...")
df = pd.read_csv(INPUT_PATH, low_memory=False)
print(f"  Shape: {df.shape}")

# ── S1: Metode Pemilihan ──────────────────────────────────────────────────────
print("\n[S1] Scoring metode pemilihan...")

METODE_SCORE = {
    'Penunjukan Langsung': 1.00,
    'Dikecualikan':        0.85,
    'Pengadaan Langsung':  0.40,
    'Tender Cepat':        0.30,
    'E-Purchasing':        0.20,
    'Seleksi':             0.10,
    'Tender':              0.05,
}

df['s1_metode'] = df['metode'].map(METODE_SCORE).fillna(0.50)

# ── S2: Pagu Anomali vs Median Kategori Sejenis ───────────────────────────────
print("[S2] Scoring pagu anomali...")

# Hitung median pagu per kombinasi jenisPengadaan + metode
df['pagu_log'] = np.log1p(df['pagu'])

group_stats = df.groupby(['jenisPengadaan', 'metode'])['pagu_log'].agg(
    median='median', std='std'
).reset_index()
group_stats.columns = ['jenisPengadaan', 'metode', 'pagu_log_median', 'pagu_log_std']

df = df.merge(group_stats, on=['jenisPengadaan', 'metode'], how='left')

# Z-score dalam grup, clip ke 0-1
df['pagu_z'] = (df['pagu_log'] - df['pagu_log_median']) / (df['pagu_log_std'] + 1e-9)
df['s2_pagu_anomali'] = df['pagu_z'].clip(0, 3) / 3  # normalize ke 0-1

# ── S3: Fragmentasi Paket (Split Contract) ────────────────────────────────────
print("[S3] Scoring fragmentasi paket (TF-IDF)... ini bisa makan waktu untuk data besar")

# Filter kandidat fragmentasi: Pengadaan Langsung + pagu < threshold
kandidat = df[
    (df['metode'] == 'Pengadaan Langsung') &
    (df['pagu'] <= FRAG_PAGU_THRESHOLD) &
    (df['uraianPekerjaan'].notna())
].copy()

print(f"  Kandidat fragmentasi: {len(kandidat):,} paket")

df['s3_fragmentasi'] = 0.0

if len(kandidat) > 1:
