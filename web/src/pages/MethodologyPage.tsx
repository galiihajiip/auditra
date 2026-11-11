import { Link } from "react-router-dom";
import Icon from "../components/Icon";

const CYCLE: { tahap: string; dasar: string; fitur: string }[] = [
  { tahap: "1 · Seleksi sasaran", dasar: "Pemilihan objek berbasis faktor risiko (Lampiran III Perban BPKP 3/2019, sumber sekunder); Perban BPKP 6/2026: pendekatan berbasis risiko", fitur: "RPI + alasan seleksi wajib diisi sebelum perencanaan" },
  { tahap: "2 · Perencanaan", dasar: "SPKN (PBPK 1/2026) Pelaksanaan par. 9–27: tujuan, pemahaman hal pokok, risiko termasuk kecurangan, kriteria, materialitas", fitur: "Form rencana + program audit dibangkitkan dari sinyal & atribut paket (kriteria bersumber pasal)" },
  { tahap: "3 · Pelaksanaan", dasar: "SPKN Pelaksanaan par. 28–38: bukti cukup & tepat (relevan, valid, andal); bentuk (par. 31); teknik (par. 32); dokumen diragukan → pendalaman (par. 34)", fitur: "Hasil per prosedur; bukti dengan bentuk, teknik, asal, penilaian ketepatan, penanda keaslian, SHA-256" },
  { tahap: "3b · Temuan", dasar: "SPKN Pelaksanaan par. 39–42; Pelaporan par. 18–21: kondisi ≠ kriteria; unsur kondisi, kriteria, akibat, sebab; sumber kriteria; indikasi awal kecurangan", fitur: "Editor temuan berunsur; kriteria + sumber wajib; penanda indikasi kecurangan + peringatan" },
  { tahap: "4 · Reviu berjenjang", dasar: "SPKN Pelaksanaan par. 43–45: supervisi berjenjang; struktur tim: pengendali teknis → ketua tim → anggota (Perban BPKP 6/2023)", fitur: "Reviewer meninjau tiap bukti; tak boleh meninjau miliknya; dapat mengembalikan dengan alasan" },
  { tahap: "5 · Komunikasi hasil", dasar: "SPKN Pelaporan par. 26–28: tanggapan tertulis pihak bertanggung jawab, didokumentasikan di kertas kerja", fitur: "Tanggapan per temuan wajib sebelum selesai" },
  { tahap: "6 · Selesai / Dihentikan", dasar: "SPKN Pelaporan par. 12, 22–25 (unsur LHP, rekomendasi menyebut pihak); Pelaksanaan par. 46–47 (penghentian tertulis)", fitur: "Kesimpulan wajib; rekomendasi + pihak; alasan henti wajib" },
  { tahap: "7 · Tindak lanjut", dasar: "SPKN Pelaporan par. 10–11: pemantauan tindak lanjut; kewenangan menindaklanjuti ada pada entitas (Perban BPKP 6/2026 L.I angka 8)", fitur: "Status tindak lanjut per rekomendasi + catatan bukti" },
];

const UNVERIFIED = [
  "Lampiran III Perban BPKP 3/2019 dan Lampiran II–VIII Perban BPKP 6/2026 (langkah kerja rinci, kertas kerja) tidak dapat diakses saat riset. Program audit disusun dari pasal Perpres, bukan salinan pedoman itu.",
  "Perban BPKP 6/2026 dibaca dari salinan pasal.id yang berstatus “belum ditinjau”; verifikasi ke Berita Negara 2026 No. 684.",
  "OECD Guidelines on Fighting Bid Rigging (2025) tidak dapat diakses; red flags diambil dari IACRC.",
  "Persetujuan program audit oleh pengendali teknis, surat tugas, dan management representation letter tidak dimodelkan.",
  "Alur ini belum divalidasi oleh auditor praktisi.",
];

export default function MethodologyPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <p className="eyebrow">Dasar metodologi</p>
        <h2 className="font-display text-3xl font-extrabold text-primary">Dari mana alur audit ini berasal</h2>
        <p className="mt-2 text-muted">Setiap tahap dan aturan di Auditra ditelusuri ke standar atau peraturan yang dibaca langsung. Riset lengkap beserta status verifikasi tiap sumber ada di <code>docs/RISET_PROSES_AUDIT.md</code>.</p>
      </header>

      <section className="panel space-y-3">
        <h3 className="panel-title">Pelaku dan landasan</h3>
        <ul className="space-y-2 text-sm text-muted">
          <li><b className="text-primary">BPK (eksternal):</b> Standar Pemeriksaan Keuangan Negara. PBPK 1/2017 berlaku; <b>PBPK 1/2026</b> (ditetapkan 10 April 2026) berlaku 2 tahun setelah diundangkan.</li>
          <li><b className="text-primary">APIP (internal):</b> Perpres 16/2018 Pasal 76 (pengawasan sejak perencanaan hingga serah terima); Peraturan BPKP 6/2026 mencabut Perban BPKP 3/2019.</li>
          <li><b className="text-primary">Kriteria hukum:</b> Perpres 16/2018 jo. 12/2021 jo. <b>46/2025</b> (teks konsolidasi JDIH LKPP). Contoh yang dipakai: Pasal 20(2)(d) pemecahan paket, Pasal 22 SIRUP, Pasal 26 HPS, Pasal 38/41 metode dan batas nilai, Pasal 54, 56–58, 61, 65, 66.</li>
        </ul>
      </section>

      <section className="panel">
        <h3 className="panel-title mb-3">Siklus penugasan dan pemetaannya</h3>
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>Tahap</th><th>Dasar</th><th>Di Auditra</th></tr></thead>
            <tbody>{CYCLE.map((r) => <tr key={r.tahap}><td className="whitespace-nowrap font-semibold text-primary">{r.tahap}</td><td className="text-muted">{r.dasar}</td><td className="text-primary">{r.fitur}</td></tr>)}</tbody>
          </table>
        </div>
      </section>

      <section className="panel space-y-2">
        <h3 className="panel-title">Koreksi metodologi hasil riset</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
          <li>Batas pengadaan langsung <b>konstruksi kini Rp400 juta</b> (Pasal 38(3)(b)); sinyal fragmentasi memakai ambang tunggal Rp200 juta. Program audit sudah memakai batas yang benar per jenis; skor RPI belum dihitung ulang.</li>
          <li>Paket ≤ <b>Rp15 miliar</b> diperuntukkan UMK (Pasal 65(3)); sinyal “anomali UMKM” memakai persentil data, bukan batas hukum ini.</li>
          <li><b>HPS bukan dasar menghitung kerugian negara</b> (Pasal 26(6)): sinyal anomali pagu tidak boleh dibaca sebagai kemahalan harga.</li>
        </ul>
      </section>

      <section className="panel space-y-2" style={{ borderColor: "#f59e0b" }}>
        <h3 className="panel-title flex items-center gap-2"><Icon name="alert" size={18} className="text-amber-500" /> Yang belum terverifikasi</h3>
        <ul className="list-disc space-y-1 pl-5 text-sm text-muted">{UNVERIFIED.map((u) => <li key={u}>{u}</li>)}</ul>
      </section>

      <Link to="/" className="btn-secondary"><Icon name="arrowLeft" size={15} /> Kembali ke dasbor</Link>
    </div>
  );
}
