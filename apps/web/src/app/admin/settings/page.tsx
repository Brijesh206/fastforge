"use client";

import { Check } from "lucide-react";

import { ADMIN_THEMES, useAdminTheme, type AdminTheme } from "@/app/admin/theme";

export default function AdminSettingsPage() {
  const { theme, setTheme } = useAdminTheme();

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-sm opacity-60">Personalize the admin panel.</p>
      </div>

      <section className="card border border-base-300 bg-base-200">
        <div className="card-body">
          <h2 className="card-title text-base">Theme</h2>
          <p className="text-sm opacity-60">
            Applies to the admin panel only. Saved to this browser.
          </p>

          <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {ADMIN_THEMES.map((name) => (
              <ThemeOption
                key={name}
                name={name}
                selected={theme === name}
                onSelect={() => setTheme(name)}
              />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function ThemeOption({
  name,
  selected,
  onSelect,
}: {
  name: AdminTheme;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      type="button"
      data-theme={name}
      onClick={onSelect}
      aria-pressed={selected}
      className={`overflow-hidden rounded-box border-2 bg-base-100 text-left text-base-content transition ${
        selected ? "border-primary" : "border-base-300 hover:border-base-content/30"
      }`}
    >
      <div className="flex items-center justify-between px-3 pt-3">
        <span className="text-sm font-medium capitalize">{name}</span>
        {selected && <Check className="size-4 text-primary" />}
      </div>
      <div className="flex gap-1 p-3">
        <span className="h-6 w-full rounded bg-primary" />
        <span className="h-6 w-full rounded bg-secondary" />
        <span className="h-6 w-full rounded bg-accent" />
        <span className="h-6 w-full rounded bg-neutral" />
      </div>
    </button>
  );
}
