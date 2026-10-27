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

