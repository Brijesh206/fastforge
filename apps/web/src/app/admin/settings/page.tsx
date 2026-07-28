"use client";

import { Check, Moon, Sun } from "lucide-react";

import { useAdminTheme, type AdminTheme } from "@/app/admin/theme";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const OPTIONS: { name: AdminTheme; icon: React.ReactNode }[] = [
  { name: "light", icon: <Sun className="size-4" /> },
  { name: "dark", icon: <Moon className="size-4" /> },
];

export default function AdminSettingsPage() {
  const { theme, toggle } = useAdminTheme();

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="text-sm text-muted-foreground">Personalize the admin panel.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Appearance</CardTitle>
          <CardDescription>
            Applies to the admin panel only. Saved to this browser.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid max-w-md grid-cols-2 gap-3">
            {OPTIONS.map((option) => (
              <button
                key={option.name}
                type="button"
                onClick={() => {
                  if (theme !== option.name) toggle();
                }}
                aria-pressed={theme === option.name}
                className={cn(
                  "flex items-center justify-between rounded-lg border-2 px-4 py-3 text-left transition-colors",
                  theme === option.name
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-muted-foreground/40",
                )}
              >
                <span className="flex items-center gap-2 text-sm font-medium capitalize">
                  {option.icon}
                  {option.name}
                </span>
                {theme === option.name && <Check className="size-4 text-primary" />}
              </button>
            ))}
          </div>

          <p className="mt-4 text-sm text-muted-foreground">
            Adding a palette is one more{" "}
            <code className="rounded bg-muted px-1 font-mono text-xs">
              .ff-admin[data-theme=&quot;…&quot;]
            </code>{" "}
            block in <span className="font-mono text-xs">globals.css</span>.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
