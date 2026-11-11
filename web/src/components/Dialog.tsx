import { useEffect, useRef, useState, type ReactNode } from "react";
import Icon from "./Icon";

export function Dialog({ title, onClose, children, wide }: { title: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const prev = document.activeElement as HTMLElement | null;
    ref.current?.querySelector<HTMLElement>("textarea,input,button")?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => { window.removeEventListener("keydown", onKey); prev?.focus(); };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 p-0 backdrop-blur-sm sm:items-center sm:p-4" onClick={onClose}>
      <div ref={ref} role="dialog" aria-modal="true" aria-label={title}
        className={`panel fade-up max-h-[92vh] w-full overflow-y-auto rounded-b-none sm:rounded-b-2xl ${wide ? "max-w-2xl" : "max-w-md"}`} onClick={(e) => e.stopPropagation()}>
        <div className="mb-3 flex items-start justify-between gap-3">
          <h3 className="panel-title">{title}</h3>
          <button type="button" className="btn-secondary !p-1.5" onClick={onClose} aria-label="Tutup"><Icon name="x" size={16} /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

/** Dialog catatan/alasan — pengganti window.prompt. */
export function ReasonDialog({
  title, description, required, confirmLabel, danger, onConfirm, onClose,
}: {
  title: string; description?: string; required?: boolean; confirmLabel: string; danger?: boolean;
  onConfirm: (text: string) => void; onClose: () => void;
}) {
  const [text, setText] = useState("");
  const invalid = required && !text.trim();
  return (
    <Dialog title={title} onClose={onClose}>
      {description && <p className="mb-3 text-sm text-muted">{description}</p>}
      <label className="field-label" htmlFor="reason">{required ? "Alasan (wajib)" : "Catatan (opsional)"}</label>
      <textarea id="reason" className="input-text" rows={3} maxLength={1000} value={text} onChange={(e) => setText(e.target.value)} />
      <div className="mt-4 flex justify-end gap-2">
        <button type="button" className="btn-secondary" onClick={onClose}>Batal</button>
        <button type="button" className={danger ? "btn-danger" : "btn-primary"} disabled={invalid} onClick={() => onConfirm(text.trim())}>{confirmLabel}</button>
      </div>
    </Dialog>
  );
}
