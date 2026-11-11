import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Icon, { type IconName } from "./Icon";
import type { PkgRow } from "./PackageCard";
import { topReasons } from "./PackageCard";
import RpiRing from "./RpiRing";
import { useToast } from "./Toast";
import { formatApiError } from "../api/errors";

const STEPS: { icon: IconName; title: string; text: string }[] = [
  { icon: "search", title: "Temukan", text: "Saring 3 juta paket per provinsi, lembaga, dan metode." },
  { icon: "radar", title: "Telusuri", text: "Buka passport: skor RPI beserta 7 sinyal dan sumber datanya." },
  { icon: "upload", title: "Rencanakan & uji", text: "Program audit dari sinyal paket, bukti per prosedur, temuan berunsur lengkap." },
  { icon: "shield", title: "Reviu & tindak lanjut", text: "Reviu berjenjang, tanggapan entitas, pemantauan rekomendasi." },
];

const SIG: [string, string][] = [
  ["s1_metode", "Metode"], ["s2_pagu_anomali", "Pagu"], ["s3_fragmentasi", "Fragmentasi"],
  ["s4_konsentrasi", "Konsentrasi"], ["s7_reputasi", "Lembaga"],
];

/** Pratinjau passport dari paket teratas yang NYATA — bukan ilustrasi palsu. */
function Preview({ row }: { row: PkgRow }) {
  return (
    <Link to={`/paket/${String(row.id)}`} className="panel interactive hidden w-[330px] shrink-0 !p-4 no-underline lg:block" aria-label="Pratinjau passport paket teratas">
      <p className="mb-3 text-xs font-bold uppercase tracking-wider text-muted">Paket teratas saat ini</p>
      <div className="flex items-center gap-3">
        <RpiRing value={Number(row.RPI) || 0} label={String(row.risk_label ?? "")} size={64} stroke={7} />
        <div className="min-w-0">
          <p className="line-clamp-2 font-semibold leading-snug text-primary">{String(row.paket)}</p>
          <p className="truncate text-sm text-muted">{String(row.lembaga ?? "")}</p>
        </div>
      </div>
      <ul className="mt-4 space-y-2">
        {SIG.map(([k, label]) => {
          const v = Math.max(0, Math.min(1, Number(row[k]) || 0));
          return (
            <li key={k} className="flex items-center gap-2 text-xs text-muted">
              <span className="w-20 shrink-0">{label}</span>
              <span className="h-1.5 flex-1 overflow-hidden rounded-full bg-[var(--bg-subtle)]"><span className="block h-full rounded-full" style={{ width: `${Math.max(3, v * 100)}%`, background: v >= 0.6 ? "linear-gradient(90deg,#f97316,#ef4444)" : "var(--accent-blue)" }} /></span>
              <span className="num w-8 text-right font-semibold text-primary">{v.toFixed(2)}</span>
            </li>
          );
        })}
      </ul>
      <p className="mt-3 text-xs text-muted">Pemicu: {topReasons(row, 2).join(" · ") || "—"}</p>
    </Link>
  );
}

export default function Hero({ onStart, preview }: { onStart: () => void; preview?: PkgRow | null }) {
  const { user, signIn } = useAuth();
  const { toast } = useToast();

  const demo = async () => {
    try {
      await signIn("auditor@auditra.demo", "auditra2026");
      toast("Masuk sebagai Auditor demo. Pilih satu paket untuk memulai.", "success");
      onStart();
    } catch (e) {
      toast(formatApiError(e), "error");
    }
  };

  return (
    <section className="hero fade-up" aria-label="Pengantar">
      <div className="flex items-center justify-between gap-8 px-5 pb-6 pt-8 sm:px-10 sm:pt-12">
       <div className="min-w-0">
        <p className="eyebrow">SIRUP LKPP · Tahun Anggaran 2026</p>
        <h2 className="mt-3 max-w-3xl font-display text-[2rem] font-extrabold leading-[1.1] text-primary sm:text-5xl">
          Temukan paket pengadaan yang paling perlu <span className="gradient-text">diaudit lebih dulu</span>
        </h2>
        <p className="mt-4 max-w-2xl text-base text-muted sm:text-lg">
          Auditra memberi skor prioritas pada jutaan rencana paket, menjelaskan alasannya, lalu menuntun tim audit
          dari perencanaan hingga temuan dan tindak lanjut, mengikuti standar pemeriksaan.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          {user ? (
            <>
              <button className="btn-primary btn-lg" onClick={onStart}>Jelajahi paket prioritas <Icon name="arrowRight" size={18} /></button>
              <Link to="/kasus" className="btn-secondary btn-lg">Penugasan saya</Link>
            </>
          ) : (
            <>
              <button className="btn-primary btn-lg" onClick={demo}><Icon name="play" size={16} /> Coba demo sekarang</button>
              <button className="btn-secondary btn-lg" onClick={onStart}>Jelajahi tanpa masuk</button>
            </>
          )}
        </div>
        {!user && <p className="mt-2 text-sm text-muted">Satu klik masuk sebagai auditor demo — tanpa pendaftaran.</p>}
       </div>
       {preview && <Preview row={preview} />}
      </div>

      <ol className="grid gap-px border-t border-[var(--border)] bg-[var(--border)] sm:grid-cols-2 lg:grid-cols-4" aria-label="Alur kerja">
        {STEPS.map((s, i) => (
          <li key={s.title} className="flex gap-3 bg-[var(--bg-panel)] p-4 sm:p-5">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[var(--glow)] text-[var(--accent-teal)]"><Icon name={s.icon} size={20} /></span>
            <div>
              <p className="font-display font-bold text-primary"><span className="text-muted">{i + 1}.</span> {s.title}</p>
              <p className="text-sm text-muted">{s.text}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
