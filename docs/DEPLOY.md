# Deploy Auditra

Arsitektur **split**: frontend static + backend Python dengan data besar.

```
[Vercel]  React (web/dist)     ──HTTPS──▶  [Railway/Render/VPS]  FastAPI + DuckDB
                                              ↑
                                    output/auditra.duckdb (~500MB–2GB)
                                    geo/kabkota_clean.geojson
```

---

## Bisa pakai Vercel?

| Komponen | Vercel? | Alasan |
|----------|---------|--------|
| **Frontend** (`web/`) | ✅ **Ya** | Static React/Vite — ideal untuk Vercel |
| **Backend** (`api/`) | ❌ **Tidak** | DuckDB + file 1GB+ butuh disk persisten & proses long-running |
| **Pipeline Python** | ❌ | Jalankan lokal/CI, upload hasil `output/` ke server |

Vercel serverless: limit ukuran deployment, **tidak ada disk persisten**, timeout function — tidak cocok untuk query 3 juta baris via DuckDB.

---

## Opsi deploy (disarankan)

### Opsi A — Vercel + Railway (paling mudah untuk demo)

**1. Backend di [Railway](https://railway.app) atau [Render](https://render.com)**

Persiapan file data (setelah `python run_pipeline.py`):

```
output/auditra.duckdb      ← wajib (atau parquet + auto-build saat startup)
output/data_network.parquet
geo/geo_lookup.csv
geo/kabkota_clean.geojson
output/kg_nodes.csv
output/kg_edges.csv
```

Upload via volume/persistent disk atau commit ke private storage lalu download saat build.

**Start command:**

```bash
pip install -r requirements-web.txt && uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

**Environment variables (backend):**

```
CORS_ORIGINS=https://auditra.vercel.app,https://your-team.vercel.app
```
