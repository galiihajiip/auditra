import type { CasePhase } from "../api/client";

export const PHASE_LABEL: Record<CasePhase, string> = {
  seleksi: "Seleksi sasaran",
  perencanaan: "Perencanaan",
  pelaksanaan: "Pelaksanaan",
  reviu: "Reviu berjenjang",
  komunikasi: "Komunikasi hasil",
  selesai: "Selesai",
  dihentikan: "Dihentikan",
};

export const PHASE_HINT: Record<CasePhase, string> = {
  seleksi: "Tetapkan alasan pemilihan sasaran",
  perencanaan: "Tujuan, lingkup, risiko, program audit",
  pelaksanaan: "Uji prosedur, kumpulkan bukti, susun temuan",
  reviu: "Pengendali teknis meninjau bukti",
  komunikasi: "Tanggapan tertulis entitas",
  selesai: "Kesimpulan & pemantauan tindak lanjut",
  dihentikan: "Penugasan dihentikan",
};

export const PHASE_COLOR: Record<CasePhase, string> = {
  seleksi: "#4f8ff7",
  perencanaan: "#a78bfa",
  pelaksanaan: "#eab308",
  reviu: "#f97316",
  komunikasi: "#2dd4bf",
  selesai: "#22c55e",
  dihentikan: "#94a3b8",
};

export const PHASE_FLOW: CasePhase[] = ["seleksi", "perencanaan", "pelaksanaan", "reviu", "komunikasi", "selesai"];
export const ACTIVE_PHASES: CasePhase[] = ["seleksi", "perencanaan", "pelaksanaan", "reviu", "komunikasi"];

export const FORM_LABEL: Record<string, string> = {
  catatan_transaksi: "Catatan transaksi",
  komunikasi_pihak_luar: "Komunikasi pihak luar",
  hasil_observasi: "Hasil observasi",
  keterangan_entitas: "Keterangan entitas",
};

export function fmtDate(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? iso
    : d.toLocaleString("id-ID", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function fmtRupiah(v: number | null | undefined): string {
  return v == null || !Number.isFinite(Number(v)) ? "—" : "Rp " + Number(v).toLocaleString("id-ID");
}

export function fmtBytes(n: number | null): string {
  if (n == null) return "";
  return n > 1024 * 1024 ? `${(n / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(n / 1024))} KB`;
}

export function fromNow(iso: string): string {
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return iso;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 60) return "baru saja";
  if (s < 3600) return `${Math.floor(s / 60)} mnt lalu`;
  if (s < 86400) return `${Math.floor(s / 3600)} jam lalu`;
  return `${Math.floor(s / 86400)} hari lalu`;
}

export function actionLabel(from: CasePhase, to: CasePhase): string {
  const k = `${from}>${to}`;
  const m: Record<string, string> = {
    "seleksi>perencanaan": "Mulai perencanaan",
    "perencanaan>pelaksanaan": "Mulai pelaksanaan",
    "pelaksanaan>reviu": "Ajukan ke reviu",
    "reviu>pelaksanaan": "Kembalikan untuk perbaikan",
    "reviu>komunikasi": "Terima kertas kerja → komunikasi",
    "reviu>selesai": "Selesaikan tanpa temuan",
    "komunikasi>selesai": "Selesaikan penugasan",
  };
  return m[k] ?? (to === "dihentikan" ? "Hentikan penugasan" : PHASE_LABEL[to]);
}
