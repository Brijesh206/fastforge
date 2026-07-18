"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { CreditCard, TrendingUp, Users } from "lucide-react";

import { api } from "@/lib/api";
import type { AdminStats } from "@/lib/types";

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.admin
      .stats()
      .then(setStats)
      .catch(() => setError(true));
  }, []);

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Overview</h1>
        <p className="text-sm opacity-60">Users and subscriptions at a glance.</p>
      </div>

      {error && (
        <div className="alert alert-error mb-6">
          <span>Couldn&apos;t load stats. Is the API running?</span>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          label="Total users"
          value={stats?.total_users}
          icon={<Users className="size-5" />}
          accent="text-primary"
        />
        <StatCard
          label="Active subscriptions"
          value={stats?.active_subscriptions}
          icon={<TrendingUp className="size-5" />}
          accent="text-success"
        />
        <StatCard
          label="Total subscriptions"
          value={stats?.total_subscriptions}
          icon={<CreditCard className="size-5" />}
          accent="text-info"
        />
      </div>

      <div className="mt-8">
        <Link href="/admin/users" className="btn btn-primary btn-sm">
          Manage users
        </Link>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  accent,
}: {
  label: string;
  value: number | undefined;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div className="card border border-base-300 bg-base-200">
      <div className="card-body gap-3 p-5">
        <div className="flex items-center justify-between">
          <span className="text-sm opacity-60">{label}</span>
          <span className={accent}>{icon}</span>
        </div>
        {value === undefined ? (
          <span className="skeleton h-9 w-16" />
        ) : (
          <span className="text-3xl font-semibold tabular-nums">{value.toLocaleString()}</span>
        )}
      </div>
    </div>
  );
}
