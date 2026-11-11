# Implementation Inventory

Audit read-only pada 11 November 2026. Status: IMPLEMENTED (kode ada dan diuji atau dijalankan), PARTIAL (ada dengan batas), NOT IMPLEMENTED. Hanya IMPLEMENTED/PARTIAL yang boleh digambarkan sebagai fitur di proposal.

| Modul | Status | Bukti kode | Bukti uji | Batas yang dinyatakan |
|---|---|---|---|---|
| Pipeline EDA, cleaning, patch lembaga | IMPLEMENTED | 00_eda.py, 01_cleaning.py, 01b_patch_lembaga_provinsi.py | 05_validate.py, tests/test_validate.py | Dedup, pagu > 0, koreksi nama lembaga |
| Scoring 7 sinyal dan RPI | IMPLEMENTED | 02_scoring.py | Distribusi RPI dikueri dari Parquet. 06_sensitivity_analysis.py | Bobot pertimbangan tim, tidak divalidasi auditor. Ambang tidak ada bukti kalibrasi |
| Knowledge Graph dan metrik | IMPLEMENTED | 03_network_analysis.py, output/kg_*.csv | kg_summary.txt | Kolom kg_pagerank sebenarnya weighted degree ternormalisasi. Tidak ada simpul penyedia |
| Geo matching | PARTIAL | 03b_geo_matching.py, geo/ | geo/unmatched_report.txt | 46 string lokasi multi wilayah sebagian gagal. Pemekaran belum seluruhnya |
| API analitik (dashboard, packages, charts, kg, geo, filters, meta, overview) | IMPLEMENTED | api/routers/*.py | tests/test_api_filters.py | Mode Parquet view hanya baca |
| Kesegaran data (live vs snapshot) | IMPLEMENTED | api/freshness.py, scraper/sirup.py, scraper/delta.py | tests/test_freshness.py, tests/test_scraper.py | Skor tetap dari snapshot. Data live belum masuk analisis |
| Package Passport | IMPLEMENTED | web/src/pages/PackagePage.tsx | e2e smoke | Perbandingan live bergantung koneksi ke SIRUP |
| Autentikasi dan peran | IMPLEMENTED | api/auth.py (scrypt, token HMAC) | tests/test_cases_workflow.py | Belum diaudit keamanan independen |
| Alur penugasan (7 fase, gerbang kesiapan) | IMPLEMENTED | api/routers/cases.py | tests/test_cases_workflow.py (11 uji), e2e | Satu penugasan aktif per paket |
| Generator program audit dari pasal | IMPLEMENTED | api/audit_program.py | tests/test_audit_program.py | Rujukan pasal dari Perpres 16/2018 jo. 12/2021 jo. 46/2025 |
| Bukti (bentuk, teknik, asal, relevan/valid/andal, SHA-256) | IMPLEMENTED | api/routers/cases.py, api/appdb.py | test_cases_workflow, e2e | Unggah maks 5 MB, tipe dibatasi dan diperiksa magic bytes |
| Temuan, tanggapan, tindak lanjut | IMPLEMENTED | api/routers/cases.py | test_cases_workflow | |
| Jejak peristiwa dan cetak laporan | IMPLEMENTED | case_events, SummaryTab.tsx | e2e | Cetak lewat dialog cetak peramban |
| Frontend (dasbor, peta, analitik, jaringan, tabel) | IMPLEMENTED | web/src | tsc dan vite build lolos | Uji kebergunaan belum ada |
| Responsif | IMPLEMENTED | Tailwind | Tangkapan layar 390, 820, 1440 px | Tidak diuji pada perangkat fisik |
| Docker | IMPLEMENTED | Dockerfile, docker-compose.yml | docs/DEPLOY_DOCKER.md (40/40 e2e, restart mempertahankan data) | Diuji arm64 saja. Tidak diuji dari internet/HTTPS |
| Deployment publik | NOT IMPLEMENTED | railway.toml, vercel.env ada tetapi tidak aktif | - | Tidak ada URL publik |
| Integrasi SDI/BPK/BPKP/LKPP | NOT IMPLEMENTED | - | - | Tidak diklaim |
| Validasi dengan auditor, usability testing | NOT IMPLEMENTED | - | - | Dinyatakan sebagai saran |
| Wawancara/survei | NOT IMPLEMENTED | - | - | Persona berbasis literatur |

## Hasil pengujian pada sesi ini
- pytest (tests, tanpa e2e): 45 passed, 1 warning (peringatan deprecasi httpx pada starlette testclient).
- tsc --noEmit: tanpa galat. Vite build: berhasil (peringatan ukuran chunk saja).
- Uji e2e Docker (40/40) dicatat sesi sebelumnya dan tidak dijalankan ulang.
- Catatan: pemeriksaan tipe pernah menggunakan konfigurasi yang kosong (vacuous), telah diperbaiki dan diungkapkan sebelumnya.
