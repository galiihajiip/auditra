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

