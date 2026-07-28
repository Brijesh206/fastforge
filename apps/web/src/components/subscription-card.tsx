"use client";

import { useEffect, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import type { Subscription } from "@/lib/types";

function statusBadge(sub: Subscription) {
  if (sub.is_active) return <Badge variant="success">Active</Badge>;
  if (!sub.status) return <Badge variant="secondary">No plan</Badge>;
  if (sub.status === "past_due" || sub.status === "unpaid")
    return <Badge variant="warning">Payment due</Badge>;
  return <Badge variant="destructive">Canceled</Badge>;
}

function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

export function SubscriptionCard() {
  const [sub, setSub] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [redirecting, setRedirecting] = useState(false);

  useEffect(() => {
    api
      .getSubscription()
      .then(setSub)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  async function goToStripe(action: "checkout" | "portal") {
    setRedirecting(true);
    try {
      const { url } =
        action === "checkout"
          ? await api.startCheckout()
          : await api.openPortal();
      window.location.href = url;
    } catch {
      setRedirecting(false);
      setError(true);
    }
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Subscription</CardTitle>
          {sub && statusBadge(sub)}
        </div>
        <CardDescription>Manage your plan and billing.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        {loading ? (
          <div className="flex items-center gap-3 text-muted-foreground">
            <Spinner className="h-5 w-5" />
            Loading your subscription…
          </div>
        ) : error ? (
          <Alert variant="error">
            We couldn&apos;t load your subscription. Please try again.
          </Alert>
        ) : sub?.is_active ? (
          <>
            <dl className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-muted-foreground">Plan</dt>
                <dd className="font-medium">Pro</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">
                  {sub.cancel_at_period_end ? "Ends on" : "Renews on"}
                </dt>
                <dd className="font-medium">
                  {formatDate(sub.current_period_end)}
                </dd>
              </div>
            </dl>
            {sub.cancel_at_period_end && (
              <Alert variant="info">
                Your plan is set to cancel at the end of the current period.
              </Alert>
            )}
            <Button
              variant="outline"
              onClick={() => goToStripe("portal")}
              loading={redirecting}
            >
              Manage billing
            </Button>
          </>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">
              You&apos;re on the Free plan. Upgrade to Pro for the full feature
              set.
            </p>
            <Button
              onClick={() => goToStripe("checkout")}
              loading={redirecting}
            >
              Upgrade to Pro — $20/mo
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
