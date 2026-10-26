"""
Auditra - Step 1: Data Cleaning
Menghapus kolom hasil enrichment Nemesis AI, hanya menyimpan kolom SIRUP murni.
"""

import pandas as pd

# ── Kolom SIRUP murni yang dipertahankan ──────────────────────────────────────
SIRUP_COLS = [
    'id',
    'paket',
    'jenisPengadaan',
    'metode',
    'lembaga',
    'satker',
    'lokasi',
    'pagu',
    'pemilihanDate',
    'sumberDana',
    'isUMKM',
    'volumePekerjaan',
    'uraianPekerjaan',
    'spesifikasiPekerjaan',
    'ownerType',
    'dalamNegeri',
]

# Kolom Nemesis yang dihapus:
# - potensiPemborosan     → hasil kalkulasi Nemesis
# - tags.isInappropriate  → label AI Nemesis
# - tags.inappropriateReason → reasoning AI Nemesis
# - jumlahTagAktif        → agregasi tag Nemesis

# ── Load ──────────────────────────────────────────────────────────────────────
INPUT_PATH  = 'data/year-2026_merged.csv'
OUTPUT_PATH = 'data/data_clean.csv'

print("Loading data...")
df_raw = pd.read_csv(INPUT_PATH)
print(f"  Raw shape  : {df_raw.shape}")

# ── Drop kolom Nemesis ────────────────────────────────────────────────────────
nemesis_cols = [c for c in df_raw.columns if c not in SIRUP_COLS]
print(f"\nKolom Nemesis yang dihapus: {nemesis_cols}")

df = df_raw[SIRUP_COLS].copy()

# ── Basic cleaning ────────────────────────────────────────────────────────────
# Hapus duplikat berdasarkan id
before = len(df)
df = df.drop_duplicates(subset='id')
print(f"\nDuplikat dihapus: {before - len(df)} baris")

# Pagu tidak boleh 0 atau negatif
before = len(df)
df = df[df['pagu'] > 0]
print(f"Pagu <= 0 dihapus: {before - len(df)} baris")

