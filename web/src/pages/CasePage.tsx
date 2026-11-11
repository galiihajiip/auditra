import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { caseApi, type CaseDetail, type CasePhase, type Transition } from "../api/client";
import { formatApiError } from "../api/errors";
import { useAuth } from "../auth/AuthContext";
import FindingsTab from "../components/case/FindingsTab";
import GateChecklist from "../components/case/GateChecklist";
import HistoryTab from "../components/case/HistoryTab";
import PlanTab from "../components/case/PlanTab";
import SummaryTab from "../components/case/SummaryTab";
import TestingTab from "../components/case/TestingTab";
import { ReasonDialog } from "../components/Dialog";
import EmptyState from "../components/EmptyState";
import Icon, { type IconName } from "../components/Icon";
import JourneyStepper from "../components/JourneyStepper";
import RpiRing from "../components/RpiRing";
import Skeleton from "../components/Skeleton";
import StatusPill from "../components/StatusPill";
import { useToast } from "../components/Toast";
import { PHASE_FLOW, PHASE_LABEL, actionLabel, fmtDate, fmtRupiah } from "../utils/caseLabels";

type Tab = "ringkasan" | "rencana" | "pengujian" | "temuan" | "riwayat";

const STEPS = [
  { label: "Seleksi", icon: "search" }, { label: "Perencanaan", icon: "file" }, { label: "Pelaksanaan", icon: "upload" },
  { label: "Reviu", icon: "shield" }, { label: "Komunikasi", icon: "layers" }, { label: "Selesai", icon: "checkCircle" },
] as { label: string; icon: IconName }[];

const COPY: Record<CasePhase, { auditor: [string, string]; reviewer: [string, string] }> = {
  seleksi: { auditor: ["Tetapkan alasan seleksi sasaran", "Jelaskan mengapa paket ini layak diaudit, lalu mulai perencanaan."], reviewer: ["Menunggu auditor", "Auditor sedang menetapkan sasaran."] },
  perencanaan: { auditor: ["Susun rencana & program audit", "Isi tujuan, lingkup, risiko, dan materialitas; bangkitkan program audit dari sinyal paket."], reviewer: ["Menunggu auditor", "Auditor menyusun rencana penugasan."] },
  pelaksanaan: { auditor: ["Uji prosedur & kumpulkan bukti", "Catat hasil tiap prosedur, nilai ketepatan bukti, dan susun temuan bila ada ketidaksesuaian."], reviewer: ["Menunggu auditor", "Auditor sedang melaksanakan pengujian."] },
  reviu: { auditor: ["Menunggu reviu berjenjang", "Pengendali teknis (reviewer) meninjau bukti dan kertas kerja."], reviewer: ["Tinjau kertas kerja & bukti", "Terima atau tolak tiap bukti, lalu putuskan: komunikasikan temuan, selesaikan, atau kembalikan."] },
  komunikasi: { auditor: ["Catat tanggapan tertulis entitas", "Peroleh tanggapan atas tiap temuan dan dokumentasikan (SPKN Pelaporan par. 26–28)."], reviewer: ["Menunggu tanggapan entitas", "Setelah semua temuan ditanggapi dan kesimpulan ditulis, selesaikan penugasan."] },
  selesai: { auditor: ["Penugasan selesai", "Pantau tindak lanjut rekomendasi di tab Temuan."], reviewer: ["Penugasan selesai", "Pantau tindak lanjut rekomendasi di tab Temuan."] },
  dihentikan: { auditor: ["Penugasan dihentikan", "Alasan penghentian tercatat. Paket dapat ditugaskan kembali."], reviewer: ["Penugasan dihentikan", "Alasan penghentian tercatat."] },
};

function forwardTransition(c: CaseDetail, role: "auditor" | "reviewer", onlyMine: boolean): Transition | undefined {
  const cand = c.transitions.filter((t) => t.to !== "dihentikan" && !(c.phase === "reviu" && t.to === "pelaksanaan") && (!onlyMine || t.roles.includes(role)));
  if (c.phase === "reviu") return cand.find((t) => t.to === (c.findings.length > 0 ? "komunikasi" : "selesai"));
  return cand[0];
}

export default function CasePage() {
  const { id = "" } = useParams();
  const { user } = useAuth();
  const { toast } = useToast();
  const [c, setC] = useState<CaseDetail | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<Tab>("rencana");
  const [dlg, setDlg] = useState<null | { to: CasePhase; required: boolean }>(null);

  useEffect(() => {
    setC(null); setErr(null);
    caseApi.get(id).then((d) => {
      setC(d);
      setTab(d.phase === "pelaksanaan" || d.phase === "reviu" ? "pengujian" : d.phase === "komunikasi" || (d.phase === "selesai" && d.findings.length) ? "temuan" : d.phase === "selesai" || d.phase === "dihentikan" ? "ringkasan" : "rencana");
    }).catch((e) => setErr(formatApiError(e)));
  }, [id]);

  const act = useCallback(async (fn: () => Promise<CaseDetail | void>, ok?: string) => {
    setBusy(true);
    try {
      const res = await fn();
      if (res) setC(res);
      if (ok) toast(ok);
      return true;
    } catch (e) { toast(formatApiError(e), "error"); return false; }
    finally { setBusy(false); }
  }, [toast]);

  if (err && !c) return <div className="panel mx-auto max-w-lg"><EmptyState icon="alert" title="Penugasan tidak dapat dimuat" action={<Link to="/kasus" className="btn-secondary">← Daftar penugasan</Link>}>{err}</EmptyState></div>;
  if (!c || !user) return <div className="space-y-4" aria-busy="true"><Skeleton className="h-10 w-1/2" /><Skeleton className="h-40" /><Skeleton className="h-72" /></div>;

  const role = user.role;
  const mine = forwardTransition(c, role, true);
  const shown = mine ?? forwardTransition(c, role, false);
  const copy = COPY[c.phase][role];
  const terminal = c.phase === "selesai" || c.phase === "dihentikan";
  const stepIdx = c.phase === "dihentikan" ? 0 : PHASE_FLOW.indexOf(c.phase) + (c.phase === "selesai" ? 1 : 0);
  const back = c.transitions.find((t) => t.to === "pelaksanaan" && t.roles.includes(role));
  const stop = c.transitions.find((t) => t.to === "dihentikan" && t.roles.includes(role));
  const tested = c.procedures.filter((p) => p.status !== "belum").length;

  const doTransition = (to: CasePhase, note?: string) => act(() => caseApi.transition(c.id, to, note), `Tahap: ${PHASE_LABEL[to]}`);
  const tabs: { id: Tab; label: string; icon: IconName; badge?: string }[] = [
    { id: "ringkasan", label: "Ringkasan", icon: "eye" },
    { id: "rencana", label: "Rencana", icon: "file", badge: c.procedures.length ? `${c.procedures.length}` : undefined },
    { id: "pengujian", label: "Pengujian", icon: "checkCircle", badge: c.procedures.length ? `${tested}/${c.procedures.length}` : undefined },
    { id: "temuan", label: "Temuan", icon: "alert", badge: c.findings.length ? `${c.findings.length}` : undefined },
    { id: "riwayat", label: "Riwayat", icon: "clock" },
  ];
  const tp = { c, user, busy, act };

  return (
    <div className="space-y-5">
      <div className="no-print flex flex-wrap items-center justify-between gap-3">
        <Link to="/kasus" className="btn-secondary !py-1.5 text-sm"><Icon name="arrowLeft" size={15} /> Semua penugasan</Link>
        <JourneyStepper steps={STEPS} current={stepIdx} failed={c.phase === "dihentikan"} />
      </div>

      <section className="hero fade-up">
        <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:p-7">
          <RpiRing value={c.rpi ?? 0} label={c.risk_label ?? undefined} size={84} stroke={9} />
          <div className="min-w-0 flex-1">
            <p className="eyebrow">Penugasan #{c.id}</p>
            <h2 className="font-display text-2xl font-extrabold leading-tight text-primary">{c.title}</h2>
            <p className="mt-1 text-sm text-muted">{c.lembaga} · {fmtRupiah(c.pagu)} · {c.metode} · dibuka {c.created_by_name}, {fmtDate(c.created_at)}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <StatusPill status={c.phase} />
              {c.outcome && <span className="chip">{c.outcome === "dengan_temuan" ? "Dengan temuan" : "Tanpa temuan"}</span>}
              <Link to={`/paket/${c.package_id}`} className="chip no-print">Passport paket <Icon name="arrowRight" size={12} /></Link>
            </div>
          </div>
        </div>
      </section>

      {!terminal && (
        <section className="no-print fade-up rounded-2xl border border-[var(--accent-teal)] p-4 sm:p-5" style={{ background: "color-mix(in srgb, var(--accent-teal) 7%, var(--bg-panel))" }} aria-label="Langkah berikutnya">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start">
            <div className="min-w-0 flex-1">
              <p className="text-xs font-bold uppercase tracking-wider text-[var(--accent-teal)]">Langkah berikutnya · {PHASE_LABEL[c.phase]}</p>
              <h3 className="font-display text-lg font-bold text-primary">{copy[0]}</h3>
              <p className="text-sm text-muted">{copy[1]}</p>
            </div>
            {shown && (
              <div className="min-w-0 flex-1 rounded-xl bg-[var(--bg-panel)] p-3">
                <p className="mb-2 text-sm font-semibold text-primary">Syarat untuk “{actionLabel(c.phase, shown.to)}”</p>
                <GateChecklist gates={shown.gates} />
              </div>
            )}
          </div>
          <div className="mt-4 flex flex-wrap items-center gap-2">
            {mine ? (
              <button className="btn-primary btn-lg" disabled={busy || !mine.ready} onClick={() => doTransition(mine.to)}
                title={mine.ready ? undefined : "Lengkapi syarat di atas terlebih dahulu"}>{actionLabel(c.phase, mine.to)} <Icon name="arrowRight" size={17} /></button>
            ) : (
              <span className="chip"><Icon name="clock" size={13} /> Menunggu {c.phase === "reviu" || c.phase === "komunikasi" ? (role === "auditor" ? "reviewer/entitas" : "auditor") : "auditor"}</span>
            )}
            {back && <button className="btn-secondary" disabled={busy} onClick={() => setDlg({ to: "pelaksanaan", required: true })}>Kembalikan untuk perbaikan</button>}
            {stop && <button className="btn-danger" disabled={busy} onClick={() => setDlg({ to: "dihentikan", required: true })}>Hentikan penugasan</button>}
          </div>
        </section>
      )}
      {terminal && <section className="no-print rounded-2xl border border-[var(--border)] bg-[var(--bg-panel)] p-4"><h3 className="font-display text-lg font-bold text-primary">{copy[0]}</h3><p className="text-sm text-muted">{copy[1]}</p></section>}

      <div className="no-print scroll-x flex gap-2" role="tablist" aria-label="Bagian penugasan">
        {tabs.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} className={`tab-btn ${tab === t.id ? "tab-btn-active" : ""}`} onClick={() => setTab(t.id)}>
            <Icon name={t.icon} size={15} /> {t.label}{t.badge && <span className="num rounded-full bg-[var(--bg-subtle)] px-1.5 text-xs">{t.badge}</span>}
          </button>
        ))}
      </div>

      <div role="tabpanel" className="fade-up" key={tab}>
        {tab === "ringkasan" && <SummaryTab {...tp} />}
        {tab === "rencana" && <PlanTab {...tp} />}
        {tab === "pengujian" && <TestingTab {...tp} />}
        {tab === "temuan" && <FindingsTab {...tp} />}
        {tab === "riwayat" && <HistoryTab {...tp} />}
      </div>

      {dlg && (
        <ReasonDialog title={dlg.to === "dihentikan" ? "Hentikan penugasan" : "Kembalikan untuk perbaikan"}
          description={dlg.to === "dihentikan" ? "Alasan penghentian dikomunikasikan tertulis kepada pihak terkait (SPKN Pelaksanaan par. 46–47)." : "Jelaskan apa yang harus diperbaiki auditor."}
          required danger={dlg.to === "dihentikan"} confirmLabel={dlg.to === "dihentikan" ? "Hentikan" : "Kembalikan"} onClose={() => setDlg(null)}
          onConfirm={(t) => { const to = dlg.to; setDlg(null); doTransition(to, t); }} />
      )}
    </div>
  );
}
