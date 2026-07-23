"use client";

import { useCallback, useEffect, useState } from "react";
import { Search } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import type { AdminUserItem, AdminUserList } from "@/lib/types";
import { UserDetailModal } from "@/app/admin/users/user-detail-modal";

const PAGE_SIZE = 20;

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export default function AdminUsersPage() {
  const [data, setData] = useState<AdminUserList | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [qInput, setQInput] = useState("");
  const [q, setQ] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  // Debounce the search field; reset to page 1 when the query changes.
  useEffect(() => {
    const t = setTimeout(() => {
      setQ(qInput.trim());
      setPage(1);
    }, 350);
    return () => clearTimeout(t);
  }, [qInput]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setData(await api.admin.users({ page, pageSize: PAGE_SIZE, q }));
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [page, q]);

  useEffect(() => {
    void load();
  }, [load]);

  function showToast(message: string) {
    setToast(message);
    setTimeout(() => setToast(null), 3000);
  }

  // Reflect a status change from a row action or the modal into the table.
  function applyUpdate(updated: AdminUserItem) {
    setData((current) =>
      current
        ? { ...current, items: current.items.map((u) => (u.id === updated.id ? { ...u, ...updated } : u)) }
        : current,
    );
  }

  async function toggleActive(user: AdminUserItem) {
    try {
      const updated = user.is_active
        ? await api.admin.deactivate(user.id)
        : await api.admin.activate(user.id);
      applyUpdate(updated);
    } catch (error) {
      showToast(error instanceof ApiError ? error.message : "Action failed.");
    }
  }

  const items = data?.items ?? [];
  const totalPages = data?.total_pages ?? 1;

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Users</h1>
          <p className="text-sm opacity-60">
            {data ? `${data.total.toLocaleString()} total` : "Loading…"}
          </p>
        </div>
        <label className="input input-bordered flex items-center gap-2">
          <Search className="size-4 opacity-50" />
          <input
            type="search"
            className="grow"
            placeholder="Search by email"
            value={qInput}
            onChange={(e) => setQInput(e.target.value)}
          />
        </label>
      </div>

      <div className="overflow-x-auto rounded-box border border-base-300 bg-base-200">
        <table className="table">
          <thead>
            <tr>
              <th>User</th>
              <th>Status</th>
              <th>Joined</th>
              <th className="text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={4} className="py-10 text-center">
                  <span className="loading loading-spinner loading-md text-primary" />
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td colSpan={4} className="py-10 text-center opacity-60">
                  No users found.
                </td>
              </tr>
            ) : (
              items.map((user) => (
                <tr key={user.id} className="hover">
                  <td>
                    <button
                      className="text-left"
                      onClick={() => setSelectedId(user.id)}
                    >
                      <div className="font-medium hover:underline">{user.email}</div>
                      {user.full_name && (
                        <div className="text-xs opacity-60">{user.full_name}</div>
                      )}
                    </button>
                  </td>
                  <td>
                    <div className="flex flex-wrap gap-1">
                      <span
                        className={`badge badge-sm ${user.is_active ? "badge-success" : "badge-ghost"}`}
                      >
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                      {user.is_verified ? (
                        <span className="badge badge-sm badge-outline">Verified</span>
                      ) : (
                        <span className="badge badge-sm badge-warning badge-outline">Unverified</span>
                      )}
                    </div>
                  </td>
                  <td className="text-sm opacity-70">{formatDate(user.created_at)}</td>
                  <td>
                    <div className="flex justify-end gap-2">
                      <button className="btn btn-ghost btn-xs" onClick={() => setSelectedId(user.id)}>
                        View
                      </button>
                      <button
                        className={`btn btn-xs ${user.is_active ? "btn-error btn-outline" : "btn-success btn-outline"}`}
                        onClick={() => toggleActive(user)}
                      >
                        {user.is_active ? "Deactivate" : "Activate"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <span className="text-sm opacity-60">
            Page {page} of {totalPages}
          </span>
          <div className="join">
            <button
              className="btn btn-sm join-item"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Prev
            </button>
            <button
              className="btn btn-sm join-item"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {selectedId && (
        <UserDetailModal
          userId={selectedId}
          onClose={() => setSelectedId(null)}
          onUpdated={applyUpdate}
          onError={showToast}
        />
      )}

      {toast && (
        <div className="toast toast-end z-50">
          <div className="alert alert-error">
            <span>{toast}</span>
          </div>
        </div>
      )}
    </div>
  );
}
