import { useEffect, useState } from "react";
import type { PaginatedPackages } from "../types";

type Row = Record<string, unknown>;

const SIGNALS: { key: string; label: string; weight: string; hint: string }[] = [
  { key: "s1_metode", label: "S1 Metode pemilihan", weight: "20%", hint: "Penunjukan langsung / dikecualikan = risiko tata kelola lebih tinggi" },
  { key: "s2_pagu_anomali", label: "S2 Anomali pagu", weight: "20%", hint: "Pagu menyimpang dari grup (jenis, metode)" },
  { key: "s3_fragmentasi", label: "S3 Fragmentasi", weight: "15%", hint: "Uraian mirip dalam satker di bawah batas penunjukan langsung" },
  { key: "s4_konsentrasi", label: "S4 Konsentrasi metode", weight: "15%", hint: "Proporsi metode berisiko dalam satker" },
  { key: "s5_umkm", label: "S5 Anomali UMKM", weight: "10%", hint: "Flag UMKM tidak wajar terhadap pagu besar" },
  { key: "s6_dana_metode", label: "S6 Dana + metode", weight: "10%", hint: "Kombinasi sumber dana APBN dan metode berisiko" },
  { key: "s7_reputasi", label: "S7 Reputasi KG", weight: "10%", hint: "Pengaruh risiko lembaga di Knowledge Graph (weighted degree × avg RPI)" },
];

function paguRupiah(row: Row): string {
  const v = Number(row.pagu);
  if (!Number.isFinite(v)) return "—";
  return "Rp " + v.toLocaleString("id-ID");
}

