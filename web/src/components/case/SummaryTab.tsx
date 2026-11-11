import { useState } from "react";
import { Link } from "react-router-dom";
import { caseApi } from "../../api/client";
import { PHASE_LABEL, fmtRupiah } from "../../utils/caseLabels";
import Icon from "../Icon";
import type { TabProps } from "./types";

export default function SummaryTab({ c, user, busy, act }: TabProps) {
  const canWrite = (user.role === "auditor" && ["pelaksanaan", "reviu", "komunikasi"].includes(c.phase)) || (user.role === "reviewer" && ["reviu", "komunikasi"].includes(c.phase));
  const [text, setText] = useState(c.conclusion ?? "");
  const tested = c.procedures.filter((p) => p.status !== "belum").length;
  const kpi = [
    { l: "Prosedur diuji", v: `${tested}/${c.procedures.length}` },
    { l: "Bukti", v: c.evidence.length },
    { l: "Bukti diterima", v: c.evidence.filter((e) => e.review_status === "verified").length },
    { l: "Temuan", v: c.findings.length },
  ];
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {kpi.map((k) => <div key={k.l} className="stat-card !p-4"><p className="text-sm text-muted">{k.l}</p><p className="num font-display text-2xl font-extrabold text-primary">{k.v}</p></div>)}
      </div>
      <section className="panel space-y-3">
        <h3 className="panel-title">Kesimpulan penugasan</h3>
        <p className="panel-sub">Unsur LHP: pernyataan sesuai standar, tujuan/lingkup/metodologi, kesimpulan, temuan, rekomendasi, tanggapan (SPKN Pelaporan par. 12).</p>
        <textarea className="input-text" rows={5} maxLength={4000} disabled={!canWrite} aria-label="Kesimpulan penugasan" value={text} onChange={(e) => setText(e.target.value)} placeholder="Tulis kesimpulan berdasarkan bukti yang cukup dan tepat…" />
        {canWrite && <div className="flex justify-end"><button className="btn-primary" disabled={busy || text === (c.conclusion ?? "")} onClick={() => act(() => caseApi.plan(c.id, { conclusion: text }), "Kesimpulan disimpan.")}>Simpan kesimpulan</button></div>}
        {!canWrite && !c.conclusion && <p className="text-xs text-muted">Kesimpulan ditulis pada tahap pelaksanaan/reviu/komunikasi.</p>}
      </section>
      <section className="panel space-y-2 text-sm">
        <h3 className="panel-title">Ringkasan penugasan</h3>
        <dl className="grid grid-cols-[auto,1fr] gap-x-4 gap-y-1.5">
          <dt className="text-muted">Paket</dt><dd className="text-primary">{c.title} · <Link className="text-[var(--accent-teal)] underline" to={`/paket/${c.package_id}`}>passport</Link></dd>
          <dt className="text-muted">Lembaga</dt><dd className="text-primary">{c.lembaga}</dd>
          <dt className="text-muted">Pagu</dt><dd className="text-primary">{fmtRupiah(c.pagu)}</dd>
          <dt className="text-muted">Tahap</dt><dd className="text-primary">{PHASE_LABEL[c.phase]}{c.outcome ? ` · ${c.outcome === "dengan_temuan" ? "dengan temuan" : "tanpa temuan"}` : ""}</dd>
          <dt className="text-muted">Tujuan</dt><dd className="whitespace-pre-wrap text-primary">{c.objective ?? "—"}</dd>
          <dt className="text-muted">Lingkup</dt><dd className="text-primary">{c.scope_stages.map((s) => c.meta.stages.find((x) => x.key === s)?.label ?? s).join(", ") || "—"}</dd>
          {c.stop_reason && (<><dt className="text-muted">Alasan henti</dt><dd className="text-primary">{c.stop_reason}</dd></>)}
        </dl>
        <button className="btn-secondary no-print mt-2" onClick={() => window.print()}><Icon name="print" size={15} /> Cetak laporan</button>
      </section>
    </div>
  );
}
