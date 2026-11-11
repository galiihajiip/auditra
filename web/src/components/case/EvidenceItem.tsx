import type { Evidence } from "../../api/client";
import { FORM_LABEL, fmtBytes, fromNow } from "../../utils/caseLabels";
import Icon from "../Icon";

const REVIEW_LABEL = { pending: "Menunggu tinjauan", verified: "Diterima reviewer", rejected: "Ditolak reviewer" } as const;
const REVIEW_COLOR = { pending: "#eab308", verified: "#22c55e", rejected: "#ef4444" } as const;

interface Props {
  ev: Evidence;
  techniques: Record<string, string>;
  canGrade: boolean;
  canReview: boolean;
  busy: boolean;
  onDownload: () => void;
  onGrade: (q: { relevan: boolean; valid: boolean; andal: boolean; authenticity_concern: boolean; authenticity_note?: string }) => void;
  onReview: (decision: "verified" | "rejected") => void;
}

export default function EvidenceItem({ ev, techniques, canGrade, canReview, busy, onDownload, onGrade, onReview }: Props) {
  const toggle = (k: "relevan" | "valid" | "andal") =>
    onGrade({ relevan: ev.relevan, valid: ev.valid, andal: ev.andal, authenticity_concern: ev.authenticity_concern, authenticity_note: ev.authenticity_note ?? undefined, [k]: !ev[k] });
  return (
    <li className="rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-3">
      <div className="flex items-start gap-3">
        <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-[var(--bg-panel)] text-[var(--accent-teal)]"><Icon name={ev.kind === "link" ? "link" : "file"} size={17} /></span>
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-primary">{ev.title}</p>
          {ev.kind === "link" ? (
            <a className="break-all text-sm text-[var(--accent-teal)] hover:underline" href={ev.url ?? "#"} target="_blank" rel="noopener noreferrer nofollow">{ev.url}</a>
          ) : (
            <button type="button" className="inline-flex items-center gap-1.5 text-sm text-[var(--accent-teal)] hover:underline" onClick={onDownload}>
              <Icon name="download" size={14} /> {ev.filename} · {fmtBytes(ev.size_bytes)}
            </button>
          )}
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            <span className="chip">{FORM_LABEL[ev.form] ?? ev.form}</span>
            <span className="chip">{techniques[ev.technique] ?? ev.technique}</span>
            {ev.doc_date && <span className="chip">dok. {ev.doc_date}</span>}
          </div>
          <p className="mt-1 text-xs text-muted">oleh {ev.added_by_name} · {fromNow(ev.added_at)}</p>
          {ev.sha256 && <p className="mt-0.5 break-all font-mono text-[11px] text-muted" title="SHA-256: sidik jari berkas (Perban BPKP 6/2026: hash value untuk integritas data elektronik)">SHA-256 {ev.sha256.slice(0, 20)}…</p>}
        </div>
        <span className="status-pill shrink-0" style={{ color: REVIEW_COLOR[ev.review_status] }}>{REVIEW_LABEL[ev.review_status]}</span>
      </div>

      <div className="mt-2.5 flex flex-wrap items-center gap-1.5" aria-label="Ketepatan bukti">
        <span className="text-xs text-muted">Ketepatan:</span>
        {(["relevan", "valid", "andal"] as const).map((k) => (
          canGrade ? (
            <button key={k} type="button" disabled={busy} onClick={() => toggle(k)} aria-pressed={ev[k]}
              className="chip cursor-pointer capitalize" style={ev[k] ? { color: "#22c55e", borderColor: "#22c55e" } : undefined}>
              {ev[k] ? "✓" : "○"} {k}
            </button>
          ) : (
            <span key={k} className="chip capitalize" style={ev[k] ? { color: "#22c55e", borderColor: "#22c55e" } : undefined}>{ev[k] ? "✓" : "○"} {k}</span>
          )
        ))}
      </div>

      {ev.authenticity_concern && (
        <p className="mt-2 flex items-start gap-1.5 rounded-lg border border-amber-500/50 bg-amber-500/10 px-2.5 py-1.5 text-xs text-amber-500">
          <Icon name="alert" size={14} className="mt-0.5 shrink-0" />
          <span>Diragukan keasliannya: {ev.authenticity_note}. Lakukan pendalaman (SPKN par. 34).</span>
        </p>
      )}
      {ev.reviewed_by_name && <p className="mt-2 text-xs text-muted">Ditinjau {ev.reviewed_by_name}{ev.review_note ? ` — “${ev.review_note}”` : ""}</p>}
      {canReview && ev.review_status === "pending" && (
        <div className="no-print mt-3 flex gap-2">
          <button className="btn-primary" disabled={busy} onClick={() => onReview("verified")}><Icon name="check" size={15} /> Terima</button>
          <button className="btn-danger" disabled={busy} onClick={() => onReview("rejected")}><Icon name="x" size={15} /> Tolak</button>
        </div>
      )}
    </li>
  );
}
