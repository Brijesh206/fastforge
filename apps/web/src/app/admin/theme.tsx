"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";

export type AdminTheme = "light" | "dark";

const STORAGE_KEY = "ff-admin-theme";

interface ThemeContextValue {
  theme: AdminTheme;
  toggle: () => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

/** Light/dark for the admin panel.
 *
 *  Replaces the previous 20-theme daisyUI switcher: the panel now runs on the
 *  same shadcn token set as the rest of the app. Adding a theme is one more
 *  `.ff-admin[data-theme="…"]` block in globals.css, which is a change a
 *  buyer can make without learning a plugin's theme format. */
export function AdminThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<AdminTheme>("light");

  // Read after mount: localStorage is client-only, and branching on it during
  // render would hydrate markup the server never produced.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "light" || saved === "dark") {
      setThemeState(saved);
      return;
    }
    setThemeState(
      window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
    );
  }, []);

  const toggle = useCallback(() => {
    setThemeState((current) => {
      const next: AdminTheme = current === "light" ? "dark" : "light";
      localStorage.setItem(STORAGE_KEY, next);
      return next;
    });
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, toggle }}>{children}</ThemeContext.Provider>
  );
}

export function useAdminTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useAdminTheme must be used within an AdminThemeProvider");
  }
  return ctx;
}
