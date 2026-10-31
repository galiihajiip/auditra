import { useEffect, useState } from "react";
import type { PaginatedPackages } from "../types";

type Row = Record<string, unknown>;

const SIGNALS: { key: string; label: string; weight: string; hint: string }[] = [
  { key: "s1_metode", label: "S1 Metode pemilihan", weight: "20%", hint: "Penunjukan langsung / dikecualikan = risiko tata kelola lebih tinggi" },
  { key: "s2_pagu_anomali", label: "S2 Anomali pagu", weight: "20%", hint: "Pagu menyimpang dari grup (jenis, metode)" },
  { key: "s3_fragmentasi", label: "S3 Fragmentasi", weight: "15%", hint: "Uraian mirip dalam satker di bawah batas penunjukan langsung" },
  { key: "s4_konsentrasi", label: "S4 Konsentrasi metode", weight: "15%", hint: "Proporsi metode berisiko dalam satker" },
  { key: "s5_umkm", label: "S5 Anomali UMKM", weight: "10%", hint: "Flag UMKM tidak wajar terhadap pagu besar" },
  { key: "s6_dana_metode", label: "S6 Dana + metode", weight: "10%", hint: "Kombinasi sumber dana APBN dan metode berisiko" },
  { key: "s7_reputasi", label: "S7 Reputasi KG", weight: "10%", hint: "Pengaruh risiko lembaga di Knowledge Graph (weighted degree × avg RPI)" },
];

function paguRupiah(row: Row): string {
  const v = Number(row.pagu);
  if (!Number.isFinite(v)) return "—";
  return "Rp " + v.toLocaleString("id-ID");
}

function PackageDetail({ row, onClose }: { row: Row; onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-0 sm:items-center sm:p-4"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Rincian paket"
        className="panel max-h-[90vh] w-full max-w-xl overflow-y-auto rounded-b-none sm:rounded-b-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-2 flex items-start justify-between gap-3">
          <h3 className="text-base font-bold text-primary">{String(row.paket)}</h3>
          <button type="button" className="btn-secondary text-xs" onClick={onClose} autoFocus>
            Tutup ✕
          </button>
        </div>
        <dl className="mb-3 grid grid-cols-[auto,1fr] gap-x-3 gap-y-1 text-xs">
          <dt className="text-muted">ID SIRUP</dt><dd className="text-primary">{String(row.id)}</dd>
          <dt className="text-muted">Lembaga</dt><dd className="text-primary">{String(row.lembaga)}</dd>
          <dt className="text-muted">Metode</dt><dd className="text-primary">{String(row.metode)}</dd>
          <dt className="text-muted">Pagu</dt><dd className="text-primary">{paguRupiah(row)}</dd>
          <dt className="text-muted">Lokasi</dt><dd className="text-primary">{String(row.lokasi || "—")}</dd>
          <dt className="text-muted">RPI</dt>
          <dd className="font-semibold text-primary">
            {Number(row.RPI).toFixed(1)} · {String(row.risk_label)}
          </dd>
        </dl>
        <h4 className="mb-1 text-xs font-semibold uppercase tracking-wide text-muted">
          Mengapa paket ini berprioritas? (sinyal 0–1)
        </h4>
        <ul className="space-y-2">
          {SIGNALS.map((sig) => {
            const v = Math.max(0, Math.min(1, Number(row[sig.key]) || 0));
            return (
              <li key={sig.key} title={sig.hint}>
                <div className="flex justify-between text-[11px] text-primary">
                  <span>{sig.label} <span className="text-muted">· bobot {sig.weight}</span></span>
                  <span className="font-semibold">{v.toFixed(2)}</span>
                </div>
                <div className="h-1.5 overflow-hidden rounded bg-[var(--bg-subtle)]">
                  <div
                    className="h-full rounded"
                    style={{ width: `${v * 100}%`, background: v >= 0.6 ? "var(--accent-orange)" : "var(--accent-blue)" }}
                  />
                </div>
                <p className="text-[10px] text-muted">{sig.hint}</p>
              </li>
            );
          })}
        </ul>
        <p className="mt-3 text-[10px] leading-relaxed text-muted">
          RPI adalah alat <strong>prioritas</strong> audit, bukan temuan atau vonis pelanggaran.
          Sumber: data rencana umum pengadaan SIRUP LKPP; metodologi di docs/METODOLOGI.md.
          Verifikasi lapangan/dokumen tetap diperlukan oleh auditor.
        </p>
        <a
          className="btn-secondary mt-3 inline-block text-xs"
          href="https://sirup.inaproc.id/sirup/caripaketctr/index"
          target="_blank"
          rel="noopener noreferrer"
        >
          Cari paket di SIRUP LKPP ↗
        </a>
      </div>
    </div>
  );
}

interface Props {
  result: PaginatedPackages | null;
  page: number;
  loading?: boolean;
  onPage: (p: number) => void;
}

export default function PackagesTable({ result, page, loading, onPage }: Props) {
  const [selected, setSelected] = useState<Row | null>(null);

  if (!result && loading) {
    return <div className="text-muted">Memuat tabel…</div>;
  }

  if (!result) {
    return <div className="text-muted">Tidak ada data.</div>;
  }

  return (
    <div>
      <p className="mb-3 text-xs text-muted">
        Menampilkan halaman {result.page} dari {result.total_pages} —{" "}
        <strong className="text-primary">{result.total.toLocaleString("id-ID")}</strong> paket
        dengan RPI ≥ 30 (Sedang ke atas) sesuai filter — paket RPI rendah (&lt; 30) tidak ditampilkan di tabel
        tetapi tetap dihitung di statistik. Klik baris untuk rincian sinyal.
        {loading && (
          <span className="ml-2 font-medium" style={{ color: "var(--accent-loading)" }}>
            Memuat…
          </span>
        )}
      </p>
      <div className="table-wrap">
        <table className="data-table">
          <thead>
