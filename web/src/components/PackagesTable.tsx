import { useNavigate } from "react-router-dom";
import type { PaginatedPackages } from "../types";
import { formatPaguCompact } from "../utils/formatPagu";
import EmptyState from "./EmptyState";
import Icon from "./Icon";
import PackageCard from "./PackageCard";
import { RISK_COLOR } from "./RpiRing";
import Skeleton from "./Skeleton";

interface Props {
  result: PaginatedPackages | null;
  page: number;
  loading?: boolean;
  onPage: (p: number) => void;
}

export default function PackagesTable({ result, page, loading, onPage }: Props) {
  const navigate = useNavigate();

  if (!result) {
    return <div className="space-y-2">{Array.from({ length: 6 }, (_, i) => <Skeleton key={i} className="h-12" />)}</div>;
  }

  if (result.data.length === 0) {
    return <EmptyState icon="search" title="Tidak ada paket yang cocok">Tidak ada paket dengan RPI ≥ 30 untuk kombinasi filter ini. Coba longgarkan filter di atas.</EmptyState>;
  }

  const open = (id: unknown) => navigate(`/paket/${String(id)}`);
  const from = (result.page - 1) * result.page_size + 1;
  const to = from + result.data.length - 1;

  return (
    <div>
      <p className="mb-3 text-sm text-muted">
        Menampilkan <b className="num text-primary">{from.toLocaleString("id-ID")}–{to.toLocaleString("id-ID")}</b> dari{" "}
        <b className="num text-primary">{result.total.toLocaleString("id-ID")}</b> paket dengan RPI ≥ 30 (Sedang ke atas).
        Paket RPI rendah tetap dihitung di statistik tetapi tidak ditampilkan di sini.
        {loading && <span className="ml-2 font-medium" style={{ color: "var(--accent-loading)" }}>Memuat…</span>}
      </p>

      {/* ponsel: kartu */}
      <div className="grid gap-3 md:hidden">
        {result.data.map((row, i) => <PackageCard key={String(row.id)} row={row} rank={from + i} />)}
      </div>

      {/* desktop: tabel */}
      <div className="table-wrap hidden md:block">
        <table className="data-table">
          <thead>
            <tr>
              <th>RPI</th><th>Paket</th><th>Lembaga</th><th>Metode</th>
              <th className="text-right" title="Pagu paket">Pagu</th><th className="hidden xl:table-cell">Lokasi</th><th><span className="sr-only">Buka</span></th>
            </tr>
          </thead>
          <tbody>
            {result.data.map((row) => {
              const label = String(row.risk_label || "");
              const rowClass = label === "KRITIS" ? "row-kriti" : label === "TINGGI" ? "row-tinggi" : "";
              const pagu = row.pagu_miliar != null ? Number(row.pagu_miliar) : Number(row.pagu) / 1e9;
              return (
                <tr key={String(row.id)} className={rowClass} tabIndex={0} role="button"
                  aria-label={`Buka passport paket ${String(row.paket)}`}
                  onClick={() => open(row.id)}
                  onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), open(row.id))}>
                  <td className="whitespace-nowrap">
                    <span className="num mr-2 font-bold text-primary">{Number(row.RPI).toFixed(1)}</span>
                    <span className="status-pill !px-2 !py-0 !text-xs" style={{ color: RISK_COLOR[label] }}>{label}</span>
                  </td>
                  <td className="max-w-sm"><span className="line-clamp-2 font-medium text-primary" title={String(row.paket)}>{String(row.paket)}</span></td>
                  <td className="max-w-[200px] truncate text-muted" title={String(row.lembaga)}>{String(row.lembaga)}</td>
                  <td className="whitespace-nowrap text-muted">{String(row.metode)}</td>
                  <td className="num whitespace-nowrap text-right font-semibold text-primary">{formatPaguCompact(pagu)}</td>
                  <td className="hidden max-w-[200px] truncate text-muted xl:table-cell">{String(row.lokasi || "")}</td>
                  <td className="text-[var(--accent-teal)]"><Icon name="arrowRight" size={16} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex items-center justify-between gap-2">
        <button type="button" disabled={page <= 1 || loading} onClick={() => onPage(page - 1)} className="btn-secondary">
          <Icon name="arrowLeft" size={15} /> Sebelumnya
        </button>
        <span className="num text-sm text-muted">Halaman {page.toLocaleString("id-ID")} / {result.total_pages.toLocaleString("id-ID")}</span>
        <button type="button" disabled={page >= result.total_pages || loading} onClick={() => onPage(page + 1)} className="btn-secondary">
          Berikutnya <Icon name="arrowRight" size={15} />
        </button>
      </div>
    </div>
  );
}
