"""Program audit: prosedur yang dibangkitkan dari atribut/sinyal paket, dengan kriteria (pasal) terverifikasi.

SEMUA kriteria dikutip dari teks konsolidasi Perpres 16/2018 jo. 12/2021 jo. 46/2025 (JDIH LKPP).
Bentuk bukti & teknik mengikuti SPKN (PBPK 1/2026, Pelaksanaan par. 31–32). Lihat docs/RISET_PROSES_AUDIT.md.

PENTING: ini disusun dari pasal peraturan, BUKAN salinan Lampiran III Pedoman Audit PBJ BPKP
(lampiran itu tidak dapat diakses saat riset). Auditor tetap harus memakai pertimbangan profesional.
"""

from __future__ import annotations

PERPRES = "Perpres 16/2018 jo. 12/2021 jo. 46/2025"

# Tahap pengadaan (Perpres Pasal 76(3); Perban BPKP 6/2026 Pasal 3(3))
STAGES = [
    ("perencanaan", "Perencanaan"),
    ("persiapan", "Persiapan"),
    ("pemilihan", "Pemilihan penyedia"),
    ("pelaksanaan_kontrak", "Pelaksanaan kontrak"),
    ("serah_terima", "Serah terima"),
    ("pemanfaatan", "Pemanfaatan hasil"),
]
STAGE_KEYS = [k for k, _ in STAGES]
# Data SIRUP = rencana umum pengadaan → default lingkup tahap awal
DEFAULT_SCOPE = ["perencanaan", "persiapan", "pemilihan"]

# SPKN PBPK 1/2026, Pelaksanaan par. 31 dan 32
EVIDENCE_FORMS = {
    "catatan_transaksi": "Catatan transaksi (elektronik/fisik)",
    "komunikasi_pihak_luar": "Komunikasi tertulis dengan pihak luar entitas",
    "hasil_observasi": "Hasil observasi pemeriksa",
    "keterangan_entitas": "Keterangan lisan/tertulis pihak yang diperiksa",
}
TECHNIQUES = {
    "pengamatan": "Pengamatan",
    "wawancara": "Wawancara",
    "survei": "Survei",
    "pengukuran": "Pengukuran",
    "inspeksi": "Inspeksi",
    "konfirmasi": "Konfirmasi",
    "rekalkulasi": "Rekalkulasi",
    "pelaksanaan_ulang": "Pelaksanaan ulang",
    "prosedur_analitis": "Prosedur analitis",
    "lainnya": "Lainnya",
}
SOURCE_ORIGINS = {"entitas": "Dari entitas diperiksa", "pihak_ketiga": "Dari pihak ketiga", "pemeriksa": "Dihasilkan pemeriksa"}

# Batas pengadaan langsung (Pasal 38(3), 41(3)) — rupiah
PL_LIMIT = {"barang": 200_000_000, "jasa lainnya": 200_000_000, "pekerjaan konstruksi": 400_000_000, "jasa konsultansi": 100_000_000}
UMK_RESERVED_CEILING = 15_000_000_000  # Pasal 65(3)


def _norm_jenis(j: str | None) -> str:
    return (j or "").strip().lower()


def pl_limit_for(jenis: str | None) -> int | None:
    return PL_LIMIT.get(_norm_jenis(jenis))


def _rp(v: float | int | None) -> str:
    return "—" if v is None else "Rp " + f"{int(v):,}".replace(",", ".")


def _ev(name: str, form: str) -> dict:
    return {"name": name, "form": form}


def _crit(ref: str, text: str) -> dict:
    return {"ref": f"{PERPRES} {ref}" if ref.startswith("Pasal") else ref, "text": text}


def _proc(code, stage, title, objective, criteria, evidence, techniques, *, triggers=None, caution=None) -> dict:
    return {
        "code": code, "stage": stage, "title": title, "objective": objective,
        "criteria": criteria, "evidence_expected": evidence, "techniques": techniques,
        "triggers": triggers or ["dasar"], "caution": caution,
    }


def build_program(pkg: dict, scope: list[str] | None = None) -> list[dict]:
    """Bangkitkan prosedur audit untuk satu paket. Deterministik; tiap prosedur memuat kriteria, bukti & teknik."""
    scope = [s for s in (scope or DEFAULT_SCOPE) if s in STAGE_KEYS]
    metode = (pkg.get("metode") or "").strip()
    jenis = _norm_jenis(pkg.get("jenisPengadaan"))
    pagu = float(pkg.get("pagu") or 0)
    sig = lambda k: float(pkg.get(k) or 0)  # noqa: E731
    out: list[dict] = []

    # ── Perencanaan ────────────────────────────────────────────────────────
    if "perencanaan" in scope:
        out.append(_proc(
            "P-RUP", "perencanaan", "Kesesuaian RUP dengan SIRUP terkini dan DIPA/DPA",
            "Memastikan paket yang direncanakan tercatat dan konsisten, termasuk setelah revisi.",
            [_crit("Pasal 22", "RUP diumumkan melalui SIRUP; diumumkan kembali bila ada perubahan/revisi paket atau DIPA/DPA (ayat 5).")],
            [_ev("Tangkapan/ekspor halaman paket di SIRUP beserta tanggal akses", "catatan_transaksi"),
             _ev("DIPA/DPA terkait dan riwayat revisinya", "catatan_transaksi")],
            ["inspeksi", "rekalkulasi"],
            caution="Auditra dapat membandingkan snapshot dengan SIRUP saat ini dari halaman passport paket.",
        ))
        out.append(_proc(
            "P-TUJUAN", "perencanaan", "Kebutuhan dan ketepatan penggunaan anggaran",
            "Menilai apakah barang/jasa 'tepat dari setiap uang yang dibelanjakan' (kualitas, kuantitas, waktu, biaya, lokasi, penyedia).",
            [_crit("Pasal 4", "Tujuan pengadaan: menghasilkan barang/jasa yang tepat dari setiap uang yang dibelanjakan, diukur dari kualitas, kuantitas, waktu, biaya, lokasi, dan penyedia.")],
            [_ev("Dokumen perencanaan kebutuhan / analisis kebutuhan", "catatan_transaksi"),
             _ev("Keterangan PPK/PA tentang dasar kebutuhan", "keterangan_entitas")],
            ["wawancara", "inspeksi"],
        ))

    # ── Persiapan ──────────────────────────────────────────────────────────
    if "persiapan" in scope:
        if sig("s3_fragmentasi") >= 0.6:
            out.append(_proc(
                "P-PEMAKETAN", "persiapan", "Uji indikasi pemecahan paket",
                "Menguji apakah paket-paket serupa dalam satuan kerja yang sama dipecah untuk menghindari Tender/Seleksi.",
                [_crit("Pasal 20(2)(d)", "Dalam pemaketan dilarang memecah Pengadaan Barang/Jasa menjadi beberapa paket dengan maksud menghindari Tender/Seleksi.")],
                [_ev("Daftar paket serupa pada satker dan periode yang sama (dari SIRUP)", "catatan_transaksi"),
                 _ev("Dokumen perencanaan kebutuhan & dasar pemaketan", "catatan_transaksi"),
                 _ev("Keterangan PPK/PA tentang alasan pemaketan", "keterangan_entitas")],
                ["prosedur_analitis", "inspeksi", "wawancara"],
                triggers=["s3_fragmentasi"],
                caution="Larangan mensyaratkan 'dengan maksud menghindari Tender/Seleksi': kemiripan uraian saja belum membuktikan maksud. Cari bukti niat/perencanaan.",
            ))
        if sig("s2_pagu_anomali") >= 0.6:
            out.append(_proc(
                "P-HPS", "persiapan", "Dasar penyusunan HPS dan kewajaran harga",
                "Menilai apakah HPS dihitung secara keahlian dengan data yang dapat dipertanggungjawabkan.",
                [_crit("Pasal 26(1),(5)", "HPS dihitung secara keahlian dan menggunakan data yang dapat dipertanggungjawabkan; dipakai menilai kewajaran harga penawaran/harga satuan."),
                 _crit("Pasal 26(6)", "HPS tidak menjadi dasar perhitungan besaran kerugian negara.")],
                [_ev("Dokumen HPS beserta rincian dan sumber data harga", "catatan_transaksi"),
                 _ev("Data harga pembanding independen (e-katalog, survei, kontrak serupa)", "komunikasi_pihak_luar")],
                ["rekalkulasi", "survei", "prosedur_analitis"],
                triggers=["s2_pagu_anomali"],
                caution="Anomali pagu hanya sinyal statistik. HPS bukan dasar menghitung kerugian negara (Pasal 26(6)): kemahalan harus dibuktikan dengan pembanding independen.",
            ))
        if pkg.get("isUMKM") and pagu > UMK_RESERVED_CEILING:
            out.append(_proc(
                "P-UMK", "persiapan", "Kesesuaian status UMK dengan pencadangan paket",
                f"Paket ditandai UMKM tetapi pagu {_rp(pagu)} melebihi Rp15 miliar: menguji dasar penandaan dan pengecualiannya.",
                [_crit("Pasal 65(3)-(4)", "Paket dengan pagu sampai Rp15 miliar diperuntukkan bagi usaha mikro/kecil dan koperasi; dikecualikan bagi paket yang menuntut kemampuan teknis yang tidak dapat dipenuhi UMK.")],
                [_ev("Dasar penetapan paket sebagai UMKM / dokumen pengecualian", "catatan_transaksi"),
                 _ev("Dokumen kualifikasi penyedia (status usaha)", "komunikasi_pihak_luar")],
                ["inspeksi", "konfirmasi"], triggers=["s5_umkm"],
            ))
        elif (not pkg.get("isUMKM")) and 0 < pagu <= UMK_RESERVED_CEILING and "konsultansi" not in jenis:
            out.append(_proc(
                "P-UMK", "persiapan", "Pencadangan paket untuk usaha kecil",
                f"Paket {_rp(pagu)} (≤ Rp15 miliar) tidak ditandai UMKM: menguji apakah ada dasar pengecualian.",
                [_crit("Pasal 65(3)-(4)", "Paket dengan pagu sampai Rp15 miliar diperuntukkan bagi usaha mikro/kecil dan koperasi, kecuali menuntut kemampuan teknis yang tidak dapat dipenuhi UMK.")],
                [_ev("Pertimbangan/dokumen pengecualian kemampuan teknis", "catatan_transaksi")],
                ["inspeksi", "wawancara"], triggers=["dasar"],
                caution="Pasal 65(3) menyebut barang/konstruksi/jasa lainnya; periksa apakah paket ini termasuk cakupan sebelum menyimpulkan.",
            ))
        if pkg.get("dalamNegeri") in (False, 0, "False", "false", "Tidak", "tidak"):
            out.append(_proc(
                "P-PDN", "persiapan", "Penggunaan produk dalam negeri",
                "Paket tidak ditandai produk dalam negeri: menguji pemenuhan kewajiban PDN/TKDN.",
                [_crit("Pasal 66", "Wajib menggunakan Produk Dalam Negeri (TKDN paling sedikit 25% dan ketentuan berjenjang)."),
                 _crit("Pasal 76(4)(c)-(d)", "Ruang lingkup pengawasan mencakup pencapaian TKDN dan penggunaan produk dalam negeri.")],
                [_ev("Spesifikasi teknis/KAK dan bukti pertimbangan PDN", "catatan_transaksi"),
                 _ev("Sertifikat TKDN / pernyataan produk (jika ada)", "komunikasi_pihak_luar")],
                ["inspeksi"], triggers=["dasar"],
            ))

    # ── Pemilihan ──────────────────────────────────────────────────────────
    if "pemilihan" in scope:
        out.extend(_metode_procedures(pkg, metode, jenis, pagu))
        if sig("s1_metode") >= 0.6 or sig("s4_konsentrasi") >= 0.6 or sig("s6_dana_metode") >= 0.6:
            out.append(_proc(
                "P-KONSENTRASI", "pemilihan", "Analisis konsentrasi metode non-kompetitif pada satuan kerja",
                "Menilai apakah satker berulang memakai metode berisiko (penunjukan langsung/dikecualikan) tanpa dasar yang kuat.",
                [_crit("Pasal 38(7)", "Tender dilaksanakan bila tidak dapat memakai e-purchasing, pengadaan langsung, penunjukan langsung, atau tender cepat."),
                 _crit("Pasal 7(1)(c),(g)", "Etika: tidak saling mempengaruhi yang berakibat persaingan usaha tidak sehat; menghindari penyalahgunaan wewenang dan/atau kolusi.")],
                [_ev("Rekap paket satker per metode pemilihan (SIRUP)", "catatan_transaksi"),
                 _ev("Daftar penyedia terpilih per paket dan frekuensinya", "catatan_transaksi")],
                ["prosedur_analitis"],
                triggers=[k for k in ("s1_metode", "s4_konsentrasi", "s6_dana_metode") if sig(k) >= 0.6],
                caution="Pola berulang pada satu penyedia adalah indikator (bukan bukti): cari pola, bukan satu indikator saja.",
            ))

    # ── Pelaksanaan kontrak ────────────────────────────────────────────────
    if "pelaksanaan_kontrak" in scope:
        out.append(_proc(
            "P-KONTRAK", "pelaksanaan_kontrak", "Kontrak, jaminan, uang muka, dan perubahan kontrak",
            "Menguji kelengkapan kontrak dan jaminan, kewajaran uang muka, serta batas perubahan nilai kontrak.",
            [_crit("Pasal 33", "Jaminan pelaksanaan untuk kontrak di atas Rp200 juta; besarnya 5% (dari nilai kontrak atau HPS sesuai posisi penawaran terhadap HPS)."),
             _crit("Pasal 54(2)", "Penambahan nilai kontrak akhir akibat perubahan tidak melebihi 10% dari harga kontrak awal (kecuali keadaan darurat)."),
             _crit("Pasal 56(2)", "Kesempatan menyelesaikan pekerjaan setelah masa kontrak dimuat dalam adendum: waktu, sanksi denda keterlambatan, perpanjangan jaminan pelaksanaan.")],
            [_ev("Dokumen kontrak, adendum, dan jaminan pelaksanaan", "catatan_transaksi"),
             _ev("Bukti pembayaran/uang muka dan perhitungan denda keterlambatan", "catatan_transaksi"),
             _ev("Konfirmasi penerbit jaminan", "komunikasi_pihak_luar")],
            ["inspeksi", "rekalkulasi", "konfirmasi"],
            caution="Besaran denda keterlambatan tidak diatur di teks Perpres yang dikaji; ikuti ketentuan kontrak.",
        ))
    if "serah_terima" in scope:
        out.append(_proc(
            "P-BAST", "serah_terima", "Serah terima dan kesesuaian hasil dengan kontrak",
            "Menguji BAST dan memastikan volume/mutu yang diserahkan sesuai kontrak.",
            [_crit("Pasal 57-58", "Setelah pekerjaan selesai 100%, penyedia meminta serah terima; PPK memeriksa barang/jasa; PPK dan penyedia menandatangani BAST; PPK menyerahkan ke PA/KPA dengan berita acara.")],
            [_ev("Berita Acara Serah Terima dan hasil pemeriksaan PPK", "catatan_transaksi"),
             _ev("Hasil pengukuran/inspeksi fisik volume dan mutu oleh pemeriksa", "hasil_observasi")],
            ["inspeksi", "pengukuran", "pengamatan"],
            caution="Temuan kekurangan volume/mutu butuh bukti observasi atau pengukuran pemeriksa, bukan hanya dokumen.",
        ))
    if "pemanfaatan" in scope:
        out.append(_proc(
            "P-MANFAAT", "pemanfaatan", "Pemanfaatan hasil pekerjaan",
            "Menilai apakah hasil dimanfaatkan sesuai tujuan (nilai manfaat).",
            [_crit("Pasal 76(4)(a)", "Ruang lingkup pengawasan mencakup pemenuhan nilai manfaat yang sebesar-besarnya.")],
            [_ev("Bukti penggunaan/pemanfaatan hasil (laporan, foto, wawancara pengguna)", "hasil_observasi")],
            ["pengamatan", "wawancara"],
        ))

    # ── Lintas tahap ───────────────────────────────────────────────────────
    out.append(_proc(
        "P-RF", "lintas", "Telaah indikator kecurangan (red flags)",
        "Menentukan respons bila ada indikasi awal kecurangan; mencari pola, bukan satu indikator.",
        [_crit("SPKN (PBPK 1/2026) Pelaksanaan par. 33, 42", "Bila ada indikasi awal kecurangan pemeriksa menentukan respons dan menindaklanjuti sesuai ketentuan atau mengusulkan PDTT Investigatif."),
         _crit("Pasal 7", "Etika dan pertentangan kepentingan pelaku pengadaan.")],
        [_ev("Rekap penetapan penyedia (pola penyedia berulang/bergilir)", "catatan_transaksi"),
         _ev("Telaah hubungan penyedia–pejabat (kepemilikan, pengurus)", "komunikasi_pihak_luar")],
        ["prosedur_analitis", "konfirmasi"],
        caution="Indikator bukan bukti. Jika menemukan indikasi, tandai temuan sebagai 'indikasi kecurangan' agar dilaporkan sesuai SPKN.",
    ))
    return out


def _metode_procedures(pkg: dict, metode: str, jenis: str, pagu: float) -> list[dict]:
    lim = pl_limit_for(jenis)
    m = metode.lower()
    if m == "pengadaan langsung":
        if lim is None:
            lim_text = "Barang/jasa lainnya ≤ Rp200 jt; konstruksi ≤ Rp400 jt; konsultansi ≤ Rp100 jt"
            obj = "Menguji kesesuaian metode pengadaan langsung dengan nilai dan jenis pengadaan (jenis paket tidak tercatat jelas)."
        else:
            lim_text = f"Batas untuk jenis '{pkg.get('jenisPengadaan')}': {_rp(lim)}"
            status = "MELEBIHI batas" if pagu > lim else "dalam batas"
            obj = f"Pagu {_rp(pagu)} {status} pengadaan langsung. {lim_text}."
        return [_proc(
            "P-MET-PL", "pemilihan", "Kesesuaian pengadaan langsung dengan batas nilai",
            obj,
            [_crit("Pasal 38(3)", "Pengadaan langsung: barang/jasa lainnya paling banyak Rp200.000.000; pekerjaan konstruksi paling banyak Rp400.000.000."),
             _crit("Pasal 41(3)", "Jasa konsultansi pengadaan langsung paling banyak Rp100.000.000."),
             _crit("Pasal 38(8)", "Pengadaan langsung di atas Rp50.000.000 wajib memakai aplikasi sistem pengadaan elektronik dengan fitur transaksional.")],
            [_ev("Dokumen pemilihan/negosiasi dan nilai kontrak", "catatan_transaksi"),
             _ev("Bukti transaksi pada sistem pengadaan elektronik (jika > Rp50 jt)", "catatan_transaksi"),
             _ev("Daftar paket serupa satker (uji pemecahan di bawah batas)", "catatan_transaksi")],
            ["inspeksi", "prosedur_analitis"],
            triggers=["metode"],
            caution="Batas konstruksi kini Rp400 juta (Perpres 46/2025), bukan Rp200 juta. Nilai berulang tepat di bawah batas adalah red flag 'Multiple Awards Just Under Procurement Thresholds'.",
        )]
    if m == "penunjukan langsung":
        konsultansi = "konsultansi" in jenis
        ref = "Pasal 41(4)-(5), 41A" if konsultansi else "Pasal 38(4)-(5), 41A"
        return [_proc(
            "P-MET-PUL", "pemilihan", "Dasar 'keadaan tertentu' penunjukan langsung",
            "Penunjukan langsung hanya sah dalam keadaan tertentu yang dirinci; menguji dokumen yang membuktikan keadaan itu.",
            [_crit(ref, "Penunjukan langsung dilaksanakan dalam keadaan tertentu (mis. program prioritas berdasarkan arahan Presiden; satu pelaku usaha yang mampu; pemegang hak paten; tender ulang gagal; pemutusan kontrak; repeat order)."),
             _crit("Pasal 41A", "Arahan Presiden dituangkan dalam risalah rapat/memorandum/dokumen lain; PA membuat dokumen tertulis dan menetapkan metode berdasarkan analisis PA; disampaikan untuk konfirmasi ke menteri yang menyelenggarakan kesekretariatan negara."),
             _crit("Pasal 38(8)", "Penunjukan langsung wajib memakai aplikasi sistem pengadaan elektronik dengan fitur transaksional.")],
            [_ev("Dokumen yang membuktikan keadaan tertentu yang dipakai (arahan Presiden/analisis PA/bukti 1 pelaku usaha/dll.)", "catatan_transaksi"),
             _ev("Konfirmasi atau surat resmi pihak berwenang terkait keadaan tertentu", "komunikasi_pihak_luar"),
             _ev("Keterangan PPK/PA tentang alasan memilih penyedia", "keterangan_entitas")],
            ["inspeksi", "konfirmasi", "wawancara"],
            triggers=["metode"],
            caution="Tentukan lebih dulu 'keadaan tertentu' mana yang diklaim; tiap keadaan punya bukti pendukung berbeda.",
        )]
    if m == "dikecualikan":
        return [_proc(
            "P-MET-KEC", "pemilihan", "Dasar pengecualian dari ketentuan Perpres",
            "Metode 'Dikecualikan' harus dibenarkan salah satu dasar pengecualian; menguji dasar yang diklaim.",
            [_crit("Pasal 61(1)", "Dikecualikan: pengadaan pada BLU/BLUD; berdasarkan tarif yang dipublikasikan luas; sesuai praktik bisnis mapan; atau diatur peraturan perundang-undangan lain."),
             _crit("Pasal 61(1a)", "Pengecualian tidak berlaku untuk kewajiban penggunaan Produk Dalam Negeri dan produk UMK/koperasi.")],
            [_ev("Dasar hukum/dokumen yang menjadi alasan pengecualian", "catatan_transaksi"),
             _ev("Bukti tarif terpublikasi atau praktik bisnis mapan (bila diklaim)", "catatan_transaksi")],
            ["inspeksi", "wawancara"],
            triggers=["metode"],
            caution="Banyak paket SIRUP berstatus 'Dikecualikan'; pastikan klaim pengecualian benar dan PDN/UMK tetap dipenuhi.",
        )]
    if m == "darurat":
        return [_proc(
            "P-MET-DAR", "pemilihan", "Keabsahan penetapan keadaan darurat",
            "Menguji apakah kondisi memenuhi keadaan darurat dan penanganannya tidak dapat ditunda.",
            [_crit("Pasal 59(1)-(3)", "Keadaan darurat untuk keselamatan/perlindungan masyarakat yang tidak dapat ditunda dan harus segera: bencana, operasi SAR, kerusakan sarana yang mengganggu pelayanan publik, dsb.; penetapan sesuai peraturan perundang-undangan.")],
            [_ev("Dokumen penetapan status/keadaan darurat", "catatan_transaksi"),
             _ev("Bukti urgensi (laporan kejadian, permintaan penanganan)", "catatan_transaksi")],
            ["inspeksi", "konfirmasi"], triggers=["metode"],
        )]
    if m == "e-purchasing":
        return [_proc(
            "P-MET-EP", "pemilihan", "E-purchasing: produk di katalog elektronik",
            "Menguji bahwa barang/jasa yang dibeli tercantum di katalog elektronik dan harga/volume sesuai pesanan.",
            [_crit("Pasal 38(2)", "E-purchasing dilaksanakan untuk barang/pekerjaan konstruksi/jasa lainnya yang sudah tercantum dalam katalog elektronik."),
             _crit("Pasal 26(7)", "Penyusunan HPS dikecualikan untuk e-purchasing dengan nilai paling banyak Rp100 juta.")],
            [_ev("Bukti pesanan/transaksi e-katalog", "catatan_transaksi"),
             _ev("Bukti produk dan harga pada katalog saat transaksi", "catatan_transaksi")],
            ["inspeksi", "rekalkulasi"], triggers=["metode"],
            caution="Pembelian berulang melalui penyedia yang sama pada e-katalog pernah menjadi modus yang ditangani KPK (sumber sekunder).",
        )]
    if m == "tender cepat":
        return [_proc(
            "P-MET-TC", "pemilihan", "Tender cepat: syarat penyedia dan spesifikasi",
            "Menguji bahwa penyedia terkualifikasi dan spesifikasi/volume sudah rinci.",
            [_crit("Pasal 38(6)", "Tender cepat bila pelaku usaha telah terkualifikasi dalam sistem informasi kinerja penyedia untuk pengadaan dengan spesifikasi dan volume yang sudah dapat ditentukan rinci, atau dapat menyebut merek sesuai Pasal 19(2).")],
            [_ev("Bukti kualifikasi penyedia di sistem informasi kinerja penyedia", "catatan_transaksi"),
             _ev("Spesifikasi teknis dan volume dalam dokumen pemilihan", "catatan_transaksi")],
            ["inspeksi"], triggers=["metode"],
        )]
    if m in ("tender", "seleksi"):
        return [_proc(
            "P-MET-TND", "pemilihan", "Proses tender/seleksi dan evaluasi",
            "Menguji kewajaran dokumen pemilihan, pengumuman, evaluasi, dan penetapan pemenang.",
            [_crit("Pasal 38(7), 41(6)", "Tender dilaksanakan bila tidak dapat memakai metode lain; seleksi untuk jasa konsultansi di atas Rp100 juta."),
             _crit("Pasal 7(2)", "Pertentangan kepentingan, mis. rangkap personel inti pada badan usaha peserta tender yang sama; PPK/Pokja mengendalikan badan usaha penyedia.")],
            [_ev("Dokumen pemilihan, pengumuman, berita acara evaluasi & penetapan pemenang", "catatan_transaksi"),
             _ev("Data kepemilikan/pengurus peserta tender", "komunikasi_pihak_luar")],
            ["inspeksi", "prosedur_analitis", "konfirmasi"], triggers=["metode"],
            caution="Periksa pola: penawaran sangat dekat HPS, penyedia bergilir, kemiripan penawaran (IACRC red flags).",
        )]
    return []
