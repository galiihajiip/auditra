"""
Auditra - Step 3: Network Analysis & Knowledge Graph
Membangun Knowledge Graph dari relasi pengadaan, menghitung centrality,
dan mendeteksi cluster lembaga berisiko.

Node types:
  - Lembaga
  - Satker
  - Metode
  - JenisPengadaan
  - Lokasi (provinsi)

Edge types:
  - lembaga → satker         (HAS_SATKER)
  - satker → metode          (USES_METHOD)
  - satker → jenisPengadaan  (PROCURES)
  - lembaga → lokasi         (OPERATES_IN)

Output:
  - data_network.csv  : df dengan tambahan kolom network metrics
  - kg_nodes.csv      : semua node + metrics
  - kg_edges.csv      : semua edge + weight
  - kg_summary.txt    : ringkasan untuk esai
"""

import pandas as pd
import numpy as np
import networkx as nx
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

INPUT_PATH        = 'output/data_scored.csv'   # ganti sesuai lokasimu
OUTPUT_DATA       = 'output/data_network.csv'
OUTPUT_NODES      = 'output/kg_nodes.csv'
OUTPUT_EDGES      = 'output/kg_edges.csv'
OUTPUT_SUMMARY    = 'output/kg_summary.txt'

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading scored data...")
df = pd.read_csv(INPUT_PATH, low_memory=False)
print(f"  Shape: {df.shape}")

# Ekstrak provinsi dari kolom lokasi (format: "Provinsi, Kota (Kab.)")
df['provinsi'] = df['lokasi'].astype(str).str.split(',').str[0].str.strip()

# ── Bangun Knowledge Graph ────────────────────────────────────────────────────
print("\nMembangun Knowledge Graph...")

G = nx.DiGraph()

# Helper: tambah node dengan attributes
def add_node(G, node_id, node_type, **attrs):
    G.add_node(node_id, type=node_type, **attrs)

# Tambah semua node
lembaga_rpi   = df.groupby('lembaga')['RPI'].mean().to_dict()
lembaga_count = df.groupby('lembaga')['id'].count().to_dict()

satker_rpi    = df.groupby('satker')['RPI'].mean().to_dict()
satker_count  = df.groupby('satker')['id'].count().to_dict()

for lembaga in df['lembaga'].unique():
    add_node(G, f"L::{lembaga}", 'lembaga',
             label=lembaga,
             avg_rpi=round(lembaga_rpi.get(lembaga, 0), 2),
             n_paket=lembaga_count.get(lembaga, 0))

for satker in df['satker'].unique():
    add_node(G, f"SK::{satker}", 'satker',
             label=satker,
             avg_rpi=round(satker_rpi.get(satker, 0), 2),
             n_paket=satker_count.get(satker, 0))

for metode in df['metode'].unique():
    add_node(G, f"M::{metode}", 'metode', label=metode)

for jenis in df['jenisPengadaan'].unique():
    add_node(G, f"J::{jenis}", 'jenis', label=jenis)

for prov in df['provinsi'].unique():
    add_node(G, f"P::{prov}", 'provinsi', label=prov)

