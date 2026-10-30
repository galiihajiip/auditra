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

