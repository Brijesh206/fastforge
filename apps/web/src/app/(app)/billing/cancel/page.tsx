import Link from "next/link";
import { CircleX } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function CheckoutCancelPage() {
  return (
    <div className="mx-auto max-w-md py-10">
      <Card>
        <CardContent className="flex flex-col items-center pt-10 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-muted text-muted-foreground">
            <CircleX className="h-8 w-8" />
          </div>
          <h1 className="mt-6 text-2xl font-bold">Checkout canceled</h1>
          <p className="mt-2 text-muted-foreground">
            No charge was made. You can upgrade any time from your dashboard.
          </p>
          <Button asChild className="mt-8 w-full">
            <Link href="/dashboard">Back to dashboard</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
