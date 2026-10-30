import type { Filters } from "../types";

interface Props {
  filters: Filters;
  onChange: (next: Partial<Filters>) => void;
  options: { lembaga: string[]; metode: string[]; provinsi: string[] };
}

export default function FilterBar({ filters, onChange, options }: Props) {
  return (
    <div className="mb-4 grid grid-cols-1 gap-3 md:grid-cols-4">
      <div>
        <p className="mb-1 text-[10px] uppercase tracking-wide text-muted">Provinsi</p>
        <select
          className="input-select"
          value={filters.provinsi}
          onChange={(e) => onChange({ provinsi: e.target.value })}
        >
          <option value="ALL">Semua Provinsi</option>
          {options.provinsi.map((p) => (
            <option key={p} value={p}>{p}</option>
          ))}
        </select>
      </div>
      <div>
        <p className="mb-1 text-[10px] uppercase tracking-wide text-muted">Lembaga</p>
