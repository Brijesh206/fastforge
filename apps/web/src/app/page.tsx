import Link from "next/link";
import {
  Check,
  Code2,
  CreditCard,
  Mail,
  ShieldCheck,
  Sparkles,
  Zap,
} from "lucide-react";

import { CheckoutButton } from "@/components/checkout-button";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { APP_NAME } from "@/lib/config";

const features = [
  {
    icon: ShieldCheck,
    title: "Authentication built in",
    body: "Secure sign-up, login, email verification, and password reset — argon2 hashing and JWT sessions out of the box.",
  },
  {
    icon: CreditCard,
    title: "Subscription billing",
    body: "Stripe checkout, a self-service billing portal, and webhook-synced subscription state, ready to charge on day one.",
  },
  {
    icon: Mail,
    title: "Transactional email",
    body: "Verification and reset emails wired through a provider-agnostic mail layer. Swap providers without touching your app.",
  },
  {
    icon: Zap,
    title: "Production-ready API",
    body: "A FastAPI backend with clean architecture, structured logging, and migrations — built to scale past the prototype.",
  },
  {
    icon: Code2,
    title: "Type-safe end to end",
    body: "Pydantic on the server, TypeScript on the client, strict mypy and lint gates in CI. Refactor with confidence.",
  },
  {
    icon: Sparkles,
    title: "Yours to rebrand",
    body: "Design tokens, a wordmark, and copy you control. Make it your product in an afternoon, not a sprint.",
  },
];

const proFeatures = [
  "Everything in Free",
  "Unlimited projects",
  "Subscription billing portal",
  "Priority email support",
  "Early access to new features",
];

export default function LandingPage() {
  return (
    <div className="flex min-h-dvh flex-col">
      <SiteHeader />

      <main className="flex-1">
        {/* Hero */}
        <section className="mx-auto max-w-6xl px-4 py-20 text-center sm:py-28">
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3 py-1 text-sm font-medium text-muted-foreground">
            <Sparkles className="h-4 w-4 text-accent" />
            The SaaS foundation that ships itself
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-4xl font-bold leading-tight text-foreground sm:text-5xl md:text-6xl">
            Launch your product, not your boilerplate
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            {APP_NAME} gives you authentication, subscription billing, and a
            polished dashboard from the first commit — so you can spend your time
            on the thing only you can build.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/signup">Get started free</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="#pricing">View pricing</Link>
            </Button>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="border-t border-border bg-card/50">
          <div className="mx-auto max-w-6xl px-4 py-20">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold sm:text-4xl">
                Everything a SaaS needs on day one
              </h2>
              <p className="mt-4 text-muted-foreground">
                The unglamorous 80% is already done, tested, and wired together.
              </p>
            </div>
            <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {features.map(({ icon: Icon, title, body }) => (
                <Card key={title}>
                  <CardContent className="pt-6">
                    <div className="flex h-11 w-11 items-center justify-center rounded-md bg-primary/10 text-primary">
                      <Icon className="h-6 w-6" />
                    </div>
                    <h3 className="mt-4 text-lg font-semibold">{title}</h3>
                    <p className="mt-2 text-sm text-muted-foreground">{body}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="border-t border-border">
          <div className="mx-auto max-w-6xl px-4 py-20">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold sm:text-4xl">
                Simple, transparent pricing
              </h2>
              <p className="mt-4 text-muted-foreground">
                Start free. Upgrade when you&apos;re ready to grow.
              </p>
            </div>

            <div className="mx-auto mt-14 grid max-w-4xl gap-6 md:grid-cols-2">
              {/* Free */}
              <Card className="flex flex-col">
                <CardContent className="flex flex-1 flex-col pt-8">
                  <h3 className="text-lg font-semibold">Free</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    For trying things out and small side projects.
                  </p>
                  <p className="mt-6">
                    <span className="text-4xl font-bold">$0</span>
                    <span className="text-muted-foreground"> / month</span>
                  </p>
                  <ul className="mt-6 flex-1 space-y-3 text-sm">
                    {["1 project", "Email verification", "Community support"].map(
                      (item) => (
                        <li key={item} className="flex items-start gap-2">
                          <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
                          {item}
                        </li>
                      ),
                    )}
                  </ul>
                  <Button asChild variant="outline" className="mt-8 w-full">
                    <Link href="/signup">Get started</Link>
                  </Button>
                </CardContent>
              </Card>

              {/* Pro */}
              <Card className="relative flex flex-col border-primary shadow-md">
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
                  Most popular
                </span>
                <CardContent className="flex flex-1 flex-col pt-8">
                  <h3 className="text-lg font-semibold">Pro</h3>
                  <p className="mt-2 text-sm text-muted-foreground">
                    For teams shipping a real product to real customers.
                  </p>
                  <p className="mt-6">
                    <span className="text-4xl font-bold">$20</span>
                    <span className="text-muted-foreground"> / month</span>
                  </p>
                  <ul className="mt-6 flex-1 space-y-3 text-sm">
                    {proFeatures.map((item) => (
                      <li key={item} className="flex items-start gap-2">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent" />
                        {item}
                      </li>
                    ))}
                  </ul>
                  <CheckoutButton variant="accent" className="mt-8 w-full">
                    Subscribe to Pro
                  </CheckoutButton>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
