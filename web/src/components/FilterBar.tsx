import type { Filters } from "../types";
import Icon from "./Icon";

interface Props {
  filters: Filters;
  onChange: (next: Partial<Filters>) => void;
  onReset: () => void;
  options: { lembaga: string[]; metode: string[]; provinsi: string[] };
}

const RPI_PRESETS: { v: number; label: string }[] = [
  { v: 0, label: "Semua" },
  { v: 30, label: "Sedang+" },
  { v: 50, label: "Tinggi+" },
  { v: 70, label: "Kritis" },
];

export default function FilterBar({ filters, onChange, onReset, options }: Props) {
  const active = [filters.provinsi !== "ALL", filters.lembaga !== "ALL", filters.metode !== "ALL", filters.riskMin > 0].filter(Boolean).length;
  const sel = (label: string, value: string, key: "provinsi" | "lembaga" | "metode", all: string, items: string[]) => (
    <div>
      <label className="field-label" htmlFor={`f-${key}`}>{label}</label>
      <select id={`f-${key}`} className="input-select" value={value} onChange={(e) => onChange({ [key]: e.target.value })}>
        <option value="ALL">{all}</option>
        {items.map((x) => <option key={x} value={x}>{x}</option>)}
      </select>
    </div>
  );

  return (
    <section className="panel" aria-label="Filter">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h2 className="panel-title flex items-center gap-2"><Icon name="filter" size={18} /> Fokuskan pencarian</h2>
        <div className="flex items-center gap-2">
          {active > 0 && <span className="chip" style={{ color: "var(--accent-teal)" }}>{active} filter aktif</span>}
          <button type="button" className="btn-secondary !py-1.5 text-sm" onClick={onReset} disabled={active === 0}>
            <Icon name="refresh" size={14} /> Reset
          </button>
        </div>
      </div>
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {sel("Provinsi", filters.provinsi, "provinsi", "Semua provinsi", options.provinsi)}
        {sel("Lembaga", filters.lembaga, "lembaga", "Semua lembaga", options.lembaga)}
        {sel("Metode pemilihan", filters.metode, "metode", "Semua metode", options.metode)}
      </div>
      <div className="mt-3">
        <span className="field-label" id="rpi-label">Tingkat risiko minimum (RPI)</span>
        <div className="flex flex-wrap gap-2" role="radiogroup" aria-labelledby="rpi-label">
          {RPI_PRESETS.map((p) => (
            <button key={p.v} type="button" role="radio" aria-checked={filters.riskMin === p.v}
              className={`tab-btn ${filters.riskMin === p.v ? "tab-btn-active" : ""}`} onClick={() => onChange({ riskMin: p.v })}>
              {p.label}{p.v > 0 && <span className="text-xs opacity-70">≥{p.v}</span>}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
