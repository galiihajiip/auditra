import { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import {
  fetchDashboardBundle,
  fetchFilterOptions,
  fetchGeoJson,
  fetchMeta,
  fetchPackages,
} from "../api/client";
import { formatApiError } from "../api/errors";
import ColorLegend from "../components/ColorLegend";
import { MetodeBar, RadarChart, RiskDonut, ScatterChart } from "../components/Charts";
import EntitySidebar from "../components/EntitySidebar";
import FilterBar from "../components/FilterBar";
import FreshnessPanel from "../components/FreshnessPanel";
import Hero from "../components/Hero";
import Icon, { type IconName } from "../components/Icon";
import Logo from "../components/Logo";
import PackagesTable from "../components/PackagesTable";
import type { PkgRow } from "../components/PackageCard";
import { RankProvinsi } from "../components/RankLists";
import StatCards from "../components/StatCards";
import TopPackages from "../components/TopPackages";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useTheme } from "../theme/ThemeContext";
import type {
  ChoroplethRow,
  FilterOptions,
  Filters,
  GeoCoverage,
  MapOwnerMode,
  OverviewStats,
  PaginatedPackages,
  RankRow,
} from "../types";

const ChoroplethMap = lazy(() => import("../components/ChoroplethMap"));
const KgNetwork = lazy(() => import("../components/KgNetwork"));

const PanelFallback = ({ h = 480 }: { h?: number }) => (
  <div className="skeleton" style={{ height: h }} role="status" aria-label="Memuat visual" />
);

type Tab = "peta" | "analitik" | "jaringan";
const TABS: { id: Tab; label: string; icon: IconName; hint: string }[] = [
  { id: "peta", label: "Peta & lembaga", icon: "map", hint: "Sebaran risiko per kab/kota dan lembaga teratas" },
  { id: "analitik", label: "Analitik risiko", icon: "chart", hint: "Distribusi skor, profil 7 sinyal, metode, dan provinsi" },
  { id: "jaringan", label: "Jaringan lembaga", icon: "graph", hint: "Knowledge Graph lembaga–satker mengikuti filter aktif" },
];

const defaultFilters: Filters = { provinsi: "ALL", lembaga: "ALL", metode: "ALL", riskMin: 0 };

export default function DashboardPage() {
  const { isDark } = useTheme();
  const [params, setParams] = useSearchParams();
  const { hash } = useLocation();

  // Filter, halaman, dan tab tersimpan di URL → dapat dibagikan, tahan refresh, dan
  // tombol "kembali" dari passport mengembalikan konteks yang sama.
  const filters: Filters = useMemo(
    () => ({
      provinsi: params.get("provinsi") ?? "ALL",
      lembaga: params.get("lembaga") ?? "ALL",
      metode: params.get("metode") ?? "ALL",
      riskMin: Number(params.get("rpi")) || 0,
    }),
    [params]
  );
  const page = Math.max(1, Number(params.get("p")) || 1);
  const tab: Tab = (["peta", "analitik", "jaringan"] as const).find((t) => t === params.get("tab")) ?? "peta";

  const patchParams = useCallback(
    (patch: Record<string, string | null>) => {
      setParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          for (const [k, v] of Object.entries(patch)) {
            if (v == null || v === "" || v === "ALL" || v === "0" || (k === "p" && v === "1") || (k === "tab" && v === "peta")) next.delete(k);
            else next.set(k, v);
          }
          return next;
        },
        { replace: true }
      );
    },
    [setParams]
  );

  const onFilterChange = useCallback(
    (next: Partial<Filters>) => {
      patchParams({
        ...(next.provinsi !== undefined && { provinsi: next.provinsi }),
        ...(next.lembaga !== undefined && { lembaga: next.lembaga }),
        ...(next.metode !== undefined && { metode: next.metode }),
        ...(next.riskMin !== undefined && { rpi: String(next.riskMin) }),
        p: null,
      });
    },
    [patchParams]
  );
  const onReset = useCallback(() => patchParams({ provinsi: null, lembaga: null, metode: null, rpi: null, p: null }), [patchParams]);
  const setPage = useCallback((p: number) => patchParams({ p: String(p) }), [patchParams]);

  const [options, setOptions] = useState<FilterOptions>({ lembaga: [], metode: [], provinsi: [] });
  const [error, setError] = useState<string | null>(null);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [packagesLoading, setPackagesLoading] = useState(false);

  const [overview, setOverview] = useState<OverviewStats | null>(null);
  const [geoCoverage, setGeoCoverage] = useState<GeoCoverage | null>(null);
  const [choroplethModes, setChoroplethModes] = useState<Record<MapOwnerMode, ChoroplethRow[]>>({ kl: [], pemprov: [], pemkot: [], others: [] });
  const [geojson, setGeojson] = useState<GeoJSON.FeatureCollection | null>(null);
  const [riskDist, setRiskDist] = useState<{ risk_label: string; count: number }[]>([]);
  const [metode, setMetode] = useState<{ metode: string; jumlah: number; avg_rpi: number }[]>([]);
  const [scatter, setScatter] = useState<{ pagu_miliar: number; RPI: number; risk_label: string }[]>([]);
  const [signals, setSignals] = useState<Record<string, number>>({});
  const [rankLembaga, setRankLembaga] = useState<RankRow[]>([]);
  const [rankProvinsi, setRankProvinsi] = useState<RankRow[]>([]);
  const [kg, setKg] = useState<{ nodes: Record<string, unknown>[]; edges: Record<string, unknown>[] }>({ nodes: [], edges: [] });
  const [packages, setPackages] = useState<PaginatedPackages | null>(null);
  const [topPkgs, setTopPkgs] = useState<PkgRow[] | null>(null);

  const debouncedFilters = useDebouncedValue(filters, 350);
  const dashboardGen = useRef(0);
  const packagesGen = useRef(0);

  const onLembagaSelect = useCallback(
    (lembaga: string) => onFilterChange({ lembaga: filters.lembaga === lembaga ? "ALL" : lembaga }),
    [filters.lembaga, onFilterChange]
  );
  const onRegionClick = useCallback(
    (provinsi: string) => onFilterChange({ provinsi: filters.provinsi === provinsi ? "ALL" : provinsi }),
    [filters.provinsi, onFilterChange]
  );

  useEffect(() => {
    if (hash) setTimeout(() => document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: "smooth", block: "start" }), 400);
  }, [hash]);

  const scrollTo = (id: string) => document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });

  useEffect(() => {
    (async () => {
      try {
        const [, opt, geo] = await Promise.all([
          fetchMeta(),
          fetchFilterOptions(),
          fetchGeoJson(),
        ]);
        setOptions(opt);
        setGeojson(geo as GeoJSON.FeatureCollection);
        setError(null);
      } catch (e: unknown) {
        setError(formatApiError(e));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    if (error) return;
    const gen = ++dashboardGen.current;
    setLoading(true);
    setDashboardError(null);
    (async () => {
      try {
        const bundle = await fetchDashboardBundle(debouncedFilters);
        if (gen !== dashboardGen.current) return;
        setOverview(bundle.overview);
        setGeoCoverage(bundle.geo_coverage);
        setChoroplethModes(
          bundle.choropleth_modes ?? {
            kl: bundle.choropleth,
            pemprov: [],
            pemkot: [],
            others: [],
          }
        );
        setRiskDist(bundle.risk_distribution);
        setMetode(bundle.metode);
        setScatter(bundle.scatter);
        setSignals(bundle.signals);
        setRankLembaga(bundle.rank_lembaga);
        setRankProvinsi(bundle.rank_provinsi);
        setKg(bundle.kg);
        setDashboardError(null);
      } catch (e) {
        console.error(e);
        if (gen === dashboardGen.current) {
          setDashboardError(formatApiError(e));
        }
      } finally {
        if (gen === dashboardGen.current) setLoading(false);
      }
    })();
  }, [debouncedFilters, error]);

  useEffect(() => {
    if (error) return;
    const gen = ++packagesGen.current;
    setPackagesLoading(true);
    (async () => {
      try {
        const pkg = await fetchPackages(debouncedFilters, page, 50);
        if (gen !== packagesGen.current) return;
        setPackages(pkg);
        if (pkg.page === 1) setTopPkgs(pkg.data);
      } catch (e) {
        console.error(e);
      } finally {
        if (gen === packagesGen.current) setPackagesLoading(false);
      }
    })();
  }, [debouncedFilters, page, error]);


  if (error) {
    return (
      <div className="flex flex-col items-center justify-center gap-6 p-6 sm:p-8">
        <Logo size="lg" />
        <div className="panel max-w-lg border-red-400 dark:border-red-800">
          <h2 className="text-lg font-bold text-red-500">Dataset belum siap</h2>
          <p className="mt-2 whitespace-pre-line text-sm text-muted">{error}</p>
        </div>
      </div>
    );
  }

  const hasFilter = filters.provinsi !== "ALL" || filters.lembaga !== "ALL" || filters.metode !== "ALL" || filters.riskMin > 0;

  return (
    <div className="space-y-8">
      {(loading || packagesLoading) && <div className="skeleton fixed inset-x-0 top-0 z-[70] h-0.5 !rounded-none" role="progressbar" aria-label="Memperbarui data" />}

      <Hero onStart={() => scrollTo("prioritas")} preview={topPkgs?.[0] ?? null} />
      <FreshnessPanel />

      {dashboardError && (
        <p role="alert" className="rounded-xl border border-red-400/50 bg-red-500/10 px-4 py-3 text-sm text-red-500">
          Gagal memuat data filter: {dashboardError}
        </p>
      )}

      <div className="space-y-4">
        <FilterBar filters={filters} onChange={onFilterChange} onReset={onReset} options={options} />
        <StatCards stats={overview} geoCoverage={geoCoverage} />
      </div>

      <TopPackages rows={topPkgs} loading={packagesLoading} hasFilter={hasFilter} />

      <section id="eksplorasi" aria-labelledby="eksplorasi-h">
        <p className="eyebrow">Langkah 2 · Pahami konteks</p>
        <h2 id="eksplorasi-h" className="font-display text-2xl font-extrabold text-primary">Jelajahi pola risiko</h2>
        <div className="scroll-x mb-3 mt-3 flex gap-2" role="tablist" aria-label="Tampilan eksplorasi">
          {TABS.map((t) => (
            <button key={t.id} role="tab" aria-selected={tab === t.id} id={`tab-${t.id}`} aria-controls={`panel-${t.id}`}
              className={`tab-btn ${tab === t.id ? "tab-btn-active" : ""}`} onClick={() => patchParams({ tab: t.id })}>
              <Icon name={t.icon} size={16} /> {t.label}
            </button>
          ))}
        </div>
        <p className="mb-3 text-sm text-muted">{TABS.find((t) => t.id === tab)?.hint}</p>

        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`} className="fade-up" key={tab}>
          {tab === "peta" && (
            <div className="grid gap-4 lg:grid-cols-12">
              <div className="panel lg:col-span-8">
                <Suspense fallback={<PanelFallback />}>
                  <ChoroplethMap modes={choroplethModes} geojson={geojson} isDark={isDark} onRegionClick={onRegionClick} />
                </Suspense>
              </div>
              <div className="panel lg:col-span-4 lg:self-start">
                <h3 className="panel-title">Lembaga prioritas</h3>
                <p className="panel-sub mb-3">Klik lembaga untuk memfilter seluruh halaman.</p>
                <EntitySidebar data={rankLembaga} selectedLembaga={filters.lembaga !== "ALL" ? filters.lembaga : undefined} onSelect={onLembagaSelect} />
              </div>
            </div>
          )}

          {tab === "analitik" && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-12">
              <div className="panel lg:col-span-4">
                <h3 className="panel-title mb-2">Distribusi risiko</h3>
                <RiskDonut data={riskDist} />
              </div>
              <div className="panel lg:col-span-4">
                <h3 className="panel-title mb-2">Profil 7 sinyal</h3>
                <RadarChart signals={signals} />
              </div>
              <div className="panel max-h-[360px] overflow-y-auto md:col-span-2 lg:col-span-4">
                <h3 className="panel-title mb-3">Provinsi paling berisiko</h3>
                <RankProvinsi data={rankProvinsi} />
              </div>
              <div className="panel lg:col-span-5">
                <h3 className="panel-title mb-2">Rata-rata RPI per metode</h3>
                <MetodeBar data={metode} />
                <ColorLegend className="mt-2" items={[{ color: "#4f8ff7", label: "RPI < 30" }, { color: "#f97316", label: "RPI ≥ 30" }]} />
              </div>
              <div className="panel lg:col-span-7">
                <h3 className="panel-title mb-1">Pagu vs RPI</h3>
                <p className="panel-sub mb-2">Sampel acak maks. 3.000 titik agar tetap ringan.</p>
                <ScatterChart points={scatter} />
              </div>
            </div>
          )}

          {tab === "jaringan" && (
            <div className="panel">
              <Suspense fallback={<PanelFallback h={400} />}>
                <KgNetwork
                  key={`${debouncedFilters.provinsi}|${debouncedFilters.lembaga}|${debouncedFilters.metode}|${debouncedFilters.riskMin}`}
                  nodes={kg.nodes}
                  edges={kg.edges}
                />
              </Suspense>
            </div>
          )}
        </div>
      </section>

      <section id="semua-paket" aria-labelledby="semua-h" className="panel">
        <p className="eyebrow">Langkah 3 · Tindak lanjuti</p>
        <h2 id="semua-h" className="mb-3 font-display text-2xl font-extrabold text-primary">Semua paket prioritas</h2>
        <PackagesTable result={packages} page={page} loading={packagesLoading} onPage={(p) => { setPage(p); scrollTo("semua-paket"); }} />
      </section>
    </div>
  );
}
