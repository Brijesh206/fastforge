"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { tokenStore } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

/** Lands here after an OAuth provider redirect. Tokens arrive in the URL
 *  fragment (not the query string) so they never hit server access logs. */
export default function OAuthCallbackPage() {
  const router = useRouter();
  const { refresh } = useSession();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");

    if (!accessToken || !refreshToken) {
      setFailed(true);
      return;
    }

    tokenStore.save({
      access_token: accessToken,
      refresh_token: refreshToken,
      token_type: "bearer",
    });
    // Drop the tokens from the visible URL/history before navigating on.
    window.history.replaceState(null, "", window.location.pathname);
    void refresh().then(() => router.replace("/dashboard"));
  }, [refresh, router]);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-2xl">Signing you in</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {failed ? (
          <>
            <Alert variant="error">Sign-in didn&apos;t complete. Please try again.</Alert>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Go to log in</Link>
            </Button>
          </>
        ) : (
          <div className="flex items-center gap-3 text-muted-foreground">
            <Spinner className="h-5 w-5" />
            Completing sign-in…
          </div>
        )}
      </CardContent>
    </Card>
  );
}
