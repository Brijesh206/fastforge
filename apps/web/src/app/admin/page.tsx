"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CreditCard, TrendingUp, Users } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useCountUp } from "@/hooks/use-count-up";
import { api } from "@/lib/api";
import type { AdminStats } from "@/lib/types";

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    api.admin.stats().then(setStats).catch(() => setError(true));
  }, []);

  return (
    <div className="mx-auto max-w-5xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">Overview</h1>
        <p className="text-sm text-muted-foreground">Users and subscriptions at a glance.</p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive">
          Couldn&apos;t load stats. Is the API running?
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          index={0}
          label="Total users"
          value={stats?.total_users}
          icon={<Users className="size-5" />}
          color="var(--color-chart-1)"
        />
        <StatCard
          index={1}
          label="Active subscriptions"
          value={stats?.active_subscriptions}
          icon={<TrendingUp className="size-5" />}
          color="var(--color-chart-5)"
        />
        <StatCard
          index={2}
          label="Total subscriptions"
          value={stats?.total_subscriptions}
          icon={<CreditCard className="size-5" />}
          color="var(--color-chart-2)"
        />
      </div>

      <div className="mt-8 flex gap-2">
        <Button asChild size="sm">
          <Link href="/admin/users">Manage users</Link>
        </Button>
        <Button asChild variant="outline" size="sm">
          <Link href="/admin/analytics">View analytics</Link>
        </Button>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  color,
  index,
}: {
  label: string;
  value: number | undefined;
  icon: React.ReactNode;
  color: string;
  index: number;
}) {
  const animated = useCountUp(value ?? 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06, duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
    >
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardContent className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">{label}</span>
            <span
              className="grid size-9 place-items-center rounded-lg"
              style={{
                backgroundColor: `color-mix(in oklab, ${color} 14%, transparent)`,
                color,
              }}
            >
              {icon}
            </span>
          </div>
          {value === undefined ? (
            <Skeleton className="h-9 w-20" />
          ) : (
            <span className="block text-3xl font-semibold tracking-tight">
              {Math.round(animated).toLocaleString()}
            </span>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
