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

