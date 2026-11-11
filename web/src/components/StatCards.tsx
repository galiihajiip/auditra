import type { GeoCoverage, OverviewStats } from "../types";
import { formatPaguCompact } from "../utils/formatPagu";
import Icon, { type IconName } from "./Icon";
import Skeleton from "./Skeleton";

interface Props {
  stats: OverviewStats | null;
  geoCoverage: GeoCoverage | null;
}

export default function StatCards({ stats, geoCoverage }: Props) {
  const n = (v: number) => v.toLocaleString("id-ID");
  const cards: { icon: IconName; label: string; value: string | null; hint: string; tone: string }[] = [
    { icon: "database", label: "Total pagu dianalisis", value: stats ? formatPaguCompact(stats.total_pagu_miliar) : null, hint: "dari paket sesuai filter aktif", tone: "var(--accent-teal)" },
    { icon: "layers", label: "Paket dianalisis", value: stats ? n(stats.total_paket) : null,
      hint: geoCoverage ? `${n(geoCoverage.mapped_packages)} dapat dipetakan ke kab/kota` : "sesuai filter aktif", tone: "var(--accent-blue)" },
    { icon: "alert", label: "Paket kritis", value: stats ? n(stats.paket_kritis) : null, hint: "RPI ≥ 70 — prioritas tertinggi", tone: "#ef4444" },
    { icon: "spark", label: "Indikasi pecah paket", value: stats ? n(stats.split_contract) : null, hint: "skor fragmentasi ≥ 0,6 (split contract)", tone: "#f97316" },
  ];
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {cards.map((c) => (
        <div key={c.label} className="stat-card fade-up">
          <span className="grid h-9 w-9 place-items-center rounded-xl" style={{ color: c.tone, background: "color-mix(in srgb, currentColor 14%, transparent)" }}>
            <Icon name={c.icon} size={18} />
          </span>
          <p className="mt-3 text-sm text-muted">{c.label}</p>
          {c.value ? (
            <p className="num font-display text-2xl font-extrabold text-primary sm:text-3xl">{c.value}</p>
          ) : (
            <Skeleton className="mt-1 h-8 w-28" />
          )}
          <p className="mt-0.5 text-xs text-muted">{c.hint}</p>
        </div>
      ))}
    </div>
  );
}
