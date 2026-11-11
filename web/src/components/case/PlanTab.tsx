import { useEffect, useState } from "react";
import { caseApi, type Criterion } from "../../api/client";
import { Dialog } from "../Dialog";
import EmptyState from "../EmptyState";
import Icon from "../Icon";
import type { TabProps } from "./types";

function ProcedureDialog({ c, busy, onSave, onClose }: { c: TabProps["c"]; busy: boolean; onSave: (b: { title: string; objective?: string; criteria: Criterion[]; techniques: string[] }) => void; onClose: () => void }) {
  const [title, setTitle] = useState(""); const [objective, setObjective] = useState("");
  const [ref, setRef] = useState(""); const [text, setText] = useState(""); const [tech, setTech] = useState<string[]>([]);
  return (
    <Dialog title="Tambah prosedur manual" onClose={onClose} wide>
      <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); onSave({ title, objective: objective || undefined, criteria: [{ ref, text }], techniques: tech }); }}>
        <div><label className="field-label" htmlFor="pr-t">Judul prosedur</label><input id="pr-t" className="input-text" required minLength={3} value={title} onChange={(e) => setTitle(e.target.value)} /></div>
        <div><label className="field-label" htmlFor="pr-o">Tujuan (opsional)</label><input id="pr-o" className="input-text" value={objective} onChange={(e) => setObjective(e.target.value)} /></div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div><label className="field-label" htmlFor="pr-r">Sumber kriteria</label><input id="pr-r" className="input-text" required minLength={3} placeholder="mis. Perpres 16/2018 Pasal 57" value={ref} onChange={(e) => setRef(e.target.value)} /></div>
          <div><label className="field-label" htmlFor="pr-x">Bunyi kriteria</label><input id="pr-x" className="input-text" required minLength={3} value={text} onChange={(e) => setText(e.target.value)} /></div>
        </div>
        <fieldset><legend className="field-label">Teknik (SPKN par. 32)</legend>
          <div className="flex flex-wrap gap-1.5">{Object.entries(c.meta.techniques).map(([k, v]) => (
            <label key={k} className={`tab-btn cursor-pointer ${tech.includes(k) ? "tab-btn-active" : ""}`}>
              <input type="checkbox" className="sr-only" checked={tech.includes(k)} onChange={() => setTech(tech.includes(k) ? tech.filter((x) => x !== k) : [...tech, k])} />{v}</label>))}</div></fieldset>
        <div className="flex justify-end gap-2"><button type="button" className="btn-secondary" onClick={onClose}>Batal</button><button className="btn-primary" disabled={busy}>Tambah</button></div>
      </form>
    </Dialog>
  );
}

export default function PlanTab({ c, user, busy, act }: TabProps) {
  const editable = user.role === "auditor" && (c.phase === "seleksi" || c.phase === "perencanaan");
  const [f, setF] = useState({ selection_reason: c.selection_reason ?? "", objective: c.objective ?? "", risk_note: c.risk_note ?? "", materiality_note: c.materiality_note ?? "", criteria_note: c.criteria_note ?? "" });
  const [scope, setScope] = useState<string[]>(c.scope_stages);
  const [addProc, setAddProc] = useState(false);
  useEffect(() => {
    setF({ selection_reason: c.selection_reason ?? "", objective: c.objective ?? "", risk_note: c.risk_note ?? "", materiality_note: c.materiality_note ?? "", criteria_note: c.criteria_note ?? "" });
    setScope(c.scope_stages);
  }, [c.id, c.selection_reason, c.objective, c.risk_note, c.materiality_note, c.criteria_note, c.scope_stages]);

  const dirty = f.selection_reason !== (c.selection_reason ?? "") || f.objective !== (c.objective ?? "") || f.risk_note !== (c.risk_note ?? "") ||
    f.materiality_note !== (c.materiality_note ?? "") || f.criteria_note !== (c.criteria_note ?? "") || scope.join() !== c.scope_stages.join();
  const area = (id: string, label: string, key: keyof typeof f, hint: string, rows = 3) => (
    <div>
      <label className="field-label" htmlFor={id}>{label}</label>
      <textarea id={id} className="input-text" rows={rows} maxLength={2000} disabled={!editable} value={f[key]} onChange={(e) => setF({ ...f, [key]: e.target.value })} />
      <p className="mt-1 text-xs text-muted">{hint}</p>
    </div>
  );
  const save = () => act(() => caseApi.plan(c.id, { ...f, scope_stages: scope }), "Rencana disimpan.");

  return (
    <div className="space-y-5">
      <section className="panel space-y-4" aria-labelledby="rencana-h">
        <div><h3 id="rencana-h" className="panel-title">Seleksi sasaran & rencana penugasan</h3>
          <p className="panel-sub">Mengikuti perencanaan penugasan SPKN: tujuan jelas, pemahaman hal pokok, risiko, kriteria, dan materialitas.</p></div>

        <div className="grid gap-2 rounded-xl border border-[var(--border-subtle)] bg-[var(--bg-subtle)] p-3 text-sm sm:grid-cols-4">
          <div><p className="text-xs text-muted">RPI</p><p className="num font-bold text-primary">{c.rpi?.toFixed(1)} · {c.risk_label}</p></div>
          <div><p className="text-xs text-muted">Pagu</p><p className="num font-bold text-primary">{c.pagu != null ? "Rp " + Number(c.pagu).toLocaleString("id-ID") : "—"}</p></div>
          <div><p className="text-xs text-muted">Metode</p><p className="font-bold text-primary">{c.metode ?? "—"}</p></div>
          <div><p className="text-xs text-muted">Jenis</p><p className="font-bold text-primary">{c.jenis_pengadaan ?? "—"}</p></div>
        </div>

        {area("alasan", "Alasan seleksi sasaran", "selection_reason", "Faktor risiko yang lazim: nilai, kompleksitas, signifikansi bagi program, kualitas pengendalian intern, perhatian pemangku kepentingan, permintaan pimpinan (sumber sekunder, lihat riset §3.1). RPI hanya prioritas, bukan temuan.")}
        {area("tujuan", "Tujuan penugasan", "objective", "Nyatakan hal pokok yang diuji dan pertanyaan audit (SPKN Pelaksanaan par. 9–10).")}

        <fieldset>
          <legend className="field-label">Lingkup tahap pengadaan</legend>
          <div className="flex flex-wrap gap-2">
            {c.meta.stages.map((s) => (
              <label key={s.key} className={`tab-btn ${editable ? "cursor-pointer" : "opacity-70"} ${scope.includes(s.key) ? "tab-btn-active" : ""}`}>
                <input type="checkbox" className="sr-only" disabled={!editable} checked={scope.includes(s.key)} onChange={() => setScope(scope.includes(s.key) ? scope.filter((x) => x !== s.key) : [...scope, s.key])} />
                {scope.includes(s.key) && <Icon name="check" size={14} />}{s.label}
              </label>
            ))}
          </div>
          <p className="mt-1 text-xs text-muted">Data SIRUP hanya mencakup <b>perencanaan</b>. Bukti tahap pelaksanaan kontrak dan serah terima harus dikumpulkan dari entitas.</p>
        </fieldset>

        {area("risiko", "Penilaian risiko (termasuk risiko kecurangan)", "risk_note", "Risiko bawaan, pengendalian, deteksi, dan risiko kecurangan (SPKN Pelaksanaan par. 16–19).")}
        {area("materialitas", "Pertimbangan materialitas", "materiality_note", "Kuantitatif dan kualitatif: nilai paket, dampak publik, persyaratan peraturan (par. 23–25).")}
        {area("kriteria", "Catatan kriteria tambahan (opsional)", "criteria_note", "Kriteria per prosedur sudah tercantum di program audit; tambahkan bila ada kriteria lain.", 2)}

        {editable && <div className="flex justify-end"><button className="btn-primary" disabled={busy || !dirty} onClick={save}>Simpan rencana</button></div>}
        {!editable && <p className="text-xs text-muted">Rencana hanya dapat diubah oleh auditor pada tahap seleksi/perencanaan.</p>}
      </section>

      <section className="panel" aria-labelledby="program-h">
        <div className="mb-3 flex flex-wrap items-start justify-between gap-2">
          <div><h3 id="program-h" className="panel-title">Program audit ({c.procedures.length} prosedur)</h3>
            <p className="panel-sub">Dibangkitkan dari atribut dan sinyal paket; tiap prosedur memuat kriteria bersumber pasal.</p></div>
          {editable && c.phase === "perencanaan" && (
            <div className="flex flex-wrap gap-2">
              <button className="btn-primary" disabled={busy} onClick={() => act(() => caseApi.generateProgram(c.id), "Program audit dibangkitkan.")}><Icon name="spark" size={15} /> {c.procedures.length ? "Bangkitkan ulang" : "Bangkitkan program"}</button>
              <button className="btn-secondary" disabled={busy} onClick={() => setAddProc(true)}><Icon name="file" size={15} /> Prosedur manual</button>
            </div>
          )}
        </div>
        <div className="mb-3 rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-subtle)] px-3 py-2 text-xs text-muted">
          Program disusun dari pasal Perpres 16/2018 jo. 46/2025 dan SPKN, <b>bukan</b> salinan pedoman audit BPKP (lampirannya tidak dapat diakses saat riset). Auditor tetap memakai pertimbangan profesional.
        </div>
        {c.procedures.length === 0 ? (
          <EmptyState icon="list" title="Belum ada prosedur">{editable && c.phase === "perencanaan" ? "Tekan “Bangkitkan program” setelah lingkup dipilih." : "Program dibuat pada tahap perencanaan."}</EmptyState>
        ) : (
          <ul className="space-y-2">
            {c.procedures.map((p) => (
              <li key={p.id} className="rounded-xl border border-[var(--border-subtle)] p-3">
                <p className="font-semibold text-primary"><span className="chip mr-2">{p.code}</span>{p.title}{p.custom && <span className="chip ml-2">manual</span>}</p>
                {p.objective && <p className="mt-1 text-sm text-muted">{p.objective}</p>}
                <p className="mt-1.5 text-xs text-muted">Kriteria: {p.criteria.map((x) => x.ref).join(" · ")}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
      {addProc && <ProcedureDialog c={c} busy={busy} onClose={() => setAddProc(false)} onSave={async (b) => { if (await act(() => caseApi.addProcedure(c.id, b), "Prosedur ditambahkan.")) setAddProc(false); }} />}
    </div>
  );
}
