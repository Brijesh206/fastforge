import { APP_NAME } from "@/lib/config";

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 py-8 text-sm text-muted-foreground sm:flex-row">
        <p>
          © {new Date().getFullYear()} {APP_NAME}. All rights reserved.
        </p>
        <p>Built on the FastForge platform.</p>
      </div>
    </footer>
  );
}
