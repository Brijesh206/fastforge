"use client";

import { SubscriptionCard } from "@/components/subscription-card";
import { VerifyEmailNotice } from "@/components/verify-email-notice";
import { useSession } from "@/providers/session-provider";

export default function DashboardPage() {
  const { user } = useSession();
  const firstName = user?.full_name?.split(" ")[0] ?? "there";

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Welcome back, {firstName}</h1>
        <p className="mt-1 text-muted-foreground">
          Here&apos;s an overview of your account.
        </p>
      </div>

      <VerifyEmailNotice />

      <SubscriptionCard />
    </div>
  );
}
