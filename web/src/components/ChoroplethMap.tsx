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

