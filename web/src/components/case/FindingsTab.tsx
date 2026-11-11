import { useState, type FormEvent } from "react";
import { caseApi, type CaseDetail, type Finding, type FindingInput, type TanggapanStatus, type TlStatus } from "../../api/client";
import { Dialog } from "../Dialog";
import EmptyState from "../EmptyState";
import Icon from "../Icon";
import type { TabProps } from "./types";

const TANGGAPAN: Record<TanggapanStatus, string> = {
  belum: "Belum ditanggapi", diterima: "Diterima entitas", diterima_sebagian: "Diterima sebagian", ditolak: "Ditolak entitas", tidak_ada_tanggapan: "Tidak ada tanggapan",
};
const TL: Record<TlStatus, string> = {
  belum: "Belum ditindaklanjuti", dalam_proses: "Dalam proses", sesuai: "Sesuai rekomendasi", tidak_sesuai: "Tidak sesuai rekomendasi", tidak_dapat_ditindaklanjuti: "Tidak dapat ditindaklanjuti",
};
const TL_COLOR: Record<TlStatus, string> = { belum: "#94a3b8", dalam_proses: "#eab308", sesuai: "#22c55e", tidak_sesuai: "#ef4444", tidak_dapat_ditindaklanjuti: "#94a3b8" };

function FindingDialog({ c, initial, busy, onSave, onClose }: { c: CaseDetail; initial?: Finding; busy: boolean; onSave: (f: FindingInput) => void; onClose: () => void }) {
  const [f, setF] = useState<FindingInput>({
    title: initial?.title ?? "", procedure_id: initial?.procedure_id ?? null, kondisi: initial?.kondisi ?? "", kriteria: initial?.kriteria ?? "",
    kriteria_sumber: initial?.kriteria_sumber ?? "", sebab: initial?.sebab ?? "", akibat: initial?.akibat ?? "", nilai_potensi: initial?.nilai_potensi ?? null,
    rekomendasi: initial?.rekomendasi ?? "", rekomendasi_kepada: initial?.rekomendasi_kepada ?? "", indikasi_kecurangan: initial?.indikasi_kecurangan ?? false,
    evidence_ids: initial?.evidence_ids ?? [],
  });
  const set = <K extends keyof FindingInput>(k: K, v: FindingInput[K]) => setF({ ...f, [k]: v });
  const proc = c.procedures.find((p) => p.id === f.procedure_id);
  const submit = (e: FormEvent) => { e.preventDefault(); onSave({ ...f, nilai_potensi: f.nilai_potensi || null, rekomendasi: f.rekomendasi || undefined, rekomendasi_kepada: f.rekomendasi_kepada || undefined, sebab: f.sebab || undefined, akibat: f.akibat || undefined }); };
  const ta = (id: string, label: string, k: "kondisi" | "kriteria" | "sebab" | "akibat" | "rekomendasi", hint: string, req = false) => (
    <div><label className="field-label" htmlFor={id}>{label}{req && " *"}</label>
      <textarea id={id} className="input-text" rows={2} required={req} maxLength={3000} value={f[k] ?? ""} onChange={(e) => set(k, e.target.value)} /><p className="mt-0.5 text-xs text-muted">{hint}</p></div>
  );
  return (
    <Dialog title={initial ? "Ubah temuan" : "Susun temuan"} onClose={onClose} wide>
      <form onSubmit={submit} className="space-y-3">
        <p className="rounded-lg bg-[var(--bg-subtle)] px-3 py-2 text-xs text-muted">Temuan disusun bila ada ketidaksesuaian antara <b>kondisi</b> dan <b>kriteria</b> (SPKN Pelaksanaan par. 39). Sebab dan akibat dipertimbangkan sesuai tujuan (par. 40).</p>
        <div><label className="field-label" htmlFor="f-t">Judul temuan *</label><input id="f-t" className="input-text" required minLength={3} value={f.title} onChange={(e) => set("title", e.target.value)} /></div>
        <div><label className="field-label" htmlFor="f-p">Prosedur terkait</label>
          <select id="f-p" className="input-select" value={f.procedure_id ?? ""} onChange={(e) => { const v = e.target.value ? Number(e.target.value) : null; const p = c.procedures.find((x) => x.id === v); setF({ ...f, procedure_id: v, kriteria_sumber: f.kriteria_sumber || p?.criteria[0]?.ref || "", kriteria: f.kriteria || p?.criteria[0]?.text || "" }); }}>
            <option value="">— tidak terkait satu prosedur —</option>{c.procedures.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.title}</option>)}</select>
          {proc && <p className="mt-0.5 text-xs text-muted">Kriteria prosedur terisi otomatis; sunting bila perlu.</p>}</div>
        {ta("f-k", "Kondisi", "kondisi", "Apa yang sebenarnya ditemukan, dengan fakta dan angka.", true)}
        {ta("f-r", "Kriteria", "kriteria", "Ketentuan/standar yang seharusnya dipenuhi.", true)}
        <div><label className="field-label" htmlFor="f-s">Sumber kriteria *</label><input id="f-s" className="input-text" required minLength={3} placeholder="mis. Perpres 16/2018 jo. 46/2025 Pasal 20(2)(d)" value={f.kriteria_sumber} onChange={(e) => set("kriteria_sumber", e.target.value)} /><p className="mt-0.5 text-xs text-muted">Wajib disajikan di laporan (SPKN Pelaporan par. 20).</p></div>
        {ta("f-b", "Sebab", "sebab", "Mengapa kondisi menyimpang dari kriteria.")}
        {ta("f-a", "Akibat", "akibat", "Dampak atau risiko yang timbul.")}
        <div className="grid gap-3 sm:grid-cols-2">
          <div><label className="field-label" htmlFor="f-n">Nilai potensi (Rp, opsional)</label><input id="f-n" className="input-text" type="number" min={0} value={f.nilai_potensi ?? ""} onChange={(e) => set("nilai_potensi", e.target.value ? Number(e.target.value) : null)} /></div>
          <div><label className="field-label" htmlFor="f-rk">Rekomendasi ditujukan kepada</label><input id="f-rk" className="input-text" placeholder="mis. Pengguna Anggaran" value={f.rekomendasi_kepada ?? ""} onChange={(e) => set("rekomendasi_kepada", e.target.value)} /></div>
        </div>
        {ta("f-rec", "Rekomendasi", "rekomendasi", "Nyatakan apa yang harus diperbaiki dan siapa yang bertanggung jawab (SPKN Pelaporan par. 24).")}
        <fieldset className="rounded-xl border border-[var(--border-subtle)] p-3">
          <legend className="px-1 text-sm font-semibold text-primary">Bukti pendukung *</legend>
          {c.evidence.length === 0 ? <p className="text-sm text-muted">Belum ada bukti. Tambahkan bukti di tab Pengujian.</p> : (
            <ul className="space-y-1">{c.evidence.map((e) => (
              <li key={e.id}><label className="flex items-start gap-2 text-sm"><input type="checkbox" className="mt-1" checked={f.evidence_ids.includes(e.id)} onChange={() => set("evidence_ids", f.evidence_ids.includes(e.id) ? f.evidence_ids.filter((x) => x !== e.id) : [...f.evidence_ids, e.id])} />
                <span><span className="text-primary">{e.title}</span> <span className="text-xs text-muted">({[e.relevan, e.valid, e.andal].filter(Boolean).length}/3 tepat)</span></span></label></li>))}</ul>)}
        </fieldset>
        <label className="flex items-start gap-2 rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm"><input type="checkbox" className="mt-1" checked={f.indikasi_kecurangan} onChange={(e) => set("indikasi_kecurangan", e.target.checked)} />
          <span><b className="text-amber-500">Indikasi awal kecurangan</b><span className="block text-xs text-muted">Menandai temuan agar ditindaklanjuti sesuai ketentuan atau diusulkan PDTT Investigatif (SPKN par. 42).</span></span></label>
        <div className="flex justify-end gap-2"><button type="button" className="btn-secondary" onClick={onClose}>Batal</button><button className="btn-primary" disabled={busy}>{initial ? "Simpan perubahan" : "Simpan temuan"}</button></div>
      </form>
    </Dialog>
  );
}

function Element({ label, children }: { label: string; children: string | null }) {
  if (!children) return null;
  return <div><dt className="text-xs font-bold uppercase tracking-wider text-muted">{label}</dt><dd className="whitespace-pre-wrap text-sm text-primary">{children}</dd></div>;
}

export default function FindingsTab({ c, user, busy, act }: TabProps) {
  const isAuditor = user.role === "auditor";
  const canEdit = isAuditor && c.phase === "pelaksanaan";
  const [dlg, setDlg] = useState<{ f?: Finding } | null>(null);
  const [resp, setResp] = useState<Record<number, { s: TanggapanStatus; t: string }>>({});
  const [tl, setTl] = useState<Record<number, { s: TlStatus; t: string }>>({});
  const code = (pid: number | null) => c.procedures.find((p) => p.id === pid)?.code;

  const saveF = async (input: FindingInput) => {
    const ok = await act(() => (dlg?.f ? caseApi.updateFinding(dlg.f.id, input) : caseApi.addFinding(c.id, input)), "Temuan disimpan.");
    if (ok) setDlg(null);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div><h3 className="panel-title">Temuan ({c.findings.length})</h3><p className="panel-sub">Unsur temuan: kondisi, kriteria, sebab, akibat (SPKN Pelaksanaan par. 40).</p></div>
        {canEdit && <button className="btn-primary" onClick={() => setDlg({})}><Icon name="file" size={15} /> Susun temuan</button>}
      </div>

      {c.advisories.map((a) => (
        <p key={a.key} role="note" className="flex items-start gap-2 rounded-xl border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-sm text-amber-500"><Icon name="alert" size={17} className="mt-0.5 shrink-0" />{a.text}</p>
      ))}

      {c.findings.length === 0 && <div className="panel"><EmptyState icon="shield" title="Belum ada temuan">{canEdit ? "Bila ada prosedur “tidak sesuai”, susun temuan dari ketidaksesuaian kondisi dan kriteria. Bila semua sesuai, penugasan dapat diselesaikan tanpa temuan." : "Temuan disusun auditor pada tahap pelaksanaan."}</EmptyState></div>}

      <ul className="space-y-4">
        {c.findings.map((f) => {
          const r = resp[f.id] ?? { s: f.tanggapan_status === "belum" ? "diterima" : f.tanggapan_status, t: f.tanggapan ?? "" };
          const t = tl[f.id] ?? { s: f.tl_status, t: f.tl_note ?? "" };
          return (
            <li key={f.id} className="panel space-y-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div><p className="text-xs text-muted">Temuan #{f.id}{code(f.procedure_id) && <span className="chip ml-2">{code(f.procedure_id)}</span>}</p>
                  <h4 className="font-display text-lg font-bold text-primary">{f.title}</h4></div>
                <div className="flex flex-wrap items-center gap-2">
                  {f.indikasi_kecurangan && <span className="status-pill" style={{ color: "#f59e0b" }}>Indikasi kecurangan</span>}
                  {f.nilai_potensi != null && <span className="chip num">Rp {Number(f.nilai_potensi).toLocaleString("id-ID")}</span>}
                  {canEdit && <button className="btn-secondary !py-1 text-sm" onClick={() => setDlg({ f })}>Ubah</button>}
                </div>
              </div>
              <dl className="grid gap-3 sm:grid-cols-2">
                <Element label="Kondisi">{f.kondisi}</Element>
                <div><dt className="text-xs font-bold uppercase tracking-wider text-muted">Kriteria</dt><dd className="text-sm text-primary">{f.kriteria}<span className="mt-0.5 block text-xs text-muted">Sumber: {f.kriteria_sumber}</span></dd></div>
                <Element label="Sebab">{f.sebab}</Element>
                <Element label="Akibat">{f.akibat}</Element>
              </dl>
              {f.rekomendasi && <p className="rounded-lg bg-[var(--bg-subtle)] px-3 py-2 text-sm"><b className="text-primary">Rekomendasi{f.rekomendasi_kepada ? ` kepada ${f.rekomendasi_kepada}` : ""}:</b> <span className="text-muted">{f.rekomendasi}</span></p>}
              <p className="text-xs text-muted">Bukti pendukung: {f.evidence_ids.length ? f.evidence_ids.map((id) => c.evidence.find((e) => e.id === id)?.title ?? `#${id}`).join(" · ") : "—"}</p>

              {(c.phase === "komunikasi" || f.tanggapan_status !== "belum") && (
                <div className="rounded-xl border border-[var(--border-subtle)] p-3">
                  <p className="mb-2 text-sm font-semibold text-primary">Tanggapan pihak yang bertanggung jawab</p>
                  {isAuditor && c.phase === "komunikasi" ? (
                    <form className="space-y-2" onSubmit={(e) => { e.preventDefault(); act(() => caseApi.respond(f.id, r.s, r.t), "Tanggapan dicatat."); }}>
                      <select className="input-select" aria-label={`Status tanggapan temuan ${f.id}`} value={r.s} onChange={(e) => setResp({ ...resp, [f.id]: { ...r, s: e.target.value as TanggapanStatus } })}>
                        {(Object.keys(TANGGAPAN) as TanggapanStatus[]).filter((k) => k !== "belum").map((k) => <option key={k} value={k}>{TANGGAPAN[k]}</option>)}</select>
                      <textarea className="input-text" rows={2} required maxLength={3000} aria-label={`Isi tanggapan temuan ${f.id}`} placeholder="Ringkas tanggapan tertulis entitas, atau alasan tidak ada tanggapan" value={r.t} onChange={(e) => setResp({ ...resp, [f.id]: { ...r, t: e.target.value } })} />
                      <button className="btn-primary" disabled={busy || !r.t.trim()}>Catat tanggapan</button>
                    </form>
                  ) : f.tanggapan_status === "belum" ? <p className="text-sm text-muted">Menunggu tanggapan entitas.</p> : (
                    <p className="text-sm"><span className="chip mr-2">{TANGGAPAN[f.tanggapan_status]}</span><span className="text-muted">{f.tanggapan}</span></p>
                  )}
                </div>
              )}

              {c.phase === "selesai" && f.rekomendasi && (
                <div className="rounded-xl border border-[var(--border-subtle)] p-3">
                  <p className="mb-2 flex items-center gap-2 text-sm font-semibold text-primary">Pemantauan tindak lanjut <span className="status-pill" style={{ color: TL_COLOR[f.tl_status] }}>{TL[f.tl_status]}</span></p>
                  <form className="space-y-2" onSubmit={(e) => { e.preventDefault(); act(() => caseApi.followup(f.id, t.s, t.t), "Tindak lanjut dicatat."); }}>
                    <select className="input-select" aria-label={`Status tindak lanjut temuan ${f.id}`} value={t.s} onChange={(e) => setTl({ ...tl, [f.id]: { ...t, s: e.target.value as TlStatus } })}>
                      {(Object.keys(TL) as TlStatus[]).map((k) => <option key={k} value={k}>{TL[k]}</option>)}</select>
                    <textarea className="input-text" rows={2} aria-label={`Catatan tindak lanjut temuan ${f.id}`} placeholder="Bukti/uraian tindak lanjut oleh entitas (wajib bila bukan 'belum')" value={t.t} onChange={(e) => setTl({ ...tl, [f.id]: { ...t, t: e.target.value } })} />
                    <button className="btn-secondary" disabled={busy}>Simpan pemantauan</button>
                  </form>
                  <p className="mt-1 text-xs text-muted">Tindak lanjut adalah kewenangan entitas; auditor memantau dan menilai kesesuaiannya (SPKN Pelaporan par. 10–11).</p>
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {dlg && <FindingDialog c={c} initial={dlg.f} busy={busy} onSave={saveF} onClose={() => setDlg(null)} />}
    </div>
  );
}
