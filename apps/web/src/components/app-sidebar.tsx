"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, LogOut, Settings, ShieldCheck } from "lucide-react";

import { UserAvatar } from "@/components/user-avatar";
import { Logo } from "@/components/logo";
import { cn } from "@/lib/utils";
import { useSession } from "@/providers/session-provider";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/settings", label: "Settings", icon: Settings },
];

/** Left rail for every authenticated page.
 *
 *  Collapses to icons-only below `lg` with pure CSS rather than a drawer —
 *  no open/close state, no focus management, no body-scroll locking. The
 *  labels are still in the DOM for screen readers via sr-only. */
export function AppSidebar() {
  const { user, signOut } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  function handleSignOut() {
    signOut();
    router.push("/");
  }

  const items = user?.is_admin
    ? [...NAV, { href: "/admin", label: "Admin", icon: ShieldCheck }]
    : NAV;

  return (
    <aside className="sticky top-0 flex h-dvh w-16 shrink-0 flex-col border-r border-border bg-card lg:w-64">
      <div className="flex h-16 items-center justify-center border-b border-border lg:justify-start lg:px-5">
        <Logo href="/dashboard" className="[&>span]:hidden lg:[&>span]:inline" />
      </div>

      <nav className="flex-1 space-y-1 p-2 lg:p-3">
        {items.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              title={label}
              className={cn(
                "flex items-center justify-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors lg:justify-start",
                active
                  ? "bg-primary/15 text-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4 shrink-0" />
              <span className="sr-only lg:not-sr-only">{label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-2 lg:p-3">
        {user && (
          <div className="flex items-center justify-center gap-3 px-1 py-2 lg:justify-start">
            <UserAvatar
              src={user.avatar_url}
              name={user.full_name}
              email={user.email}
              className="h-8 w-8"
            />
            <div className="hidden min-w-0 lg:block">
              <p className="truncate text-sm font-medium">
                {user.full_name ?? "Your account"}
              </p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
          </div>
        )}
        <button
          type="button"
          onClick={handleSignOut}
          title="Sign out"
          className="flex w-full cursor-pointer items-center justify-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-muted hover:text-foreground lg:justify-start"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          <span className="sr-only lg:not-sr-only">Sign out</span>
        </button>
      </div>
    </aside>
  );
}
