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
    # TF-IDF pada uraianPekerjaan
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2
    )
    tfidf_matrix = tfidf.fit_transform(kandidat['uraianPekerjaan'].fillna(''))

    # Proses per satker untuk efisiensi memori
    frag_scores = {}
    satker_groups = kandidat.groupby('satker')

    for satker, grp in satker_groups:
        if len(grp) < 2:
            continue

        idx = grp.index.tolist()
        mat = tfidf_matrix[kandidat.index.get_indexer(idx)]

        # Cosine similarity antar paket dalam satker yang sama
        sim_matrix = cosine_similarity(mat)
        np.fill_diagonal(sim_matrix, 0)

        # Skor fragmentasi = max similarity dengan paket lain di satker yang sama
        for i, orig_idx in enumerate(idx):
            max_sim = sim_matrix[i].max()
            if max_sim >= FRAG_SIMILARITY_THRESHOLD:
                frag_scores[orig_idx] = max_sim

    for idx, score in frag_scores.items():
        df.loc[idx, 's3_fragmentasi'] = score

    n_frag = sum(1 for v in frag_scores.values() if v >= FRAG_SIMILARITY_THRESHOLD)
    print(f"  Terdeteksi potensi fragmentasi: {n_frag:,} paket")

# ── S4: Konsentrasi Metode Berisiko per Satker ────────────────────────────────
print("[S4] Scoring konsentrasi metode berisiko per satker...")

METODE_BERISIKO = {'Penunjukan Langsung', 'Dikecualikan'}

df['is_berisiko'] = df['metode'].isin(METODE_BERISIKO).astype(int)

satker_stats = df.groupby('satker').agg(
    total_paket=('id', 'count'),
    paket_berisiko=('is_berisiko', 'sum')
).reset_index()
satker_stats['rasio_berisiko'] = satker_stats['paket_berisiko'] / satker_stats['total_paket']

# Normalize rasio ke 0-1 berdasarkan persentil
p95 = satker_stats['rasio_berisiko'].quantile(0.95)
satker_stats['s4_konsentrasi'] = (satker_stats['rasio_berisiko'] / p95).clip(0, 1)

df = df.merge(satker_stats[['satker', 's4_konsentrasi']], on='satker', how='left')
df['s4_konsentrasi'] = df['s4_konsentrasi'].fillna(0)

# ── S5: Ketidaksesuaian UMKM vs Nilai Paket ──────────────────────────────────
print("[S5] Scoring anomali UMKM...")

# Threshold wajar UMKM berdasarkan Perpres: barang/jasa ≤ 15M untuk PL ke UMKM
# Tapi banyak yang jauh di atas itu — kita pakai persentil 90 dalam grup isUMKM=True
umkm_df = df[df['isUMKM'] == True]
p90_umkm = umkm_df['pagu'].quantile(0.90)

def score_umkm(row):
    if row['isUMKM'] == True and row['pagu'] > p90_umkm:
        # Semakin jauh di atas p90, skor makin tinggi
        return min((row['pagu'] / p90_umkm - 1) / 9, 1.0)
    return 0.0

df['s5_umkm'] = df.apply(score_umkm, axis=1)

# ── S6: Kombinasi Sumber Dana APBN + Metode Berisiko ─────────────────────────
print("[S6] Scoring kombinasi sumber dana + metode...")

def score_dana_metode(row):
    is_apbn = str(row.get('sumberDana_cat', '')).startswith('APBN') or \
              str(row.get('sumberDana', '')).startswith('APBN')
    is_berisiko = row['metode'] in METODE_BERISIKO
    if is_apbn and is_berisiko:
        return 1.0
    elif is_apbn and row['metode'] == 'Pengadaan Langsung':
        return 0.4
    elif is_berisiko:
        return 0.6
    return 0.0

df['s6_dana_metode'] = df.apply(score_dana_metode, axis=1)

