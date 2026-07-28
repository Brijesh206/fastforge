"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

/** A user's picture with a lettered fallback.
 *
 *  Wraps shadcn's Avatar primitives rather than replacing them: this keeps
 *  the app's `src / name / email` call sites in one place, and Radix already
 *  handles the loading and error states that make a bare <img> fall over.
 *
 *  `avatar_url` is populated from the OAuth provider at sign-in, so it points
 *  at Google/GitHub's CDN and can 404 once their cache rotates — the fallback
 *  is load-bearing, not decorative.
 */
export function UserAvatar({
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
  const initial = (name?.trim() || email).charAt(0).toUpperCase();

  return (
    <Avatar className={cn("shrink-0", className)}>
      {src && <AvatarImage src={src} alt="" referrerPolicy="no-referrer" />}
      <AvatarFallback className="bg-primary font-semibold text-primary-foreground">
        {initial}
      </AvatarFallback>
    </Avatar>
  );
}
