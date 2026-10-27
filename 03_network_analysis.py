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

