"""
Auditra - Step 3b: Geo Matching
Mencocokkan kolom 'lokasi' SIRUP (format: "Provinsi, Nama (Kab./Kota)")
ke GeoJSON 514 kabupaten/kota Indonesia.

Sumber GeoJSON: eppofahmi/geojson-indonesia (kota/all_kabkota_ind.geojson)

Output:
  - geo_lookup.csv      : mapping lokasi_sirup -> kabkota_id (untuk join cepat)
  - kabkota_clean.geojson : geojson dengan properties disederhanakan
  - unmatched_report.txt : daftar lokasi yang gagal di-match (untuk manual fix)
"""

import json
import re
import pandas as pd
from difflib import get_close_matches
import unicodedata

GEOJSON_PATH = 'kabkota.geojson'
DATA_PATH = 'output/data_network.csv'        # ganti sesuai lokasimu
OUTPUT_LOOKUP   = 'geo/geo_lookup.csv'
OUTPUT_GEOJSON  = 'geo/kabkota_clean.geojson'
OUTPUT_REPORT   = 'geo/unmatched_report.txt'

# ── Normalisasi teks ──────────────────────────────────────────────────────────
def normalize(s):
    if pd.isna(s):
        return ''
    s = str(s).upper()
    s = unicodedata.normalize('NFKD', s)
    s = re.sub(r'[^A-Z0-9\s]', ' ', s)
    s = re.sub(r'\bKAB\b|\bKABUPATEN\b', '', s)
    s = re.sub(r'\bKOTA\b', '', s)
    s = re.sub(r'\bADM\b|\bADMINISTRASI\b', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

# Mapping provinsi pemekaran baru -> provinsi induk (geojson belum punya yang baru)
PROVINSI_PEMEKARAN = {
    'PAPUA TENGAH': 'PAPUA',
    'PAPUA PEGUNUNGAN': 'PAPUA',
    'PAPUA SELATAN': 'PAPUA',
    'PAPUA BARAT DAYA': 'PAPUA BARAT',
}

def normalize_provinsi(s):
    s = str(s).strip()
    # Fix DI Yogyakarta SEBELUM normalize umum (karena normalize() hapus titik)
    s = re.sub(r'^DI\s+Yogyakarta$', 'Daerah Istimewa Yogyakarta', s, flags=re.IGNORECASE)
    s_norm = normalize(s)
    if s_norm in PROVINSI_PEMEKARAN:
        s_norm = PROVINSI_PEMEKARAN[s_norm]
    return s_norm

# ── Load GeoJSON ──────────────────────────────────────────────────────────────
print("Loading geojson...")
with open(GEOJSON_PATH) as f:
    geo = json.load(f)

print(f"  Total features: {len(geo['features'])}")

# Build lookup table dari geojson: normalized_name -> kabkot_id
geo_lookup = []
for feat in geo['features']:
    props = feat['properties']
    geo_lookup.append({
        'kabkot_id':   f"{props['province_id']}.{props['kabkot_id']}",
        'prov_name':   props['prov_name'],
        'prov_norm':   normalize(props['prov_name']),
        'name':        props['name'],
        'name_norm':   normalize(props['name']),
        'alt_name':    props.get('alt_name', ''),
    })
df_geo = pd.DataFrame(geo_lookup)

# ── Load data SIRUP ───────────────────────────────────────────────────────────
print("\nLoading data SIRUP...")
df = pd.read_csv(DATA_PATH, low_memory=False, usecols=['lokasi'])
unique_lokasi = df['lokasi'].dropna().unique()
print(f"  Unique lokasi: {len(unique_lokasi)}")

# ── Parsing & Matching ────────────────────────────────────────────────────────
def parse_single_lokasi(loc_str):
    """Parse SATU lokasi 'Provinsi, Nama (Kab./Kota)' -> (provinsi, nama_kabkota)"""
    parts = str(loc_str).split(',', 1)
    if len(parts) != 2:
        return None, None
    provinsi = parts[0].strip()
    rest = parts[1].strip()
    nama = re.sub(r'\s*\((Kab\.?|Kota)\)\s*$', '', rest).strip()
    nama = re.sub(r'\(Kab\)$', '', nama).strip()  # handle "Sijunjung(Kab)" tanpa spasi/titik
    return provinsi, nama

