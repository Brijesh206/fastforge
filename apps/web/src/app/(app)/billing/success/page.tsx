import Link from "next/link";
import { CircleCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function CheckoutSuccessPage() {
  return (
    <div className="mx-auto max-w-md py-10">
      <Card>
        <CardContent className="flex flex-col items-center pt-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-accent/10 text-accent">
            <CircleCheck className="h-8 w-8" />
          </div>
          <h1 className="mt-6 text-2xl font-bold">You&apos;re all set</h1>
          <p className="mt-2 text-muted-foreground">
            Thanks for subscribing. Your plan activates as soon as Stripe
            confirms the payment — usually within a few seconds.
          </p>
          <Button asChild className="mt-8 w-full">
            <Link href="/dashboard">Go to dashboard</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
