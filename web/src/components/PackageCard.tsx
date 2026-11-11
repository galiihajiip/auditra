import { Link } from "react-router-dom";
import { formatPaguCompact } from "../utils/formatPagu";
import Icon from "./Icon";
import RpiRing, { RISK_COLOR } from "./RpiRing";

export type PkgRow = Record<string, unknown>;

const SIGNALS: { key: string; label: string; weight: number }[] = [
  { key: "s1_metode", label: "Metode berisiko", weight: 0.2 },
  { key: "s2_pagu_anomali", label: "Pagu tak wajar", weight: 0.2 },
  { key: "s3_fragmentasi", label: "Indikasi pecah paket", weight: 0.15 },
  { key: "s4_konsentrasi", label: "Konsentrasi metode", weight: 0.15 },
  { key: "s5_umkm", label: "UMKM janggal", weight: 0.1 },
  { key: "s6_dana_metode", label: "Dana + metode", weight: 0.1 },
  { key: "s7_reputasi", label: "Lembaga berisiko", weight: 0.1 },
];

/** Dua sinyal yang paling menyumbang ke skor — alasan singkat "kenapa paket ini?". */
export function topReasons(row: PkgRow, n = 2): string[] {
  return SIGNALS.map((s) => ({ ...s, c: (Number(row[s.key]) || 0) * s.weight }))
    .filter((s) => s.c >= 0.04)
    .sort((a, b) => b.c - a.c)
    .slice(0, n)
    .map((s) => s.label);
}

export default function PackageCard({ row, rank }: { row: PkgRow; rank?: number }) {
  const rpi = Number(row.RPI) || 0;
  const label = String(row.risk_label ?? "");
  const pagu = Number(row.pagu) / 1e9;
  const reasons = topReasons(row);
  return (
    <Link to={`/paket/${String(row.id)}`} className="panel interactive group flex flex-col gap-3 !p-4 no-underline" aria-label={`Buka passport paket ${String(row.paket)}`}>
      <div className="flex items-start gap-3">
        <RpiRing value={rpi} label={label} size={58} />
        <div className="min-w-0 flex-1">
          <div className="mb-0.5 flex items-center gap-2 text-xs">
            {rank != null && <span className="font-bold text-muted">#{rank}</span>}
            <span className="font-bold" style={{ color: RISK_COLOR[label] }}>{label}</span>
          </div>
          <p className="line-clamp-2 text-[15px] font-semibold leading-snug text-primary">{String(row.paket)}</p>
          <p className="mt-0.5 truncate text-sm text-muted">{String(row.lembaga ?? "")}</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-1.5">
        <span className="chip" style={{ color: "var(--text)" }}>{formatPaguCompact(pagu)}</span>
        <span className="chip">{String(row.metode ?? "")}</span>
      </div>
      {reasons.length > 0 && (
        <p className="text-xs text-muted"><span className="font-semibold text-primary">Pemicu:</span> {reasons.join(" · ")}</p>
      )}
      <span className="mt-auto flex items-center gap-1 text-sm font-semibold text-[var(--accent-teal)]">
        Buka passport <Icon name="arrowRight" size={15} className="transition-transform group-hover:translate-x-1" />
      </span>
    </Link>
  );
}
