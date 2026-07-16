import { AppNav } from "@/components/app-nav";
import { AuthGuard } from "@/components/auth-guard";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex min-h-dvh flex-col">
        <AppNav />
        <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-10">
          {children}
        </main>
      </div>
    </AuthGuard>
  );
}
