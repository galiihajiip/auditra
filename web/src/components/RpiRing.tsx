export const RISK_COLOR: Record<string, string> = {
  KRITIS: "#ef4444",
  TINGGI: "#f97316",
  SEDANG: "#eab308",
  RENDAH: "#4f8ff7",
};

export function riskLabelOf(rpi: number): string {
  return rpi >= 70 ? "KRITIS" : rpi >= 50 ? "TINGGI" : rpi >= 30 ? "SEDANG" : "RENDAH";
}

/** Cincin skor RPI 0–100 — elemen visual khas Auditra. */
export default function RpiRing({ value, label, size = 64, stroke = 7 }: { value: number; label?: string; size?: number; stroke?: number }) {
  const lbl = label ?? riskLabelOf(value);
  const color = RISK_COLOR[lbl] ?? "#4f8ff7";
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, value)) / 100;
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }} role="img" aria-label={`RPI ${value.toFixed(1)} dari 100, ${lbl}`}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} opacity={0.7} />
        <circle
          cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round"
          strokeDasharray={`${c * pct} ${c}`} style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>
      <span className="num absolute inset-0 grid place-items-center font-display font-extrabold text-primary" style={{ fontSize: size * 0.3 }}>
        {value.toFixed(0)}
      </span>
    </div>
  );
}
