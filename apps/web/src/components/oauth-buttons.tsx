import { Button } from "@/components/ui/button";
import { API_URL } from "@/lib/config";

const PROVIDERS = [
  { name: "google", label: "Google" },
  { name: "github", label: "GitHub" },
] as const;

/** Full-page navigation links (not fetch calls) — each kicks off the
 *  provider's redirect-based OAuth flow, handled entirely by the API. */
export function OAuthButtons() {
  return (
    <div className="space-y-2">
      {PROVIDERS.map((provider) => (
        <Button key={provider.name} asChild variant="outline" className="w-full">
          <a href={`${API_URL}/auth/${provider.name}/login`}>Continue with {provider.label}</a>
        </Button>
      ))}
    </div>
  );
}
