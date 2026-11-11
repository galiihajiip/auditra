import type { ReactNode } from "react";
import Icon, { type IconName } from "./Icon";

export default function EmptyState({ icon = "inbox", title, children, action }: { icon?: IconName; title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="grid place-items-center px-4 py-10 text-center">
      <div className="mb-3 grid h-14 w-14 place-items-center rounded-2xl border border-[var(--border)] bg-[var(--bg-subtle)] text-[var(--accent-teal)]">
        <Icon name={icon} size={26} />
      </div>
      <p className="font-display text-base font-bold text-primary">{title}</p>
      {children && <p className="mt-1 max-w-sm text-sm text-muted">{children}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
