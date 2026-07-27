import { AppSidebar } from "@/components/app-sidebar";
import { AuthGuard } from "@/components/auth-guard";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex min-h-dvh">
        <AppSidebar />
        <main className="min-w-0 flex-1 px-4 py-8 sm:px-8 lg:py-10">
          <div className="mx-auto w-full max-w-4xl">{children}</div>
        </main>
      </div>
    </AuthGuard>
  );
}
