# Metodologi Auditra — Step by Step

Dokumen ini melengkapi esai SEC: algoritma ditulis eksplisit agar juri dapat menelusuri setiap langkah.

---

## 1. Sumber Data

Lihat [SUMBER_DATA.md](SUMBER_DATA.md).

---

## 2. Exploratory Data Analysis (Step 0)

**Input:** `data/year-2026_merged.csv` (N = 3.009.760 baris)

1. Profil dimensi, tipe data, missing value per kolom
2. Statistik deskriptif `pagu`: mean, median, kuartil, IQR outlier
3. Distribusi frekuensi: `metode`, `jenisPengadaan`, `lembaga`
4. Identifikasi duplikat `id`, pagu ≤ 0

**Output:** `output/reports/eda_report.md`, `eda_stats.json`, `eda_charts.html`

---

## 3. Preprocessing (Step 1–1b)

1. **Seleksi kolom** — hanya field SIRUP murni; drop enrichment pihak ketiga
2. **Deduplikasi** — `drop_duplicates(id)`
3. **Filter validitas** — `pagu > 0`
4. **Normalisasi teks** — strip whitespace
5. **Encoding kategori** — varian APBN → `sumberDana_cat = 'APBN'`
6. **Patch DQ** — hapus baris `lembaga` = nama provinsi polos (artefak SIRUP)

**Hasil:** N = 3.002.992 baris × 17 kolom

---

