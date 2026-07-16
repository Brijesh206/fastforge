"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { Spinner } from "@/components/ui/spinner";
import { useSession } from "@/providers/session-provider";

/** Client-side guard for authenticated pages. Redirects to /login when there is
 *  no session once loading settles. ponytail: client guard, not middleware —
 *  tokens live in localStorage (not cookies), so the server can't see them. */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-dvh items-center justify-center">
        <Spinner className="h-6 w-6 text-muted-foreground" />
      </div>
    );
  }

  return <>{children}</>;
}
