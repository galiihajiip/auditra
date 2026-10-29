"""DuckDB data layer — materialized cache for fast repeated queries."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

import duckdb
import pandas as pd

from api.cache import TTLCache
from api.config import (
    DASHBOARD_CACHE_SIZE,
    DATA_CHUNKS_DIR,
    DATA_CHUNKS_GLOB,
    DATA_NETWORK_CSV,
    DATA_NETWORK_PARQUET,
    DUCKDB_CACHE,
    GEO_LOOKUP_CSV,
    GEOJSON_PATH,
    KG_EDGES_CSV,
    KG_NODES_CSV,
)
from api.filters import build_where
from api.owner_category import MAP_MODES, OWNER_CATEGORY_EXPR


