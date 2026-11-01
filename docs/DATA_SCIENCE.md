# Auditra — Data Science Lifecycle

Dokumen ini memetakan implementasi proyek Auditra terhadap **teori sains data** dari tingkat dasar hingga tingkat tinggi, dari data mentah hingga siap deploy.

---

## Ringkasan Maturitas

| Tahap DS | Status | Implementasi |
|----------|--------|--------------|
| **Problem framing** | ✅ | Audit prioritas pengadaan publik berbasis SIRUP + KG |
| **EDA** | ✅ | `00_eda.py` → `output/reports/eda_*` |
| **Data collection** | ✅ | `data/year-2026_merged.csv` (SIRUP) |
| **Preprocessing / cleaning** | ✅ | `01_cleaning.py`, `01b_patch_lembaga_provinsi.py` |
| **Feature engineering** | ✅ | 7 sinyal risiko di `02_scoring.py` |
| **Anomaly detection** | ✅ | Z-score pagu (S2), IQR outlier di EDA |
| **NLP / similarity** | ✅ | TF-IDF + cosine similarity (S3 fragmentasi) |
| **Graph analytics** | ✅ | Knowledge Graph, centrality, community detection |
| **Geo-spatial join** | ✅ | `03b_geo_matching.py` |
| **Model scoring** | ✅ | Rule-based weighted RPI (bukan ML supervised — by design) |
| **Validation / QA** | ✅ | `05_validate.py`, `pipeline/validate.py` |
| **Visualization** | ✅ | React dashboard + EDA Plotly HTML |
| **Serving / API** | ✅ | FastAPI + DuckDB materialized cache |
| **Deployment** | ⚠️ | Manual run; Docker opsional (lihat bawah) |
| **Monitoring / MLOps** | ❌ | Belum (tidak ada model ML yang perlu retrain) |
| **Supervised ML** | ➖ | Tidak dipakai — domain expert rules + KG |

**Kesimpulan:** Pipeline sudah mencakup **dasar → menengah → lanjut** untuk use case **rule-based risk scoring + knowledge graph**. Yang sebelumnya kurang (EDA formal, validasi terstruktur, orchestrator) sudah dilengkapi.

---

## Alur End-to-End

```mermaid
flowchart LR
    A[Data Mentah SIRUP] --> B[00 EDA]
    B --> C[01 Cleaning]
    C --> D[01b Patch DQ]
    D --> E[02 Feature + RPI]
    E --> F[03 Knowledge Graph]
    F --> G[03b Geo Matching]
    G --> H[05 Validation]
    H --> I[Parquet + DuckDB]
    I --> J[FastAPI + React]
```

---

## Tingkat Dasar

### 1. Exploratory Data Analysis (EDA)
**Script:** `00_eda.py`

- Profil dimensi, tipe data, missing values
- Statistik deskriptif `pagu` (mean, median, percentil)
- Deteksi outlier IQR
- Distribusi kategorikal (metode, jenis, lembaga)
- Kardinalitas (unique lembaga, satker, lokasi)
- Output: `output/reports/eda_report.md`, `eda_stats.json`, `eda_charts.html`

### 2. Preprocessing
**Script:** `01_cleaning.py`, `01b_patch_lembaga_provinsi.py`

| Operasi | Detail |
|---------|--------|
| Column selection | Hanya kolom SIRUP murni; drop enrichment Nemesis AI |
| Deduplication | `drop_duplicates(subset='id')` |
| Invalid filter | `pagu > 0` |
| Text normalization | Strip whitespace |
| Category encoding | `sumberDana` → `sumberDana_cat` (APBN variants) |
| Data quality patch | Hapus baris `lembaga` = nama provinsi polos |

### 3. Validasi Kualitas Data
**Script:** `05_validate.py`, modul `pipeline/validate.py`

- Cek kolom wajib, duplikat, rentang RPI, label risiko
- Integrity row count antar tahap
- Geo lookup completeness

---

## Tingkat Menengah

### 4. Feature Engineering
**Script:** `02_scoring.py`

| Sinyal | Metode | Teori DS |
|--------|--------|----------|
| S1 Metode | Rule-based mapping | Domain knowledge encoding |
| S2 Pagu anomali | Z-score dalam grup | Statistical anomaly detection |
| S3 Fragmentasi | TF-IDF + cosine similarity | NLP + similarity learning |
| S4 Konsentrasi | Rasio agregat per satker | Aggregation features |
| S5 UMKM | Percentile threshold | Rule + distribution |
| S6 Dana+Metode | Boolean combination | Feature interaction |
| S7 Reputasi | KG node weight | Graph-derived feature |

**RPI** = weighted sum (bobot di `config/pipeline.yaml`), skala 0–100.

### 5. Agregasi & Visualisasi
- Pipeline: summary print di setiap script
- Web: agregat penuh via DuckDB (bukan sample kecuali scatter max 3.000 titik)

---

## Tingkat Lanjut / Tinggi

### 6. Knowledge Graph & Network Science
**Script:** `03_network_analysis.py`

- **Graph construction:** Node (lembaga, satker, metode, jenis, provinsi) + weighted edges
- **Centrality:** degree, in-degree, betweenness (subgraph)
- **Influence score:** weighted degree × avg RPI
- **Community detection:** greedy modularity (cluster lembaga berisiko)
- **Feedback loop:** S7 di-update dari graph metrics → RPI recalculated

### 7. Geo-Spatial Integration
**Script:** `03b_geo_matching.py`

- Normalisasi Unicode + fuzzy matching
- Join lokasi SIRUP → kab/kota GeoJSON (514 features)
- Unmatched report untuk manual QA

### 8. Production Data Layer
**Folder:** `api/`

- Materialized DuckDB cache (`output/auditra.duckdb`)
- Parquet columnar storage
- TTL LRU cache untuk dashboard bundle
- Thread-safe queries
- Integrity endpoint `GET /api/meta`

---

