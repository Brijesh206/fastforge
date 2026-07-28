"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { api, ApiError } from "@/lib/api";
import type { AdminUserDetail, AdminUserItem } from "@/lib/types";

function formatDateTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function UserDetailModal({
  userId,
  onClose,
  onUpdated,
  onError,
}: {
  userId: string;
  onClose: () => void;
  onUpdated: (user: AdminUserItem) => void;
  onError: (message: string) => void;
}) {
  const [user, setUser] = useState<AdminUserDetail | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    api.admin
      .user(userId)
      .then((u) => active && setUser(u))
      .catch(() => active && onError("Couldn't load user."));
    return () => {
      active = false;
    };
  }, [userId, onError]);

  async function toggleActive() {
    if (!user) return;
    setBusy(true);
    try {
      const updated = user.is_active
        ? await api.admin.deactivate(user.id)
        : await api.admin.activate(user.id);
      setUser({ ...user, is_active: updated.is_active });
      onUpdated(updated);
    } catch (error) {
      onError(error instanceof ApiError ? error.message : "Action failed.");
    } finally {
      setBusy(false);
    }
  }

  const sub = user?.subscription;

  return (
    <Sheet open onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-lg">
        <SheetHeader>
          <SheetTitle>User detail</SheetTitle>
          <SheetDescription>{user?.email ?? "Loading…"}</SheetDescription>
        </SheetHeader>

        {!user ? (
          <div className="flex min-h-32 items-center justify-center">
            <Loader2 className="size-5 animate-spin text-primary" />
          </div>
        ) : (
          <div className="space-y-6 px-4 pb-4">
            <section className="grid grid-cols-2 gap-4 text-sm">
              <Field label="Name" value={user.full_name ?? "—"} />
              <Field label="User ID" value={user.id} mono />
              <Field
                label="Status"
                value={
                  <Badge variant={user.is_active ? "success" : "secondary"}>
                    {user.is_active ? "Active" : "Inactive"}
                  </Badge>
                }
              />
              <Field
                label="Email verified"
                value={
                  <Badge variant={user.is_verified ? "outline" : "warning"}>
                    {user.is_verified ? "Yes" : "No"}
                  </Badge>
                }
              />
              <Field label="Joined" value={formatDateTime(user.created_at)} />
              <Field label="Last login" value={formatDateTime(user.last_login_at)} />
            </section>

            <section>
              <h4 className="mb-2 text-sm font-medium text-muted-foreground">Subscription</h4>
              {sub ? (
                <div className="rounded-lg border border-border bg-muted/40 p-4 text-sm">
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <Badge variant={sub.is_active ? "success" : "secondary"}>
                      {sub.status ?? "none"}
                    </Badge>
                    {sub.cancel_at_period_end && (
                      <Badge variant="warning">Cancels at period end</Badge>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <Field label="Renews / ends" value={formatDateTime(sub.current_period_end)} />
                    <Field label="Price ID" value={sub.price_id ?? "—"} mono />
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No subscription.</p>
              )}
            </section>

            <Button
              variant={user.is_active ? "outline" : "primary"}
              className={user.is_active ? "text-destructive hover:text-destructive" : ""}
              onClick={toggleActive}
              disabled={busy}
            >
              {busy && <Loader2 className="size-4 animate-spin" />}
              {user.is_active ? "Deactivate user" : "Activate user"}
            </Button>
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Field({
  label,
  value,
  mono,
}: {
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className={mono ? "mt-0.5 truncate font-mono text-xs" : "mt-0.5"}>{value}</div>
    </div>
  );
}
