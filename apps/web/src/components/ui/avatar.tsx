"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

function initial(name: string | null, email: string): string {
  return (name?.trim() || email).charAt(0).toUpperCase();
}

/** Profile image with a lettered fallback.
 *
 *  `avatar_url` is populated from the OAuth provider at sign-in, so it points
 *  at Google/GitHub's CDN and can 404 once their cache rotates — hence the
 *  onError fallback rather than trusting the URL to keep resolving. */
export function Avatar({
  src,
  name,
  email,
  className,
}: {
  src: string | null;
  name: string | null;
  email: string;
  className?: string;
}) {
  const [broken, setBroken] = useState(false);

  const base = cn(
    "shrink-0 overflow-hidden rounded-full object-cover",
    className ?? "h-9 w-9",
  );

  if (src && !broken) {
    // Plain <img>: next/image would need the provider CDNs whitelisted in
    // next.config, which every buyer would have to edit for their own setup.
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={src}
        alt=""
        className={base}
        referrerPolicy="no-referrer"
        onError={() => setBroken(true)}
      />
    );
  }

  return (
    <span
      aria-hidden="true"
      className={cn(
        base,
        "flex items-center justify-center bg-primary font-semibold text-primary-foreground",
      )}
    >
      {initial(name, email)}
    </span>
  );
}
