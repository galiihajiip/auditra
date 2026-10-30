export type MapOwnerMode = "kl" | "pemprov" | "pemkot" | "others";

export interface Filters {
  provinsi: string;
  lembaga: string;
  metode: string;
  riskMin: number;
}

export interface MetaResponse {
  total_rows: number;
  total_columns: number;
  columns: string[];
  source_file: string;
  source_kind: string;
  integrity: string;
  note: string;
}

export interface OverviewStats {
  total_paket: number;
  total_pagu_miliar: number;
  paket_kritis: number;
  avg_rpi: number;
  split_contract: number;
}

export interface GeoCoverage {
  total_packages: number;
  mapped_packages: number;
  unmapped_packages: number;
  multi_lokasi_packages: number;
}

export interface FilterOptions {
  lembaga: string[];
  metode: string[];
  provinsi: string[];
}

export interface PaginatedPackages {
  data: Record<string, unknown>[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DashboardBundle {
  overview: OverviewStats;
  signals: Record<string, number>;
  risk_distribution: { risk_label: string; count: number }[];
  metode: { metode: string; jumlah: number; avg_rpi: number }[];
  scatter: { pagu_miliar: number; RPI: number; risk_label: string }[];
  rank_lembaga: RankRow[];
  choropleth: ChoroplethRow[];
  choropleth_modes: Record<MapOwnerMode, ChoroplethRow[]>;
  rank_provinsi: RankRow[];
  geo_coverage: GeoCoverage;
  kg: { nodes: Record<string, unknown>[]; edges: Record<string, unknown>[] };
}

