# Fact Reconciliation

Prinsip: angka mengikuti data dan kode yang dapat diperiksa ulang, bukan dokumen naratif. Penanda Unverified berarti tidak dapat diverifikasi dari repo atau data.

| Fakta | Source of truth | Value selected | Reason | Proposal treatment |
|---|---|---|---|---|
| Jumlah paket analitik | Kueri DuckDB atas output/chunks (11 Nov 2026) | 3.002.992 | Data aktual. SEC menulis 3.009.668 (mentah) dan 3.002.678 (final) | Dipakai. Angka SEC tidak dipakai |
| Jumlah lembaga | Kueri DuckDB | 662 | SEC menulis 663 | Dipakai 662 |
| Jumlah satker | Kueri DuckDB | 34.602 | SEC menulis 34.618 | Dipakai 34.602 |
| Simpul dan sisi KG | output/kg_summary.txt | 35.320 simpul, 207.427 sisi | SEC menulis 35.317 dan 207.375 | Dipakai angka repo |
| Paket tinggi dan kritis | Kueri DuckDB | 23.626 tinggi + 568 kritis = 24.194 (0,806%) | SEC menulis 45.367 (1,51%) | Dipakai angka repo |
| Total pagu | Kueri DuckDB | Rp640,70 triliun | Hanya agregat rencana | Dinyatakan sebagai pagu rencana, bukan realisasi |
| Paket SIRUP saat ini | Hasil crawl 11 Nov 2026 (dasbor) | sekitar 3,65 juta (selisih sekitar 643 ribu belum dianalisis) | Crawl dinyatakan lengkap dan terekonsiliasi | Dinyatakan sebagai batas snapshot |
| Bobot dan rumus RPI | Skrip 02_scoring.py dan 03_network_analysis.py | 0,20/0,20/0,15/0,15/0,10/0,10/0,10 | Kode | Dipakai |
| Ambang kategori 30/50/70 | Kode | Dipakai | docs/METODOLOGI.md menyebut kalibrasi, tidak ada bukti di kode | Tidak disebut dikalibrasi. Unverified bila ada klaim kalibrasi |
| "PageRank" | Kode (03_network_analysis) | Weighted degree ternormalisasi | Nama kolom menyesatkan | Dijelaskan di Bab III butir b |
| "100% transparan" (pitch deck) | Tidak dapat dibuktikan | Tidak dipakai | Klaim absolut | Diganti pernyataan keterbukaan metode |
| Jumlah uji otomatis | pytest 11 Nov 2026 | 45 lolos | Dijalankan ulang | Dipakai |
| Uji ujung ke ujung Docker | docs/DEPLOY_DOCKER.md | 40/40 lolos (sesi sebelumnya) | Tidak dijalankan ulang pada sesi ini | Dinyatakan "sebelumnya mencatat" |
| Nama anggota | Pengguna | Galih, Nashwa, Adristha (UPNVJT) | Footer dan README memuat nama tim SEC lama | Footer dan README diperbarui. Tangkapan layar footer dipotong |
| ID tim SEC SD2026020000253 | SEC | Tidak dipakai | Bukan identitas tim WIA | Dihapus dari footer dan README |
| Tautan GitHub | FDS dan pengguna | github.com/galiihajiip/auditra | Footer lama menunjuk danisharizka/auditra | Diperbarui |
| URL aplikasi publik | Pengguna | Belum ada | Tidak ada deployment | Dicatat Belum tersedia pada Lampiran |
| Figma | Pengguna | Akan dilampirkan | Belum diterima | Penanda pada Lampiran |
| Validasi dengan auditor | Tidak ada | Tidak dilakukan | Tidak ada wawancara | Persona diberi label berbasis literatur. Unverified bila klaim efektivitas |
| Kualitas data SIRUP | Sifat data | Self-reported | Tidak diverifikasi lapangan | Dinyatakan pada batasan |
