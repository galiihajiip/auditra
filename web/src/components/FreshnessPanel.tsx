import { useCallback, useEffect, useState } from "react";
import { fetchFreshness, type Freshness } from "../api/client";
import Icon from "./Icon";

const n = (v: number) => v.toLocaleString("id-ID");
const short = (v: number) => (v >= 1e6 ? `${(v / 1e6).toLocaleString("id-ID", { maximumFractionDigits: 2 })} jt` : n(v));

export default function FreshnessPanel() {
  const [f, setF] = useState<Freshness | null>(null);
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);

  const load = useCallback(async (refresh = false) => {
    setBusy(true);
    try { setF(await fetchFreshness(refresh)); } catch { /* panel opsional */ } finally { setBusy(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  if (!f) return null;
  const live = f.live.total;
  const behind = f.behind_rows;
  const tone = live == null ? "#94a3b8" : behind && behind > 0 ? "#f59e0b" : "#22c55e";
  const summary =
    live == null ? "SIRUP tidak terjangkau saat ini — menampilkan snapshot analisis."
    : behind && behind > 0 ? `Snapshot ${short(f.snapshot.rows)} paket · SIRUP kini ${short(live)} (+${short(behind)} belum masuk analisis)`
    : "Snapshot sinkron dengan SIRUP.";
  const checked = new Date(f.live.checked_at * 1000).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });

  return (
    <section className="rounded-2xl border bg-[var(--bg-panel)] px-4 py-2.5" style={{ borderColor: `color-mix(in srgb, ${tone} 55%, var(--border))` }} aria-label="Kesegaran data">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <button type="button" className="flex min-w-0 items-center gap-2 text-left text-sm text-primary" aria-expanded={open} onClick={() => setOpen((o) => !o)}>
          <span className="h-2.5 w-2.5 shrink-0 rounded-full" style={{ background: tone, boxShadow: `0 0 0 4px color-mix(in srgb, ${tone} 25%, transparent)` }} />
          <span className="font-semibold">Kesegaran data</span>
          <span className="truncate text-muted">{summary}</span>
        </button>
        <div className="flex items-center gap-2">
          <button type="button" className="btn-secondary !py-1 text-xs" disabled={busy} onClick={() => load(true)}>
            <Icon name="refresh" size={13} /> {busy ? "Memeriksa…" : "Periksa SIRUP"}
          </button>
          <button type="button" className="text-sm font-semibold text-[var(--accent-teal)]" onClick={() => setOpen((o) => !o)}>{open ? "Tutup" : "Detail"}</button>
        </div>
      </div>

      {open && (
        <div className="fade-up mt-3 grid gap-4 border-t border-[var(--border-subtle)] pt-3 text-sm sm:grid-cols-3">
          <div>
            <p className="text-muted">Snapshot analisis</p>
            <p className="num font-display text-xl font-extrabold text-primary">{n(f.snapshot.rows)}</p>
            <p className="text-xs text-muted">{f.snapshot.exported_at ? `diekspor ${f.snapshot.exported_at}` : "tanggal ekspor tidak tercatat"}</p>
          </div>
          <div>
            <p className="text-muted">SIRUP LKPP saat ini</p>
            <p className="num font-display text-xl font-extrabold text-primary">{live == null ? "—" : n(live)}</p>
            <p className="text-xs text-muted">{live == null ? f.live.error : `dicek pukul ${checked}`}{f.live.stale ? " (hasil sebelumnya)" : ""}</p>
          </div>
          <div>
            <p className="text-muted">Belum masuk analisis</p>
            <p className="num font-display text-xl font-extrabold" style={{ color: tone }}>{behind == null ? "—" : `${behind > 0 ? "+" : ""}${n(behind)}`}{f.behind_pct != null && behind! > 0 ? ` (${f.behind_pct}%)` : ""}</p>
            <p className="text-xs text-muted">Skor RPI dihitung dari snapshot, bukan data live.</p>
          </div>
          {f.delta && (
            <p className="text-xs text-muted sm:col-span-3">
              Audit delta ({f.delta.live_dir}): <b className="text-primary">{n(f.delta.new_in_live)}</b> paket baru ·{" "}
              <b className="text-primary">{n(f.delta.removed_from_live)}</b> tidak lagi ada · <b className="text-primary">{n(f.delta.pagu_changed)}</b> pagu berubah ·{" "}
              <b className="text-primary">{n(f.delta.metode_changed)}</b> metode berubah.
            </p>
          )}
          <p className="text-xs text-muted sm:col-span-3">
            Sumber: <a className="underline" href={f.source_url} target="_blank" rel="noopener noreferrer">SIRUP LKPP</a>. Buka passport paket untuk membandingkannya langsung dengan SIRUP.
          </p>
        </div>
      )}
    </section>
  );
}
