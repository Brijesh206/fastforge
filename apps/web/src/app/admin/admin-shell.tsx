"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  ArrowLeft,
  LayoutDashboard,
  LogOut,
  Menu,
  Settings,
  ShieldAlert,
  Users,
} from "lucide-react";

import { useSession } from "@/providers/session-provider";
import { useAdminTheme } from "@/app/admin/theme";

const NAV = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/admin/users", label: "Users", icon: Users, exact: false },
  { href: "/admin/settings", label: "Settings", icon: Settings, exact: false },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { theme } = useAdminTheme();
  const { user, signOut } = useSession();
  const router = useRouter();
  const pathname = usePathname();

  function handleSignOut() {
    signOut();
    router.push("/");
  }

  // is_admin comes straight off /auth/me and mirrors the API's own gate, so
  // no probe request is needed. AuthGuard has already resolved the session.
  return (
    <div className="ff-admin" data-theme={theme}>
      {!user?.is_admin ? (
        <AccessDenied email={user?.email ?? ""} onSignOut={handleSignOut} />
      ) : (
        <div className="drawer min-h-dvh bg-base-100 text-base-content lg:drawer-open">
          <input id="admin-drawer" type="checkbox" className="drawer-toggle" />

          <div className="drawer-content flex min-h-dvh flex-col">
            {/* Topbar */}
            <header className="navbar sticky top-0 z-20 border-b border-base-300 bg-base-100/90 px-4 backdrop-blur">
              <div className="flex-none lg:hidden">
                <label htmlFor="admin-drawer" className="btn btn-square btn-ghost" aria-label="Open menu">
                  <Menu className="size-5" />
                </label>
              </div>
              <div className="flex-1">
                <span className="text-sm font-medium opacity-70">Admin</span>
              </div>
              <div className="flex-none items-center gap-3">
                <span className="hidden text-sm opacity-70 sm:inline">{user?.email}</span>
                <button className="btn btn-ghost btn-sm" onClick={handleSignOut}>
                  <LogOut className="size-4" />
                  Sign out
                </button>
              </div>
            </header>

            <main className="flex-1 p-4 lg:p-8">{children}</main>
          </div>

          {/* Sidebar */}
          <div className="drawer-side z-30">
            <label htmlFor="admin-drawer" aria-label="Close menu" className="drawer-overlay" />
            <aside className="flex min-h-dvh w-64 flex-col bg-base-200">
              <div className="flex h-16 items-center gap-2 border-b border-base-300 px-5">
                <span className="grid size-8 place-items-center rounded-lg bg-primary font-bold text-primary-content">
                  F
                </span>
                <span className="text-lg font-semibold">FastForge</span>
              </div>

              <ul className="menu w-full flex-1 gap-1 p-3">
                {NAV.map(({ href, label, icon: Icon, exact }) => {
                  const activeLink = exact ? pathname === href : pathname.startsWith(href);
                  return (
                    <li key={href}>
                      <Link href={href} className={activeLink ? "active font-medium" : ""}>
                        <Icon className="size-4" />
                        {label}
                      </Link>
                    </li>
                  );
                })}
              </ul>

              <div className="border-t border-base-300 p-3">
                <Link href="/dashboard" className="btn btn-ghost btn-sm w-full justify-start">
                  <ArrowLeft className="size-4" />
                  Back to app
                </Link>
              </div>
            </aside>
          </div>
        </div>
      )}
    </div>
  );
}

function AccessDenied({ email, onSignOut }: { email: string; onSignOut: () => void }) {
  return (
    <div className="grid min-h-dvh place-items-center bg-base-100 p-4 text-base-content">
      <div className="card w-full max-w-md border border-base-300 bg-base-200">
        <div className="card-body items-center text-center">
          <ShieldAlert className="size-10 text-warning" />
          <h1 className="card-title">Admin access required</h1>
          <p className="text-sm opacity-70">
            {email ? (
              <>
                <span className="font-medium">{email}</span> isn&apos;t on the admin allowlist.
                Add it to <code className="rounded bg-base-300 px-1">ADMIN_EMAILS</code> and
                restart the API.
              </>
            ) : (
              "Your account isn't on the admin allowlist."
            )}
          </p>
          <div className="card-actions mt-2">
            <Link href="/dashboard" className="btn btn-sm">
              Back to app
            </Link>
            <button className="btn btn-ghost btn-sm" onClick={onSignOut}>
              Sign out
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
