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

# Tambah semua edge dengan weight = jumlah paket + avg RPI
print("  Menambah edges...")

# lembaga → satker
ls_weight = df.groupby(['lembaga','satker']).agg(
    n=('id','count'), avg_rpi=('RPI','mean')
).reset_index()
for _, row in ls_weight.iterrows():
    G.add_edge(f"L::{row['lembaga']}", f"SK::{row['satker']}",
               relation='HAS_SATKER', weight=row['n'], avg_rpi=round(row['avg_rpi'],2))

# satker → metode
sm_weight = df.groupby(['satker','metode']).agg(
    n=('id','count'), avg_rpi=('RPI','mean')
).reset_index()
for _, row in sm_weight.iterrows():
    G.add_edge(f"SK::{row['satker']}", f"M::{row['metode']}",
               relation='USES_METHOD', weight=row['n'], avg_rpi=round(row['avg_rpi'],2))

# satker → jenis
sj_weight = df.groupby(['satker','jenisPengadaan']).agg(
    n=('id','count'), avg_rpi=('RPI','mean')
).reset_index()
for _, row in sj_weight.iterrows():
    G.add_edge(f"SK::{row['satker']}", f"J::{row['jenisPengadaan']}",
               relation='PROCURES', weight=row['n'], avg_rpi=round(row['avg_rpi'],2))

# lembaga → provinsi
lp_weight = df.groupby(['lembaga','provinsi']).agg(
    n=('id','count')
).reset_index()
for _, row in lp_weight.iterrows():
    G.add_edge(f"L::{row['lembaga']}", f"P::{row['provinsi']}",
               relation='OPERATES_IN', weight=row['n'])

print(f"  Nodes: {G.number_of_nodes():,}")
print(f"  Edges: {G.number_of_edges():,}")

# ── Hitung Centrality Metrics ─────────────────────────────────────────────────
print("\nMenghitung centrality metrics...")

# Degree centrality (normalized)
degree_cent = nx.degree_centrality(G)

# In-degree centrality (seberapa banyak yang "pointing ke" node ini)
in_degree_cent = nx.in_degree_centrality(G)

# Weighted Degree Centrality — lebih meaningful dari PageRank untuk sparse graph
# = total bobot edge (jumlah paket) yang masuk/keluar dari node
print("  Weighted degree centrality...")
weighted_degree = {}
for node in G.nodes():
    out_weight = sum(d.get('weight', 1) for _, _, d in G.out_edges(node, data=True))
    in_weight  = sum(d.get('weight', 1) for _, _, d in G.in_edges(node, data=True))
    weighted_degree[node] = out_weight + in_weight

# Normalize ke 0-1
max_wd = max(weighted_degree.values()) if weighted_degree else 1
pagerank = {n: v / max_wd for n, v in weighted_degree.items()}  # pakai nama pagerank agar kompatibel

# Risk-weighted influence — untuk lembaga: weighted degree * avg_rpi node
print("  Risk-weighted influence score...")
risk_influence = {}
for node in G.nodes():
    avg_rpi = G.nodes[node].get('avg_rpi', 0)
    wd = weighted_degree.get(node, 0)
    risk_influence[node] = (wd / max_wd) * (avg_rpi / 100)

# Betweenness centrality hanya untuk lembaga & satker nodes (mahal secara komputasi)
print("  Betweenness centrality (subgraph lembaga-satker)...")
lembaga_satker_nodes = [n for n in G.nodes if G.nodes[n]['type'] in ('lembaga', 'satker')]
subG = G.subgraph(lembaga_satker_nodes)
betweenness = nx.betweenness_centrality(subG, weight='weight', normalized=True)
# Isi 0 untuk node yang tidak ada di subgraph
betweenness_full = {n: betweenness.get(n, 0) for n in G.nodes}

# ── Deteksi Komunitas / Cluster ───────────────────────────────────────────────
print("\nDeteksi cluster lembaga berisiko...")

# Buat undirected graph hanya untuk lembaga nodes
lembaga_nodes = [n for n in G.nodes if G.nodes[n]['type'] == 'lembaga']
G_lembaga = G.subgraph(lembaga_nodes).to_undirected()

# Tambah edge antar lembaga yang punya satker overlap (connected via satker)
G_lembaga_full = nx.Graph()
G_lembaga_full.add_nodes_from(lembaga_nodes)

# Lembaga terhubung jika share metode berisiko yang sama di satker
METODE_BERISIKO = {'Penunjukan Langsung', 'Dikecualikan'}
lembaga_berisiko_methods = defaultdict(set)
for _, row in df[df['metode'].isin(METODE_BERISIKO)].iterrows():
    lembaga_berisiko_methods[f"L::{row['lembaga']}"].add(row['metode'])

# Buat edge berdasarkan shared risk profile
lembaga_list = list(lembaga_berisiko_methods.keys())
for i in range(len(lembaga_list)):
    for j in range(i+1, len(lembaga_list)):
        shared = lembaga_berisiko_methods[lembaga_list[i]] & \
                 lembaga_berisiko_methods[lembaga_list[j]]
        if shared:
            G_lembaga_full.add_edge(lembaga_list[i], lembaga_list[j],
                                    weight=len(shared))

# Greedy modularity communities
if G_lembaga_full.number_of_edges() > 0:
    from networkx.algorithms.community import greedy_modularity_communities
    communities = list(greedy_modularity_communities(G_lembaga_full, weight='weight'))
    community_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            community_map[node] = i
else:
    community_map = {}

print(f"  Cluster terdeteksi: {len(set(community_map.values()))}")

