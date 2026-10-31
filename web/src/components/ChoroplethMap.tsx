import { useEffect, useMemo, useState } from "react";
import ColorLegend from "./ColorLegend";
import Plot from "react-plotly.js";
import type { PlotMouseEvent } from "plotly.js";
import { useTheme } from "../theme/ThemeContext";
import type { ChoroplethRow, MapOwnerMode } from "../types";
import { formatPaguCompact } from "../utils/formatPagu";
import { normalizeKabkotId } from "../utils/kabkotId";

export type MapMetric = "rpi" | "pagu_risiko";

const MODE_OPTIONS: { id: MapOwnerMode; label: string }[] = [
  { id: "kl", label: "Kementerian/Lembaga" },
  { id: "pemprov", label: "Pemprov" },
  { id: "pemkot", label: "Pemkot/Kab" },
  { id: "others", label: "Lainnya" },
];

const MODE_LEGEND_TITLE: Record<MapOwnerMode, string> = {
  kl: "Prioritas audit paket K/L per kab/kota",
  pemprov: "Prioritas audit paket pemprov per kab/kota",
  pemkot: "Prioritas audit paket pemkot/kab per kab/kota",
  others: "Prioritas audit paket lainnya per kab/kota",
};

/** Warna lebih kontras — mirip referensi AUD (biru → kuning → oranye → merah). */
const COLORSCALE_DARK: [number, string][] = [
  [0, "#1e293b"],
  [0.08, "#2563eb"],
  [0.28, "#60a5fa"],
  [0.48, "#fbbf24"],
  [0.68, "#f97316"],
  [0.88, "#ef4444"],
  [1, "#b91c1c"],
];

const COLORSCALE_LIGHT: [number, string][] = [
  [0, "#e2e8f0"],
  [0.08, "#93c5fd"],
  [0.28, "#fde047"],
  [0.48, "#fb923c"],
  [0.68, "#f97316"],
  [0.88, "#ef4444"],
  [1, "#991b1b"],
];

const INDONESIA_GEO = {
  lonaxis: { range: [94, 142] as [number, number] },
  lataxis: { range: [-12, 7] as [number, number] },
};

interface Props {
  modes: Record<MapOwnerMode, ChoroplethRow[]>;
  geojson: GeoJSON.FeatureCollection | null;
  isDark?: boolean;
  onRegionClick?: (provinsi: string, kabkotName: string) => void;
}

function quantileLabels(values: number[], isDark: boolean): { color: string; label: string }[] {
  const positive = values.filter((v) => v > 0);
  if (positive.length === 0) {
    return [{ color: isDark ? "#1e293b" : "#e2e8f0", label: "Tidak ada data" }];
  }
  const sorted = [...positive].sort((a, b) => a - b);
  const q = (p: number) => sorted[Math.min(sorted.length - 1, Math.floor(p * (sorted.length - 1)))];

  const breaks = [0, q(0.2), q(0.4), q(0.6), q(0.8), q(1)];
  const palette = isDark ? COLORSCALE_DARK : COLORSCALE_LIGHT;

  const items = [{ color: palette[0][1], label: "Tidak ada / nol" }];
  for (let i = 0; i < 5; i++) {
    const lo = breaks[i];
    const hi = breaks[i + 1];
    const color = palette[Math.min(i + 2, palette.length - 1)][1];
    const label =
      i === 0 && lo === hi
        ? formatPaguCompact(lo)
        : `${formatPaguCompact(Math.max(lo, 0.0001))} – ${formatPaguCompact(hi)}`;
    items.push({ color, label });
  }
  return items;
}

export default function ChoroplethMap({ modes, geojson, isDark: isDarkProp, onRegionClick }: Props) {
  const { colors, isDark: isDarkTheme } = useTheme();
  const isDark = isDarkProp ?? isDarkTheme;
  const [ownerMode, setOwnerMode] = useState<MapOwnerMode>("kl");
  const [metric, setMetric] = useState<MapMetric>("pagu_risiko");

  const data = modes[ownerMode] ?? [];

  // Paket K/L (pusat) umumnya tidak punya lokasi kab/kota → mode default bisa kosong.
  // Pindah otomatis ke mode terbesar yang berisi data agar peta tidak tampil kosong.
  useEffect(() => {
    if ((modes[ownerMode] ?? []).length > 0) return;
    const next = (["pemprov", "pemkot", "others", "kl"] as MapOwnerMode[]).find(
      (id) => (modes[id] ?? []).length > 0
    );
    if (next) setOwnerMode(next);
  }, [modes, ownerMode]);

  const isNarrow = typeof window !== "undefined" && window.innerWidth < 640;

  const normalizedGeo = useMemo(() => {
    if (!geojson) return null;
    return {
      ...geojson,
      features: geojson.features.map((f) => ({
        ...f,
        properties: {
          ...f.properties,
          kabkot_id: normalizeKabkotId(f.properties?.kabkot_id as string | number),
        },
      })),
    };
  }, [geojson]);

  const plotConfig = useMemo(() => {
    if (!normalizedGeo) return null;

    const dataById = new Map(
      data.map((d) => [normalizeKabkotId(d.kabkot_id), d] as const)
    );

    const locations = normalizedGeo.features.map(
      (f) => f.properties?.kabkot_id as string
    );
    const isPagu = metric === "pagu_risiko";
    const z = locations.map((id) => {
      const row = dataById.get(id);
      return isPagu ? (row?.pagu_risiko_miliar ?? 0) : (row?.avg_rpi ?? 0);
    });
    const text = locations.map((id) => {
      const row = dataById.get(id);
      if (!row) return `${id}<br>Tidak ada paket (mode ini)`;
      const paguLine = `Pagu berisiko: ${formatPaguCompact(row.pagu_risiko_miliar ?? 0)}`;
      return `${row.kabkot_name}<br>${row.prov_name}<br>Paket: ${row.n_paket}<br>Avg RPI: ${row.avg_rpi}<br>${paguLine}<br>Kritis: ${row.n_kritis}`;
    });

    const colorscale = isDark ? COLORSCALE_DARK : COLORSCALE_LIGHT;
    const positiveZ = z.filter((v) => v > 0);
    const zmax = isPagu
      ? Math.max(...positiveZ, 0.01)
      : Math.max(60, ...positiveZ, 1);

    return {
      data: [
        {
