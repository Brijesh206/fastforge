import { SubscriptionCard } from "@/components/subscription-card";

/** The subscription card is the whole billing surface — everything past
 *  checkout (payment method, invoices, cancellation) lives in Stripe's
 *  hosted portal, which the card links to. */
export default function BillingSettingsPage() {
  return <SubscriptionCard />;
}
