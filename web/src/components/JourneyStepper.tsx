import Icon, { type IconName } from "./Icon";

export interface Step { label: string; icon: IconName }

const DEFAULT_STEPS: Step[] = [
  { label: "Temukan", icon: "search" },
  { label: "Telusuri", icon: "radar" },
  { label: "Audit", icon: "upload" },
  { label: "Reviu & lapor", icon: "shield" },
];

/** current: indeks langkah aktif; steps.length = semua selesai; failed menandai langkah aktif gagal/dihentikan. */
export default function JourneyStepper({ current, failed, steps = DEFAULT_STEPS }: { current: number; failed?: boolean; steps?: Step[] }) {
  return (
    <ol className="no-print scroll-x flex items-center gap-1.5 sm:gap-2" aria-label="Alur audit">
      {steps.map((s, i) => {
        const done = i < current;
        const active = i === current;
        const bad = active && failed;
        const color = bad ? "#ef4444" : done || active ? "var(--accent-teal)" : "var(--text-muted)";
        return (
          <li key={s.label} className="flex shrink-0 items-center gap-1.5 sm:gap-2" aria-current={active ? "step" : undefined}>
            <span className="flex items-center gap-2 rounded-full border px-3 py-1.5 text-sm font-semibold"
              style={{ color, borderColor: active ? color : "var(--border)", background: active ? "color-mix(in srgb, currentColor 12%, transparent)" : "transparent" }}>
              <Icon name={done ? "check" : s.icon} size={15} />
              <span className={active ? "" : "hidden lg:inline"}>{s.label}</span>
            </span>
            {i < steps.length - 1 && <span className="h-px w-3 bg-[var(--border)] sm:w-5" />}
          </li>
        );
      })}
    </ol>
  );
}
