"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useRef, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { api } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

type Status = "verifying" | "success" | "error" | "missing";

function VerifyEmailInner() {
  const token = useSearchParams().get("token") ?? "";
  const { refresh } = useSession();
  const [status, setStatus] = useState<Status>(token ? "verifying" : "missing");
  const started = useRef(false);

  useEffect(() => {
    if (!token || started.current) return;
    started.current = true; // StrictMode double-invoke guard — token is single-use.
    api
      .verifyEmail(token)
      .then(async () => {
        setStatus("success");
        await refresh();
      })
      .catch(() => setStatus("error"));
  }, [token, refresh]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Email verification</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {status === "verifying" && (
          <div className="flex items-center gap-3 text-muted-foreground">
            <Spinner className="h-5 w-5" />
            Verifying your email…
          </div>
        )}

        {status === "success" && (
          <>
            <Alert variant="success">
              Your email is verified. Your account is now fully active.
            </Alert>
            <Button asChild className="w-full">
              <Link href="/dashboard">Go to dashboard</Link>
            </Button>
          </>
        )}

        {status === "error" && (
          <>
            <Alert variant="error">
              This verification link is invalid or has expired. Log in and
              request a new one from your dashboard.
            </Alert>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Go to log in</Link>
            </Button>
          </>
        )}

        {status === "missing" && (
          <Alert variant="error">This link is missing its token.</Alert>
        )}
      </CardContent>
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense>
      <VerifyEmailInner />
    </Suspense>
  );
}
