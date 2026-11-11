import { useState, type FormEvent } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { formatApiError } from "../api/errors";
import { useAuth } from "../auth/AuthContext";
import Icon, { type IconName } from "../components/Icon";
import { useToast } from "../components/Toast";

const ROLES: { icon: IconName; title: string; text: string; email: string; label: string }[] = [
  { icon: "search", title: "Auditor", text: "Membuka kasus dari paket berisiko, menelaah, dan mengunggah bukti.", email: "auditor@auditra.demo", label: "Masuk sebagai Auditor demo" },
  { icon: "shield", title: "Reviewer", text: "Memverifikasi atau menolak bukti dan memutuskan kasus. Tidak dapat meninjau bukti miliknya sendiri.", email: "reviewer@auditra.demo", label: "Masuk sebagai Reviewer demo" },
];

export default function LoginPage() {
  const { user, signIn, signUp } = useAuth();
  const { toast } = useToast();
  const nav = useNavigate();
  const from = (useLocation().state as { from?: string } | null)?.from ?? "/kasus";
  const [mode, setMode] = useState<"login" | "register">("login");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to={from} replace />;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setErr(null); setBusy(true);
    try {
      if (mode === "login") await signIn(email, password); else await signUp(name, email, password);
      nav(from, { replace: true });
    } catch (e2) { setErr(formatApiError(e2)); } finally { setBusy(false); }
  };

  const demo = async (em: string) => {
    setBusy(true);
    try { await signIn(em, "auditra2026"); nav(from, { replace: true }); }
    catch (e) { toast(formatApiError(e), "error"); setBusy(false); }
  };

  return (
    <div className="mx-auto grid max-w-5xl gap-5 lg:grid-cols-2">
      <section className="hero fade-up">
        <div className="p-6 sm:p-9">
          <p className="eyebrow">Ruang kerja audit</p>
          <h2 className="mt-2 font-display text-3xl font-extrabold leading-tight text-primary sm:text-4xl">Dari paket berisiko ke <span className="gradient-text">bukti terverifikasi</span></h2>
          <p className="mt-3 text-muted">Masuk untuk membuka kasus, mengunggah bukti, dan meninjau hasil kerja tim. Setiap langkah tercatat di riwayat yang tidak dapat diubah.</p>
          <div className="mt-6 space-y-3">
            {ROLES.map((r) => (
              <button key={r.email} type="button" disabled={busy} onClick={() => demo(r.email)}
                className="panel interactive flex w-full items-start gap-3 !p-4 text-left">
                <span className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-[var(--glow)] text-[var(--accent-teal)]"><Icon name={r.icon} size={21} /></span>
                <span className="min-w-0 flex-1">
                  <span className="block font-display font-bold text-primary">{r.title}</span>
                  <span className="block text-sm text-muted">{r.text}</span>
                  <span className="mt-2 inline-flex items-center gap-1 text-sm font-semibold text-[var(--accent-teal)]">{r.label} <Icon name="arrowRight" size={14} /></span>
                </span>
              </button>
            ))}
          </div>
        </div>
      </section>

      <form className="panel fade-up space-y-4 self-start !p-6 sm:!p-8" onSubmit={submit} aria-label={mode === "login" ? "Form masuk" : "Form daftar"}>
        <div className="flex gap-2" role="tablist">
          <button type="button" role="tab" aria-selected={mode === "login"} className={`tab-btn ${mode === "login" ? "tab-btn-active" : ""}`} onClick={() => setMode("login")}>Masuk</button>
          <button type="button" role="tab" aria-selected={mode === "register"} className={`tab-btn ${mode === "register" ? "tab-btn-active" : ""}`} onClick={() => setMode("register")}>Daftar</button>
        </div>
        <h3 className="font-display text-2xl font-extrabold text-primary">{mode === "login" ? "Selamat datang kembali" : "Buat akun auditor"}</h3>
        {mode === "register" && (
          <div><label className="field-label" htmlFor="name">Nama lengkap</label>
            <input id="name" className="input-text" required minLength={2} maxLength={80} value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" /></div>
        )}
        <div><label className="field-label" htmlFor="email">Email</label>
          <input id="email" className="input-text" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" /></div>
        <div><label className="field-label" htmlFor="pw">Kata sandi{mode === "register" && " (min. 8 karakter)"}</label>
          <input id="pw" className="input-text" type="password" required minLength={mode === "register" ? 8 : 1} value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={mode === "login" ? "current-password" : "new-password"} /></div>
        {err && <p role="alert" className="flex items-start gap-2 rounded-xl border border-red-400/50 bg-red-500/10 px-3 py-2.5 text-sm text-red-500"><Icon name="alert" size={16} className="mt-0.5 shrink-0" />{err}</p>}
        <button className="btn-primary btn-lg w-full" disabled={busy}>{busy ? "Memproses…" : mode === "login" ? "Masuk" : "Buat akun"}</button>
        <p className="text-center text-xs text-muted">Pendaftaran publik selalu berperan auditor. Akun reviewer dibuat oleh admin.</p>
      </form>
    </div>
  );
}
