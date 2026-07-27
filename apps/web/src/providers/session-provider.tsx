"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";

import { api, tokenStore } from "@/lib/api";
import type { User } from "@/lib/types";

interface SessionContextValue {
  user: User | null;
  loading: boolean;
  /** Resolves with the signed-in user so callers can route on is_admin
   *  without waiting for the context value to propagate. */
  signIn: (email: string, password: string) => Promise<User>;
  signOut: () => void;
  refresh: () => Promise<User | null>;
}

const SessionContext = createContext<SessionContextValue | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    if (!tokenStore.access) {
      setUser(null);
      setLoading(false);
      return null;
    }
    try {
      const current = await api.me();
      setUser(current);
      return current;
    } catch {
      tokenStore.clear();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const signIn = useCallback(async (email: string, password: string) => {
    await api.login({ email, password });
    const current = await api.me();
    setUser(current);
    return current;
  }, []);

  const signOut = useCallback(() => {
    api.logout();
    setUser(null);
  }, []);

  return (
    <SessionContext.Provider value={{ user, loading, signIn, signOut, refresh }}>
      {children}
    </SessionContext.Provider>
  );
}

export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return ctx;
}
