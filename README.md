<p align="center">
  <img src="web/public/logo-header.png" alt="Auditra" width="160" />
</p>

<h1 align="center">Auditra</h1>

<p align="center">
  <strong>Sistem Prioritas Audit Pengadaan Publik berbasis Knowledge Graph &amp; Analisis Jaringan</strong><br/>
  Mengolah ~3 juta paket SIRUP LKPP untuk membantu auditor fokus pada yang paling mendesak — bukan menebak.
</p>

<p align="center">
  <a href="https://github.com/danisharizka/auditra">GitHub</a> ·
  <a href="https://sirup.lkpp.go.id/">SIRUP LKPP</a> ·
  Tim <code>SD2026020000253</code> · TA 2026
</p>

<p align="center">
  <img src="https://img.shields.io/badge/data-SIRUP%20LKPP-269494?style=flat-square" alt="SIRUP LKPP" />
  <img src="https://img.shields.io/badge/rows-3.002.992-1e3a5f?style=flat-square" alt="3M rows" />
  <img src="https://img.shields.io/badge/stack-FastAPI%20%2B%20React-646cff?style=flat-square" alt="Stack" />
  <img src="https://img.shields.io/badge/PWA-ready-000000?style=flat-square" alt="PWA" />
</p>

---

## Mengapa Auditra?

Indonesia mencatat **jutaan rencana paket pengadaan** di SIRUP setiap tahun. Auditor dan pemeriksa tidak mungkin menelusuri semuanya satu per satu. Auditra menjawab pertanyaan praktis:

> **Paket mana yang paling layak masuk antrean audit berikutnya — dan mengapa?**

Bukan dengan skor hitam-putih, melainkan **Risk Priority Index (RPI)**: alat **prioritas**, bukan vonis. Setiap angka dapat ditelusuri ke **7 sinyal risiko** yang transparan, diperkaya **Knowledge Graph** lembaga–satker, dan divisualisasikan di dashboard interaktif peta seluruh Indonesia.

---

## Fitur Dashboard

| Modul | Apa yang bisa dilakukan |
|-------|-------------------------|
| **KPI & Stat Cards** | Total paket, pagu berisiko, distribusi tier risiko, cakupan geografi |
| **Peta Choropleth** | Prioritas audit per kab/kota — seluruh Indonesia; 4 mode pemilik (K/L · Pemprov · Pemkot · Lainnya); toggle RPI / Pagu Berisiko |
| **Sidebar Lembaga** | Top lembaga prioritas audit; klik untuk filter; tier Ekstrem (KRITIS + anomali) |
| **7 Sinyal RPI** | Radar chart profil risiko; bar chart per metode; scatter pagu vs RPI |
| **Knowledge Graph** | Subgraf lembaga–satker mengikuti filter aktif; kesimpulan otomatis |
| **Daftar Paket** | Tabel prioritas dengan pagination (50/halaman) — akses penuh ke dataset via API |
| **Filter Global** | Provinsi · Lembaga · Metode · Ambang RPI minimum |
| **Tema & PWA** | Dark / light mode; installable di mobile & desktop; responsif PC–tablet–ponsel |

**Integritas data:** statistik agregat, ranking, peta, dan KG dihitung dari **seluruh baris** yang cocok filter. Satu-satunya sampling eksplisit: scatter chart (max 3.000 titik acak untuk performa render).

Verifikasi runtime:

```http
GET http://127.0.0.1:8000/api/meta
```

---

## 7 Sinyal RPI (Ringkas)

| # | Sinyal | Bobot | Intuisi |
|---|--------|-------|---------|
| S1 | Metode pemilihan | 20% | Penunjukan langsung / dikecualikan = risiko tata kelola lebih tinggi |
| S2 | Anomali pagu | 20% | Z-score pagu dalam grup `(jenis, metode)` |
| S3 | Fragmentasi / split contract | 15% | TF-IDF + cosine similarity uraian dalam satker (batas PL Rp 200 jt) |
| S4 | Konsentrasi metode berisiko | 15% | Proporsi penunjukan/dikecualikan per satker |
| S5 | Anomali UMKM | 10% | Flag UMKM vs pagu besar |
| S6 | Dana + metode | 10% | Kombinasi sumber dana APBN dan metode berisiko |
| S7 | Reputasi lembaga (KG) | 10% | Risk influence node lembaga di Knowledge Graph (weighted degree × avg RPI) |

Formula lengkap, dasar regulasi (PP 12/2019, Perpres 16/2018), dan analisis sensitivitas bobot → [`docs/METODOLOGI.md`](docs/METODOLOGI.md).

---
