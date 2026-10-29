"""Auditra API configuration — paths resolve from project root."""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_NETWORK_CSV = ROOT / "output" / "data_network.csv"
DATA_NETWORK_PARQUET = ROOT / "output" / "data_network.parquet"
DATA_CHUNKS_DIR = ROOT / "output" / "chunks"
DATA_CHUNKS_GLOB = DATA_CHUNKS_DIR / "*.parquet"
DUCKDB_CACHE = ROOT / "output" / "auditra.duckdb"
KG_NODES_CSV = ROOT / "output" / "kg_nodes.csv"
KG_EDGES_CSV = ROOT / "output" / "kg_edges.csv"
GEO_LOOKUP_CSV = ROOT / "geo" / "geo_lookup.csv"
