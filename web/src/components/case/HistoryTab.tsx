import { useState } from "react";
import { caseApi } from "../../api/client";
import { PHASE_COLOR, PHASE_LABEL, fmtDate } from "../../utils/caseLabels";
import type { CasePhase } from "../../api/client";
import Icon, { type IconName } from "../Icon";
import type { TabProps } from "./types";

const EVENT: Record<string, { label: string; icon: IconName }> = {
  dibuat: { label: "Sasaran dipilih", icon: "play" }, status: { label: "Tahap berubah", icon: "layers" }, rencana: { label: "Rencana diperbarui", icon: "file" },
  program: { label: "Program audit", icon: "list" }, hasil: { label: "Hasil pengujian", icon: "check" }, bukti: { label: "Bukti ditambahkan", icon: "upload" },
  kualitas_bukti: { label: "Ketepatan bukti dinilai", icon: "eye" }, tinjau_bukti: { label: "Bukti ditinjau", icon: "shield" }, temuan: { label: "Temuan", icon: "alert" },
  tanggapan: { label: "Tanggapan entitas", icon: "file" }, tindak_lanjut: { label: "Tindak lanjut", icon: "refresh" }, catatan: { label: "Catatan", icon: "file" },
};

export default function HistoryTab({ c, busy, act }: TabProps) {
  const [note, setNote] = useState("");
  return (
    <section className="panel" aria-labelledby="riwayat-h">
      <h3 id="riwayat-h" className="panel-title">Riwayat</h3>
      <p className="panel-sub mb-3">Catatan audit yang tidak dapat diubah (dokumentasi SPKN Umum par. 71–72).</p>
      <ol className="relative space-y-4 border-l border-[var(--border)] pl-5">
        {c.events.map((e) => {
          const meta = EVENT[e.type] ?? { label: e.type, icon: "file" as IconName };
          const color = e.to_status && PHASE_COLOR[e.to_status as CasePhase] ? PHASE_COLOR[e.to_status as CasePhase] : "var(--accent-teal)";
          return (
            <li key={e.id} className="relative">
              <span className="absolute -left-[31px] top-0 grid h-6 w-6 place-items-center rounded-full border-2 border-[var(--bg-panel)] text-white" style={{ background: color }}><Icon name={meta.icon} size={12} /></span>
              <p className="text-sm font-semibold text-primary">{meta.label}{e.to_status && <span className="font-normal text-muted"> · {e.from_status ? `${PHASE_LABEL[e.from_status as CasePhase]} → ` : ""}{PHASE_LABEL[e.to_status as CasePhase] ?? e.to_status}</span>}</p>
              {e.body && <p className="whitespace-pre-wrap text-sm text-muted">{e.body}</p>}
              <p className="text-xs text-muted">{e.user_name} · {e.user_role} · {fmtDate(e.created_at)}</p>
            </li>
          );
        })}
      </ol>
      <form className="no-print mt-4 flex gap-2" onSubmit={async (e) => { e.preventDefault(); if (await act(() => caseApi.note(c.id, note), "Catatan ditambahkan.")) setNote(""); }}>
        <input className="input-text" required maxLength={2000} placeholder="Tambah catatan…" value={note} onChange={(e) => setNote(e.target.value)} aria-label="Catatan" />
        <button className="btn-secondary" disabled={busy || !note.trim()}>Kirim</button>
      </form>
    </section>
  );
}
