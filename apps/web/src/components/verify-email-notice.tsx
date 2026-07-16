"use client";

import { MailWarning } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

export function VerifyEmailNotice() {
  const { user } = useSession();
  const [sent, setSent] = useState(false);
  const [sending, setSending] = useState(false);

  if (!user || user.is_verified) return null;

  async function handleResend() {
    setSending(true);
    try {
      await api.resendVerification();
      setSent(true);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex flex-col gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-3">
        <MailWarning className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div>
          <p className="text-sm font-medium text-amber-900">
            Verify your email address
          </p>
          <p className="text-sm text-amber-700">
            {sent
              ? "Sent — check your inbox for the verification link."
              : "We sent a link to your inbox. Didn't get it?"}
          </p>
        </div>
      </div>
      {!sent && (
        <Button
          variant="outline"
          size="sm"
          onClick={handleResend}
          loading={sending}
          className="shrink-0 border-amber-300"
        >
          Resend email
        </Button>
      )}
    </div>
  );
}
