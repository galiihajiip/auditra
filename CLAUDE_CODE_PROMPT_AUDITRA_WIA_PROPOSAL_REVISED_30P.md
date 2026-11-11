# MASTER PROMPT UNTUK CLAUDE CODE

## Penyusunan Proposal Final Auditra untuk Web In Action MIA 2026

> Jalankan Claude Code dari root repository Auditra yang sedang aktif dikembangkan di VS Code. Pastikan seluruh file panduan, hasil review FDS, pitch deck, proposal SEC SATRIA DATA, template proposal WIA, serta Gitingest terbaru tersedia dan dapat dibaca oleh Claude Code. Jika berkas belum berada di root repository, tempatkan berkas tersebut di folder referensi yang mudah ditemukan, misalnya `reference/` atau `input/`, lalu jalankan prompt ini.

---

# 0. PERAN, MANDAT, DAN HASIL AKHIR

Bertindaklah sebagai gabungan dari seorang **principal software architect, senior full-stack engineer, product strategist, civic-tech researcher, academic researcher, UX researcher, technical writer, dan editor proposal kompetisi nasional**. Kamu bertanggung jawab menyusun proposal final Auditra untuk kompetisi Multimedia In Action 2026, cabang Web In Action, mulai dari pemahaman bahan, audit fakta, riset ilmiah dan regulasi, perumusan narasi, pembuatan visual pendukung, penyusunan dokumen, sampai pemeriksaan akhir sebelum submit.

Tugas ini bukan sekadar merangkum proposal Statistics Essay Competition SATRIA DATA 2026. Tugasmu adalah menerjemahkan fondasi riset dan data science Auditra menjadi proposal karya pengembangan aplikasi web yang kuat, dapat diverifikasi, berorientasi pada pengguna, dan sesuai dengan ketentuan WIA. Proposal harus memperlihatkan bahwa Auditra merupakan aplikasi web yang benar-benar dikembangkan, bukan hanya gagasan penelitian atau dashboard statis.

Hasil akhir yang wajib dihasilkan adalah dokumen proposal dalam format DOCX dan PDF, mengikuti template proposal resmi WIA yang dilampirkan. Berdasarkan klarifikasi terbaru panitia melalui chat yang diberikan peserta, batas maksimal 30 halaman hanya menghitung isi inti proposal. Cover, daftar isi, lampiran, dan daftar pustaka tidak masuk hitungan 30 halaman. Karena itu, maksimalkan ruang isi inti hingga 30 halaman yang benar-benar substantif, bukan membatasi seluruh file PDF menjadi 30 halaman. Cover, daftar isi, lampiran, dan daftar pustaka tetap disertakan sesuai template, tetapi ditempatkan di luar hitungan isi inti. Kata Pengantar tidak disebut sebagai bagian yang dikecualikan oleh klarifikasi panitia, sehingga untuk kehati-hatian hitung Kata Pengantar ke dalam 30 halaman isi inti kecuali ada klarifikasi resmi lain. Dokumen harus siap diperiksa dan diserahkan setelah informasi identitas tim, tautan, dan persyaratan administratif yang memang belum tersedia dilengkapi. Jangan mengklaim dokumen administratif sudah ada jika belum disediakan.

Gunakan nama produk **Auditra** secara konsisten. Pertahankan identitas, ruang lingkup, pendekatan, dan kontribusi inti Auditra. Jangan mengganti produk menjadi ide lain, jangan mengubahnya menjadi platform pelaporan warga yang berbeda, dan jangan menambahkan fitur khayalan hanya demi membuat proposal terlihat lebih besar.

## Prinsip paling penting

1. Kebenaran lebih penting daripada klaim yang terdengar mengesankan.
2. Repository aktif di VS Code adalah sumber utama untuk menentukan fitur dan implementasi yang benar-benar ada saat ini.
3. Gitingest adalah snapshot pendukung dan dapat tertinggal dari perkembangan repository. Jangan menganggap Gitingest sebagai keadaan kode terbaru.
4. Dokumen proposal SEC SATRIA DATA adalah sumber bagi latar belakang, pendekatan analitik, hasil penelitian, dan referensi awal. Jangan memindahkan framing esai secara mentah ke WIA.
5. Guidebook WIA dan template proposal WIA adalah acuan utama untuk ketentuan dan struktur dokumen.
6. Hasil review FDS adalah umpan balik pembinaan. Nilainya bukan nilai resmi babak penyisihan dan tidak boleh dipresentasikan sebagai hasil penjurian final.
7. Semua angka, fitur, sitasi, regulasi, dan klaim teknis harus memiliki sumber atau bukti yang dapat diperiksa.
8. Jangan mengubah source code aplikasi saat mengerjakan proposal. Audit repository bersifat read-only. Simpan seluruh keluaran proposal dan asetnya di folder deliverables terpisah.
9. Jangan berhenti setelah membuat outline atau laporan audit. Selesaikan dokumen proposal, visual pendukung, DOCX, PDF, dan checklist kelayakan submit.

---

# 1. KONTEKS KOMPETISI YANG WAJIB DIPATUHI

Kompetisi yang dituju adalah **Multimedia In Action 2026, Web In Action (WIA)**. Tema utama pada materi teknis yang diterima tim adalah **Designing Digital Futures – Powering Public Transparency**. Subtema yang dipilih tim pada FDS adalah **Open Government Data**. Konsep Auditra dapat menunjukkan relevansi pendukung terhadap pengambilan keputusan berbasis data, tetapi jangan mengganti subtema pilihan yang tercatat tanpa alasan dan bukti.

WIA merupakan kompetisi pengembangan aplikasi berbasis web. Karya diharapkan berupa website yang fungsional, responsif, dan menyelesaikan permasalahan nyata. Dengan demikian, proposal harus menonjolkan kualitas produk web, pengalaman pengguna, struktur informasi, interaksi, implementasi teknis, dan kegunaan bagi target pengguna. Metode analitik dan Knowledge Graph tetap menjadi pembeda teknologi, tetapi keduanya harus dijelaskan sebagai kemampuan yang dihadirkan melalui aplikasi.

## 1.1 Rubrik penilaian babak penyisihan

Gunakan bobot ini untuk menentukan penekanan proposal dan bukti yang harus disertakan.

| Kriteria | Bobot | Hal yang harus dibuktikan proposal |
|---|---:|---|
| Orisinalitas Ide dan Konsep | 20% | Masalah jelas, pendekatan khas, alasan kebaruan, dan pembeda terhadap solusi yang sudah ada |
| Fungsionalitas Website | 25% | Modul dan alur kerja nyata, fitur berjalan, navigasi, responsivitas, dan bukti implementasi |
| Desain dan Estetika | 20% | Hierarki informasi, konsistensi visual, keterbacaan, desain responsif, dan screenshot aktual |
| Konten dan Informasi | 20% | Informasi tepat, relevan, dapat ditelusuri, metode dijelaskan, dan keterbatasan diungkap |
| Kesesuaian Tema dan Subtema | 15% | Hubungan eksplisit dengan Open Government Data dan transparansi informasi pengadaan publik |

Rubrik final dalam guidebook menekankan orisinalitas dan konsep website sebesar 15%, fungsionalitas dan user experience sebesar 25%, desain dan kreativitas visual sebesar 20%, serta presentasi dan komunikasi sebesar 20%. Jangan mencoba menyimpulkan sendiri kekurangan bobot yang tidak tertulis. Proposal ini ditujukan untuk penyisihan, tetapi ceritanya harus tetap mudah dikembangkan menjadi pitch final.

## 1.2 Ketentuan pengumpulan yang wajib diverifikasi

Guidebook menetapkan proposal PDF maksimal 30 halaman. Namun, berdasarkan klarifikasi terbaru panitia yang disampaikan melalui chat dan harus diperlakukan sebagai pembaruan ketentuan, cover, daftar isi, lampiran, dan daftar pustaka tidak dihitung dalam batas tersebut. Dengan demikian, isi inti proposal dapat mencapai maksimal 30 halaman di luar empat komponen itu. Jangan menerapkan batas 30 halaman pada total file PDF. Tetap sertakan komponen tersebut sesuai template, tetapi hitung secara terpisah. Kata Pengantar tidak termasuk dalam daftar pengecualian yang disampaikan panitia, sehingga hitung Kata Pengantar ke dalam 30 halaman isi inti. Simpan bukti atau salinan chat klarifikasi dalam bahan kerja jika tersedia. Jika ada pengumuman tertulis resmi yang lebih baru, ikuti pengumuman tersebut dan catat perubahan pada checklist.

Tanggal pada guidebook menyebut final submission penyisihan pada 11 November 2026. Karena tenggat dapat berubah atau telah diperbarui panitia, jangan mengandalkan asumsi. Periksa pengumuman resmi atau informasi terbaru yang diberikan peserta. Jika tidak dapat memverifikasi perubahan, cantumkan tenggat sesuai guidebook sebagai informasi sumber dan tandai kebutuhan konfirmasi pada checklist internal, bukan di isi proposal.

Guidebook menyebut susunan proposal mengikuti template yang disediakan panitia. Gunakan template tersebut sebagai struktur wajib dan jangan mengganti urutannya dengan struktur karya ilmiah bebas.

---

# 2. BERKAS REFERENSI YANG WAJIB DIBACA

Lakukan inventarisasi semua file yang tersedia di root, `reference/`, `input/`, folder attachment, dan folder terkait lainnya. Cari file berdasarkan nama dan juga isi, bukan hanya mengandalkan nama file. Setidaknya cari bahan berikut.

1. `Guidebook WIA.pdf` atau file guidebook WIA dengan nama lain.
2. `[WIA] Template Proposal .docx` atau template proposal resmi WIA.
3. `[FDS] WIA...pdf` atau hasil review dan penilaian tahap First Draft Submission.
4. `pitch deck auditra.pdf` atau pitch deck sementara Auditra.
5. `SEC_SD2026020000253.pdf` atau proposal Statistics Essay Competition SATRIA DATA 2026.
6. Gitingest terbaru yang memuat snapshot repository.
7. File tambahan terbaru dari user, termasuk screenshot aplikasi, hasil pengujian, hasil deployment, data, catatan pengembangan, atau dokumen teknis lainnya.

Jika ada beberapa versi dari file yang sama, bandingkan tanggal dan kontennya. Gunakan versi terbaru sebagai sumber utama, tetapi jangan menghapus atau mengabaikan informasi historis yang berguna. Catat versi yang dipilih.

## 2.1 Prioritas sumber dan penyelesaian konflik

Gunakan hierarki berikut.

- Ketentuan kompetisi: guidebook WIA terbaru dan pengumuman resmi panitia yang dapat diverifikasi.
- Format proposal: template DOCX resmi WIA.
- Implementasi aktual: repository aktif di VS Code dan file source code yang benar-benar ada.
- Bukti dan klaim historis: proposal SEC, pitch deck, laporan pipeline, hasil eksperimen, serta laporan pengujian yang dapat diverifikasi.
- Umpan balik pengembangan: review FDS.
- Snapshot lama: Gitingest.
- Pengetahuan eksternal: sumber ilmiah, peraturan resmi, dan publikasi tepercaya yang diperiksa secara mandiri.

Jika dua sumber bertentangan, jangan memilih angka atau klaim secara diam-diam. Masukkan konflik tersebut ke `FACT_RECONCILIATION.md`, telusuri penyebabnya, periksa kode dan data aktual, lalu pilih angka yang memiliki dasar bukti paling kuat. Jika konflik belum bisa diselesaikan, hilangkan angka dari narasi utama atau nyatakan keterbatasannya secara jujur.

---

# 3. TAHAP PERTAMA: AUDIT REPOSITORY AKTIF SECARA MENYELURUH

Sebelum menulis satu paragraf proposal, pahami repository aktif yang terbuka di VS Code. Repository masih dalam pengembangan dan Gitingest yang pernah dibuat belum tentu mewakili keadaan terkini.

## 3.1 Prosedur inspeksi

Lakukan inspeksi read-only.

1. Periksa direktori kerja dan pastikan itu benar-benar root Auditra.
2. Jalankan `git status --short`, `git branch --show-current`, dan `git log -5 --oneline` bila repository Git tersedia. Jangan melakukan checkout, reset, clean, commit, push, atau perubahan Git lainnya.
3. Catat file yang berubah dan belum di-commit. Jangan mengubah atau menghapus perubahan tersebut.
4. Baca seluruh README, dokumentasi metodologi, dokumentasi data, dokumentasi deployment, audit report, konfigurasi pipeline, dependency manifest, dan file environment example yang aman untuk dibaca.
5. Inspeksi source code pipeline data, backend FastAPI, database, API router, autentikasi, workflow penugasan audit, frontend React/TypeScript, komponen UI, halaman, tema, dan test.
6. Jangan membaca atau menyalin secret, token, password produksi, private key, atau isi `.env` rahasia. Catat hanya nama variabel dan keberadaan konfigurasi yang relevan.
7. Periksa apakah data dan artefak besar tersedia. Jangan mengasumsikan file output ada hanya karena didokumentasikan.
8. Jika aplikasi dapat dijalankan tanpa mengubah data, lakukan pemeriksaan lokal secara hati-hati. Jangan menjalankan pipeline penuh yang menimpa output, mengunduh dataset besar, memodifikasi database, atau mengubah environment tanpa persetujuan.
9. Periksa test report dan hasil build yang sudah tersedia. Jika hendak menjalankan test atau build, pastikan perintah tidak menimpa file yang sedang diedit. Gunakan hanya pemeriksaan aman dan jelaskan apa yang benar-benar dijalankan.
10. Untuk setiap fitur yang dicantumkan dalam proposal, temukan file, komponen, endpoint, model data, atau hasil uji yang membuktikannya.

## 3.2 Cakupan file dan modul yang harus diperiksa

Periksa semua yang relevan, termasuk tetapi tidak terbatas pada.

- Pipeline EDA, cleaning, patch data quality, scoring, network analysis, geo matching, validation, sensitivity analysis, dan pipeline orchestrator.
- Konfigurasi bobot, threshold, lokasi data, dan proses reproducibility.
- Scraper dan freshness checker. Bedakan data snapshot dari pembaruan atau pembandingan live.
- FastAPI application, router, schemas, filters, database adapters, cache, freshness, authentication, authorization, dan audit program generator.
- SQLite schema dan migration untuk data transaksional.
- DuckDB atau Parquet sebagai lapisan analitik.
- Modul case management, evidence, finding, review, response, recommendation, follow-up, dan event log.
- Frontend routes, pages, components, hooks, context, theme tokens, API client, loading/error states, responsive layout, accessibility, serta interaksi.
- Deployment configuration, Dockerfile, compose, Railway, Vercel, static hosting, health checks, storage, environment variables, dan dokumentasi deployment.
- Unit test, integration test, API test, browser E2E, smoke test, fixture, dan laporan pengujian.

## 3.3 Hasil audit implementasi

Buat file `deliverables/wia-proposal/IMPLEMENTATION_INVENTORY.md` berisi matriks dengan kolom berikut.

| Modul atau fitur | Tujuan pengguna | Status aktual | Bukti implementasi | Bukti pengujian | Batasan |

Gunakan status yang jelas seperti `Implemented and verified`, `Implemented but not fully verified`, `In progress`, `Planned`, atau `Not implemented`. Jangan menyebut fitur `Implemented and verified` hanya karena ada nama file atau dokumentasi. Periksa perilakunya atau bukti test-nya.

Bedakan secara eksplisit antara fitur yang sudah ada, fitur yang sedang dikembangkan, dan rencana lanjutan. Proposal boleh menyebut rencana masa depan, tetapi tidak boleh menarasikannya seolah fitur tersebut sudah berfungsi.

Jangan mengedit source code produk dalam tugas proposal ini. Jika menemukan bug atau ketidaksesuaian, dokumentasikan sebagai batasan atau rekomendasi, kecuali user secara terpisah meminta perubahan kode.

---

# 4. TAHAP KEDUA: REKONSILIASI FAKTA, DATA, DAN KLAIM

Buat `deliverables/wia-proposal/FACT_RECONCILIATION.md` sebelum menyusun proposal. File ini adalah sumber kebenaran kerja bagi seluruh angka dan klaim yang akan dimasukkan ke dokumen.

## 4.1 Angka dataset

Verifikasi seluruh angka, termasuk.

- Jumlah baris mentah.
- Jumlah baris sesudah cleaning.
- Jumlah paket yang benar-benar dianalisis dan digunakan oleh API.
- Jumlah kolom atau variabel.
- Jumlah lembaga dan satuan kerja.
- Jumlah lokasi dan cakupan geospasial.
- Jumlah node dan edge Knowledge Graph.
- Jenis node dan jenis relasi.
- Total pagu anggaran, jika angka itu memang dapat direproduksi.
- Jumlah paket pada setiap kategori RPI.
- Persentase paket pada setiap kategori RPI.
- Jumlah paket yang ditampilkan API dan batas filter yang diterapkan.
- Tanggal atau periode snapshot data.
- Jumlah data saat ini di SIRUP jika freshness checker melakukan pembandingan live.
- Jumlah data yang belum termasuk snapshot analitik.

Jangan mencampur angka dari snapshot yang berbeda. Jangan menyebut jumlah paket pada SIRUP terkini sebagai jumlah paket yang sudah dianalisis oleh pipeline jika belum dijalankan ulang.

Jika jumlah data berubah selama pengembangan, gunakan angka dari sumber yang terhubung ke build dan aplikasi yang akan ditunjukkan saat penilaian. Simpan timestamp atau identitas snapshot jika tersedia.

## 4.2 Angka dan metode RPI

Periksa kode aktual, konfigurasi YAML, output scoring, metodologi, dan proposal SEC untuk mengonfirmasi.

- Nama serta definisi setiap sinyal S1 sampai S7.
- Bobot setiap sinyal dan apakah total bobot 100 persen.
- Formula normalisasi dan formula agregasi.
- Threshold kategori rendah, sedang, tinggi, dan kritis.
- Jumlah paket di setiap kategori.
- Definisi RWIS.
- Peran Knowledge Graph pada S7.
- Apakah skor dihitung ulang setelah network analysis.
- Apakah skor yang ditampilkan aplikasi sama dengan output pipeline.
- Bagaimana kontribusi masing-masing sinyal terhadap nilai akhir dijelaskan di antarmuka.

Jangan menyebut RPI sebagai probabilitas korupsi, probabilitas fraud, prediksi pelanggaran, atau tingkat kerugian. Gunakan istilah **heuristik prioritas pemeriksaan** atau istilah metodologis lain yang paling sesuai dengan implementasi.

Jangan menyebut bobot sebagai hasil machine learning jika bobot ditetapkan berdasarkan expert judgment atau pertimbangan metodologis. Jangan mengklaim akurasi, precision, recall, F1, AUC, atau kemampuan prediksi jika tidak ada ground truth dan evaluasi yang mendukungnya.

## 4.3 Pemeriksaan ketidaksesuaian yang perlu diprioritaskan

Periksa secara khusus potensi konflik berikut dan jangan menganggap semuanya masih berlaku tanpa verifikasi.

1. Proposal SEC pernah menyebut angka dataset mentah, angka data bersih, jumlah lembaga, satker, node, dan edge yang mungkin berbeda dari repository terbaru.
2. Visualisasi distribusi RPI pada proposal SEC pernah memiliki angka yang tidak sama dengan narasi paket tinggi dan kritis. Hitung ulang dari data aktual.
3. Dokumentasi lama pernah menyebut PageRank, sedangkan implementasi terdahulu menggunakan weighted degree yang dinormalisasi dengan nama variabel yang kompatibel. Periksa kode aktif dan pastikan istilah yang digunakan akurat.
4. README dan dokumentasi sinyal RPI pernah tidak konsisten dengan kode scoring. Gunakan definisi yang benar-benar dihitung.
5. Sinyal S3 pernah menggunakan batas Rp200 juta untuk semua kategori pengadaan langsung. Periksa kesesuaian dengan regulasi terbaru menurut jenis pengadaan.
6. Sinyal S5 pernah menggunakan persentil nilai UMKM, sedangkan ketentuan regulasi terkait pencadangan UMK menggunakan ketentuan nilai tertentu dan pengecualian. Jangan samakan heuristik statistik dengan batas hukum.
7. HPS tidak boleh digunakan sebagai dasar langsung untuk menyimpulkan kerugian negara. Bedakan anomali pagu dari pembuktian kewajaran harga.
8. Klaim peta seluruh Indonesia harus memperhatikan paket yang tidak mempunyai lokasi kabupaten/kota atau tidak berhasil dicocokkan ke geometri.
9. Endpoint daftar paket atau filter minimum RPI mungkin tidak menyediakan seluruh baris dataset kepada pengguna. Jelaskan cakupan aktual.
10. Data SIRUP merupakan data tahap rencana pengadaan dan bersifat self-declared. Jangan menyebutnya bukti realisasi, penyelesaian kontrak, kualitas pekerjaan, atau hasil pemeriksaan lapangan.
11. Label `LIVE`, freshness, scraper, dan pembandingan detail SIRUP harus menjelaskan mana yang live dan mana yang masih snapshot. Jangan mengatakan RPI telah dihitung menggunakan seluruh data live jika belum.
12. Deployment lama pernah dilaporkan tidak aktif. Uji ulang URL dan health endpoint terbaru sebelum memasukkan klaim deployment aktif.
13. Akun demo, keamanan autentikasi, penyimpanan token, rate limit, penyimpanan bukti, dan pengaturan role harus dievaluasi sebelum menampilkan kredensial atau mengklaim kesiapan produksi.

Tambahkan kolom `Source of truth`, `Value selected`, `Reason`, dan `Proposal treatment` pada fact reconciliation. Tandai fakta yang belum dapat diverifikasi sebagai `Unverified`. Jangan menyembunyikan konflik yang belum selesai.

---

# 5. TAHAP KETIGA: RISET ILMIAH, STATE OF THE ART, DAN RESEARCH GAP

Lakukan riset eksternal secara mendalam. Proposal WIA tetap proposal pengembangan produk web, tetapi argumen masalah, relevansi, kebaruan, dan pemilihan teknologi harus memiliki fondasi ilmiah yang kredibel.

Riset harus menjawab bukan hanya bahwa pengadaan publik penting, tetapi juga apa yang telah dilakukan penelitian dan sistem sebelumnya, keterbatasan apa yang masih tersisa, dan bagian spesifik mana yang dijawab oleh Auditra.

## 5.1 Tema riset yang harus ditelusuri

Telusuri literatur dan sumber primer terkait.

1. Public procurement transparency dan open government data.
2. Public procurement corruption risks, red flags, dan risk indicators.
3. Risk-based audit dan audit planning pada pengadaan publik.
4. Procurement analytics pada data pengadaan skala besar.
5. Explainable risk scoring dan interpretability dalam audit atau public-sector analytics.
6. Knowledge Graph untuk representasi entitas pengadaan dan hubungan antarentitas.
7. Network analysis untuk mengidentifikasi pola relasi, konsentrasi, atau hubungan antaraktor pengadaan.
8. Graph-based anomaly detection dan procurement network analysis.
9. Fragmentation atau split procurement dan pendekatan deteksi berbasis kemiripan dokumen atau teks.
10. Data quality, data integration, interoperability, dan provenance pada data pemerintah.
11. Decision-support systems untuk auditor, internal oversight, dan public accountability.
12. Digital audit workflow, audit evidence management, review, finding, dan follow-up management.

## 5.2 Strategi sumber

Utamakan sumber dengan kualitas dan relevansi tertinggi.

- Artikel jurnal peer-reviewed yang terindeks Scopus atau Web of Science jika status indeksnya dapat diperiksa.
- Artikel jurnal nasional terakreditasi SINTA jika relevan.
- Prosiding konferensi bereputasi yang relevan dengan graph mining, knowledge representation, information systems, atau public procurement.
- Laporan resmi OECD, World Bank, Open Contracting Partnership, Open Government Partnership, atau lembaga penelitian yang kredibel.
- Dokumen dan publikasi resmi KPK, LKPP, BPK, BPKP, Bappenas, BPS, dan lembaga pemerintah yang relevan.
- Regulasi resmi melalui JDIH atau portal pemerintah yang berwenang.

Jangan mengandalkan blog, artikel SEO, agregator kutipan, atau halaman tanpa identitas penulis sebagai dasar klaim ilmiah utama. Sumber sekunder boleh dipakai untuk menemukan sumber primer, tetapi kutip sumber primer jika tersedia.

Cari literatur yang paling relevan dan mutakhir. Sertakan karya seminal yang menjadi dasar teori walaupun lebih lama, tetapi jelaskan mengapa tetap relevan. Periksa tahun terbit dan konteks waktu setiap statistik.

## 5.3 Protokol verifikasi referensi

Setiap referensi yang dipakai harus diperiksa.

- Judul asli.
- Nama penulis atau institusi.
- Tahun terbit.
- Nama jurnal atau penerbit.
- Volume, nomor, dan halaman atau article number jika ada.
- DOI atau URL resmi.
- Apakah DOI benar-benar menuju publikasi yang dimaksud.
- Apakah temuan yang dikutip memang dinyatakan dalam sumber.
- Apakah sumber merupakan penelitian primer, review, regulasi, atau laporan.
- Status indeks hanya boleh disebut jika dapat diverifikasi melalui sumber resmi pengindeks atau halaman jurnal yang meyakinkan.

Jangan menciptakan DOI, penulis, volume, nomor, halaman, nama jurnal, atau status indeks. Jangan mengutip artikel hanya karena judulnya muncul di hasil pencarian. Buka dan baca abstrak serta bagian yang mendukung klaim, dan baca full text bila tersedia.

Buat `deliverables/wia-proposal/RESEARCH_LEDGER.md` yang mencatat referensi, tautan, jenis sumber, klaim yang didukung, relevansi bagi Auditra, batasan sumber, serta status verifikasi.

## 5.4 Penyusunan state of the art

Bangun tabel state of the art yang membandingkan studi dan pendekatan terdahulu berdasarkan aspek yang benar-benar dibahas oleh publikasi.

Kolom minimum yang disarankan meliputi.

| Penulis dan tahun | Fokus penelitian | Data atau konteks | Metode | Output atau temuan utama | Keterbatasan yang relevan | Posisi kontribusi Auditra |

Pilih studi yang mewakili pendekatan berbeda, misalnya.

- Procurement red-flag indicators berbasis rule atau statistik.
- Machine learning untuk deteksi anomali pengadaan.
- Knowledge Graph atau graph mining pada data procurement.
- Network analysis untuk procurement risk.
- Explainable audit decision-support system.
- Digital workflow atau evidence management jika terdapat penelitian yang benar-benar relevan.

Jangan memaksa semua studi dibandingkan pada dimensi yang tidak mereka teliti. Jika suatu studi tidak mengevaluasi explainability, tulis `Tidak dievaluasi` daripada membuat asumsi.

## 5.5 Research gap dan posisi kontribusi

Research gap harus berasal dari perbandingan nyata, bukan kalimat generik seperti belum ada sistem serupa di Indonesia tanpa bukti penelusuran yang cukup.

Uji apakah terdapat gap pada kombinasi aspek berikut.

1. Data pengadaan nasional berskala besar yang diintegrasikan dari sumber perencanaan resmi.
2. Representasi relasional entitas pengadaan menggunakan Knowledge Graph.
3. Prioritas pemeriksaan yang dapat ditelusuri ke sinyal pembentuknya.
4. Eksplorasi interaktif dari level agregat ke detail paket.
5. Keterhubungan analytical decision support dengan workflow penugasan audit.
6. Pengelolaan bukti, review berjenjang, komunikasi tanggapan, dan tindak lanjut dalam satu aplikasi.
7. Dokumentasi metodologi, provenance, dan batasan data yang dapat diakses pengguna.

Kombinasi tersebut boleh menjadi posisi kontribusi Auditra hanya jika repository aktif memang membuktikan fitur dan integrasinya. Jika ada komponen yang masih dalam pengembangan, posisikan sebagai pengembangan lanjutan, bukan kontribusi yang sudah selesai.

Gunakan istilah **kontribusi integratif pada tingkat sistem** bila kebaruannya terutama berupa penggabungan pipeline analitik, Knowledge Graph, dan workflow audit ke dalam aplikasi web. Jangan mengklaim algoritma baru atau state of the art global jika Auditra tidak memperkenalkan algoritma yang benar-benar baru.

Rumuskan setidaknya satu paragraf research gap yang logis dengan urutan.

- Apa yang telah dikerjakan penelitian terdahulu.
- Apa keterbatasan atau ruang yang belum dijawab.
- Mengapa gap itu penting dalam konteks pengadaan Indonesia.
- Bagaimana Auditra mengisi gap melalui fitur dan arsitektur yang benar-benar tersedia.
- Apa batas kontribusi yang tetap belum diselesaikan.

## 5.6 Jangan membuat klaim empiris palsu

Tidak ada wawancara, survei, uji kegunaan, adopsi institusi, atau validasi auditor yang boleh diklaim jika tidak ditemukan buktinya. Jika belum ada, jelaskan pendekatan desain berdasarkan studi literatur dan evaluasi teknis internal, serta nyatakan validasi dengan calon pengguna sebagai keterbatasan atau rencana pengembangan.

Jika perlu menggunakan persona sesuai template, buat **proto-persona atau persona berbasis literatur** dan beri label bahwa persona merupakan representasi awal berdasarkan karakteristik peran pengguna, bukan hasil wawancara langsung. Jangan membuat nama, kutipan, angka survei, atau pengalaman pengguna seolah nyata.

---

# 6. TAHAP KEEMPAT: RISET DATA PUBLIK, REGULASI, DAN KERANGKA KEBIJAKAN

Lakukan verifikasi regulasi secara teliti karena kesalahan dasar hukum dapat merusak kredibilitas Auditra.

## 6.1 Sumber data dan tata kelola

Periksa dan dokumentasikan sumber utama SIRUP LKPP. Pastikan definisi data, tahun anggaran, waktu pengambilan, skema variabel, karakteristik self-declared, metode akses, serta batasan data. Periksa sumber data pendukung untuk geospasial dan pastikan lisensi atau ketentuan pemanfaatannya dapat diterangkan.

Jelaskan posisi SIRUP sebagai informasi Rencana Umum Pengadaan. Bedakan antara rencana pengadaan, proses pemilihan, kontrak, realisasi, serah terima, dan pemanfaatan. Jangan menggambarkan data perencanaan sebagai data realisasi.

Jika aplikasi memiliki fungsi pembandingan dengan halaman SIRUP terkini, jelaskan bahwa hal itu merupakan pemeriksaan sumber tertentu atau freshness check sesuai implementasi. Jangan menyiratkan seluruh snapshot analitik otomatis diperbarui atau seluruh skor dihitung ulang bila kenyataannya tidak.

## 6.2 Regulasi pengadaan

Verifikasi versi konsolidasi regulasi yang berlaku pada periode pengembangan. Telusuri setidaknya Perpres 16/2018 beserta perubahannya, termasuk Perpres 12/2021 dan Perpres 46/2025 bila relevan. Gunakan JDIH LKPP atau portal resmi, bukan hanya blog atau ringkasan.

Verifikasi nomor pasal, ayat, batas nilai, kategori pengadaan, pengecualian, serta tanggal berlakunya. Jangan menyalin pasal lama secara otomatis.

Periksa paling tidak ketentuan yang berhubungan dengan.

- Pengumuman dan perubahan RUP melalui SIRUP.
- Prinsip, tujuan, dan etika pengadaan.
- Pemaketan dan larangan memecah paket dengan maksud menghindari tender atau seleksi.
- Metode pemilihan menurut jenis pengadaan dan batas nilainya.
- Pengadaan langsung dan penunjukan langsung.
- Harga Perkiraan Sendiri dan batas interpretasinya.
- Alokasi bagi usaha mikro, kecil, dan koperasi.
- Penggunaan produk dalam negeri dan TKDN.
- Pengawasan, pengaduan, dan sanksi.
- Kontrak, perubahan kontrak, keterlambatan, dan serah terima bila dijelaskan dalam workflow aplikasi.

Jangan menambahkan prosedur atau kewajiban audit yang tidak dinyatakan dalam peraturan yang dirujuk. Jika ada interpretasi metodologis, beri label sebagai interpretasi atau prosedur analitis yang perlu pertimbangan auditor.

## 6.3 Standar pemeriksaan dan proses audit

Jika workflow Auditra menjelaskan proses audit, verifikasi standar dan peraturan yang berlaku pada saat proposal dibuat. Periksa sumber primer seperti Standar Pemeriksaan Keuangan Negara dari BPK, peraturan BPKP terkait pengawasan pengadaan, dan ketentuan lain yang benar-benar relevan bagi peran pengguna Auditra.

Bedakan antara pemeriksaan oleh BPK sebagai pemeriksa eksternal dan pengawasan intern oleh APIP atau BPKP. Jangan menyatukan semua aktor sebagai satu jenis auditor.

Periksa prinsip kecukupan dan ketepatan bukti, relevansi, validitas, keandalan, dokumentasi, supervisi, kriteria, unsur temuan, tanggapan entitas, rekomendasi, dan pemantauan tindak lanjut. Pastikan sistem tidak mengklaim menggantikan pertimbangan profesional auditor atau kewenangan lembaga pemeriksa.

Jika sumber primer tidak dapat diakses atau status regulasi belum dapat diverifikasi, jangan menuliskan kepastian hukum. Tandai sebagai keterbatasan riset.

---

# 7. TAHAP KELIMA: POSISI PRODUK DAN NARASI UTAMA

Susun satu narasi yang kuat, mengalir, dan konsisten dari awal sampai akhir. Cerita harus dimulai dari masalah nyata dalam pengawasan pengadaan publik, membawa pembaca memahami skala dan kompleksitas data, menunjukkan keterbatasan pendekatan yang ada, memperkenalkan Auditra sebagai solusi, menjelaskan cara kerja aplikasi, dan berakhir dengan manfaat serta kontribusi yang realistis.

## 7.1 Hook pembuka

Buat satu hook pembuka yang kuat dan elegan. Hook dapat menggunakan pertanyaan reflektif yang spesifik mengenai bagaimana pengawas menentukan paket mana yang harus ditelaah lebih dahulu ketika jutaan rencana pengadaan tersedia, tetapi kapasitas pemeriksaan terbatas.

Hook tidak boleh menggunakan statistik bombastis tanpa sumber. Jangan memakai kalimat klise yang terlalu umum seperti `Di era perkembangan teknologi yang semakin pesat`. Hindari dramatisasi bahwa semua pengadaan korup atau seluruh pengawasan gagal.

Contoh arah hook, bukan kalimat wajib.

> Di tengah jutaan rencana pengadaan yang tersebar di berbagai instansi, tantangan pengawasan bukan hanya menemukan data, melainkan menentukan informasi mana yang perlu ditelaah lebih dahulu dan bagaimana setiap prioritas dapat dipertanggungjawabkan.

Kembangkan menjadi kalimat pembuka yang khas dan tidak terasa seperti tulisan generik AI.

## 7.2 Problem framing

Bangun masalah dalam urutan yang mudah diikuti.

1. Pengadaan publik adalah instrumen penting untuk layanan dan pembangunan.
2. RUP dan data pengadaan tersedia dalam skala besar melalui sistem pemerintah.
3. Skala data dan hubungan antarentitas membuat penelusuran manual atau pembacaan tabel menjadi menantang.
4. Pendekatan agregasi sederhana dapat kehilangan konteks relasional.
5. Skor otomatis yang tidak transparan dapat sulit ditindaklanjuti.
6. Auditor membutuhkan alat bantu untuk menemukan prioritas, memahami alasan prioritas, menelusuri konteks, dan mendokumentasikan proses pemeriksaan.

Bedakan fakta dari interpretasi. Setiap statistik eksternal harus diberi sitasi di kalimat yang sama.

## 7.3 Solusi

Posisikan Auditra sebagai **aplikasi web pendukung prioritas dan pengelolaan penugasan audit pengadaan publik berbasis analitik yang dapat dijelaskan**. Gunakan nama dan deskripsi akhir yang konsisten dengan fitur aktual.

Cerita solusi minimal mencakup dua lapisan yang saling terhubung.

**Lapisan analitik dan eksplorasi data** yang memungkinkan pengguna memahami distribusi pengadaan, menjelajahi peta, menyaring paket, melihat prioritas, menelusuri alasan pembentuk RPI, serta mengeksplorasi hubungan entitas melalui Knowledge Graph.

**Lapisan workflow penugasan audit** yang memungkinkan pengguna yang berwenang membuat penugasan dari paket terpilih, menyusun atau meninjau prosedur, mengelola bukti, mencatat hasil, menyusun temuan, melakukan reviu, mencatat tanggapan, dan memantau tindak lanjut. Masukkan hanya tahapan yang telah diverifikasi di repository aktif.

Jangan membuat Auditra terdengar sebagai sistem pelaporan masyarakat umum jika antarmuka dan autentikasinya memang ditujukan untuk auditor dan reviewer. Jangan menyebut ada integrasi resmi dengan BPK, BPKP, Inspektorat, LKPP, atau portal Satu Data Indonesia tanpa bukti perjanjian atau integrasi yang berjalan.

## 7.4 Target pengguna dan manfaat

Tentukan target primer berdasarkan fungsi nyata aplikasi. Kemungkinan pengguna langsung adalah auditor atau pemeriksa yang melakukan penilaian awal, perencanaan penugasan, dokumentasi prosedur, dan review. Pastikan istilahnya sesuai dengan batas peran yang didukung sistem.

Pengguna sekunder dapat mencakup pengendali teknis, reviewer, pengelola pengawasan, atau analis pengadaan jika memang didukung oleh role dan alur kerja. Masyarakat luas boleh disebut sebagai penerima manfaat tidak langsung dari peningkatan transparansi dan akuntabilitas, bukan pengguna yang sudah dapat mengakses semua fungsi aplikasi.

Jangan mengada-adakan survei, wawancara, atau angka ukuran pasar. Jika persona diperlukan, buat satu atau dua proto-persona berbasis literatur dan fungsi pekerjaan.

---

# 8. TAHAP KEENAM: MENYUSUN ISI PROPOSAL PERSIS SESUAI TEMPLATE WIA

Gunakan template DOCX WIA sebagai basis dokumen. Pertahankan urutan bab dan subbab. Jangan menghapus bagian wajib. Jangan mengganti struktur dengan struktur paper ilmiah. Jika template memiliki elemen desain, header, footer, atau identitas MIA, pertahankan dengan rapi dan tidak merusak formatnya.

## 8.1 ATURAN HITUNG HALAMAN BERDASARKAN KLARIFIKASI TERBARU PANITIA

Klarifikasi panitia yang diterima peserta menyatakan bahwa cover, daftar isi, lampiran, dan daftar pustaka tidak termasuk dalam hitungan batas 30 halaman proposal. Terapkan aturan berikut secara ketat.

- Maksimal **30 halaman isi inti** di luar cover, daftar isi, lampiran, dan daftar pustaka.
- Cover tetap dibuat sesuai template, tetapi tidak masuk hitungan isi inti.
- Daftar isi tetap dibuat dan diperbarui, tetapi tidak masuk hitungan isi inti.
- Lampiran tetap disertakan bila diperlukan, termasuk tautan Figma, tautan aplikasi atau versi playable, serta materi pendukung yang relevan. Lampiran tidak masuk hitungan isi inti.
- Daftar pustaka tetap disertakan lengkap dengan APA 7 dan tidak masuk hitungan isi inti.
- Kata Pengantar tidak disebut panitia sebagai bagian yang dikecualikan. Karena itu, masukkan Kata Pengantar ke dalam hitungan 30 halaman isi inti. Jangan mengeluarkannya dari hitungan tanpa klarifikasi tertulis lain.
- Jangan memadatkan isi inti menjadi 20 atau 24 halaman hanya karena total dokumen dengan cover dan referensi berpotensi lebih dari 30 halaman. Targetkan pemanfaatan ruang isi inti secara maksimal sampai 30 halaman.
- Jangan menambahkan halaman kosong, memperbesar spasi secara artifisial, mengulang uraian, atau memasukkan konten dekoratif hanya untuk mencapai 30 halaman. Setiap halaman harus memberikan informasi baru, bukti, analisis, visual, atau penjelasan yang relevan.
- Apabila konten yang kuat dan terverifikasi memungkinkan, susun tepat 30 halaman isi inti. Jika ada kendala layout yang menyebabkan isi inti sedikit di bawah 30 halaman, jangan mengorbankan keterbacaan atau menambahkan filler. Laporkan jumlah aktual dengan jujur. Isi inti tidak boleh melampaui 30 halaman.

### Alokasi halaman isi inti yang ditargetkan

Gunakan alokasi berikut sebagai rencana awal. Boleh menggeser maksimal satu halaman antar subbab apabila diperlukan oleh kebutuhan bukti atau layout, tetapi total seluruh bagian yang dihitung tetap maksimal 30 halaman. Alokasi ini merupakan target editorial, bukan alasan untuk mengisi halaman dengan materi yang tidak substantif.

| Bagian yang dihitung | Target halaman | Fokus isi |
|---|---:|---|
| Kata Pengantar | 1 | Maksud penyusunan, konteks singkat, ucapan terima kasih yang faktual |
| BAB I Pendahuluan | 6 | Hook, urgensi, data pengadaan, studi terdahulu, state of the art, gap, tujuan, manfaat |
| BAB II Rancangan Sistem | 6 | Tema, Satu Data Indonesia dan SDG, inventaris alat dan bahan, alur pengembangan |
| BAB III Hasil dan Pembahasan | 15 | Target pengguna, kebutuhan, batasan, platform, persona, SWOT, arsitektur, user flow, information architecture, wireframe dan bukti implementasi |
| BAB IV Penutup | 2 | Kesimpulan dan saran pengembangan yang realistis |
| **Total isi inti** | **30** | **Maksimal 30 halaman di luar komponen yang dikecualikan panitia** |

Pembagian internal BAB I yang disarankan adalah 4 halaman untuk latar belakang, 1 halaman untuk tujuan, dan 1 halaman untuk manfaat. Pembagian BAB II yang disarankan adalah 1 halaman untuk tema, 2 halaman untuk alat dan bahan, dan 3 halaman untuk alur pembuatan. Pembagian BAB III yang disarankan adalah sekitar 7 halaman untuk analisis desain karya, 4 halaman untuk user flow dan information architecture, serta 4 halaman untuk wireframe. BAB IV memperoleh 2 halaman. Sesuaikan secara proporsional setelah layout DOCX dan PDF diuji.

### Pengendalian jumlah halaman

Buat file `PAGE_BUDGET.md` yang memuat nama setiap bagian, nomor halaman awal dan akhir pada PDF, jumlah halaman yang dihitung, jumlah halaman yang dikecualikan, serta total isi inti. Setelah DOCX diekspor ke PDF, hitung secara eksplisit halaman cover, daftar isi, isi inti, lampiran, dan daftar pustaka. Jangan sekadar melihat total halaman PDF. Verifikasi bahwa jumlah halaman Kata Pengantar sampai BAB IV tidak melebihi 30 setelah mengecualikan hanya cover, daftar isi, lampiran, dan daftar pustaka. Jika PDF memiliki section atau halaman sisipan, periksa satu per satu agar klasifikasi halaman benar.

Isi proposal harus mengikuti struktur berikut.

## Halaman sampul

Cantumkan judul karya, nama tim, nama ketua, nama anggota, dan universitas sesuai identitas yang benar. Pastikan ejaan nama dan nama universitas sama dengan dokumen pendaftaran. Gunakan judul yang ringkas, akademis, dan menjelaskan fungsi utama Auditra. Jangan membuat nama anggota, NIM, atau identitas yang tidak ada di sumber.

Gunakan `Auditra` sebagai nama produk. Judul lengkap dapat mengangkat sistem prioritas audit pengadaan publik berbasis Knowledge Graph dan analitik risiko yang dapat dijelaskan, serta mendeskripsikan aplikasi web dan workflow audit apabila sesuai dengan implementasi aktif.

## Daftar isi

Buat daftar isi otomatis atau daftar isi yang diperbarui sesuai heading final. Pastikan nomor halaman cocok dengan dokumen PDF final.

## Kata Pengantar

Tulis singkat, formal, dan natural. Jelaskan tujuan penyusunan proposal dan apresiasi kepada pihak yang benar-benar berkontribusi. Jangan membuat nama pemberi dukungan atau mentor yang tidak terkonfirmasi. Sisakan identitas dan tempat/tanggal sesuai fakta.

## BAB I PENDAHULUAN

### 1.1 Latar Belakang

Susun cerita secara bertahap dan utuh. Mulai dari hook, urgensi pengadaan publik, skala dan sifat data SIRUP, tantangan pengawasan, keterbatasan pendekatan, state of the art, research gap, konsep Auditra, serta urgensi pengembangan website. Sertakan sitasi APA 7 dalam kalimat, bukan hanya menaruh daftar sumber di akhir.

Masukkan data Indonesia yang paling relevan dan terbaru setelah diverifikasi. Jangan memenuhi latar belakang dengan terlalu banyak statistik. Pilih data yang secara langsung memperkuat urgensi.

Jelaskan bahwa Auditra tidak mendeteksi korupsi dan tidak memberikan vonis. RPI merupakan alat bantu prioritas pemeriksaan berbasis sinyal yang telah ditentukan. Sumber data utama SIRUP menggambarkan rencana pengadaan, bukan bukti realisasi lapangan.

Akhiri latar belakang dengan kebutuhan yang dijawab Auditra dan alasan mengapa solusi web interaktif diperlukan.

### 1.2 Tujuan

Tuliskan tujuan dalam paragraf yang jelas dan berorientasi pada keluaran nyata. Tujuan harus merangkum pengembangan aplikasi web, integrasi data publik, analitik yang dapat dijelaskan, eksplorasi relasi, dukungan workflow audit, serta akses informasi yang lebih terstruktur sesuai implementasi.

Bila template mengharapkan daftar tujuan, gunakan daftar bernomor yang ringkas. Jangan mengubah tujuan menjadi klaim hasil yang belum tercapai.

### 1.3 Manfaat

Jelaskan manfaat untuk pengguna primer, pengguna sekunder, dan manfaat publik secara tidak langsung. Hubungkan manfaat dengan proses yang benar-benar didukung website. Bedakan manfaat potensial dari dampak yang sudah terukur.

## BAB II RANCANGAN SISTEM

### 2.1 Tema

Nyatakan tema utama sesuai dokumen teknis MIA dan subtema pilihan Open Government Data sebagaimana tercatat pada FDS. Terangkan bagaimana Auditra mengolah data pengadaan publik yang tersedia menjadi informasi yang lebih mudah ditelusuri dan digunakan untuk mendukung pengambilan keputusan pengawasan.

Kaitkan dengan prinsip Satu Data Indonesia secara hati-hati. Jelaskan relevansi integrasi, standar data, metadata, interoperabilitas, dan pemanfaatan data untuk pengambilan keputusan. Jangan menyebut Auditra telah terintegrasi secara resmi dengan portal Satu Data Indonesia jika belum ada integrasi tersebut.

Kaitkan dengan SDG 16 secara proporsional, terutama target 16.5 terkait pengurangan korupsi dan penyuapan serta target 16.6 terkait institusi yang efektif, akuntabel, dan transparan. Gunakan sumber PBB resmi untuk definisi target. Nyatakan bahwa kontribusi Auditra bersifat mendukung transparansi dan kapasitas pengawasan, bukan bukti bahwa sistem telah menurunkan korupsi.

### 2.2 Alat dan Bahan

Bagian ini wajib menjawab klarifikasi panitia bahwa poin 2.2 dapat mencantumkan perangkat keras, software, tools, dan teknologi yang digunakan selama proses pengembangan. Jangan membatasi bagian ini hanya pada library pemrograman. Susun inventaris yang akurat, cukup rinci, dan relevan dengan proses pengembangan Auditra.

Lakukan verifikasi langsung terhadap repository aktif, konfigurasi mesin pengembangan jika dapat diakses, dependency manifest, lockfile, dokumentasi, dan riwayat pengerjaan yang tersedia. Kelompokkan alat dan bahan sekurang-kurangnya ke dalam kategori berikut.

1. **Perangkat keras pengembangan.** Cantumkan laptop atau komputer yang benar-benar digunakan untuk coding, pemrosesan data, pengujian, dan penyusunan produk. Jika dapat diverifikasi dengan aman, cantumkan model perangkat, jenis prosesor, arsitektur, kapasitas RAM, sistem operasi, dan spesifikasi relevan lainnya. Informasi dapat diperoleh dari konfigurasi sistem atau keterangan eksplisit peserta. Jangan menampilkan serial number, device identifier, alamat perangkat, atau informasi pribadi yang tidak relevan. Jangan mengarang kapasitas RAM atau spesifikasi lain. Jika spesifikasi detail tidak dapat dipastikan, tulis secara umum sebagai laptop pengembangan.
2. **Perangkat lunak pengembangan.** Periksa dan cantumkan code editor atau IDE yang benar-benar digunakan, misalnya Visual Studio Code, terminal, Git, GitHub, Claude Code atau coding assistant lain jika memang dipakai, serta browser untuk pengujian. Jangan mengasumsikan semua tools tersebut digunakan hanya karena populer.
3. **Bahasa pemrograman, framework, dan library.** Verifikasi komponen aktual pada repository, misalnya Python, JavaScript atau TypeScript, React, Vite, Tailwind CSS, FastAPI, Pandas, NumPy, scikit-learn, NetworkX, library visualisasi, library peta, dan komponen lain yang benar-benar ditemukan. Jelaskan fungsi setiap komponen dalam Auditra, bukan hanya menumpuk nama teknologi.
4. **Database dan penyimpanan.** Jelaskan peran DuckDB, Parquet, SQLite, file storage, atau teknologi lain sesuai implementasi aktif. Bedakan penyimpanan analitik dari penyimpanan data transaksional apabila arsitektur memang memisahkannya.
5. **Data dan bahan pendukung.** Cantumkan SIRUP LKPP, data geospasial, GeoJSON, konfigurasi pipeline, dataset hasil pemrosesan, dokumentasi regulasi, dan bahan lain yang digunakan. Jelaskan periode, fungsi, dan keterbatasan sumber. Jangan menyebut data sebagai data realisasi jika hanya berisi rencana pengadaan.
6. **Tools desain, dokumentasi, dan diagram.** Cantumkan Figma, Canva, Draw.io, Mermaid, atau tools sejenis hanya jika benar-benar digunakan dalam desain UI, wireframe, diagram, atau dokumen. Jika wireframe dibuat langsung dari implementasi dan tidak menggunakan aplikasi desain tertentu, jelaskan secara jujur.
7. **Tools pengujian dan quality assurance.** Verifikasi penggunaan pytest, Playwright, browser DevTools, lint, TypeScript typecheck, build tool, atau alat lain. Jelaskan jenis pengujian yang didukung dan jangan menyebut pengujian telah lulus jika belum dijalankan atau buktinya tidak tersedia.
8. **Tools deployment dan kolaborasi.** Cantumkan Docker, Docker Compose, Vercel, Railway, VPS, GitHub, atau layanan lain hanya bila terbukti digunakan dalam alur pengembangan atau deployment. Bedakan konfigurasi yang tersedia dari deployment yang benar-benar aktif.

Sajikan inventaris utama dalam tabel dengan kolom kategori, nama alat atau teknologi, fungsi dalam pengembangan Auditra, dan dasar verifikasi. Setelah tabel, tulis paragraf yang menjelaskan bagaimana seluruh alat tersebut saling mendukung proses pengembangan. Gunakan penjelasan yang berorientasi pada kontribusi teknologi terhadap produk.

Nama dan versi teknologi harus mengikuti repository aktif. Ambil versi dari `package-lock.json`, `requirements.txt`, `pyproject.toml`, konfigurasi, atau perintah versi yang aman. Jangan menebak versi. Jika versi tidak diketahui, tulis nama teknologi tanpa nomor versi. Jangan menambahkan library hanya karena pernah disebut dalam rencana atau prompt terdahulu.

Cantumkan spesifikasi laptop hanya jika benar-benar diketahui sebagai perangkat yang dipakai dalam proses ini. Bila perangkat pengembangan berubah selama proyek, utamakan perangkat utama yang dipakai pada tahap pengembangan terkini dan beri keterangan singkat bila riwayat perangkat relevan. Jangan menjadikan cerita keterbatasan perangkat pribadi sebagai fokus bagian Alat dan Bahan.

Jika bahan data berasal dari SIRUP atau sumber geospasial, jelaskan asal, tujuan penggunaan, tanggal atau periode akses jika tersedia, dan status lisensi atau ketentuan penggunaan. Jangan mengklaim lisensi terbuka sebelum memverifikasi ketentuan sumbernya.

### 2.3 Alur Pembuatan

Jelaskan alur pengembangan secara sistematis dari riset dan identifikasi masalah, studi literatur dan regulasi, analisis kebutuhan pengguna, desain sistem, data acquisition, data cleaning, pembangunan pipeline analitik, Knowledge Graph dan network analysis, backend API, database, frontend, integrasi, pengujian, evaluasi, sampai deployment atau demonstrasi.

Sesuaikan urutan dengan sejarah dan proses yang benar-benar terjadi. Jangan menarasikan semua tahap sebagai metode yang direncanakan jika proyek telah dibangun. Gunakan bentuk lampau untuk proses yang sudah dilakukan, bentuk sekarang untuk fitur yang tersedia, dan bentuk rencana untuk hal yang belum dilaksanakan.

Sertakan flowchart alur pembuatan atau arsitektur proses dengan caption dan sumber. Diagram harus menggambarkan repository aktual, bukan arsitektur aspiratif.

## BAB III HASIL DAN PEMBAHASAN

Bagian ini menjadi pusat pembuktian bahwa Auditra adalah karya web yang nyata. Gunakan screenshot aplikasi aktual, diagram arsitektur, user flow, sitemap, wireframe, tabel, dan gambar yang relevan. Jangan memasukkan visual dekoratif yang tidak menjelaskan sistem.

### 3.1 Analisis Desain Karya

Bahas kelima unsur yang diwajibkan template.

#### a. Target Pengguna

Jelaskan pengguna primer, sekunder, tugas utama, kebutuhan, pain points, dan manfaat penggunaan aplikasi. Hubungkan target pengguna dengan fitur yang sudah tersedia. Sertakan bukti dari literatur atau sumber resmi untuk konteks profesi dan kebutuhan. Jika belum ada wawancara langsung, tulis secara transparan bahwa profil pengguna merupakan proto-persona berbasis literatur dan analisis kebutuhan awal.

#### b. Batasan Aplikasi

Jelaskan batasan dari aspek data, metodologi, sistem, keamanan, aksesibilitas, integrasi, dan penerapan institusional.

Wajib dijelaskan bahwa.

- SIRUP terutama berisi data perencanaan pengadaan.
- Data perencanaan tidak membuktikan kontrak, realisasi, serah terima, kualitas hasil, atau kerugian negara.
- Nilai RPI adalah prioritas heuristik dan bukan probabilitas fraud atau kesimpulan hukum.
- Bobot dan threshold harus dijelaskan sesuai implementasi dan dasar yang benar.
- Similarity pada uraian paket bukan bukti niat memecah paket.
- Anomali pagu bukan bukti kemahalan atau kerugian negara.
- Hasil pencocokan geospasial mempunyai cakupan dan kasus yang tidak cocok.
- Data live dan data snapshot mungkin memiliki perbedaan.
- Bukti pelaksanaan dan klarifikasi harus diperoleh dari sumber atau pihak yang berwenang.
- Aplikasi merupakan alat bantu dan tidak menggantikan penilaian profesional, kewenangan, atau prosedur resmi auditor.

Tambahkan batasan teknis yang ditemukan saat audit repository, tetapi jangan memenuhi bagian ini dengan detail yang tidak relevan bagi pembaca.

#### c. Platform yang Digunakan

Jelaskan aplikasi sebagai web-based application dan target penggunaan melalui browser desktop, tablet, atau ponsel sesuai hasil pengujian aktual. Jelaskan alasan platform web cocok untuk eksplorasi data, akses lintas perangkat, dan konsolidasi workflow. Jangan mengklaim kompatibilitas browser atau PWA jika belum diuji.

#### d. User Persona

Buat proto-persona yang realistis sesuai pengguna primer. Persona paling tidak mencakup peran, tujuan, kebutuhan, hambatan, konteks kerja, dan keterampilan teknologi yang relevan. Jangan membuat profil demografis pribadi yang tidak diperlukan. Jangan mengarang kutipan wawancara. Beri catatan bahwa persona merupakan representasi awal berbasis literatur dan analisis peran jika tidak ada wawancara.

#### e. Analisis SWOT

Buat analisis SWOT berdasarkan keadaan produk yang benar-benar ada.

- Strengths dapat mencakup skala data, explainable signals, Knowledge Graph, package drill-down, workflow audit, atau provenance jika terverifikasi.
- Weaknesses dapat mencakup keterbatasan data RUP, heuristic scoring, belum adanya validasi auditor praktisi, keterbatasan integration, atau keterbatasan operasional yang nyata.
- Opportunities dapat mencakup peningkatan keterbukaan data, penguatan pengawasan berbasis risiko, interoperabilitas, dan pengembangan integrasi resmi.
- Threats dapat mencakup perubahan regulasi, perubahan struktur sumber data, kualitas data, risiko keamanan, keterbatasan adopsi, dan kesalahpahaman publik terhadap skor.

Buat tabel SWOT yang ringkas atau diagram kuadran empat bagian. Tambahkan uraian interpretasi yang menghubungkan SWOT dengan strategi pengembangan.

### 3.2 User Flow dan Information Architecture

Jelaskan bagaimana pengguna berpindah dari tujuan awal ke tindakan akhir. Pisahkan alur eksplorasi analitik dan alur penugasan audit jika keduanya merupakan journey berbeda.

Alur eksplorasi dapat mencakup.

- Pengguna membuka dashboard dan memahami konteks data.
- Pengguna memilih filter atau wilayah.
- Pengguna melihat indikator agregat, ranking, atau peta.
- Pengguna memilih instansi, node, atau paket.
- Pengguna masuk ke halaman Package Passport.
- Pengguna memeriksa atribut paket, sumber data, tujuh sinyal, kontribusi RPI, dan relasi yang relevan.
- Pengguna mengambil keputusan untuk menelaah lebih lanjut sesuai kewenangan.

Alur workflow audit harus mengikuti implementasi aktual. Jika repository mendukung, jelaskan pembuatan penugasan, seleksi sasaran, perencanaan, program audit, pelaksanaan, evidence, review berjenjang, komunikasi tanggapan, penyelesaian, dan follow-up. Gunakan status dan role yang tepat sebagaimana kode.

Buat visual user flow yang menunjukkan keputusan, percabangan, dan peran pengguna. Buat information architecture atau sitemap yang menggambarkan halaman dan hubungan navigasi aktual. Beri nomor gambar dan caption.

### 3.3 Wireframe

Sertakan wireframe atau visual struktur antarmuka yang sesuai dengan halaman aktual. Minimal gambarkan atau tampilkan halaman yang relevan dari aplikasi, misalnya.

- Halaman landing atau dashboard entry.
- Dashboard analitik.
- Package Passport.
- Knowledge Graph explorer.
- Halaman penugasan audit atau evidence management.
- Halaman metodologi dan sumber data.

Prioritaskan screenshot aktual dari repository yang sedang berjalan dibandingkan mockup yang tidak sesuai. Jika memakai screenshot, catat route, tanggal pengambilan, viewport, dan status data. Jika membuat wireframe, labeli sebagai wireframe dan jangan menyamarkannya sebagai tampilan final.

Berikan penjelasan singkat mengenai hierarki informasi, navigasi, interaksi, responsivitas, warna, tipografi, empty state, loading state, error handling, dan aksesibilitas hanya sejauh dibuktikan oleh tampilan atau kode.

## BAB IV PENUTUP

### 4.1 Kesimpulan

Rangkum masalah, pendekatan, fitur aplikasi, dan manfaat potensial secara mengalir. Tegaskan posisi Auditra sebagai alat bantu pengambilan keputusan dan dokumentasi audit berbasis data. Jangan menutup dengan klaim bahwa Auditra telah memberantas korupsi, meningkatkan akuntabilitas secara terukur, atau diadopsi lembaga tertentu jika hal itu belum terbukti.

### 4.2 Saran

Jelaskan roadmap yang realistis seperti validasi dengan auditor praktisi, perbaikan kualitas dan pembaruan data, penyesuaian regulasi dan scoring, benchmarking, security hardening, usability testing, optimasi query, integrasi tahap pengadaan lainnya, dan integrasi resmi jika memungkinkan. Bedakan pekerjaan yang sudah direncanakan dari target yang belum disetujui atau belum dimulai.

## Lampiran

Template meminta tautan menuju desain Figma dan versi playable agar rancangan dapat dilihat serta diuji langsung. Sertakan tautan Figma jika tersedia dan URL aplikasi yang benar-benar dapat diakses. Jika salah satu belum tersedia, tandai sebagai item yang perlu dilengkapi, jangan mengarang URL.

Jika bermanfaat dan muat dalam batas halaman, sertakan QR code yang menuju URL yang benar-benar berfungsi. Pastikan QR code diuji.

## Daftar Pustaka

Gunakan APA edisi ke-7 secara konsisten. Pastikan semua sumber yang dikutip dalam teks muncul di daftar pustaka dan setiap item daftar pustaka benar-benar dikutip di dalam teks, kecuali template atau pedoman mengizinkan referensi tambahan. Urutkan alfabetis. Lengkapi DOI sebagai URL `https://doi.org/...` jika DOI valid. Untuk regulasi, gunakan format sitasi hukum Indonesia yang konsisten dan informasi dokumen resmi.

---

# 9. PANDUAN KUALITAS NARASI DAN GAYA PENULISAN

Ini merupakan ketentuan wajib untuk seluruh isi proposal.

1. Tulis dalam Bahasa Indonesia formal, profesional, natural, dan mudah dipahami.
2. Gunakan narasi storytelling yang mengalir dari masalah, konteks, gap, solusi, cara kerja, hasil implementasi, sampai manfaat.
3. Utamakan paragraf utuh daripada daftar poin yang terlalu banyak. Gunakan tabel dan diagram untuk merangkum informasi teknis yang padat.
4. Jangan membuat setiap paragraf terlalu panjang. Pecah paragraf berdasarkan satu gagasan utama dan transisi logis.
5. Buat kalimat hook yang kuat pada awal latar belakang.
6. Gunakan sitasi dalam kalimat dengan gaya APA 7, misalnya `(Nama, 2024)` atau `Nama (2024) menjelaskan bahwa ...`.
7. Letakkan sitasi sedekat mungkin dengan klaim yang didukung. Jangan mengumpulkan semua sitasi di akhir paragraf jika klaim yang didukung berbeda-beda.
8. Setiap angka, regulasi, definisi, klaim ilmiah, atau pernyataan tentang sistem eksternal harus memiliki sumber.
9. Jangan gunakan em dash atau tanda pisah panjang `—` di seluruh proposal.
10. Hindari tanda titik dua `:` dan titik koma `;` dalam narasi. Ubah menjadi kalimat lengkap atau struktur tabel jika diperlukan. Tanda tersebut hanya boleh muncul jika menjadi bagian tak terhindarkan dari nama resmi, URL, kode, atau format bibliografi.
11. Jangan menggunakan bold berlebihan. Gunakan bold hanya untuk istilah kunci atau bagian yang benar-benar membutuhkan penekanan.
12. Hindari frasa klise, repetisi, kalimat promosi kosong, dan gaya bahasa yang terasa dibuat oleh AI.
13. Hindari klaim absolut seperti `100% akurat`, `paling presisi`, `tanpa kesalahan`, `real-time` jika tidak terbukti, `menjamin transparansi`, atau `mendeteksi korupsi`.
14. Gunakan istilah secara konsisten. Pilih satu bentuk untuk Knowledge Graph, Risk Priority Index, Risk-Weighted Influence Score, SIRUP, satuan kerja, paket pengadaan, auditor, reviewer, dan penugasan audit.
15. Definisikan singkatan pada penyebutan pertama.
16. Jelaskan istilah teknis dengan bahasa yang cukup mudah dimengerti juri non-spesialis tanpa menghilangkan ketepatan teknis.
17. Hindari paragraf yang hanya berisi daftar fitur. Kaitkan setiap fitur dengan kebutuhan dan tindakan pengguna.
18. Jangan mengulang angka yang sama pada banyak bagian tanpa tujuan. Gunakan satu set angka final yang sudah direkonsiliasi.
19. Jangan mencantumkan narasi bahwa proposal merupakan hasil bantuan AI. Namun, jangan menyembunyikan penggunaan sumber atau aset pihak lain yang wajib diatribusikan.
20. Pastikan seluruh kalimat, tabel, caption, dan sitasi bebas typo, istilah campur aduk, serta inkonsistensi angka.

---

# 10. VISUAL, TABEL, DIAGRAM, DAN CAPTION

Proposal harus enak dibaca dan tidak menjadi tumpukan teks. Buat visual yang benar-benar menjelaskan substansi. Jangan membuat gambar dekoratif generik atau mengambil ilustrasi internet yang tidak relevan.

## 10.1 Visual minimum yang disarankan

Pilih visual berdasarkan ketersediaan bukti dan ruang halaman. Prioritaskan yang paling menjelaskan produk.

1. **Gambar 1. Kerangka konseptual Auditra** yang menunjukkan hubungan data pengadaan, analitik, Knowledge Graph, prioritas pemeriksaan, dan workflow audit.
2. **Gambar 2. Arsitektur sistem Auditra** yang menggambarkan data pipeline, storage analitik, backend API, database transaksional, dan frontend sesuai source code aktual.
3. **Gambar 3. Alur pemrosesan data dan pembentukan RPI** yang memperlihatkan tahap input, cleaning, tujuh sinyal, agregasi, dan hasil.
4. **Gambar 4. Struktur Knowledge Graph** yang memperlihatkan tipe node dan relasi yang benar-benar digunakan.
5. **Gambar 5. User flow eksplorasi paket dan Package Passport**.
6. **Gambar 6. User flow penugasan audit** sesuai status dan role aktual.
7. **Gambar 7. Sitemap atau information architecture**.
8. **Gambar 8. Screenshot dashboard aktual**.
9. **Gambar 9. Screenshot Package Passport aktual**.
10. **Gambar 10. Screenshot Knowledge Graph atau modul workflow audit aktual**.
11. **Gambar 11. Wireframe atau detail halaman penting** jika tidak seluruh halaman dapat diwakili screenshot.
12. **Gambar 12. Diagram hubungan Auditra, Satu Data Indonesia, dan SDG 16** jika hubungan konseptualnya dapat dijelaskan dengan tepat.

Tidak perlu memaksakan semua 12 gambar. Pilih visual yang paling bernilai dan gunakan ruang isi inti hingga maksimal 30 halaman sebagaimana klarifikasi panitia. Gambar dan tabel yang menjelaskan substansi dapat dipakai untuk memperkaya isi, tetapi tidak boleh menjadi pengisi halaman dekoratif.

## 10.2 Ketentuan pembuatan gambar

- Diagram arsitektur, flowchart, sitemap, user flow, dan SWOT harus dibuat sendiri dengan diagram yang rapi dan dapat diedit jika memungkinkan.
- Gunakan Mermaid, SVG, Draw.io, Python, atau alat diagram lain yang tersedia. Pilih format yang menghasilkan gambar tajam di PDF.
- Screenshot harus diambil dari aplikasi aktual dan tidak boleh dimanipulasi untuk menyembunyikan error atau membuat fitur yang tidak ada.
- Jangan mengambil screenshot dari mockup lama jika UI sudah berubah.
- Jika screenshot memuat data demo, beri label yang jelas.
- Jangan menampilkan informasi pribadi, token, kredensial, atau data sensitif.
- Gunakan satu gaya visual yang konsisten dengan identitas Auditra dan template MIA.
- Pastikan tulisan pada diagram terbaca setelah masuk ke dokumen ukuran A4.
- Tambahkan sumber pada visual. Gunakan `Sumber: Dokumentasi pengembangan Auditra, 2026` jika memang merupakan karya tim. Untuk diagram yang diadaptasi dari sumber lain, tuliskan `Diadaptasi dari ...` dan cantumkan sitasinya.
- Setiap gambar harus disebut di dalam paragraf sebelum atau setelah gambar tersebut.

## 10.3 Format caption

Gunakan format yang konsisten seperti berikut.

`Gambar 1. Kerangka Konseptual Auditra`

`Sumber: Dikembangkan oleh tim, 2026.`

Untuk tabel gunakan format seperti.

`Tabel 1. Perbandingan Penelitian Terdahulu dan Posisi Auditra`

`Sumber: Diolah dari ...`

Nomor gambar dan tabel harus urut berdasarkan kemunculan. Pastikan tidak ada caption tanpa visual atau visual tanpa caption.

## 10.4 Tabel yang harus dipertimbangkan

Gunakan tabel ketika membantu perbandingan atau menyederhanakan detail.

- Tabel state of the art.
- Tabel ringkasan sumber data dan variabel.
- Tabel definisi tujuh sinyal RPI dan bobotnya.
- Tabel teknologi dan fungsinya.
- Tabel modul website dan kebutuhan pengguna.
- Tabel batasan aplikasi atau skenario penggunaan jika diperlukan.
- Tabel SWOT jika lebih jelas daripada diagram.

Jangan memaksakan tabel yang terlalu lebar. Jika tabel menjadi padat, pecah atau ubah menjadi diagram.

---

# 11. PEMBAHASAN METODOLOGI AUDITRA YANG HARUS AKURAT

Jelaskan metode teknis dengan kedalaman yang cukup untuk meyakinkan juri, tetapi jangan mengubah proposal menjadi paper statistika.

## 11.1 Akuisisi dan prapemrosesan

Jelaskan sumber data, skema, periode, pengambilan, validasi, normalisasi, penanganan missing values, duplikasi, anomali input, dan field turunan. Gunakan angka yang telah direkonsiliasi. Jelaskan apa yang dilakukan otomatis dan apa yang merupakan koreksi data quality yang terkontrol.

## 11.2 Tujuh sinyal risiko

Cantumkan definisi setiap sinyal, bobot, logika dasar, dan makna interpretasinya berdasarkan kode aktual. Pastikan tidak ada perbedaan antara kode, konfigurasi, dokumentasi, tabel proposal, dan visual.

Jelaskan bahwa sinyal merupakan indikator untuk membantu penelaahan, bukan bukti pelanggaran. Jelaskan pula bahwa bobot dan threshold merupakan keputusan metodologis yang perlu dievaluasi dan dapat berubah mengikuti regulasi serta validasi lapangan.

## 11.3 Risk Priority Index

Tuliskan formula hanya jika formula aktual telah diverifikasi. Definisikan setiap variabel, rentang, bobot, dan cara agregasi. Jelaskan interpretasi skor, klasifikasi, dan threshold. Hindari penggunaan kata akurasi jika tidak ada ground truth.

## 11.4 Knowledge Graph dan Network Analysis

Jelaskan tipe node, tipe edge, arah relasi, bobot edge, agregasi, dan metrik jaringan yang sungguh dihitung. Bedakan degree centrality, weighted degree, betweenness, PageRank, community detection, dan RWIS secara tepat. Jangan memakai istilah PageRank jika implementasi hanya normalisasi weighted degree.

Jika RWIS menggunakan kombinasi intensitas aktivitas dan rata-rata RPI, jelaskan formula serta normalisasi berdasarkan implementasi aktif. Terangkan mengapa metrik tersebut dipakai dan batas interpretasinya.

## 11.5 Geospasial

Jelaskan pemetaan lokasi, normalisasi nama wilayah, pencocokan ke geometri, cakupan data, serta unmatched cases. Jangan menyebut 100 persen cakupan jika ada lokasi yang gagal dicocokkan. Bedakan lokasi administratif lembaga dengan lokasi paket.

## 11.6 Backend, database, dan frontend

Jelaskan bagaimana pipeline dan analytical storage disajikan melalui API ke UI. Bedakan data analitik yang bersifat read-oriented dari data transaksional yang menyimpan akun, kasus, bukti, temuan, review, dan riwayat bila memang arsitektur aktif menggunakannya.

Jelaskan peran frontend dalam memberi alur interaktif, filter, drill-down, Package Passport, Knowledge Graph, dan workflow. Jangan sekadar menyebut nama framework. Kaitkan teknologi dengan kebutuhan sistem.

## 11.7 Workflow audit

Jika diimplementasikan, jelaskan peran auditor dan reviewer, state machine, aturan transisi, readiness gates, program audit, evidence, assessment kualitas bukti, findings, tanggapan, rekomendasi, dan follow-up. Verifikasi semua nama status, aturan, dan role terhadap kode.

Jelaskan bahwa sistem membantu struktur dokumentasi dan kontrol proses, tetapi keputusan substantif tetap berada pada auditor dan pejabat berwenang.

---

# 12. KAITAN DENGAN SATU DATA INDONESIA DAN SDGS

Bagian ini harus substantif, bukan sekadar menempelkan logo atau menyebut tujuan pembangunan berkelanjutan.

## 12.1 Satu Data Indonesia

Gunakan Perpres Nomor 39 Tahun 2019 tentang Satu Data Indonesia hanya setelah memeriksa teks dan statusnya melalui sumber resmi. Jelaskan prinsip yang relevan seperti standar data, metadata, interoperabilitas, kode referensi atau data induk, serta tata kelola data sesuai naskah regulasi.

Hubungkan dengan Auditra secara proporsional.

- Auditra memanfaatkan data pengadaan publik yang tersedia melalui SIRUP.
- Pipeline mengubah dan menata data menjadi skema analitik yang lebih siap digunakan.
- Knowledge Graph menghubungkan entitas yang relevan.
- Metadata, sumber, periode, dan batas data perlu dijelaskan.
- Sistem dapat menjadi demonstrasi pemanfaatan dan integrasi data untuk pengambilan keputusan.

Jangan menyebut aplikasi telah memenuhi seluruh prinsip atau standar Satu Data Indonesia jika tidak ada audit kesesuaian formal. Jangan menyebut integrasi nasional yang belum benar-benar terjadi.

## 12.2 SDG 16

Gunakan sumber resmi United Nations untuk target SDG 16. Jelaskan relevansi target 16.5 dan 16.6 jika didukung sumber yang tepat. Tunjukkan jalur kontribusi yang masuk akal melalui penguatan akses informasi pengadaan, prioritas pengawasan, dokumentasi bukti, dan keterlacakan proses.

Gunakan bahasa `mendukung`, `berkontribusi secara tidak langsung`, atau `selaras dengan`. Jangan mengklaim hasil penurunan korupsi atau peningkatan efektivitas institusi tanpa evaluasi dampak.

Jika ada target SDG tambahan yang benar-benar relevan, jangan memperluas secara berlebihan. SDG 16 harus tetap menjadi fokus utama.

---

# 13. STRATEGI PENULISAN SITASI DAN DAFTAR PUSTAKA APA 7

Sitasi dalam teks wajib tersebar secara proporsional pada seluruh bagian yang memuat fakta, teori, hasil riset terdahulu, regulasi, dan kebijakan.

Contoh gaya yang diharapkan.

- `Menurut OECD (2023), ...`
- `Pendekatan berbasis red flags telah digunakan untuk mengidentifikasi pola risiko dalam pengadaan publik (Penulis, 2022).`
- `Regulasi pengadaan mengatur ... (Republik Indonesia, 2025).`

Jangan membuat sitasi yang tidak merujuk ke sumber yang benar-benar dibaca. Jangan membuat referensi sekunder seolah sumber primer. Jangan mengutip klaim dari abstrak seolah membaca hasil lengkap jika bagian itu tidak tersedia. Jika sumber hanya dibaca pada abstrak, catat batasan ini di research ledger.

Periksa ulang seluruh sitasi dengan daftar pustaka secara otomatis atau manual. Lakukan audit dua arah.

1. Setiap sitasi dalam isi harus ditemukan di daftar pustaka.
2. Setiap daftar pustaka harus dirujuk dalam isi.
3. DOI harus valid dan sesuai judul.
4. URL harus dapat diakses dan mengarah ke sumber yang benar.
5. Tahun, nama penulis, judul, jurnal, volume, nomor, dan halaman harus benar.
6. Regulasi harus ditulis menggunakan identitas resmi dan tahun yang tepat.

Prioritaskan sumber primer untuk data statistik dan regulasi. Jika angka dalam sumber lama sudah diperbarui oleh sumber resmi yang lebih baru, gunakan angka terbaru dengan konteks waktu yang jelas dan jangan mengubah sejarah data.

---

# 14. DESAIN DOKUMEN DAN PENGOLAHAN TEMPLATE DOCX

Gunakan template DOCX WIA yang dilampirkan sebagai file dasar, bukan membuat dokumen kosong lalu meniru tampilannya secara kasar.

Sebelum mengisi, periksa struktur template, section, margin, ukuran kertas, header, footer, logo, tema warna, font, heading styles, tabel, page break, dan elemen visual. Pertahankan komponen resmi yang relevan.

Jika ada instruksi placeholder dalam template, ganti dengan isi final yang benar. Jangan meninggalkan placeholder seperti `[JUDUL KARYA]`, `[Nama Tim]`, `Nama Ketua`, atau teks petunjuk pengisian.

Gunakan format A4 dan margin serta style yang konsisten dengan template. Jika template mengandung footer MIA, jangan merusak proporsi logo atau identitas panitia. Gunakan jenis huruf yang mudah dibaca dan tersedia pada lingkungan. Jangan mengubah logo institusi atau logo panitia.

Pastikan heading menggunakan style yang tepat sehingga daftar isi dapat diperbarui. Pastikan nomor halaman konsisten. Hindari heading yang menggantung pada bagian bawah halaman.

Tabel harus memiliki header yang jelas, ukuran font terbaca, alignment konsisten, dan tidak terpotong antarhalaman. Diagram dan gambar harus tajam, proporsional, dan memiliki caption.

Jangan menggunakan warna berlebihan. Pertahankan identitas MIA dari template dan identitas visual Auditra secara harmonis. Hindari layout ramai dan penggunaan terlalu banyak kotak atau ornamen.

---

# 15. STRUKTUR FOLDER KELUARAN

Simpan seluruh hasil kerja di folder baru dan terpisah dari source code, misalnya.

```text
deliverables/
└── wia-proposal/
    ├── 00_SOURCE_INVENTORY.md
    ├── IMPLEMENTATION_INVENTORY.md
    ├── FACT_RECONCILIATION.md
    ├── RESEARCH_LEDGER.md
    ├── PROPOSAL_OUTLINE.md
    ├── PAGE_BUDGET.md
    ├── FINAL_PROPOSAL_AUDIT.md
    ├── assets/
    │   ├── figures/
    │   ├── screenshots/
    │   └── diagrams/
    ├── working/
    │   └── proposal_working.docx
    ├── WIA_PenyisihanMIA2026_NamaTim.docx
    └── WIA_PenyisihanMIA2026_NamaTim.pdf
```

Gunakan nama tim yang benar setelah memverifikasinya dari bahan. Jika nama tim yang tercatat adalah `UPNVJT Mau Final ke UPNVJ`, gunakan nama itu dan pastikan konsisten. Jangan mengubah nama tim atau menebak ejaan.

Jangan menyimpan hasil di atas file source yang sudah ada. Jangan mengganti file input. Jangan menimpa DOCX template asli.

---

# 16. TAHAP KETUJUH: PROSES EKSEKUSI WAJIB

Kerjakan dengan urutan berikut. Jangan melompati tahap rekonsiliasi fakta.

## Tahap A. Inventarisasi

Buat `00_SOURCE_INVENTORY.md` berisi daftar file yang ditemukan, versi atau tanggalnya bila tersedia, cakupan konten, dan peran setiap file.

## Tahap B. Audit implementasi

Baca repository aktif dan buat `IMPLEMENTATION_INVENTORY.md`. Gitingest digunakan untuk konteks tambahan. Jika isi Gitingest bertentangan dengan repository aktif, repository aktif yang menjadi acuan status implementasi.

## Tahap C. Rekonsiliasi fakta

Buat `FACT_RECONCILIATION.md`. Selesaikan semua angka dan klaim yang penting. Jangan mulai menulis proposal final sebelum bagian ini cukup lengkap.

## Tahap D. Riset eksternal

Lakukan pencarian literatur, studi terdahulu, regulasi, statistik resmi, Satu Data Indonesia, dan SDG 16. Buat `RESEARCH_LEDGER.md`.

## Tahap E. Sintesis dan outline

Buat `PROPOSAL_OUTLINE.md` sesuai template, dengan ringkasan per subbab, klaim utama, sumber yang mendukung, tabel dan gambar yang akan digunakan, serta bukti dari repository.

Pastikan outline memetakan semua lima kriteria penilaian WIA ke isi proposal.

## Tahap F. Pembuatan aset

Buat diagram, flowchart, sitemap, user flow, SWOT, dan screenshot dari aplikasi aktual bila tersedia. Simpan file gambar sumber di `assets/`.

## Tahap G. Penulisan proposal

Isi template DOCX secara lengkap. Tulis narasi yang utuh dan saling terhubung. Gunakan sitasi in-text APA 7. Masukkan tabel dan gambar dengan caption. Maksimalkan isi inti hingga 30 halaman, dengan cover, daftar isi, lampiran, dan daftar pustaka di luar hitungan sesuai klarifikasi terbaru panitia. Kata Pengantar tetap dihitung sebagai isi inti. Buat PAGE_BUDGET.md dan pastikan isi inti tidak melebihi 30 halaman.

## Tahap H. Pemeriksaan editorial dan teknis

Lakukan pemeriksaan berulang terhadap isi dan layout. Jangan langsung menyatakan selesai setelah file berhasil disimpan.

## Tahap I. Ekspor final

Hasilkan DOCX dan PDF. Pastikan file dapat dibuka. Jika ada LibreOffice atau tool ekspor dokumen yang tersedia, gunakan secara aman. Periksa PDF yang dihasilkan dengan merender halaman untuk memastikan layout, tabel, gambar, font, dan page number tidak rusak.

## Tahap J. Audit final

Buat `FINAL_PROPOSAL_AUDIT.md` dan catat seluruh pemeriksaan yang lulus, tidak lulus, dan belum dapat dilakukan.

---

# 17. CHECKLIST KELENGKAPAN DAN KUALITAS FINAL

Gunakan checklist berikut sebelum menyatakan proposal selesai.

## A. Kepatuhan guidebook

- [ ] Mengikuti struktur template proposal WIA.
- [ ] Isi inti maksimal 30 halaman, tidak termasuk cover, daftar isi, lampiran, dan daftar pustaka sesuai klarifikasi terbaru panitia.
- [ ] Kata Pengantar dihitung sebagai bagian isi inti karena tidak disebut dalam daftar pengecualian panitia.
- [ ] Isi inti dimaksimalkan hingga mendekati atau tepat 30 halaman dengan materi substantif, bukan filler.
- [ ] `PAGE_BUDGET.md` menunjukkan pemisahan halaman isi inti dan bagian yang dikecualikan.
- [ ] Format PDF dapat dibuka.
- [ ] Nama tim, judul, anggota, dan universitas konsisten.
- [ ] Tema utama dan subtema sesuai pendaftaran dan dokumen kompetisi.
- [ ] Tidak ada placeholder atau instruksi template yang tertinggal.
- [ ] Lampiran memiliki tautan Figma dan versi playable jika tersedia.
- [ ] Nama file sesuai format panitia.

## B. Kualitas substansi

- [ ] Hook pembuka kuat dan relevan.
- [ ] Latar belakang menyampaikan problem statement yang spesifik.
- [ ] Urgensi didukung data resmi dan sitasi.
- [ ] State of the art berdasarkan studi yang diverifikasi.
- [ ] Research gap dibangun dari perbandingan penelitian terdahulu.
- [ ] Tujuan dan manfaat realistis.
- [ ] Target pengguna dan persona dijelaskan secara jujur.
- [ ] Batasan sistem dijelaskan.
- [ ] Kaitan Open Government Data jelas.
- [ ] Kaitan Satu Data Indonesia tidak berlebihan.
- [ ] Kaitan SDG 16 menggunakan target dan sumber resmi.
- [ ] Arsitektur dan metode sesuai implementasi.
- [ ] Fitur yang belum selesai dibedakan dari fitur aktual.
- [ ] Kesimpulan tidak berisi klaim dampak yang belum diuji.

## C. Kualitas software engineering

- [ ] Frontend, backend, data processing, storage, dan database dijelaskan.
- [ ] Arsitektur sesuai repository aktif.
- [ ] API, autentikasi, role, dan workflow dijelaskan secara tepat.
- [ ] Alur pengguna dapat dipahami.
- [ ] Fitur penting memiliki bukti implementasi.
- [ ] Hasil pengujian memiliki sumber.
- [ ] Responsivitas dan aksesibilitas tidak diklaim tanpa pengujian.
- [ ] Deployment status benar.
- [ ] Batas keamanan dan operasional diungkap secara proporsional.

## D. Kualitas data dan metodologi

- [ ] Sumber dan periode data jelas.
- [ ] Jumlah data konsisten.
- [ ] Jumlah node, edge, lembaga, dan satker konsisten.
- [ ] Tujuh sinyal dan bobot sesuai kode.
- [ ] Formula RPI sesuai implementasi.
- [ ] Definisi RWIS dan metrik graph tepat.
- [ ] Threshold dan kategori RPI benar.
- [ ] Tidak ada klaim prediksi fraud atau akurasi tanpa bukti.
- [ ] Keterbatasan data SIRUP diungkap.
- [ ] Peraturan dan ambang nilai diperiksa pada sumber resmi.
- [ ] Data live dibedakan dari snapshot.
- [ ] Hasil geospasial memiliki batasan yang dijelaskan.

## E. Sitasi dan referensi

- [ ] Sitasi berada di dalam kalimat.
- [ ] Semua klaim eksternal penting memiliki sumber.
- [ ] Referensi dapat ditelusuri.
- [ ] DOI dan URL valid.
- [ ] APA 7 konsisten.
- [ ] Daftar pustaka dan sitasi dalam teks cocok dua arah.
- [ ] Tidak ada referensi fiktif atau metadata yang ditebak.

## F. Visual dan layout

- [ ] Setiap gambar memiliki nomor, judul, dan sumber.
- [ ] Setiap tabel memiliki nomor, judul, dan sumber.
- [ ] Semua visual disebut dalam narasi.
- [ ] Screenshot berasal dari aplikasi aktual.
- [ ] Diagram sesuai arsitektur aktual.
- [ ] Tidak ada gambar pecah atau teks terlalu kecil.
- [ ] Tabel tidak terpotong.
- [ ] Tidak ada halaman kosong yang tidak disengaja.
- [ ] Tidak ada heading menggantung.
- [ ] Daftar isi dan nomor halaman sesuai.
- [ ] PDF diperiksa secara visual dari halaman pertama sampai terakhir.

## G. Gaya penulisan

- [ ] Tidak menggunakan em dash.
- [ ] Narasi mengalir dan mayoritas berupa paragraf lengkap.
- [ ] Tidak banyak bold.
- [ ] Tidak menggunakan titik dua atau titik koma dalam narasi kecuali kebutuhan tak terhindarkan.
- [ ] Tidak ada repetisi atau frasa klise.
- [ ] Tidak ada klaim absolut yang tidak terbukti.
- [ ] Ejaan dan istilah konsisten.

---

# 18. AUDIT AKHIR TERHADAP RUBRIK WIA

Setelah proposal selesai, buat matriks evaluasi internal. Jangan mengarang nilai resmi atau menjamin lolos final.

| Kriteria WIA | Bobot | Bagian proposal yang menjawab | Bukti utama | Kesenjangan yang tersisa |
|---|---:|---|---|---|
| Orisinalitas ide dan konsep | 20% | ... | ... | ... |
| Fungsionalitas website | 25% | ... | ... | ... |
| Desain dan estetika | 20% | ... | ... | ... |
| Konten dan informasi | 20% | ... | ... | ... |
| Kesesuaian tema dan subtema | 15% | ... | ... | ... |

Evaluasi harus jujur. Bedakan antara kualitas proposal dan kualitas website yang akan dinilai secara langsung. Proposal yang bagus tidak menggantikan fitur yang belum berfungsi.

---

# 19. FORMAT LAPORAN PENYELESAIAN KEPADA USER

Setelah semua pekerjaan selesai, berikan ringkasan yang singkat tetapi lengkap mengenai.

1. File DOCX final dan file PDF final beserta lokasi persisnya.
2. Jumlah total halaman PDF dan jumlah halaman isi inti yang dihitung secara terpisah, dengan daftar halaman yang dikecualikan.
3. Judul karya yang digunakan.
4. Jumlah referensi yang tervalidasi.
5. Visual, tabel, dan diagram yang dibuat.
6. Pemeriksaan repository yang dilakukan.
7. Pemeriksaan data dan klaim yang diselesaikan.
8. Test atau build yang benar-benar dijalankan, bila ada.
9. Masalah yang belum dapat diselesaikan.
10. Item administratif yang masih harus dilengkapi sebelum submit, seperti surat orisinalitas, tautan Drive, URL Figma, URL aplikasi, atau video pitching.

Sertakan tautan atau path ke seluruh deliverable. Jangan menyatakan `siap submit` jika masih ada item wajib yang belum lengkap atau jika PDF belum diperiksa.

---

# 20. INSTRUKSI PENUTUP

Mulai dengan menginventarisasi dan membaca semua bahan. Setelah itu audit repository aktif, rekonsiliasi fakta, lakukan riset eksternal, susun state of the art dan research gap, buat outline, hasilkan visual, tulis proposal berdasarkan template, ekspor DOCX dan PDF, lalu lakukan audit akhir.

Jangan meminta user mengulang informasi yang sudah ada di file. Jika ada identitas atau data yang benar-benar tidak tersedia, jangan menebaknya. Gunakan placeholder yang jelas hanya pada dokumen kerja dan catat sebagai item yang harus dilengkapi. Jangan menyisipkan placeholder yang belum terselesaikan ke file final tanpa menandainya pada laporan akhir.

Jangan berhenti pada saran, outline, atau draft parsial. Selesaikan pekerjaan sejauh sumber dan akses yang tersedia memungkinkan. Bila suatu sumber eksternal, file, atau fitur tidak dapat diverifikasi, jelaskan dengan jujur dan lanjutkan bagian lain yang dapat diselesaikan.

Hasil akhir harus terasa seperti proposal karya teknologi yang ditulis oleh tim yang memahami masalah, menguasai implementasi, menghargai bukti, dan mampu menjelaskan produknya kepada juri lintas disiplin. Proposal harus meyakinkan karena ketepatan substansi, kedalaman riset, kematangan produk, kualitas engineering, dan kejelasan cerita, bukan karena bahasa promosi yang berlebihan.

**Bangun satu cerita yang utuh. Mulai dari kebutuhan pengawasan pengadaan publik, lanjutkan ke bagaimana Auditra mengolah data menjadi prioritas yang dapat dijelaskan, lalu tunjukkan bagaimana aplikasi web membawa prioritas tersebut ke dalam proses kerja audit yang lebih terstruktur. Setiap klaim harus dapat ditelusuri, setiap gambar harus menjelaskan sesuatu, dan setiap fitur yang disebut harus dapat dibuktikan.**
