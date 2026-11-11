# Final Proposal Audit

Jujur per 11 November 2026. PASS = terverifikasi. UNABLE = tidak dapat diverifikasi pada sesi ini. FAIL = belum memenuhi.

## Daftar periksa
| Item | Hasil | Catatan |
|---|---|---|
| Memakai template resmi (header, gaya, font) | PASS | DOCX dibangun dari template, sampul dan Daftar Isi dipertahankan |
| Tidak ada placeholder template | PASS | Dicek pada teks paragraf (cover, kata pengantar). Kecuali penanda Figma pada Lampiran (sengaja) |
| Nama berkas WIA_PenyisihanMIA2026_NamaTim | PASS (DOCX) / FAIL (PDF) | PDF belum ada |
| Inti maksimal 30 halaman | UNABLE | Estimasi 26 dari render HTML. Perlu PDF Word |
| Daftar Isi terisi | FAIL sementara | Berisi entri bawaan template. updateFields diaktifkan: Word akan menawarkan pembaruan saat dibuka. Perlu Update Field lalu ekspor PDF |
| Tanpa em dash | PASS | Dicek pada seluruh teks dokumen |
| Tanpa titik dua dan titik koma pada narasi | PASS (sumber) | Lint pada content.py. Tabel dan label Sumber dikecualikan |
| Sitasi APA 7 dua arah | PASS | 16 referensi, semua dikutip. Semua kutipan ada di daftar |
| Referensi tervalidasi | PASS | 11 DOI Crossref. Regulasi dibaca. URL rinci JDIH tidak dicatat |
| Gambar dan tabel bernomor, ada caption dan Sumber | PASS | 25 gambar, 11 tabel |
| Tangkapan layar nyata | PASS | Dari aplikasi berjalan, MANIFEST.json |
| Tanpa klaim absolut, RPI sebagai heuristik | PASS | Lint kata absolut |
| Tidak ada wawancara atau survei fiktif | PASS | Persona berlabel berbasis literatur |
| Tidak ada klaim integrasi resmi | PASS | Dinyatakan di batasan |
| Kode sumber tidak diubah | PASS dengan catatan | Hanya SiteFooter.tsx dan README.md (nama tim) atas permintaan pengguna |
| Pemeriksaan visual halaman Word | UNABLE | Word tidak dapat digerakkan. Hanya preview HTML yang dilihat |

## Matriks rubrik
| Kriteria (bobot) | Bukti di proposal | Risiko |
|---|---|---|
| Orisinalitas 20 | Tabel celah, skor terjelaskan, graf, alur penugasan berstandar | Belum divalidasi auditor |
| Fungsionalitas 25 | 45 uji lolos, gerbang kesiapan, user flow, responsif | Tidak ada URL publik untuk juri |
| Desain 20 | 13 layar desktop, ponsel, tablet, diagram | Gambar layar memakai data demo |
| Konten 20 | Sumber tiap klaim, batas jujur, snapshot vs live | Bagian riset pengguna lemah |
| Tema 15 | OGD, SDI, SDG 16, Designing Digital Futures | |

## Item administratif masih kurang
Tautan Figma, URL aplikasi publik, surat orisinalitas bermaterai, tautan Google Drive, video pitching YouTube. Tempat penandatanganan Kata Pengantar diasumsikan Surabaya.
