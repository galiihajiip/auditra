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

