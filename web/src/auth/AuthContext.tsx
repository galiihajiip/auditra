import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { authApi, getToken, setToken, type User } from "../api/client";

interface AuthState {
  user: User | null;
  ready: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) { setReady(true); return; }
    authApi.me().then(setUser).catch(() => setToken(null)).finally(() => setReady(true));
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const s = await authApi.login(email, password);
    setToken(s.token); setUser(s.user);
  }, []);
  const signUp = useCallback(async (name: string, email: string, password: string) => {
    const s = await authApi.register(name, email, password);
    setToken(s.token); setUser(s.user);
  }, []);
  const signOut = useCallback(() => { setToken(null); setUser(null); }, []);

  const value = useMemo(() => ({ user, ready, signIn, signUp, signOut }), [user, ready, signIn, signUp, signOut]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth(): AuthState {
  const v = useContext(Ctx);
  if (!v) throw new Error("useAuth di luar AuthProvider");
  return v;
}
