import axios from "axios";
import type {
  DashboardBundle,
  FilterOptions,
  Filters,
  MetaResponse,
  PaginatedPackages,
} from "../types";

/** Dev: Vite proxy `/api` → localhost:8000. Prod: set VITE_API_URL di Vercel. */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 120_000,
});

const dashboardApi = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/api",
  timeout: 300_000,
});

async function withWarmupRetry<T>(fn: () => Promise<T>, attempts = 40): Promise<T> {
  let lastError: unknown;
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (e) {
      lastError = e;
      if (axios.isAxiosError(e) && e.response?.status === 503) {
        await new Promise((r) => setTimeout(r, 3000));
        continue;
      }
      if (axios.isAxiosError(e) && e.response?.status === 502 && i < attempts - 1) {
        await new Promise((r) => setTimeout(r, 5000));
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}

function params(f: Filters, extra: Record<string, unknown> = {}) {
  return {
    provinsi: f.provinsi,
    lembaga: f.lembaga,
    metode: f.metode,
    risk_min: f.riskMin,
    ...extra,
  };
}

export async function fetchMeta(): Promise<MetaResponse> {
  const { data } = await withWarmupRetry(() => api.get<MetaResponse>("/meta"));
  return data;
}

export async function fetchFilterOptions(): Promise<FilterOptions> {
  const { data } = await withWarmupRetry(() => api.get<FilterOptions>("/filters/options"));
  return data;
}

/** All chart data in ONE request (fast, cached server-side). */
export async function fetchDashboardBundle(f: Filters): Promise<DashboardBundle> {
  const { data } = await withWarmupRetry(() =>
    dashboardApi.get<DashboardBundle>("/dashboard/bundle", { params: params(f) })
  );
  return data;
}

export async function fetchPackages(
  f: Filters,
  page: number,
  pageSize: number
): Promise<PaginatedPackages> {
  const { data } = await withWarmupRetry(() =>
    api.get<PaginatedPackages>("/packages", {
      params: {
        ...params(f),
        risk_min: Math.max(f.riskMin, 30),
        page,
        page_size: pageSize,
      },
    })
  );
  return data;
}

export async function fetchGeoJson() {
  const { data } = await withWarmupRetry(() => api.get("/geo/kabkota"));
  return data;
}


// ── Auth & kasus audit ──────────────────────────────────────────────────────
const TOKEN_KEY = "auditra-token";

export function getToken(): string | null {
  try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
}
export function setToken(t: string | null) {
  try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY); } catch { /* storage diblokir */ }
}

const authed = axios.create({ baseURL: import.meta.env.VITE_API_URL ?? "/api", timeout: 60_000 });
authed.interceptors.request.use((cfg) => {
  const t = getToken();
  if (t) cfg.headers.Authorization = `Bearer ${t}`;
  return cfg;
});

export type Role = "auditor" | "reviewer";
export interface User { id: number; email: string; name: string; role: Role }

/** Tahap penugasan audit (docs/RISET_PROSES_AUDIT.md §8). */
export type CasePhase = "seleksi" | "perencanaan" | "pelaksanaan" | "reviu" | "komunikasi" | "selesai" | "dihentikan";
export type ProcStatus = "belum" | "sesuai" | "tidak_sesuai" | "tidak_dapat_diuji";
export type TanggapanStatus = "belum" | "diterima" | "diterima_sebagian" | "ditolak" | "tidak_ada_tanggapan";
export type TlStatus = "belum" | "dalam_proses" | "sesuai" | "tidak_sesuai" | "tidak_dapat_ditindaklanjuti";

export interface CaseRow {
  id: number; package_id: number; title: string; lembaga: string | null; rpi: number | null;
  risk_label: string | null; pagu: number | null; phase: CasePhase; outcome: string | null;
  created_at: string; updated_at: string; created_by_name: string;
  n_evidence: number; n_findings: number; n_tested: number; n_procedures: number;
}
export interface Criterion { ref: string; text: string }
export interface Procedure {
  id: number; code: string; stage: string; title: string; objective: string | null;
  criteria: Criterion[]; evidence_expected: { name: string; form: string }[]; techniques: string[];
  caution: string | null; custom: boolean; status: ProcStatus; result_note: string | null;
}
export interface Evidence {
  id: number; procedure_id: number | null; kind: "link" | "file"; title: string; url: string | null; filename: string | null;
  size_bytes: number | null; sha256: string | null; form: string; technique: string; origin: string; doc_date: string | null;
  relevan: boolean; valid: boolean; andal: boolean; authenticity_concern: boolean; authenticity_note: string | null;
  added_at: string; added_by_name: string; review_status: "pending" | "verified" | "rejected";
  reviewed_by_name: string | null; reviewed_at: string | null; review_note: string | null;
}
export interface Finding {
  id: number; procedure_id: number | null; title: string; kondisi: string; kriteria: string; kriteria_sumber: string;
  sebab: string | null; akibat: string | null; nilai_potensi: number | null; rekomendasi: string | null;
  rekomendasi_kepada: string | null; indikasi_kecurangan: boolean; evidence_ids: number[];
  tanggapan_status: TanggapanStatus; tanggapan: string | null; tl_status: TlStatus; tl_note: string | null;
}
export interface CaseEvent {
  id: number; type: string; from_status: string | null; to_status: string | null;
  body: string | null; created_at: string; user_name: string; user_role: Role;
}
export interface Gate { key: string; label: string; ok: boolean; hint: string | null; blocking: boolean; na?: boolean }
export interface Transition { to: CasePhase; roles: Role[]; note_required: boolean; gates: Gate[]; ready: boolean }
export interface CaseDetail extends Omit<CaseRow, "n_evidence" | "n_findings" | "n_tested" | "n_procedures"> {
  jenis_pengadaan: string | null; metode: string | null;
  selection_reason: string | null; objective: string | null; scope_stages: string[];
  criteria_note: string | null; materiality_note: string | null; risk_note: string | null;
  conclusion: string | null; stop_reason: string | null;
  procedures: Procedure[]; evidence: Evidence[]; findings: Finding[]; events: CaseEvent[];
  transitions: Transition[]; advisories: { key: string; text: string }[];
  meta: { stages: { key: string; label: string }[]; forms: Record<string, string>; techniques: Record<string, string>; origins: Record<string, string> };
}
export interface PackagePassport {
  package: Record<string, string | number | boolean | null>;
  signals: { key: string; label: string; value: number; weight: number; contribution: number }[];
  provenance: {
    source: string; source_url: string; sirup_id: number; dataset_rows: number;
    pipeline: string[]; methodology_doc: string; caveat: string;
  };
}

export const authApi = {
  login: async (email: string, password: string) =>
    (await authed.post<{ token: string; user: User }>("/auth/login", { email, password })).data,
  register: async (name: string, email: string, password: string) =>
    (await authed.post<{ token: string; user: User }>("/auth/register", { name, email, password })).data,
  me: async () => (await authed.get<User>("/auth/me")).data,
};

export interface EvidenceMeta {
  procedure_id?: number | null; form: string; technique: string; origin: string; doc_date?: string;
  relevan: boolean; valid: boolean; andal: boolean; authenticity_concern: boolean; authenticity_note?: string;
}
export type FindingInput = {
  title: string; procedure_id?: number | null; kondisi: string; kriteria: string; kriteria_sumber: string;
  sebab?: string; akibat?: string; nilai_potensi?: number | null; rekomendasi?: string; rekomendasi_kepada?: string;
  indikasi_kecurangan: boolean; evidence_ids: number[];
};

const D = async <T,>(p: Promise<{ data: T }>) => (await p).data;

export const caseApi = {
  passport: async (id: string | number) =>
    (await withWarmupRetry(() => authed.get<PackagePassport>(`/packages/${id}`))).data,
  byPackage: async (id: string | number) =>
    (await authed.get<{ data: { id: number; phase: CasePhase; updated_at: string }[] }>(`/cases/by-package/${id}`)).data.data,
  create: (package_id: number, selection_reason?: string) =>
    D(authed.post<CaseDetail>("/cases", { package_id, selection_reason: selection_reason || undefined })),
  list: async (phase?: string, mine?: boolean) =>
    (await authed.get<{ data: CaseRow[] }>("/cases", { params: { phase, mine } })).data.data,
  stats: () => D(authed.get<{ counts: Record<CasePhase, number>; total: number }>("/cases/stats")),
  get: (id: string | number) => D(authed.get<CaseDetail>(`/cases/${id}`)),
  plan: (id: number, patch: Partial<Pick<CaseDetail, "selection_reason" | "objective" | "scope_stages" | "criteria_note" | "materiality_note" | "risk_note" | "conclusion">>) =>
    D(authed.put<CaseDetail>(`/cases/${id}/plan`, patch)),
  generateProgram: (id: number) => D(authed.post<CaseDetail>(`/cases/${id}/program/generate`)),
  addProcedure: (id: number, body: { title: string; objective?: string; criteria: Criterion[]; techniques: string[] }) =>
    D(authed.post<CaseDetail>(`/cases/${id}/procedures`, body)),
  setResult: (procId: number, status: ProcStatus, result_note?: string) =>
    D(authed.put<CaseDetail>(`/procedures/${procId}/result`, { status, result_note: result_note || undefined })),
  transition: (id: number, to: CasePhase, note?: string) =>
    D(authed.post<CaseDetail>(`/cases/${id}/transition`, { to, note: note || undefined })),
  note: (id: number, body: string) => D(authed.post<CaseDetail>(`/cases/${id}/notes`, { body })),
  addEvidence: (id: number, title: string, opts: { url?: string; file?: File }, meta: EvidenceMeta) => {
    const fd = new FormData();
    fd.append("title", title);
    if (opts.url) fd.append("url", opts.url);
    if (opts.file) fd.append("file", opts.file);
    if (meta.procedure_id) fd.append("procedure_id", String(meta.procedure_id));
    fd.append("form", meta.form); fd.append("technique", meta.technique); fd.append("origin", meta.origin);
    if (meta.doc_date) fd.append("doc_date", meta.doc_date);
    fd.append("relevan", String(meta.relevan)); fd.append("valid", String(meta.valid)); fd.append("andal", String(meta.andal));
    fd.append("authenticity_concern", String(meta.authenticity_concern));
    if (meta.authenticity_note) fd.append("authenticity_note", meta.authenticity_note);
    return D(authed.post<CaseDetail>(`/cases/${id}/evidence`, fd));
  },
  setQuality: (evId: number, q: { relevan: boolean; valid: boolean; andal: boolean; authenticity_concern: boolean; authenticity_note?: string }) =>
    D(authed.put<CaseDetail>(`/evidence/${evId}/quality`, q)),
  review: (evId: number, decision: "verified" | "rejected", note?: string) =>
    D(authed.post<CaseDetail>(`/evidence/${evId}/review`, { decision, note: note || undefined })),
  addFinding: (id: number, f: FindingInput) => D(authed.post<CaseDetail>(`/cases/${id}/findings`, f)),
  updateFinding: (fid: number, f: FindingInput) => D(authed.put<CaseDetail>(`/findings/${fid}`, f)),
  respond: (fid: number, tanggapan_status: TanggapanStatus, tanggapan: string) =>
    D(authed.put<CaseDetail>(`/findings/${fid}/response`, { tanggapan_status, tanggapan })),
  followup: (fid: number, tl_status: TlStatus, tl_note?: string) =>
    D(authed.put<CaseDetail>(`/findings/${fid}/followup`, { tl_status, tl_note })),
  download: async (evidenceId: number, filename: string) => {
    const res = await authed.get(`/evidence/${evidenceId}/file`, { responseType: "blob" });
    const url = URL.createObjectURL(res.data as Blob);
    const a = document.createElement("a");
    a.href = url; a.download = filename; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  },
};

// ── Kesegaran data (snapshot vs SIRUP live) ─────────────────────────────────
export interface Freshness {
  snapshot: { rows: number; exported_at: string | null; note: string | null };
  live: { total: number | null; checked_at: number; error: string | null; stale?: boolean };
  behind_rows: number | null;
  behind_pct: number | null;
  delta: null | {
    live_dir: string; computed_at: string; snapshot_rows: number; live_rows: number;
    new_in_live: number; removed_from_live: number; pagu_changed: number; metode_changed: number;
    paket_renamed: number; new_pagu_total: number;
  };
  source_url: string;
}
export interface LiveCheck {
  package_id: number; checked_at: number; in_sync: boolean;
  differences: { field: string; label: string; snapshot: string | number | null; live: string | number | null }[];
  live: { uraianPekerjaan?: string; volumePekerjaan?: string; spesifikasiPekerjaan?: string };
}

export async function fetchFreshness(refresh = false): Promise<Freshness> {
  const { data } = await api.get<Freshness>("/freshness", { params: { refresh } });
  return data;
}
export async function fetchLiveCheck(id: string | number): Promise<LiveCheck> {
  const { data } = await api.get<LiveCheck>(`/packages/${id}/live`, { timeout: 30_000 });
  return data;
}
