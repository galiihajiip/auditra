# Auditra Web Dashboard (FastAPI + React)

Stack **Opsi A**: Python backend + React frontend. **Seluruh 3 juta baris tetap utuh** di file sumber; API hanya mengirim agregat/pagination ke browser.

## Integritas data

| Lapisan | Isi |
|---|---|
| `output/data_network.csv` | **100% baris & kolom** pipeline (di `.gitignore`) |
| DuckDB | Query tanpa memotong source file |
| `GET /api/meta` | Verifikasi `total_rows` & `total_columns` |
| `GET /api/packages?page=N` | Akses **semua** baris via pagination (50/halaman) |
| Browser | Hanya terima JSON ringkas untuk chart/tabel |

Satu-satunya "sample" eksplisit: **scatter chart** (max 3.000 titik random untuk performa). Stat cards, peta, ranking, dan tabel menghitung dari **seluruh** baris yang match filter.

