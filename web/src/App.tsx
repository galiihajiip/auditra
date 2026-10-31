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

