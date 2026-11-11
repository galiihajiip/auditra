import { useState } from "react";
import { caseApi, type CaseDetail, type EvidenceMeta, type Procedure, type ProcStatus } from "../../api/client";
import { ReasonDialog } from "../Dialog";
import EmptyState from "../EmptyState";
import Icon from "../Icon";
import EvidenceDialog from "./EvidenceDialog";
import EvidenceItem from "./EvidenceItem";
import type { TabProps } from "./types";

const STATUS: { v: ProcStatus; label: string; color: string }[] = [
  { v: "sesuai", label: "Sesuai", color: "#22c55e" },
  { v: "tidak_sesuai", label: "Tidak sesuai", color: "#ef4444" },
  { v: "tidak_dapat_diuji", label: "Tidak dapat diuji", color: "#94a3b8" },
];

function ResultForm({ p, busy, onSave }: { p: Procedure; busy: boolean; onSave: (s: ProcStatus, note: string) => void }) {
  const [s, setS] = useState<ProcStatus>(p.status);
  const [note, setNote] = useState(p.result_note ?? "");
  const needNote = s === "tidak_sesuai" || s === "tidak_dapat_diuji";
  return (
    <div className="mt-3 rounded-xl border border-[var(--border-subtle)] p-3">
      <p className="mb-2 text-sm font-semibold text-primary">Hasil pengujian</p>
      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={`Hasil ${p.code}`}>
        {STATUS.map((o) => (
          <button key={o.v} type="button" role="radio" aria-checked={s === o.v} className={`tab-btn ${s === o.v ? "tab-btn-active" : ""}`}
            style={s === o.v ? { borderColor: o.color, color: o.color } : undefined} onClick={() => setS(o.v)}>{o.label}</button>
        ))}
      </div>
      <textarea className="input-text mt-2" rows={2} maxLength={2000} aria-label={`Catatan hasil ${p.code}`}
        placeholder={needNote ? "Catatan wajib: apa yang ditemukan / mengapa tidak dapat diuji" : "Catatan (opsional)"} value={note} onChange={(e) => setNote(e.target.value)} />
      <div className="mt-2 flex justify-end">
        <button className="btn-primary" disabled={busy || s === "belum" || (needNote && !note.trim())} onClick={() => onSave(s, note)}>Simpan hasil</button>
      </div>
    </div>
  );
}

export default function TestingTab({ c, user, busy, act }: TabProps) {
  const isAuditor = user.role === "auditor";
  const canWork = isAuditor && c.phase === "pelaksanaan";
  const canAddEv = isAuditor && (c.phase === "perencanaan" || c.phase === "pelaksanaan");
  const canReview = user.role === "reviewer" && c.phase === "reviu";
  const [evDlg, setEvDlg] = useState<{ procedureId: number | null } | null>(null);
  const [reviewDlg, setReviewDlg] = useState<{ id: number; title: string; decision: "verified" | "rejected" } | null>(null);
  const [open, setOpen] = useState<Set<number>>(() => new Set(c.phase === "reviu" ? c.procedures.map((p) => p.id) : c.procedures[0] ? [c.procedures[0].id] : []));
  const toggleOpen = (id: number) => setOpen((prev) => { const n = new Set(prev); if (n.has(id)) n.delete(id); else n.add(id); return n; });

  const evFor = (pid: number | null) => c.evidence.filter((e) => e.procedure_id === pid);
  const stageLabel = (k: string) => c.meta.stages.find((s) => s.key === k)?.label ?? (k === "lintas" ? "Lintas tahap" : k);

  const item = (ev: CaseDetail["evidence"][number]) => (
    <EvidenceItem key={ev.id} ev={ev} techniques={c.meta.techniques} busy={busy} canReview={false} canGrade={canWork}
      onDownload={() => act(() => caseApi.download(ev.id, ev.filename ?? "bukti"))}
      onGrade={(q) => act(() => caseApi.setQuality(ev.id, q))}
      onReview={(d) => setReviewDlg({ id: ev.id, title: ev.title, decision: d })} />
  );
  const submitEv = async (title: string, opts: { url?: string; file?: File }, meta: EvidenceMeta) => {
    if (await act(() => caseApi.addEvidence(c.id, title, opts, meta), "Bukti ditambahkan.")) setEvDlg(null);
  };

  if (c.procedures.length === 0) {
    return <div className="panel"><EmptyState icon="list" title="Belum ada program audit">Susun program di tab Rencana (tahap perencanaan) sebelum menguji prosedur.</EmptyState></div>;
  }
  const general = evFor(null);
  const toReview = canReview ? c.evidence.filter((e) => e.review_status === "pending") : [];
  const pcode = (pid: number | null) => c.procedures.find((p) => p.id === pid)?.code;

  return (
    <div className="space-y-3">
      {canReview && (
        <section className="panel space-y-3" style={{ borderColor: "var(--accent-teal)" }} aria-labelledby="tinjau-h">
          <div><h3 id="tinjau-h" className="panel-title">Bukti yang perlu ditinjau ({toReview.length})</h3>
            <p className="panel-sub">Reviu berjenjang: nilai kecukupan dan ketepatan tiap bukti (SPKN Pelaksanaan par. 29, 43–44). Anda tidak dapat meninjau bukti yang Anda unggah sendiri.</p></div>
          {toReview.length === 0 ? <p className="text-sm text-muted">Semua bukti sudah ditinjau.</p> : (
            <ul className="space-y-2">{toReview.map((ev) => (
              <div key={ev.id}>
                {pcode(ev.procedure_id) && <p className="mb-1 text-xs text-muted">Prosedur <span className="chip">{pcode(ev.procedure_id)}</span></p>}
                <EvidenceItem ev={ev} techniques={c.meta.techniques} busy={busy} canReview canGrade={false}
                  onDownload={() => act(() => caseApi.download(ev.id, ev.filename ?? "bukti"))} onGrade={() => {}}
                  onReview={(d) => setReviewDlg({ id: ev.id, title: ev.title, decision: d })} />
              </div>))}</ul>)}
        </section>
      )}
      {c.phase === "perencanaan" && <p className="rounded-xl border border-[var(--border)] bg-[var(--bg-subtle)] px-4 py-3 text-sm text-muted">Pengujian dimulai setelah tahap <b>Pelaksanaan</b>. Anda sudah dapat melampirkan bukti awal.</p>}
      <ul className="space-y-3">
        {c.procedures.map((p) => {
          const evs = evFor(p.id);
          const isOpen = open.has(p.id);
          const st = STATUS.find((s) => s.v === p.status);
          return (
            <li key={p.id} className="panel !p-0 overflow-hidden">
              <button type="button" className="flex w-full flex-wrap items-center gap-x-3 gap-y-1.5 p-4 text-left sm:flex-nowrap" aria-expanded={isOpen} onClick={() => toggleOpen(p.id)}>
                <span className="chip shrink-0">{p.code}</span>
                <span className="order-last w-full min-w-0 sm:order-none sm:w-auto sm:flex-1"><span className="block font-semibold text-primary">{p.title}</span><span className="block text-xs text-muted">{stageLabel(p.stage)} · {evs.length} bukti</span></span>
                <span className="status-pill ml-auto shrink-0 sm:ml-0" style={{ color: st?.color ?? "var(--text-muted)" }}>{st?.label ?? "Belum diuji"}</span>
                <Icon name="arrowRight" size={16} className={`shrink-0 transition-transform ${isOpen ? "rotate-90" : ""}`} />
              </button>
              {isOpen && (
                <div className="space-y-3 border-t border-[var(--border-subtle)] p-4">
                  {p.objective && <p className="text-sm text-muted">{p.objective}</p>}
                  <div>
                    <p className="mb-1 text-xs font-bold uppercase tracking-wider text-muted">Kriteria</p>
                    <ul className="space-y-1.5">{p.criteria.map((k, i) => (
                      <li key={i} className="text-sm"><span className="chip mr-2">{k.ref}</span><span className="text-primary">{k.text}</span></li>))}</ul>
                  </div>
                  {p.evidence_expected.length > 0 && (
                    <div>
                      <p className="mb-1 text-xs font-bold uppercase tracking-wider text-muted">Bukti yang diharapkan</p>
                      <ul className="space-y-1">{p.evidence_expected.map((e, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-primary"><Icon name="file" size={14} className="mt-1 shrink-0 text-[var(--accent-teal)]" />{e.name}</li>))}</ul>
                    </div>
                  )}
                  {p.techniques.length > 0 && <div className="flex flex-wrap items-center gap-1.5"><span className="text-xs text-muted">Teknik:</span>{p.techniques.map((t) => <span key={t} className="chip">{c.meta.techniques[t] ?? t}</span>)}</div>}
                  {p.caution && <p className="flex items-start gap-2 rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-500"><Icon name="alert" size={15} className="mt-0.5 shrink-0" /><span>{p.caution}</span></p>}

                  <div>
                    <div className="mb-2 flex items-center justify-between"><p className="text-sm font-semibold text-primary">Bukti ({evs.length})</p>
                      {canAddEv && <button className="btn-secondary !py-1.5 text-sm" onClick={() => setEvDlg({ procedureId: p.id })}><Icon name="upload" size={14} /> Tambah bukti</button>}</div>
                    {evs.length === 0 ? <p className="text-sm text-muted">Belum ada bukti untuk prosedur ini.</p> : <ul className="space-y-2">{evs.map(item)}</ul>}
                  </div>
                  {p.status !== "belum" && p.result_note && !canWork && <p className="text-sm text-muted">Catatan hasil: {p.result_note}</p>}
                  {canWork && <ResultForm key={`${p.id}-${p.status}`} p={p} busy={busy} onSave={(s, n) => act(() => caseApi.setResult(p.id, s, n), "Hasil disimpan.")} />}
                </div>
              )}
            </li>
          );
        })}
      </ul>

      <section className="panel">
        <div className="mb-2 flex items-center justify-between"><h3 className="panel-title">Bukti umum ({general.length})</h3>
          {canAddEv && <button className="btn-secondary !py-1.5 text-sm" onClick={() => setEvDlg({ procedureId: null })}><Icon name="upload" size={14} /> Tambah</button>}</div>
        {general.length === 0 ? <p className="text-sm text-muted">Bukti yang tidak terkait satu prosedur.</p> : <ul className="space-y-2">{general.map(item)}</ul>}
      </section>

      {evDlg && <EvidenceDialog c={c} procedureId={evDlg.procedureId} busy={busy} onSubmit={submitEv} onClose={() => setEvDlg(null)} />}
      {reviewDlg && (
        <ReasonDialog title={reviewDlg.decision === "verified" ? `Terima “${reviewDlg.title}”` : `Tolak “${reviewDlg.title}”`}
          description={reviewDlg.decision === "verified" ? "Bukti dinilai cukup dan tepat untuk mendukung kesimpulan." : "Jelaskan mengapa bukti tidak cukup/tepat. Penugasan dapat dikembalikan ke auditor."}
          required={reviewDlg.decision === "rejected"} danger={reviewDlg.decision === "rejected"} confirmLabel={reviewDlg.decision === "verified" ? "Terima bukti" : "Tolak bukti"}
          onClose={() => setReviewDlg(null)}
          onConfirm={(t) => { const d = reviewDlg; setReviewDlg(null); act(() => caseApi.review(d.id, d.decision, t), d.decision === "verified" ? "Bukti diterima." : "Bukti ditolak."); }} />
      )}
    </div>
  );
}
