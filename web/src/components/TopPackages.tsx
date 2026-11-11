import Icon from "./Icon";
import PackageCard, { type PkgRow } from "./PackageCard";
import Skeleton from "./Skeleton";

export default function TopPackages({ rows, loading, hasFilter }: { rows: PkgRow[] | null; loading: boolean; hasFilter: boolean }) {
  return (
    <section id="prioritas" aria-labelledby="prioritas-h">
      <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
        <div>
          <p className="eyebrow">Langkah 1 · Temukan</p>
          <h2 id="prioritas-h" className="font-display text-2xl font-extrabold text-primary">Prioritas audit teratas</h2>
          <p className="text-sm text-muted">{hasFilter ? "Paket dengan RPI tertinggi sesuai filter Anda." : "Paket dengan RPI tertinggi di seluruh dataset."} Klik kartu untuk melihat alasannya.</p>
        </div>
        <a href="#semua-paket" className="inline-flex items-center gap-1 text-sm font-semibold text-[var(--accent-teal)]">Lihat semua paket <Icon name="arrowRight" size={14} /></a>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {!rows || (loading && rows.length === 0)
          ? Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-[184px] !rounded-2xl" />)
          : rows.slice(0, 6).map((r, i) => <PackageCard key={String(r.id)} row={r} rank={i + 1} />)}
      </div>
      {rows && rows.length === 0 && !loading && (
        <p className="panel text-center text-sm text-muted">Tidak ada paket RPI ≥ 30 untuk kombinasi filter ini. Coba longgarkan filter.</p>
      )}
    </section>
  );
}
