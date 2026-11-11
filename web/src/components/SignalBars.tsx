import type { PackagePassport } from "../api/client";

export default function SignalBars({ signals }: { signals: PackagePassport["signals"] }) {
  return (
    <ul className="space-y-3">
      {signals.map((s) => (
        <li key={s.key}>
          <div className="flex justify-between gap-2 text-xs text-primary">
            <span>
              {s.label} <span className="text-muted">· bobot {(s.weight * 100).toFixed(0)}%</span>
            </span>
            <span className="font-semibold">
              {s.value.toFixed(2)} <span className="text-muted">→ +{s.contribution.toFixed(1)} RPI</span>
            </span>
          </div>
          <div
            className="mt-1 h-2 overflow-hidden rounded bg-[var(--bg-subtle)]"
            role="progressbar"
            aria-label={s.label}
            aria-valuemin={0}
            aria-valuemax={1}
            aria-valuenow={s.value}
          >
            <div
              className="h-full rounded"
              style={{ width: `${Math.min(1, s.value) * 100}%`, background: s.value >= 0.6 ? "var(--accent-orange)" : "var(--accent-blue)" }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
