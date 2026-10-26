"""
Auditra - Patch: Hapus baris dengan lembaga = nama provinsi murni
Data quality issue dari SIRUP: sebagian baris kolom 'lembaga' keisi nama
provinsi polos (bukan nama instansi), sehingga mencemari dropdown filter
'Lembaga' di dashboard dengan entri yang seharusnya cuma ada di filter
'Provinsi'.

Jalankan SETELAH 01_cleaning.py tapi SEBELUM 02_scoring.py jika kamu sudah
punya data_clean.csv dari run sebelumnya dan tidak mau cleaning ulang dari awal.

Bisa juga dijalankan di tahap manapun (data_scored.csv, data_network.csv)
karena hanya filter baris, tidak mengubah kolom.
"""

import pandas as pd

INPUT_PATH  = 'data/data_clean.csv'    # ganti ke tahap data yang mau dipatch
OUTPUT_PATH = 'data/data_clean.csv'    # overwrite in-place, atau ganti nama baru

LIST_PROVINSI = {
    'aceh','sumatera utara','sumatera barat','riau','jambi','sumatera selatan',
    'bengkulu','lampung','kepulauan bangka belitung','kepulauan riau','dki jakarta',
    'jawa barat','jawa tengah','di yogyakarta','daerah istimewa yogyakarta','jawa timur',
    'banten','bali','nusa tenggara barat','nusa tenggara timur','kalimantan barat',
    'kalimantan tengah','kalimantan selatan','kalimantan timur','kalimantan utara',
    'sulawesi utara','sulawesi tengah','sulawesi selatan','sulawesi tenggara','gorontalo',
