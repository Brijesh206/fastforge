"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowLeft,
  ChartLine,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Settings,
  ShieldAlert,
  Sun,
  Users,
} from "lucide-react";

import { useAdminTheme } from "@/app/admin/theme";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { UserAvatar } from "@/components/user-avatar";
import { cn } from "@/lib/utils";
import { useSession } from "@/providers/session-provider";

const NAV = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/admin/analytics", label: "Analytics", icon: ChartLine, exact: false },
  { href: "/admin/users", label: "Users", icon: Users, exact: false },
  { href: "/admin/settings", label: "Settings", icon: Settings, exact: false },
];

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="space-y-1">
      {NAV.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={cn(
              "relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "text-foreground"
                : "text-muted-foreground hover:bg-accent hover:text-foreground",
            )}
          >
            {/* One shared layoutId means the highlight slides between items
                instead of cross-fading — the whole reason for framer here. */}
            {active && (
              <motion.span
                layoutId="admin-nav-active"
                className="absolute inset-0 rounded-lg bg-accent"
                transition={{ type: "spring", stiffness: 380, damping: 32 }}
              />
            )}
            <Icon className="relative size-4 shrink-0" />
            <span className="relative">{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

function SidebarBody({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useSession();

  return (
    <div className="flex h-full flex-col">
      <div className="flex h-16 items-center gap-2.5 px-5">
        <span className="grid size-8 place-items-center rounded-lg bg-primary font-bold text-primary-foreground">
          F
        </span>
        <span className="text-base font-semibold">FastForge</span>
      </div>

      <Separator />

      <div className="flex-1 overflow-y-auto p-3">
        <NavLinks onNavigate={onNavigate} />
      </div>

      <Separator />

      <div className="space-y-1 p-3">
        {user && (
          <div className="flex items-center gap-2.5 px-2 py-2">
            <UserAvatar
              src={user.avatar_url}
              name={user.full_name}
              email={user.email}
              className="size-8"
            />
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{user.full_name ?? "Admin"}</p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
          </div>
        )}
        <Button asChild variant="ghost" size="sm" className="w-full justify-start">
          <Link href="/dashboard" onClick={onNavigate}>
            <ArrowLeft className="size-4" />
            Back to app
          </Link>
        </Button>
      </div>
    </div>
  );
}

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { theme, toggle } = useAdminTheme();
  const { user, signOut } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  function handleSignOut() {
    signOut();
    router.push("/");
  }

  // is_admin comes straight off /auth/me and mirrors the API's own gate, so
  // no probe request is needed. AuthGuard has already resolved the session.
  if (!user?.is_admin) {
    return (
      <div className="ff-admin" data-theme={theme}>
        <AccessDenied email={user?.email ?? ""} onSignOut={handleSignOut} />
      </div>
    );
  }

  return (
    <div className="ff-admin" data-theme={theme}>
      <div className="flex min-h-dvh bg-background text-foreground">
        <aside className="sticky top-0 hidden h-dvh w-64 shrink-0 border-r border-border bg-card lg:block">
          <SidebarBody />
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-border bg-background/85 px-4 backdrop-blur lg:px-8">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Open menu">
                  <Menu className="size-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="left" className="w-64 p-0">
                <SheetTitle className="sr-only">Admin navigation</SheetTitle>
                <SidebarBody />
              </SheetContent>
            </Sheet>

            <span className="flex-1 text-sm text-muted-foreground">Admin</span>

            <Button
              variant="ghost"
              size="icon"
              onClick={toggle}
              aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            >
              {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
            </Button>

            <Button variant="ghost" size="sm" onClick={handleSignOut}>
              <LogOut className="size-4" />
              <span className="hidden sm:inline">Sign out</span>
            </Button>
          </header>

          <main className="flex-1 p-4 lg:p-8">
            {/* Keyed on the route so each page animates in on navigation. */}
            <AnimatePresence mode="wait">
              <motion.div
                key={pathname}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
              >
                {children}
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </div>
  );
}

function AccessDenied({ email, onSignOut }: { email: string; onSignOut: () => void }) {
  return (
    <div className="grid min-h-dvh place-items-center bg-background p-4 text-foreground">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 text-center">
        <ShieldAlert className="mx-auto size-10 text-warning" />
        <h1 className="mt-4 text-lg font-semibold">Admin access required</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          {email ? (
            <>
              <span className="font-medium text-foreground">{email}</span> isn&apos;t on the
              admin allowlist. Add it to{" "}
              <code className="rounded bg-muted px-1 font-mono">ADMIN_EMAILS</code> and restart
              the API.
            </>
          ) : (
            "Your account isn't on the admin allowlist."
          )}
        </p>
        <div className="mt-6 flex justify-center gap-2">
          <Button asChild size="sm">
            <Link href="/dashboard">Back to app</Link>
          </Button>
          <Button variant="ghost" size="sm" onClick={onSignOut}>
            Sign out
          </Button>
        </div>
      </div>
    </div>
  );
}
