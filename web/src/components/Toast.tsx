import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from "react";
import Icon from "./Icon";

type Kind = "success" | "error" | "info";
interface ToastItem { id: number; kind: Kind; text: string }
interface Ctx { toast: (text: string, kind?: Kind) => void }

const ToastCtx = createContext<Ctx>({ toast: () => {} });
export const useToast = () => useContext(ToastCtx);

const COLOR: Record<Kind, string> = { success: "#22c55e", error: "#ef4444", info: "var(--accent-teal)" };

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const seq = useRef(0);

  const toast = useCallback((text: string, kind: Kind = "success") => {
    const id = ++seq.current;
    setItems((x) => [...x.slice(-3), { id, kind, text }]);
    setTimeout(() => setItems((x) => x.filter((t) => t.id !== id)), kind === "error" ? 7000 : 4000);
  }, []);

  const value = useMemo(() => ({ toast }), [toast]);
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="no-print pointer-events-none fixed inset-x-0 bottom-4 z-[60] flex flex-col items-center gap-2 px-3" aria-live="polite">
        {items.map((t) => (
          <div key={t.id} role={t.kind === "error" ? "alert" : "status"}
            className="fade-up pointer-events-auto flex max-w-md items-start gap-2.5 rounded-xl border bg-[var(--bg-panel)] px-4 py-3 text-sm text-primary shadow-2xl"
            style={{ borderColor: COLOR[t.kind] }}>
            <span style={{ color: COLOR[t.kind] }} className="mt-0.5"><Icon name={t.kind === "error" ? "alert" : "checkCircle"} /></span>
            <span>{t.text}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
