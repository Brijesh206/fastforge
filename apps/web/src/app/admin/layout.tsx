import { AuthGuard } from "@/components/auth-guard";
import { AdminShell } from "@/app/admin/admin-shell";
import { AdminThemeProvider } from "@/app/admin/theme";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AdminThemeProvider>
        <AdminShell>{children}</AdminShell>
      </AdminThemeProvider>
    </AuthGuard>
  );
}
