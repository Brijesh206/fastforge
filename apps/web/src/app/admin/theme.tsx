"use client";

import { createContext, useContext, useEffect, useState } from "react";

/** daisyUI themes exposed in the panel. Keep in sync with the `themes:` list in
 *  src/styles/globals.css — a theme not enabled there won't render. */
export const ADMIN_THEMES = [
  "light",
  "dark",
  "corporate",
  "business",
  "emerald",
  "synthwave",
  "retro",
  "dracula",
  "night",
  "forest",
  "luxury",
  "nord",
  "winter",
  "autumn",
  "coffee",
  "dim",
  "sunset",
  "cupcake",
  "valentine",
  "lofi",
] as const;

export type AdminTheme = (typeof ADMIN_THEMES)[number];

const STORAGE_KEY = "ff-admin-theme";
const DEFAULT_THEME: AdminTheme = "light";

interface ThemeContextValue {
  theme: AdminTheme;
  setTheme: (theme: AdminTheme) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function AdminThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<AdminTheme>(DEFAULT_THEME);

  // Read the saved theme after mount (localStorage is client-only).
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY) as AdminTheme | null;
    if (saved && (ADMIN_THEMES as readonly string[]).includes(saved)) {
      setThemeState(saved);
    }
  }, []);

  function setTheme(next: AdminTheme) {
    setThemeState(next);
    localStorage.setItem(STORAGE_KEY, next);
  }

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useAdminTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useAdminTheme must be used within an AdminThemeProvider");
  }
  return ctx;
}
