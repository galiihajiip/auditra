import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { caseApi, fetchLiveCheck, type LiveCheck, type PackagePassport } from "../api/client";
import { formatApiError } from "../api/errors";
import { useAuth } from "../auth/AuthContext";
import { ReasonDialog } from "../components/Dialog";
import EmptyState from "../components/EmptyState";
import Icon from "../components/Icon";
import JourneyStepper from "../components/JourneyStepper";
import RpiRing, { RISK_COLOR } from "../components/RpiRing";
import Skeleton from "../components/Skeleton";
import StatusPill from "../components/StatusPill";
import { useToast } from "../components/Toast";
import { ACTIVE_PHASES, fmtRupiah } from "../utils/caseLabels";

type CaseRef = Awaited<ReturnType<typeof caseApi.byPackage>>;

const HINT: Record<string, string> = {
  s1_metode: "Penunjukan langsung atau pengecualian lebih rentan terhadap masalah tata kelola dibanding tender terbuka.",
  s2_pagu_anomali: "Nilai pagu menyimpang jauh dari paket sejenis (jenis dan metode yang sama).",
  s3_fragmentasi: "Ada paket mirip dalam satuan kerja yang sama, tepat di bawah batas penunjukan langsung — pola pecah paket.",
  s4_konsentrasi: "Satuan kerja ini banyak memakai metode berisiko dibanding yang lain.",
  s5_umkm: "Paket ditandai UMKM padahal nilainya jauh di atas kewajaran paket UMKM.",
  s6_dana_metode: "Dana APBN dikombinasikan dengan metode pemilihan berisiko.",
  s7_reputasi: "Lembaga ini punya pengaruh risiko tinggi di Knowledge Graph pengadaan.",
};

export default function PackagePage() {
  const { id = "" } = useParams();
  const nav = useNavigate();
  const loc = useLocation();
  const { user } = useAuth();
  const { toast } = useToast();
  const [data, setData] = useState<PackagePassport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cases, setCases] = useState<CaseRef>([]);
  const [askNote, setAskNote] = useState(false);
  const [busy, setBusy] = useState(false);
  const [live, setLive] = useState<LiveCheck | null>(null);
  const [liveBusy, setLiveBusy] = useState(false);
  const [showSrc, setShowSrc] = useState(false);

  useEffect(() => {
    setData(null); setError(null); setLive(null);
    if (!/^\d+$/.test(id)) { setError("ID paket tidak valid."); return; }
    caseApi.passport(id).then(setData).catch((e) => setError(formatApiError(e)));
  }, [id]);

  useEffect(() => {
    if (!user) { setCases([]); return; }
    caseApi.byPackage(id).then(setCases).catch(() => setCases([]));
  }, [id, user]);

  const back = () => (window.history.length > 1 && loc.key !== "default" ? nav(-1) : nav("/"));

  if (error) {
    return (
      <div className="panel mx-auto max-w-lg">
        <EmptyState icon="alert" title="Paket tidak dapat dimuat" action={<button className="btn-secondary" onClick={back}><Icon name="arrowLeft" size={15} /> Kembali</button>}>{error}</EmptyState>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="space-y-4" aria-busy="true">
        <Skeleton className="h-10 w-2/3" /><Skeleton className="h-48" />
        <div className="grid gap-4 lg:grid-cols-12"><Skeleton className="h-96 lg:col-span-7" /><Skeleton className="h-96 lg:col-span-5" /></div>
      </div>
    );
  }

  const p = data.package;
  const label = String(p.risk_label ?? "");
  const rpi = Number(p.RPI);
  const active = cases.find((c) => ACTIVE_PHASES.includes(c.phase));
  const latest = cases[0];
  const step = !latest ? 1 : latest.phase === "selesai" ? 4 : latest.phase === "reviu" || latest.phase === "komunikasi" ? 3 : 2;

  const openCase = async (note: string) => {
    setAskNote(false); setBusy(true);
    try {
      const c = await caseApi.create(Number(p.id), note);
      toast("Penugasan audit dibuka. Lanjut ke perencanaan.");
      nav(`/kasus/${c.id}`);
    } catch (e) { toast(formatApiError(e), "error"); setBusy(false); }
  };

  const checkLive = async () => {
    setLiveBusy(true);
    try { setLive(await fetchLiveCheck(id)); }
    catch (e) { toast(formatApiError(e), "error"); }
    finally { setLiveBusy(false); }
  };

  /** Aksi utama kontekstual — satu tombol yang selalu menunjukkan langkah berikutnya. */
  const primary = !user ? (
    <Link to="/masuk" state={{ from: `/paket/${id}` }} className="btn-primary btn-lg">Masuk untuk membuka penugasan <Icon name="arrowRight" size={18} /></Link>
  ) : active ? (
    <Link to={`/kasus/${active.id}`} className="btn-primary btn-lg">Lanjutkan penugasan #{active.id} <Icon name="arrowRight" size={18} /></Link>
  ) : user.role === "auditor" ? (
    <button className="btn-primary btn-lg" onClick={() => setAskNote(true)} disabled={busy}><Icon name="shield" size={18} /> Buka penugasan audit</button>
  ) : (
    <span className="chip">Hanya auditor yang dapat membuka penugasan</span>
  );

  const facts: [string, string][] = [
    ["ID SIRUP", String(p.id)],
    ["Lembaga", String(p.lembaga ?? "—")],
    ["Satuan kerja", String(p.satker ?? "—")],
    ["Metode pemilihan", String(p.metode ?? "—")],
    ["Jenis pengadaan", String(p.jenisPengadaan ?? "—")],
    ["Sumber dana", String(p.sumberDana ?? "—")],
    ["Lokasi", String(p.lokasi ?? "—")],
    ["Rencana pemilihan", String(p.pemilihanDate ?? "—")],
    ["UMKM", p.isUMKM ? "Ya" : "Tidak"],
  ];
  const total = data.signals.reduce((a, s) => a + s.contribution, 0);

  return (
    <div className="space-y-5 pb-24 sm:pb-0">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button className="btn-secondary !py-1.5 text-sm" onClick={back}><Icon name="arrowLeft" size={15} /> Kembali ke hasil</button>
        <JourneyStepper current={step} failed={latest?.phase === "dihentikan"} />
      </div>

      <section className="hero fade-up">
        <div className="flex flex-col gap-5 p-5 sm:flex-row sm:items-center sm:p-8">
          <RpiRing value={rpi} label={label} size={108} stroke={10} />
          <div className="min-w-0 flex-1">
            <p className="eyebrow">Passport paket</p>
            <h2 className="font-display text-2xl font-extrabold leading-tight text-primary sm:text-3xl">{String(p.paket)}</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="status-pill" style={{ color: RISK_COLOR[label] }}>RPI {rpi.toFixed(1)} · {label}</span>
              <span className="chip"><Icon name="database" size={13} /> {fmtRupiah(Number(p.pagu))}</span>
              <span className="chip">{String(p.metode ?? "")}</span>
              <span className="chip"><Icon name="map" size={13} /> {String(p.lokasi ?? "—")}</span>
              {latest && <StatusPill status={latest.phase} />}
            </div>
          </div>
          <div className="hidden shrink-0 sm:block no-print">{primary}</div>
        </div>
        <p className="border-t border-[var(--border)] bg-[var(--bg-panel)] px-5 py-3 text-sm text-muted sm:px-8">
          <Icon name="alert" size={14} className="mr-1 inline -translate-y-px" />{data.provenance.caveat} Verifikasi dokumen tetap diperlukan oleh auditor.
        </p>
      </section>

      <div className="grid gap-5 lg:grid-cols-12">
        <section className="panel lg:col-span-7">
          <h3 className="panel-title">Mengapa paket ini berprioritas?</h3>
          <p className="panel-sub mb-4">Skor RPI adalah jumlah dari 7 sinyal berbobot. Makin panjang batang, makin besar sumbangannya.</p>
          <ul className="space-y-4">
            {[...data.signals].sort((a, b) => b.contribution - a.contribution).map((s) => (
              <li key={s.key}>
                <div className="flex items-baseline justify-between gap-3">
                  <span className="font-semibold text-primary">{s.label} <span className="text-xs font-normal text-muted">bobot {(s.weight * 100).toFixed(0)}%</span></span>
                  <span className="num shrink-0 text-sm font-bold" style={{ color: s.value >= 0.6 ? "var(--accent-orange)" : "var(--text-muted)" }}>+{s.contribution.toFixed(1)}</span>
                </div>
                <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-[var(--bg-subtle)]" role="progressbar" aria-label={s.label} aria-valuemin={0} aria-valuemax={1} aria-valuenow={s.value}>
                  <div className="h-full rounded-full" style={{ width: `${Math.max(2, Math.min(1, s.value) * 100)}%`, background: s.value >= 0.6 ? "linear-gradient(90deg,#f97316,#ef4444)" : "linear-gradient(90deg,var(--accent-blue),var(--accent-teal-2))", transition: "width .6s ease" }} />
                </div>
                {s.value >= 0.4 && <p className="mt-1 text-sm text-muted">{HINT[s.key]}</p>}
              </li>
            ))}
          </ul>
          <p className="mt-4 border-t border-[var(--border-subtle)] pt-3 text-xs text-muted">
            Jumlah sumbangan = {total.toFixed(1)} poin. RPI akhir dapat berbeda tipis karena penyesuaian skor jaringan setelah Knowledge Graph dihitung.
          </p>
        </section>

        <div className="space-y-5 lg:col-span-5">
          <section className="panel">
            <h3 className="panel-title mb-3">Rincian paket</h3>
            <dl className="grid grid-cols-[auto,1fr] gap-x-4 gap-y-2 text-sm">
              {facts.map(([k, v]) => (<div key={k} className="contents"><dt className="text-muted">{k}</dt><dd className="break-words font-medium text-primary">{v}</dd></div>))}
            </dl>
            {p.uraianPekerjaan ? <p className="mt-3 border-t border-[var(--border-subtle)] pt-3 text-sm text-muted">{String(p.uraianPekerjaan).slice(0, 500)}</p> : null}
          </section>

          <section className="panel">
            <h3 className="panel-title">Cek ke sumber</h3>
            <p className="panel-sub mb-3">Bandingkan paket ini dengan halaman resmi SIRUP saat ini.</p>
            <div className="flex flex-wrap gap-2">
              <button className="btn-secondary" onClick={checkLive} disabled={liveBusy}><Icon name="refresh" size={15} className={liveBusy ? "animate-spin" : ""} /> {liveBusy ? "Memeriksa…" : "Bandingkan dengan SIRUP"}</button>
              <a className="btn-secondary" href={data.provenance.source_url} target="_blank" rel="noopener noreferrer">Cari ID {data.provenance.sirup_id} <Icon name="external" size={14} /></a>
            </div>
            {live && (
              <div className="fade-up mt-3 rounded-xl border p-3 text-sm" role="status" style={{ borderColor: live.in_sync ? "#22c55e" : "#f59e0b" }}>
                <p className="flex items-center gap-2 font-semibold" style={{ color: live.in_sync ? "#22c55e" : "#f59e0b" }}>
                  <Icon name={live.in_sync ? "checkCircle" : "alert"} size={17} />
                  {live.in_sync ? "Sinkron dengan SIRUP saat ini" : "Berbeda dari SIRUP saat ini"}
                </p>
                {live.differences.map((d) => (
                  <p key={d.field} className="mt-1 text-muted">{d.label}: snapshot <b className="text-primary">{String(d.snapshot)}</b> → SIRUP <b className="text-primary">{String(d.live)}</b></p>
                ))}
                {live.live.uraianPekerjaan && <p className="mt-2 text-muted">Uraian (SIRUP): {live.live.uraianPekerjaan.slice(0, 300)}</p>}
                <p className="mt-1 text-xs text-muted">Dicek {new Date(live.checked_at * 1000).toLocaleTimeString("id-ID")}</p>
              </div>
            )}
            <button className="mt-4 flex w-full items-center justify-between text-sm font-semibold text-[var(--accent-teal)]" onClick={() => setShowSrc((v) => !v)} aria-expanded={showSrc}>
              Asal data & metodologi <Icon name="arrowRight" size={14} className={showSrc ? "rotate-90" : ""} />
            </button>
            {showSrc && (
              <dl className="fade-up mt-2 grid grid-cols-[auto,1fr] gap-x-4 gap-y-1.5 text-sm">
                <dt className="text-muted">Sumber</dt><dd className="text-primary">{data.provenance.source}</dd>
                <dt className="text-muted">Dataset</dt><dd className="text-primary">{data.provenance.dataset_rows.toLocaleString("id-ID")} baris</dd>
                <dt className="text-muted">Pipeline</dt><dd className="text-primary">{data.provenance.pipeline.join(" → ")}</dd>
                <dt className="text-muted">Dokumen</dt><dd className="text-primary">{data.provenance.methodology_doc}</dd>
              </dl>
            )}
          </section>
        </div>
      </div>

      {/* bar aksi lengket untuk ponsel */}
      <div className="no-print fixed inset-x-0 bottom-0 z-40 border-t border-[var(--border)] bg-[color-mix(in_srgb,var(--bg-panel)_92%,transparent)] p-3 backdrop-blur-xl sm:hidden">
        <div className="flex [&>*]:w-full">{primary}</div>
      </div>

      {askNote && (
        <ReasonDialog title="Buka penugasan audit" description="Tuliskan alasan memilih paket ini sebagai sasaran audit (faktor risiko: nilai, sinyal RPI, kompleksitas, perhatian pemangku kepentingan). Bisa dilengkapi nanti." confirmLabel="Buka penugasan" onConfirm={openCase} onClose={() => setAskNote(false)} />
      )}
    </div>
  );
}
