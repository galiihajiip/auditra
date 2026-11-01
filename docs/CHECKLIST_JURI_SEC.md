# Checklist Juri — Statistics Essay Competition (SEC)

Pemetaan karya **Auditra** terhadap [kriteria penilaian SEC Satria Data](https://satriadata.kemdikbud.go.id/) (Pedoman 2024, struktur 2026 serupa).

---

## Ringkasan: Apakah Aman Lolos Final?

**Implementasi teknis: kuat (8/10).**  
**Esai + presentasi: menentukan (6–9/10)** — bergantung penulisan, orisinalitas Turnitin, dan kemampuan tim menjawab tanya jawab.

Tidak ada yang **otomatis** menjamin lolos final — kompetisi memilih 12 tim dari ratusan. Yang bisa dipastikan: **tidak ada celah fatal** di sisi metodologi/data jika esai dan demo selaras dengan repo ini.

---

## Tahap Penyisihan (Bobot Kriteria)

### 1. Orisinalitas (20%)

| Kriteria | Status | Catatan |
|----------|--------|---------|
| Belum pernah dilombakan | ⚠️ **Tim wajib pastikan** | Surat orisinalitas SEC wajib |
| Turnitin < 25% | ⚠️ **Cek sebelum upload** | Kutip regulasi + metode standar (TF-IDF, z-score) wajar; parafrase sendiri |
| Tidak plagiat | ✅ | Pipeline ditulis khusus proyek ini |

**Risiko:** Esai yang terlalu mirip paper KG/audit umum → similarity tinggi. **Solusi:** tekankan konteks Indonesia, SIRUP, 7 sinyal spesifik Auditra.

---

### 2. Penulisan (15%)

| Kriteria | Status |
|----------|--------|
| Struktur pendahuluan–pembahasan–penutup | ⚠️ Esai tim |
| PUEBI, 2000–3000 kata | ⚠️ Esai tim |
| Tabel/gambar terbaca | ✅ Sediakan dari `output/reports/eda_charts.html`, dashboard screenshot |
| Persamaan standar | ✅ Gunakan formula di [METODOLOGI.md](METODOLOGI.md) |

---

### 3. Kesesuaian Tema (15%)

**Tema 2026:** *Integrasi Sains, Teknologi, dan Industri dalam Menghadapi Tren Sains Data di Era Society 5.0*

| Kriteria | Status | Rekomendasi |
|----------|--------|-------------|
| Judul sesuai tema | ✅ | Auditra + Satu Data + Society 5.0 |
| Sub-tema resmi | ⚠️ | Pilih **Sosial-Ekonomi** (pengadaan = belanja negara) — jangan buat sub-tema sendiri di form jika panitia hanya sediakan 5 opsi |
| Kontribusi masyarakat | ✅ | Efisiensi audit → penghematan APBN, transparansi |

---

### 4. Substansi dan Data (40%) — **PALING KRITIS**

| Kriteria | Status | Bukti di Repo |
|----------|--------|---------------|
| Sumber data jelas | ✅ | [SUMBER_DATA.md](SUMBER_DATA.md) — SIRUP LKPP 2026 |
| Data terkini & reliabel | ✅ | 3.009.760 baris mentah → 3.002.992 setelah cleaning |
| Metode step-by-step | ✅ | `00`→`05` + [METODOLOGI.md](METODOLOGI.md) |
| Analisis deskriptif → lanjutan | ✅ | EDA → z-score → TF-IDF → KG → geo |
| Inovatif & aplikatif | ✅ | RPI + KG + dashboard interaktif |
| **Tanpa ML supervised** | ✅ by design | Jelaskan: tidak ada label ground-truth audit |

**Yang WAJIB disebutkan di esai (juri pasti tanya):**

1. **Kenapa rule-based, bukan ML?** — Tidak ada label "terbukti korup"; RPI = heuristik regulasi + statistik deskriptif.
2. **Bobot RPI 0.20/0.20/…** — Dasar domain + sensitivity analysis (`06_sensitivity_analysis.py`).
3. **Scatter chart 3.000 titik** — Hanya visualisasi; statistik card/peta/tabel = **100% baris** via DuckDB.
4. **Limitasi geo** — 46 lokasi komposit edge case (`geo/unmatched_report.txt`), match rate 99,2%.

---

### 5. Penarikan Kesimpulan (10%)

| Kriteria | Status |
|----------|--------|
| Kesimpulan selaras analisis | ⚠️ Esai tim — gunakan angka dari `output/scoring_log.txt`, `kg_summary.txt` |
| Rekomendasi aplikatif | ✅ Integrasi API BPK/Inspektorat, refresh data SIRUP berkala |
| Saran penelitian lanjut | ✅ Validasi dengan temuan audit riil, semi-supervised learning |

---

