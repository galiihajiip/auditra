import { Suspense, lazy, useCallback, useEffect, useRef, useState } from "react";
import {
  fetchDashboardBundle,
  fetchFilterOptions,
  fetchGeoJson,
  fetchMeta,
  fetchPackages,
} from "./api/client";
import { formatApiError } from "./api/errors";
import ColorLegend from "./components/ColorLegend";
import { MetodeBar, RadarChart, RiskDonut, ScatterChart } from "./components/Charts";
import EntitySidebar from "./components/EntitySidebar";
import FilterBar from "./components/FilterBar";
import PackagesTable from "./components/PackagesTable";
import { RankProvinsi } from "./components/RankLists";
import AppHeader from "./components/AppHeader";
import Logo from "./components/Logo";
import SiteFooter from "./components/SiteFooter";
import StatCards from "./components/StatCards";
import { useDebouncedValue } from "./hooks/useDebouncedValue";
import { useTheme } from "./theme/ThemeContext";
import type {
  ChoroplethRow,
  FilterOptions,
  Filters,
  GeoCoverage,
  MapOwnerMode,
  OverviewStats,
  PaginatedPackages,
  RankRow,
} from "./types";

const ChoroplethMap = lazy(() => import("./components/ChoroplethMap"));
const KgNetwork = lazy(() => import("./components/KgNetwork"));

const PanelFallback = ({ h = 480 }: { h?: number }) => (
  <div className="flex items-center justify-center text-muted" style={{ height: h }}>
    Memuat visual…
  </div>
);

const defaultFilters: Filters = {
  provinsi: "ALL",
  lembaga: "ALL",
  metode: "ALL",
  riskMin: 0,
};

export default function App() {
  const { toggle, isDark } = useTheme();
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [options, setOptions] = useState<FilterOptions>({
    lembaga: [],
    metode: [],
    provinsi: [],
  });
  const [error, setError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [packagesLoading, setPackagesLoading] = useState(false);

  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [geoCoverage, setGeoCoverage] = useState<GeoCoverage | null>(null);
  const [choroplethModes, setChoroplethModes] = useState<Record<MapOwnerMode, ChoroplethRow[]>>({
    kl: [],
    pemprov: [],
    pemkot: [],
    others: [],
  });
  const [geojson, setGeojson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [riskDist, setRiskDist] = useState<{ risk_label: string; count: number }[]>([]);
  const [metode, setMetode] = useState<{ metode: string; jumlah: number; avg_rpi: number }[]>([]);
  const [scatter, setScatter] = useState<{ pagu_miliar: number; RPI: number; risk_label: string }[]>(
    []
  );
  const [signals, setSignals] = useState<Record<string, number>>({});
  const [rankLembaga, setRankLembaga] = useState<RankRow[]>([]);
  const [rankProvinsi, setRankProvinsi] = useState<RankRow[]>([]);
  const [kg, setKg] = useState<{ nodes: Record<string, unknown>[]; edges: Record<string, unknown>[] }>(
    { nodes: [], edges: [] }
  );
  const [packages, setPackages] = useState<PaginatedPackages | null>(null);
  const [page, setPage] = useState(1);

  const debouncedFilters = useDebouncedValue(filters, 350);
  const dashboardGen = useRef(0);
  const packagesGen = useRef(0);

  const onFilterChange = useCallback((next: Partial<Filters>) => {
    setFilters((prev) => ({ ...prev, ...next }));
    setPage(1);
  }, []);

  const onLembagaSelect = useCallback(
    (lembaga: string) => {
      onFilterChange({
        lembaga: filters.lembaga === lembaga ? "ALL" : lembaga,
      });
    },
    [filters.lembaga, onFilterChange]
  );

  const onRegionClick = useCallback(
    (provinsi: string) => {
      onFilterChange({
        provinsi: filters.provinsi === provinsi ? "ALL" : provinsi,
      });
    },
    [filters.provinsi, onFilterChange]
  );
