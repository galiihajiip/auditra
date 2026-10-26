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

