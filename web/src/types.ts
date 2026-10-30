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

