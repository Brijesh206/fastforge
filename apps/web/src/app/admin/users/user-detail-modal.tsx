"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";

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
    <dialog className="modal modal-open" onClose={onClose}>
      <div className="modal-box max-w-lg">
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 className="text-lg font-semibold">User detail</h3>
            {user && <p className="text-sm opacity-60">{user.email}</p>}
          </div>
          <button className="btn btn-square btn-ghost btn-sm" onClick={onClose} aria-label="Close">
            <X className="size-4" />
          </button>
        </div>

        {!user ? (
          <div className="flex min-h-32 items-center justify-center">
            <span className="loading loading-spinner loading-md text-primary" />
          </div>
        ) : (
          <div className="space-y-5">
            <section className="grid grid-cols-2 gap-3 text-sm">
              <Field label="Name" value={user.full_name ?? "—"} />
              <Field label="User ID" value={user.id} mono />
              <Field
                label="Status"
                value={
                  <span className={`badge badge-sm ${user.is_active ? "badge-success" : "badge-ghost"}`}>
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                }
              />
              <Field
                label="Email verified"
                value={
                  <span className={`badge badge-sm ${user.is_verified ? "badge-outline" : "badge-warning badge-outline"}`}>
                    {user.is_verified ? "Yes" : "No"}
                  </span>
                }
              />
              <Field label="Joined" value={formatDateTime(user.created_at)} />
              <Field label="Last login" value={formatDateTime(user.last_login_at)} />
            </section>

            <section>
              <h4 className="mb-2 text-sm font-medium opacity-70">Subscription</h4>
              {sub ? (
                <div className="rounded-box border border-base-300 bg-base-200 p-3 text-sm">
                  <div className="mb-2 flex items-center gap-2">
                    <span className={`badge badge-sm ${sub.is_active ? "badge-success" : "badge-ghost"}`}>
                      {sub.status ?? "none"}
                    </span>
                    {sub.cancel_at_period_end && (
                      <span className="badge badge-sm badge-warning badge-outline">Cancels at period end</span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-2 opacity-80">
                    <Field label="Renews / ends" value={formatDateTime(sub.current_period_end)} />
                    <Field label="Price ID" value={sub.price_id ?? "—"} mono />
                  </div>
                </div>
              ) : (
                <p className="text-sm opacity-60">No subscription.</p>
              )}
            </section>

            <div className="modal-action">
              <button
                className={`btn btn-sm ${user.is_active ? "btn-error btn-outline" : "btn-success"}`}
                onClick={toggleActive}
                disabled={busy}
              >
                {busy && <span className="loading loading-spinner loading-xs" />}
                {user.is_active ? "Deactivate user" : "Activate user"}
              </button>
            </div>
          </div>
        )}
      </div>
      <button className="modal-backdrop" onClick={onClose}>
        close
      </button>
    </dialog>
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
      <div className="text-xs uppercase tracking-wide opacity-50">{label}</div>
      <div className={`mt-0.5 ${mono ? "truncate font-mono text-xs" : ""}`}>{value}</div>
    </div>
  );
}
