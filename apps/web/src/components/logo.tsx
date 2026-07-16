import Link from "next/link";

import { APP_NAME } from "@/lib/config";
import { cn } from "@/lib/utils";

/** Wordmark + geometric "forge" mark. Swap the SVG and APP_NAME to rebrand. */
export function Logo({
  className,
  href = "/",
}: {
  className?: string;
  href?: string;
}) {
  return (
    <Link
      href={href}
      className={cn(
        "inline-flex items-center gap-2 font-display text-lg font-bold text-primary",
        className,
      )}
    >
      <svg
        width="28"
        height="28"
        viewBox="0 0 32 32"
        fill="none"
        aria-hidden="true"
        className="shrink-0"
      >
        <rect width="32" height="32" rx="8" className="fill-primary" />
        <path
          d="M11 9h11l-1.6 4H14l-.7 2.8h5.4l-1.6 4H12l-1.4 5H8L11 9z"
          className="fill-primary-foreground"
        />
      </svg>
      {APP_NAME}
    </Link>
  );
}
