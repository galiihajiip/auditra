import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { caseApi, type CaseRow, type CasePhase } from "../api/client";
import { formatApiError } from "../api/errors";
import { useAuth } from "../auth/AuthContext";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icon";
import RpiRing from "../components/RpiRing";
import Skeleton from "../components/Skeleton";
import StatusPill from "../components/StatusPill";
import { PHASE_COLOR, PHASE_FLOW, PHASE_HINT, PHASE_LABEL, fromNow } from "../utils/caseLabels";
import { formatPaguCompact } from "../utils/formatPagu";

const COLUMNS: CasePhase[] = [...PHASE_FLOW, "dihentikan"];

function KanbanCard({ c }: { c: CaseRow }) {
  const pct = c.n_procedures ? Math.round((c.n_tested / c.n_procedures) * 100) : 0;
  return (
    <Link to={`/kasus/${c.id}`} className="panel interactive block !p-3 no-underline">
      <div className="flex items-start gap-2.5">
        <RpiRing value={c.rpi ?? 0} label={c.risk_label ?? undefined} size={40} stroke={5} />
        <div className="min-w-0 flex-1">
          <p className="line-clamp-2 text-sm font-semibold leading-snug text-primary">{c.title}</p>
          <p className="truncate text-xs text-muted">{c.lembaga}</p>
        </div>
      </div>
      {c.n_procedures > 0 && (
        <div className="mt-2.5" aria-label={`Pengujian ${c.n_tested} dari ${c.n_procedures}`}>
          <div className="h-1.5 overflow-hidden rounded-full bg-[var(--bg-subtle)]"><div className="h-full rounded-full" style={{ width: `${pct}%`, background: "var(--accent-teal)" }} /></div>
          <p className="mt-0.5 text-xs text-muted">{c.n_tested}/{c.n_procedures} prosedur diuji</p>
        </div>
      )}
      <div className="mt-2 flex items-center justify-between text-xs text-muted">
        <span className="inline-flex items-center gap-1"><Icon name="file" size={12} /> {c.n_evidence} bukti</span>
        {c.n_findings > 0 && <span className="inline-flex items-center gap-1 text-amber-500"><Icon name="alert" size={12} /> {c.n_findings} temuan</span>}
        <span className="num font-semibold text-primary">{formatPaguCompact((c.pagu ?? 0) / 1e9)}</span>
      </div>
      <p className="mt-1 flex items-center gap-1 text-xs text-muted"><Icon name="clock" size={12} /> {fromNow(c.updated_at)}</p>
    </Link>
  );
}

export default function CasesPage() {
  const { user } = useAuth();
  const nav = useNavigate();
  const [view, setView] = useState<"board" | "list">(() => (localStorage.getItem("auditra-cases-view") === "list" ? "list" : "board"));
  const [mine, setMine] = useState(false);
  const [rows, setRows] = useState<CaseRow[] | null>(null);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => { try { localStorage.setItem("auditra-cases-view", view); } catch { /* abaikan */ } }, [view]);
  useEffect(() => {
    setRows(null); setErr(null);
    caseApi.list(undefined, mine).then(setRows).catch((e) => setErr(formatApiError(e)));
  }, [mine]);

  const grouped = useMemo(() => {
    const g = Object.fromEntries(COLUMNS.map((s) => [s, [] as CaseRow[]])) as Record<CasePhase, CaseRow[]>;
    rows?.forEach((r) => g[r.phase].push(r));
    return g;
  }, [rows]);

  const needsAction = !rows || !user ? 0
    : user.role === "reviewer" ? grouped.reviu.length
    : rows.filter((c) => c.created_by_name === user.name && ["seleksi", "perencanaan", "pelaksanaan", "komunikasi"].includes(c.phase)).length;

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="eyebrow">Ruang kerja</p>
          <h2 className="font-display text-3xl font-extrabold text-primary">Penugasan audit</h2>
          <p className="text-sm text-muted">{user?.role === "reviewer" ? "Reviu berjenjang: tinjau kertas kerja dan bukti yang diajukan auditor." : "Dari seleksi sasaran, perencanaan, pengujian, hingga pemantauan tindak lanjut."}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="chip cursor-pointer select-none" style={mine ? { color: "var(--accent-teal)", borderColor: "var(--accent-teal)" } : undefined}>
            <input type="checkbox" className="sr-only" checked={mine} onChange={(e) => setMine(e.target.checked)} /> Hanya penugasan saya
          </label>
          <div className="flex rounded-full border border-[var(--border)] p-0.5" role="group" aria-label="Tampilan">
            <button className={`tab-btn !border-0 ${view === "board" ? "tab-btn-active" : ""}`} aria-pressed={view === "board"} onClick={() => setView("board")}><Icon name="board" size={15} /> Papan</button>
            <button className={`tab-btn !border-0 ${view === "list" ? "tab-btn-active" : ""}`} aria-pressed={view === "list"} onClick={() => setView("list")}><Icon name="list" size={15} /> Daftar</button>
          </div>
          {user?.role === "auditor" && <Link to="/#prioritas" className="btn-primary"><Icon name="search" size={15} /> Cari paket</Link>}
        </div>
      </div>

      {needsAction > 0 && (
        <div className="fade-up flex items-center gap-3 rounded-2xl border border-[var(--accent-teal)] bg-[var(--glow)] px-4 py-3" role="status">
          <Icon name="spark" size={20} className="text-[var(--accent-teal)]" />
          <p className="text-sm text-primary"><b>{needsAction} penugasan</b> {user?.role === "reviewer" ? "menunggu reviu Anda." : "perlu Anda tindak lanjuti."}</p>
        </div>
      )}
      {err && <p role="alert" className="rounded-xl border border-red-400/50 bg-red-500/10 px-4 py-3 text-sm text-red-500">{err}</p>}
      {!rows && !err && <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-5">{Array.from({ length: 5 }, (_, i) => <Skeleton key={i} className="h-64 !rounded-2xl" />)}</div>}

      {rows && rows.length === 0 && (
        <div className="panel">
          <EmptyState icon="board" title="Belum ada penugasan" action={<Link to="/#prioritas" className="btn-primary">Cari paket berisiko</Link>}>
            Mulai dari dasbor: pilih paket dengan RPI tinggi, buka passport-nya, lalu tekan “Buka penugasan audit”.
          </EmptyState>
        </div>
      )}

      {rows && rows.length > 0 && view === "board" && (
        <div className="scroll-x -mx-3 flex snap-x gap-3 px-3 pb-2 sm:mx-0 sm:px-0">
          {COLUMNS.map((s) => (
            <section key={s} className={`min-w-[78%] shrink-0 snap-start rounded-2xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-2.5 sm:min-w-[260px] sm:max-w-[280px] sm:flex-1 ${grouped[s].length === 0 ? "max-sm:order-last" : ""}`} aria-label={PHASE_LABEL[s]}>
              <header className="mb-2 flex items-center justify-between px-1.5 pt-1">
                <div>
                  <p className="flex items-center gap-2 text-sm font-bold text-primary"><span className="h-2.5 w-2.5 rounded-full" style={{ background: PHASE_COLOR[s] }} />{PHASE_LABEL[s]}</p>
                  <p className="text-xs text-muted">{PHASE_HINT[s]}</p>
                </div>
                <span className="num rounded-full bg-[var(--bg-panel)] px-2.5 py-0.5 text-sm font-bold text-primary">{grouped[s].length}</span>
              </header>
              <div className="space-y-2">
                {grouped[s].length === 0 ? <p className="px-2 py-6 text-center text-xs text-muted">Kosong</p> : grouped[s].map((c) => <KanbanCard key={c.id} c={c} />)}
              </div>
            </section>
          ))}
        </div>
      )}

      {rows && rows.length > 0 && view === "list" && (
        <div className="table-wrap">
          <table className="data-table">
            <thead><tr><th>#</th><th>Paket</th><th>Lembaga</th><th>RPI</th><th>Tahap</th><th>Uji</th><th>Bukti</th><th>Temuan</th><th>Diperbarui</th></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} tabIndex={0} role="button" onClick={() => nav(`/kasus/${r.id}`)} onKeyDown={(e) => e.key === "Enter" && nav(`/kasus/${r.id}`)}>
                  <td className="num text-muted">{r.id}</td>
                  <td className="max-w-sm"><span className="line-clamp-2 font-medium text-primary">{r.title}</span></td>
                  <td className="max-w-[200px] truncate text-muted">{r.lembaga}</td>
                  <td className="num font-bold">{r.rpi?.toFixed(1)}</td>
                  <td><StatusPill status={r.phase} /></td>
                  <td className="num">{r.n_tested}/{r.n_procedures}</td>
                  <td className="num">{r.n_evidence}</td>
                  <td className="num">{r.n_findings}</td>
                  <td className="whitespace-nowrap text-muted">{fromNow(r.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
