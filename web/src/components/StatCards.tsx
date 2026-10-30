import { formatPaguCompact } from "../utils/formatPagu";
import type { GeoCoverage, OverviewStats } from "../types";

interface Props {
  stats: OverviewStats | null;
  geoCoverage: GeoCoverage | null;
}

export default function StatCards({ stats, geoCoverage }: Props) {
  const mapped = geoCoverage?.mapped_packages ?? 0;
  const total = geoCoverage?.total_packages ?? 0;
  const unmapped = geoCoverage?.unmapped_packages ?? 0;
  const multi = geoCoverage?.multi_lokasi_packages ?? 0;

  return (
    <div className="mb-4 grid grid-cols-1 gap-3 lg:grid-cols-12">
      <div className="stat-card border-blue-500 lg:col-span-4">
        <p className="text-[11px] uppercase tracking-wide text-muted">Total Nilai Pagu (filter)</p>
        <p className="mt-1 text-3xl font-extrabold text-primary">
          {stats ? formatPaguCompact(stats.total_pagu_miliar) : "—"}
        </p>
        <p className="text-[11px] text-muted">
          Akumulasi pagu paket dalam filter aktif · prioritas audit via RPI
        </p>
      </div>
