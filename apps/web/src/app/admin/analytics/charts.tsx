"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from "recharts";

import type { Channel, Point, StatusSlice } from "@/app/admin/analytics/mock";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

function shortDate(iso: string): string {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    timeZone: "UTC",
  });
}

/** Trend over time. Area for a single accumulating series, line for a rate —
 *  never two series on two y-scales, which is what makes a dual-axis chart
 *  invent a correlation that isn't in the data. */
export function TrendChart({
  points,
  label,
  format,
  variant = "area",
  color = "var(--color-chart-1)",
}: {
  points: Point[];
  label: string;
  format: (value: number) => string;
  variant?: "area" | "line";
  color?: string;
}) {
  const config = { value: { label, color } } satisfies ChartConfig;
  const data = points.map((p) => ({ ...p, label: shortDate(p.date) }));

  const axes = (
    <>
      <CartesianGrid vertical={false} strokeDasharray="0" className="stroke-border" />
      <XAxis
        dataKey="label"
        tickLine={false}
        axisLine={false}
        tickMargin={10}
        minTickGap={40}
        className="text-xs"
      />
      <YAxis
        tickLine={false}
        axisLine={false}
        width={48}
        tickFormatter={format}
        className="text-xs"
      />
      <ChartTooltip
        cursor={{ strokeDasharray: "0" }}
        content={<ChartTooltipContent formatter={(value) => format(Number(value))} />}
      />
    </>
  );

  return (
    <ChartContainer config={config} className="h-[220px] w-full">
      {variant === "area" ? (
        <AreaChart data={data} margin={{ left: 4, right: 8, top: 8 }}>
          <defs>
            <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity={0.3} />
              <stop offset="100%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          {axes}
          <Area
            dataKey="value"
            type="monotone"
            stroke={color}
            strokeWidth={2}
            fill="url(#trend-fill)"
            // Recharts' own entrance animation — the equivalent of the CSS
            // line-draw, but it also knows the path geometry.
            animationDuration={900}
          />
        </AreaChart>
      ) : (
        <LineChart data={data} margin={{ left: 4, right: 8, top: 8 }}>
          {axes}
          <Line
            dataKey="value"
            type="monotone"
            stroke={color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
            animationDuration={900}
          />
        </LineChart>
      )}
    </ChartContainer>
  );
}

/** Bare trend line for a stat tile. No axes, no tooltip: the tile already
 *  shows the value and delta as text, so nothing is gated behind a pointer. */
export function Sparkline({ points, color }: { points: Point[]; color: string }) {
  const config = { value: { label: "Trend", color } } satisfies ChartConfig;
  const gradientId = `spark-${color.replace(/[^a-z0-9]/gi, "")}`;

  return (
    <ChartContainer config={config} className="h-12 w-full">
      <AreaChart data={points} margin={{ top: 2, bottom: 2, left: 0, right: 0 }}>
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.28} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area
          dataKey="value"
          type="monotone"
          stroke={color}
          strokeWidth={2}
          fill={`url(#${gradientId})`}
          animationDuration={900}
        />
      </AreaChart>
    </ChartContainer>
  );
}

const SLICE_COLORS = [
  "var(--color-chart-1)",
  "var(--color-chart-2)",
  "var(--color-chart-3)",
  "var(--color-chart-4)",
  "var(--color-chart-5)",
];

/** Donut with a centre total and a text legend.
 *
 *  Capped at five slices including "Other" — past that adjacent segments stop
 *  being tellable apart, and the honest answer is a table. Every slice is
 *  repeated in the legend with its label, value and share, so identity never
 *  rests on colour alone. */
export function ChannelDonut({ channels }: { channels: Channel[] }) {
  const total = channels.reduce((sum, c) => sum + c.value, 0) || 1;
  const config = Object.fromEntries(
    channels.map((c, i) => [c.label, { label: c.label, color: SLICE_COLORS[i % SLICE_COLORS.length] }]),
  ) satisfies ChartConfig;

  return (
    <div className="flex flex-col items-center gap-6 sm:flex-row">
      <div className="relative shrink-0">
        <ChartContainer config={config} className="h-44 w-44">
          <PieChart>
            <ChartTooltip content={<ChartTooltipContent nameKey="label" hideLabel />} />
            <Pie
              data={channels}
              dataKey="value"
              nameKey="label"
              innerRadius="62%"
              outerRadius="100%"
              paddingAngle={2}
              strokeWidth={0}
              animationDuration={800}
            >
              {channels.map((channel, i) => (
                <Cell key={channel.label} fill={SLICE_COLORS[i % SLICE_COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ChartContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-semibold">{total.toLocaleString()}</span>
          <span className="text-xs text-muted-foreground">signups</span>
        </div>
      </div>

      <ul className="w-full space-y-2.5">
        {channels.map((channel, i) => (
          <li key={channel.label} className="flex items-center gap-2.5 text-sm">
            <span
              className="size-2.5 shrink-0 rounded-full"
              style={{ backgroundColor: SLICE_COLORS[i % SLICE_COLORS.length] }}
              aria-hidden="true"
            />
            <span className="flex-1 truncate text-muted-foreground">{channel.label}</span>
            <span className="tabular-nums">{channel.value.toLocaleString()}</span>
            <span className="w-9 text-right tabular-nums text-muted-foreground">
              {Math.round((channel.value / total) * 100)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const TONE_BAR: Record<StatusSlice["tone"], string> = {
  success: "bg-success",
  warning: "bg-warning",
  error: "bg-destructive",
};

/** Horizontal bars for subscription state. Status colours are correct here
 *  because these *are* states, and each carries a text label so the colour is
 *  never the only encoding. */
export function StatusBars({ slices }: { slices: StatusSlice[] }) {
  const total = slices.reduce((sum, s) => sum + s.value, 0) || 1;

  return (
    <ul className="space-y-4">
      {slices.map((slice) => (
        <li key={slice.label}>
          <div className="mb-1.5 flex items-baseline justify-between text-sm">
            <span className="text-muted-foreground">{slice.label}</span>
            <span className="tabular-nums">
              {slice.value.toLocaleString()}
              <span className="ml-2 text-muted-foreground">
                {Math.round((slice.value / total) * 100)}%
              </span>
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
            <div
              className={`ff-grow h-full rounded-full ${TONE_BAR[slice.tone]}`}
              style={{ width: `${(slice.value / total) * 100}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}
