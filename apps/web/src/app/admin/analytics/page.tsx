"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ArrowDownRight,
  ArrowUpRight,
  CreditCard,
  TrendingDown,
  Users,
  Wallet,
} from "lucide-react";

import {
  ChannelDonut,
  Sparkline,
  StatusBars,
  TrendChart,
} from "@/app/admin/analytics/charts";
import { buildAnalytics, type Analytics, type Metric } from "@/app/admin/analytics/mock";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { UserAvatar } from "@/components/user-avatar";
import { useCountUp } from "@/hooks/use-count-up";
import { cn } from "@/lib/utils";

const RANGES = [7, 30, 90];

const money = (value: number) => `$${Math.round(value).toLocaleString()}`;
const count = (value: number) => Math.round(value).toLocaleString();
const percent = (value: number) => `${value.toFixed(1)}%`;

/** Shared entrance for every card. `custom` carries the stagger index so the
 *  delay lives with the animation rather than in a style attribute. */
const rise = {
  hidden: { opacity: 0, y: 14 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.06, duration: 0.45, ease: [0.16, 1, 0.3, 1] as const },
  }),
};

function Rise({
  index = 0,
  className,
  children,
}: {
  index?: number;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <motion.div
      variants={rise}
      initial="hidden"
      animate="show"
      custom={index}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export default function AdminAnalyticsPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<Analytics | null>(null);

  // Built after mount rather than during render: the series is anchored to
  // today's date, and generating it on the server too would risk a hydration
  // mismatch across a midnight boundary. Also mirrors the shape of the real
  // fetch this becomes.
  useEffect(() => {
    setData(buildAnalytics(days));
  }, [days]);

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <Rise className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-sm text-muted-foreground">
            Growth, revenue and subscription health.
          </p>
        </div>

        {/* One filter row scoping every chart below — never per-card filters. */}
        <div
          role="group"
          aria-label="Time range"
          className="inline-flex rounded-lg border border-border bg-card p-1"
        >
          {RANGES.map((range) => (
            <button
              key={range}
              type="button"
              onClick={() => setDays(range)}
              aria-pressed={days === range}
              className={cn(
                "relative rounded-md px-3 py-1 text-sm font-medium transition-colors",
                days === range
                  ? "text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              {days === range && (
                <motion.span
                  layoutId="range-pill"
                  className="absolute inset-0 rounded-md bg-primary"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                />
              )}
              <span className="relative">{range}d</span>
            </button>
          ))}
        </div>
      </Rise>

      <Rise index={1}>
        <Card className="border-primary/20 bg-primary/5 py-3">
          <CardContent className="text-sm text-muted-foreground">
            Showing sample data. Wire{" "}
            <code className="rounded bg-muted px-1 font-mono text-xs">buildAnalytics()</code>{" "}
            to a real endpoint to go live.
          </CardContent>
        </Card>
      </Rise>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          index={2}
          label="Total users"
          metric={data?.users}
          format={count}
          icon={<Users className="size-5" />}
          color="var(--color-chart-1)"
        />
        <StatTile
          index={3}
          label="Active subscriptions"
          metric={data?.activeSubscriptions}
          format={count}
          icon={<CreditCard className="size-5" />}
          color="var(--color-chart-2)"
        />
        <StatTile
          index={4}
          label="MRR"
          metric={data?.mrr}
          format={money}
          icon={<Wallet className="size-5" />}
          color="var(--color-chart-5)"
        />
        {/* Churn falling is good, so the arrow's meaning is inverted here. */}
        <StatTile
          index={5}
          label="Churn rate"
          metric={data?.churnRate}
          format={percent}
          icon={<TrendingDown className="size-5" />}
          color="var(--color-chart-3)"
          lowerIsBetter
        />
      </div>

      {/* Two charts, never one dual-axis plot: signups and MRR have
          incompatible scales and pairing them would invent a correlation. */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Rise index={6}>
          <ChartCard
            title="Signups per day"
            value={data ? count(data.signups[data.signups.length - 1].value) : undefined}
          >
            {data ? (
              <TrendChart points={data.signups} label="Signups" format={count} />
            ) : (
              <Skeleton className="h-[220px] w-full" />
            )}
          </ChartCard>
        </Rise>

        <Rise index={7}>
          <ChartCard
            title="MRR"
            value={data ? money(data.mrrSeries[data.mrrSeries.length - 1].value) : undefined}
          >
            {data ? (
              <TrendChart
                points={data.mrrSeries}
                label="MRR"
                format={money}
                variant="line"
                color="var(--color-chart-5)"
              />
            ) : (
              <Skeleton className="h-[220px] w-full" />
            )}
          </ChartCard>
        </Rise>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Rise index={8} className="lg:col-span-3">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-base">Signups by channel</CardTitle>
            </CardHeader>
            <CardContent>
              {data ? (
                <ChannelDonut channels={data.channels} />
              ) : (
                <Skeleton className="h-44 w-full" />
              )}
            </CardContent>
          </Card>
        </Rise>

        <Rise index={9} className="lg:col-span-2">
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="text-base">Subscriptions by status</CardTitle>
            </CardHeader>
            <CardContent>
              {data ? <StatusBars slices={data.statuses} /> : <Skeleton className="h-44 w-full" />}
            </CardContent>
          </Card>
        </Rise>
      </div>

      <Rise index={10}>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent signups</CardTitle>
          </CardHeader>
          <CardContent>
            {data ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>User</TableHead>
                    <TableHead>Plan</TableHead>
                    <TableHead className="text-right">Joined</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.recentSignups.map((user) => (
                    <TableRow key={user.email}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <UserAvatar
                            src={null}
                            name={user.name}
                            email={user.email}
                            className="size-8"
                          />
                          <div className="min-w-0">
                            <div className="truncate font-medium">{user.name}</div>
                            <div className="truncate text-xs text-muted-foreground">
                              {user.email}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={user.plan === "Pro" ? "default" : "outline"}>
                          {user.plan}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right text-muted-foreground">
                        {user.joinedDaysAgo === 0
                          ? "Today"
                          : user.joinedDaysAgo === 1
                            ? "Yesterday"
                            : `${user.joinedDaysAgo} days ago`}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <Skeleton className="h-52 w-full" />
            )}
          </CardContent>
        </Card>
      </Rise>
    </div>
  );
}

function ChartCard({
  title,
  value,
  children,
}: {
  title: string;
  value: string | undefined;
  children: React.ReactNode;
}) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {value === undefined ? (
          <Skeleton className="h-8 w-24" />
        ) : (
          <div className="text-2xl font-semibold">{value}</div>
        )}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

function StatTile({
  label,
  metric,
  format,
  icon,
  color,
  lowerIsBetter = false,
  index,
}: {
  label: string;
  metric: Metric | undefined;
  format: (value: number) => string;
  icon: React.ReactNode;
  color: string;
  lowerIsBetter?: boolean;
  index: number;
}) {
  // Hooks can't sit behind the loading branch, so the count-up runs against 0
  // until the data lands and then animates to the real figure.
  const animated = useCountUp(metric?.value ?? 0);

  // A delta that rounds to 0.0% is neither good nor bad — colouring it red
  // and pointing an arrow at it invents a trend that isn't there.
  const flat = metric !== undefined && Math.abs(metric.delta) < 0.0005;
  const rising = (metric?.delta ?? 0) >= 0;
  const good = lowerIsBetter ? !rising : rising;
  const Arrow = rising ? ArrowUpRight : ArrowDownRight;

  return (
    <Rise index={index}>
      <Card className="h-full gap-0 overflow-hidden py-0 transition-shadow hover:shadow-md">
        <CardContent className="space-y-3 p-5 pb-0">
          <div className="flex items-start justify-between gap-3">
            <span
              className="grid size-10 place-items-center rounded-xl"
              style={{ backgroundColor: `color-mix(in oklab, ${color} 14%, transparent)`, color }}
            >
              {icon}
            </span>

            {metric !== undefined &&
              (flat ? (
                <Badge variant="outline">No change</Badge>
              ) : (
                <Badge variant={good ? "success" : "destructive"}>
                  <Arrow className="size-3" aria-hidden="true" />
                  <span className="tabular-nums">
                    {Math.abs(metric.delta * 100).toFixed(1)}%
                  </span>
                </Badge>
              ))}
          </div>

          <div>
            <div className="text-sm text-muted-foreground">{label}</div>
            {metric === undefined ? (
              <Skeleton className="mt-1 h-8 w-24" />
            ) : (
              // Proportional figures, not tabular-nums: equal-width digits read
              // loose at display sizes.
              <div className="mt-0.5 text-3xl font-semibold tracking-tight">
                {format(animated)}
              </div>
            )}
          </div>
        </CardContent>

        {metric === undefined ? (
          <Skeleton className="m-5 mt-3 h-12" />
        ) : (
          <Sparkline points={metric.series} color={color} />
        )}
      </Card>
    </Rise>
  );
}
