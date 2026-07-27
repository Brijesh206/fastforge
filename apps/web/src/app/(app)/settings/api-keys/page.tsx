"use client";

import { useEffect, useState } from "react";
import { Check, Copy } from "lucide-react";

import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Dialog } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Spinner } from "@/components/ui/spinner";
import { ApiError, api } from "@/lib/api";
import type { ApiKey, ApiKeyCreated } from "@/lib/types";

function formatDate(iso: string | null): string {
  if (!iso) return "Never";
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

/** Reveal panel for a freshly created key — the only moment the raw secret
 *  exists client-side, so it must be copyable before the dialog closes. */
function RevealedKey({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(value);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard is blocked outside a secure context; the value is selectable.
      setCopied(false);
    }
  }

  return (
    <div className="space-y-3">
      <Alert variant="info">
        Copy this key now — it can&apos;t be shown again.
      </Alert>
      <div className="flex items-center gap-2">
        <code className="min-w-0 flex-1 truncate rounded-md border border-border bg-muted px-3 py-2 font-mono text-xs">
          {value}
        </code>
        <Button variant="outline" size="icon" onClick={copy} aria-label="Copy key">
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}

export default function ApiKeysSettingsPage() {
  const [keys, setKeys] = useState<ApiKey[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [busy, setBusy] = useState(false);
  const [created, setCreated] = useState<ApiKeyCreated | null>(null);

  async function load() {
    try {
      setKeys(await api.apiKeys.list());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load your API keys.");
      setKeys([]);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function createKey(name: string) {
    setError(null);
    setBusy(true);
    try {
      const key = await api.apiKeys.create(name);
      setCreated(key);
      setCreating(false);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create the key.");
    } finally {
      setBusy(false);
    }
  }

  async function revokeKey(id: string) {
    setError(null);
    try {
      await api.apiKeys.revoke(id);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not revoke the key.");
    }
  }

  const active = keys?.filter((key) => !key.revoked_at) ?? [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-4">
          <div>
            <CardTitle>API keys</CardTitle>
            <CardDescription>
              Authenticate requests to the API without a login.
            </CardDescription>
          </div>
          <Button size="sm" onClick={() => setCreating(true)}>
            New key
          </Button>
        </div>
      </CardHeader>

      <CardContent>
        {error && (
          <Alert variant="error" className="mb-4">
            {error}
          </Alert>
        )}

        {keys === null ? (
          <div className="flex items-center gap-3 py-4 text-sm text-muted-foreground">
            <Spinner className="h-5 w-5" />
            Loading your keys…
          </div>
        ) : active.length === 0 ? (
          <p className="py-4 text-sm text-muted-foreground">
            You don&apos;t have any API keys yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-muted-foreground">
                  <th className="py-2 pr-4 font-medium">Name</th>
                  <th className="py-2 pr-4 font-medium">Key</th>
                  <th className="py-2 pr-4 font-medium">Last used</th>
                  <th className="py-2 pl-4 text-right font-medium">
                    <span className="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {active.map((key) => (
                  <tr key={key.id} className="border-b border-border last:border-b-0">
                    <td className="py-3 pr-4 font-medium">{key.name}</td>
                    <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">
                      {key.key_prefix}…
                    </td>
                    <td className="py-3 pr-4 text-muted-foreground">
                      {formatDate(key.last_used_at)}
                    </td>
                    <td className="py-3 pl-4 text-right">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-destructive hover:bg-destructive/10"
                        onClick={() => void revokeKey(key.id)}
                      >
                        Revoke
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>

      <Dialog
        open={creating}
        onClose={() => setCreating(false)}
        title="Create an API key"
        description="Give it a name so you can tell your keys apart later."
      >
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            const name = new FormData(event.currentTarget).get("name");
            void createKey(String(name));
          }}
        >
          <div>
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              name="name"
              required
              maxLength={255}
              placeholder="Production server"
              autoFocus
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={() => setCreating(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={busy}>
              Create key
            </Button>
          </div>
        </form>
      </Dialog>

      <Dialog
        open={created !== null}
        onClose={() => setCreated(null)}
        title={created ? `Key "${created.name}" created` : "Key created"}
      >
        {created && (
          <div className="space-y-4">
            <RevealedKey value={created.api_key} />
            <div className="flex justify-end">
              <Button onClick={() => setCreated(null)}>Done</Button>
            </div>
          </div>
        )}
      </Dialog>
    </Card>
  );
}
