/** Mock analytics data.
 *
 *  UI-first: the screens are built and reviewed against this before any
 *  backend exists. `buildAnalytics` is shaped like the response a future
 *  GET /admin/analytics would return, so swapping it for a real fetch is a
 *  one-line change in the page.
 *
 *  Seeded, not Math.random: an unseeded series would redraw differently on
 *  every render and every range switch, which makes the UI impossible to
 *  review and hides real bugs behind noise.
 */

export interface Point {
  /** ISO date, YYYY-MM-DD. */
  date: string;
  value: number;
}

export interface Metric {
  value: number;
  /** Fractional change vs the preceding window of equal length, e.g. 0.12 = +12%. */
  delta: number;
  series: Point[];
}

export interface StatusSlice {
  label: string;
  value: number;
  /** Maps to a daisyUI status colour — these are states, not identities. */
  tone: "success" | "warning" | "error";
}

export interface Channel {
  label: string;
  value: number;
}

export interface RecentSignup {
  name: string;
  email: string;
  plan: "Free" | "Pro";
  joinedDaysAgo: number;
}

export interface Analytics {
  users: Metric;
  activeSubscriptions: Metric;
  mrr: Metric;
  churnRate: Metric;
  signups: Point[];
  mrrSeries: Point[];
  statuses: StatusSlice[];
  /** Capped at four named sources plus "Other" — past that, adjacent slices
   *  stop being tellable apart and the honest answer is a table. */
  channels: Channel[];
  recentSignups: RecentSignup[];
}

/** mulberry32 — small, fast, and deterministic for a given seed. */
function seeded(seed: number): () => number {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function isoDaysAgo(n: number): string {
  const d = new Date();
  d.setUTCHours(0, 0, 0, 0);
  d.setUTCDate(d.getUTCDate() - n);
  return d.toISOString().slice(0, 10);
}

/** A rising series with weekly seasonality and mild noise. */
function series(days: number, seed: number, base: number, growth: number): Point[] {
  const rand = seeded(seed);
  return Array.from({ length: days }, (_, i) => {
    const trend = base + growth * i;
    // Weekends dip — without it the line reads as synthetic.
    const weekday = new Date(`${isoDaysAgo(days - 1 - i)}T00:00:00Z`).getUTCDay();
    const weekend = weekday === 0 || weekday === 6 ? 0.65 : 1;
    const noise = 0.82 + rand() * 0.36;
    return {
      date: isoDaysAgo(days - 1 - i),
      value: Math.max(0, Math.round(trend * weekend * noise)),
    };
  });
}

function sum(points: Point[]): number {
  return points.reduce((total, p) => total + p.value, 0);
}

/** Change vs the preceding window of the same length. */
function deltaOf(points: Point[]): number {
  const half = Math.floor(points.length / 2);
  if (half === 0) return 0;
  const previous = sum(points.slice(0, half));
  const current = sum(points.slice(half));
  if (previous === 0) return 0;
  return (current - previous) / previous;
}

export function buildAnalytics(days: number): Analytics {
  const signups = series(days, 11, 6, 0.32);
  const mrrSeries = series(days, 29, 420, 11);

  // Cumulative users: a running total reads as a stock, not a flow.
  let running = 1180;
  const userSeries = signups.map((p) => {
    running += p.value;
    return { date: p.date, value: running };
  });

  const activeSeries = series(days, 47, 74, 0.5);
  // Tenths of a percent, so the tile can render one decimal. Floored well
  // below the trend rather than at it — a clamp near the mean would flatten
  // every point to the same value and the sparkline would carry no signal.
  const churnSeries = series(days, 83, 34, -0.04).map((p) => ({
    date: p.date,
    value: Math.max(8, p.value),
  }));

  const latest = (points: Point[]) => points[points.length - 1]?.value ?? 0;
  const total = sum(signups);

  return {
    users: { value: latest(userSeries), delta: deltaOf(signups), series: userSeries },
    activeSubscriptions: {
      value: latest(activeSeries),
      delta: deltaOf(activeSeries),
      series: activeSeries,
    },
    mrr: { value: latest(mrrSeries), delta: deltaOf(mrrSeries), series: mrrSeries },
    churnRate: {
      value: latest(churnSeries) / 10,
      delta: deltaOf(churnSeries),
      series: churnSeries,
    },
    signups,
    mrrSeries,
    statuses: [
      { label: "Active", value: latest(activeSeries), tone: "success" },
      { label: "Past due", value: 9, tone: "warning" },
      { label: "Canceled", value: 31, tone: "error" },
    ],
    channels: [
      { label: "Organic search", value: Math.round(total * 0.34) },
      { label: "GitHub", value: Math.round(total * 0.26) },
      { label: "Referral", value: Math.round(total * 0.19) },
      { label: "Direct", value: Math.round(total * 0.13) },
      { label: "Other", value: Math.round(total * 0.08) },
    ],
    recentSignups: [
      { name: "Ada Lovelace", email: "ada@example.com", plan: "Pro", joinedDaysAgo: 0 },
      { name: "Grace Hopper", email: "grace@example.com", plan: "Pro", joinedDaysAgo: 0 },
      { name: "Alan Turing", email: "alan@example.com", plan: "Free", joinedDaysAgo: 1 },
      { name: "Katherine Johnson", email: "kj@example.com", plan: "Pro", joinedDaysAgo: 1 },
      { name: "Linus Torvalds", email: "linus@example.com", plan: "Free", joinedDaysAgo: 2 },
    ],
  };
}
