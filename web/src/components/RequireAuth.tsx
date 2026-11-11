import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export default function RequireAuth({ children }: { children: ReactNode }) {
  const { user, ready } = useAuth();
  const loc = useLocation();
  if (!ready) return <p className="text-muted">Memeriksa sesi…</p>;
  if (!user) return <Navigate to="/masuk" replace state={{ from: loc.pathname }} />;
  return <>{children}</>;
}
