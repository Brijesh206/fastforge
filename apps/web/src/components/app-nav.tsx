"use client";

import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";

import { Logo } from "@/components/logo";
import { Button } from "@/components/ui/button";
import { useSession } from "@/providers/session-provider";

export function AppNav() {
  const { user, signOut } = useSession();
  const router = useRouter();

  function handleSignOut() {
    signOut();
    router.push("/");
  }

  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-4">
        <Logo href="/dashboard" />
        <div className="flex items-center gap-4">
          {user && (
            <span className="hidden text-sm text-muted-foreground sm:inline">
              {user.email}
            </span>
          )}
          <Button variant="ghost" size="sm" onClick={handleSignOut}>
            <LogOut className="h-4 w-4" />
            Sign out
          </Button>
        </div>
      </div>
    </header>
  );
}
