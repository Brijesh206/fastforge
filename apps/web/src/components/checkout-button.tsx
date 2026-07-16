"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { Button, type ButtonProps } from "@/components/ui/button";
import { api } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

/** Starts Stripe checkout for a logged-in user, or sends a guest to sign up
 *  first. The API creates the hosted session; we just redirect to its URL. */
export function CheckoutButton({
  children,
  ...props
}: ButtonProps) {
  const { user, loading } = useSession();
  const router = useRouter();
  const [working, setWorking] = useState(false);

  async function handleClick() {
    if (!user) {
      router.push("/signup");
      return;
    }
    setWorking(true);
    try {
      const { url } = await api.startCheckout();
      window.location.href = url;
    } catch {
      setWorking(false);
      router.push("/dashboard?checkout=error");
    }
  }

  return (
    <Button onClick={handleClick} loading={loading || working} {...props}>
      {children}
    </Button>
  );
}
