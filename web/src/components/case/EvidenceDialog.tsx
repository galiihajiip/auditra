import { useRef, useState, type FormEvent } from "react";
import type { CaseDetail, EvidenceMeta } from "../../api/client";
import { fmtBytes } from "../../utils/caseLabels";
import { Dialog } from "../Dialog";
import Icon from "../Icon";

interface Props {
  c: CaseDetail;
  procedureId: number | null;
  busy: boolean;
  onSubmit: (title: string, opts: { url?: string; file?: File }, meta: EvidenceMeta) => void;
  onClose: () => void;
}

/** Bentuk (SPKN par. 31), teknik (par. 32), dan kualitas: relevan, valid, andal (par. 29). */
export default function EvidenceDialog({ c, procedureId, busy, onSubmit, onClose }: Props) {
  const [title, setTitle] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [proc, setProc] = useState<number | "">(procedureId ?? "");
  const [form, setForm] = useState("catatan_transaksi");
  const [technique, setTechnique] = useState("inspeksi");
  const [origin, setOrigin] = useState("entitas");
  const [docDate, setDocDate] = useState("");
  const [q, setQ] = useState({ relevan: false, valid: false, andal: false });
  const [concern, setConcern] = useState(false);
  const [concernNote, setConcernNote] = useState("");
  const ref = useRef<HTMLInputElement>(null);

  const expected = c.procedures.find((p) => p.id === proc)?.evidence_expected ?? [];
  const submit = (e: FormEvent) => {
    e.preventDefault();
    onSubmit(title, file ? { file } : { url }, {
      procedure_id: proc === "" ? null : proc, form, technique, origin, doc_date: docDate || undefined,
      ...q, authenticity_concern: concern, authenticity_note: concernNote || undefined,
    });
  };

  return (
    <Dialog title="Tambah bukti" onClose={onClose} wide>
      <form onSubmit={submit} className="space-y-3">
        <div>
          <label className="field-label" htmlFor="ev-proc">Untuk prosedur</label>
          <select id="ev-proc" className="input-select" value={proc} onChange={(e) => setProc(e.target.value ? Number(e.target.value) : "")}>
            <option value="">— bukti umum (tidak terkait satu prosedur) —</option>
            {c.procedures.map((p) => <option key={p.id} value={p.id}>{p.code} · {p.title}</option>)}
          </select>
          {expected.length > 0 && (
            <p className="mt-1 text-xs text-muted">Bukti yang diharapkan: {expected.map((x) => x.name).join(" · ")}</p>
          )}
        </div>

        <div className="rounded-xl border-2 border-dashed border-[var(--border)] p-3 text-center">
          {file ? (
            <p className="text-sm text-primary">{file.name} <span className="text-muted">({fmtBytes(file.size)})</span>{" "}
              <button type="button" className="text-red-500 underline" onClick={() => { setFile(null); if (ref.current) ref.current.value = ""; }}>hapus</button></p>
          ) : (
            <p className="text-sm text-muted"><Icon name="upload" size={16} className="mr-1 inline" />
              <button type="button" className="font-semibold text-[var(--accent-teal)] underline" onClick={() => ref.current?.click()}>Pilih berkas</button>{" "}
              (PDF, PNG, JPG, TXT, CSV · maks. 5 MB) atau isi tautan di bawah</p>
          )}
          <input ref={ref} className="sr-only" type="file" accept=".pdf,.png,.jpg,.jpeg,.txt,.csv" aria-label="Berkas bukti"
            onChange={(e) => { const f = e.target.files?.[0] ?? null; setFile(f); if (f) { setUrl(""); if (!title) setTitle(f.name.replace(/\.[^.]+$/, "")); } }} />
        </div>
        <input className="input-text" type="url" placeholder="https://… (tautan dokumen online)" value={url} disabled={!!file} onChange={(e) => setUrl(e.target.value)} aria-label="Tautan bukti" />
        <input className="input-text" required minLength={2} maxLength={160} placeholder="Judul bukti, mis. Dokumen HPS paket" value={title} onChange={(e) => setTitle(e.target.value)} aria-label="Judul bukti" />

        <div className="grid gap-3 sm:grid-cols-2">
          <div><label className="field-label" htmlFor="ev-form">Bentuk bukti</label>
            <select id="ev-form" className="input-select" value={form} onChange={(e) => setForm(e.target.value)}>
              {Object.entries(c.meta.forms).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
          <div><label className="field-label" htmlFor="ev-tech">Teknik perolehan</label>
            <select id="ev-tech" className="input-select" value={technique} onChange={(e) => setTechnique(e.target.value)}>
              {Object.entries(c.meta.techniques).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
          <div><label className="field-label" htmlFor="ev-origin">Asal bukti</label>
            <select id="ev-origin" className="input-select" value={origin} onChange={(e) => setOrigin(e.target.value)}>
              {Object.entries(c.meta.origins).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</select></div>
          <div><label className="field-label" htmlFor="ev-date">Tanggal dokumen (opsional)</label>
            <input id="ev-date" className="input-text" type="date" value={docDate} onChange={(e) => setDocDate(e.target.value)} /></div>
        </div>

        <fieldset className="rounded-xl border border-[var(--border-subtle)] p-3">
          <legend className="px-1 text-sm font-semibold text-primary">Penilaian ketepatan bukti</legend>
          <p className="mb-2 text-xs text-muted">Ketepatan = relevan, valid, dan andal (SPKN Pelaksanaan par. 29). Nilai jujur: bukti yang belum meyakinkan sebaiknya tidak dicentang.</p>
          <div className="flex flex-wrap gap-x-5 gap-y-1">
            {([["relevan", "Relevan dengan tujuan/kriteria"], ["valid", "Valid"], ["andal", "Andal (sumber dapat dipercaya)"]] as const).map(([k, l]) => (
              <label key={k} className="flex items-center gap-2 text-sm"><input type="checkbox" checked={q[k]} onChange={(e) => setQ({ ...q, [k]: e.target.checked })} /> {l}</label>
            ))}
          </div>
          <label className="mt-3 flex items-center gap-2 text-sm"><input type="checkbox" checked={concern} onChange={(e) => setConcern(e.target.checked)} /> Dokumen diragukan keasliannya / diduga dimodifikasi</label>
          {concern && <textarea className="input-text mt-2" rows={2} required placeholder="Alasan keraguan (wajib). SPKN par. 34 mewajibkan pendalaman." value={concernNote} onChange={(e) => setConcernNote(e.target.value)} />}
        </fieldset>

        <div className="flex justify-end gap-2">
          <button type="button" className="btn-secondary" onClick={onClose}>Batal</button>
          <button className="btn-primary" disabled={busy || (!url && !file) || !title.trim()}>Simpan bukti</button>
        </div>
      </form>
    </Dialog>
  );
}
