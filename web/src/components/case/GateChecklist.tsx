import type { Gate } from "../../api/client";
import Icon from "../Icon";

/** Syarat objektif untuk lanjut ke tahap berikutnya — dihitung & ditegakkan server. */
export default function GateChecklist({ gates }: { gates: Gate[] }) {
  if (gates.length === 0) return null;
  return (
    <ul className="space-y-1.5" aria-label="Syarat tahap berikutnya">
      {gates.map((g) => (
        <li key={g.key} className="flex items-start gap-2 text-sm">
          <span className="mt-0.5 shrink-0" style={{ color: g.na ? "#94a3b8" : g.ok ? "#22c55e" : g.blocking ? "#f59e0b" : "#94a3b8" }}>
            <Icon name={g.na ? "clock" : g.ok ? "checkCircle" : "alert"} size={16} />
          </span>
          <span>
            <span className={g.na ? "text-muted" : g.ok ? "text-primary" : "font-semibold text-primary"}>{g.label}</span>
            {g.na && <span className="block text-xs text-muted">belum berlaku — belum ada yang dinilai</span>}
            {!g.ok && g.hint && <span className="block text-xs text-muted">{g.hint}</span>}
            {!g.blocking && !g.ok && <span className="block text-xs text-muted">(peringatan, tidak menghalangi)</span>}
          </span>
        </li>
      ))}
    </ul>
  );
}
