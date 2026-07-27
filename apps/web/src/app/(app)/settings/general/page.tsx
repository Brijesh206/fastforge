"use client";

import { useState } from "react";

import { SettingRow } from "@/components/setting-row";
import { Alert } from "@/components/ui/alert";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ApiError, api } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

export default function GeneralSettingsPage() {
  const { user, refresh } = useSession();
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  if (!user) return null;

  async function saveName(fullName: string, close: () => void) {
    setError(null);
    setSaving(true);
    try {
      await api.updateProfile({ full_name: fullName.trim() || null });
      await refresh();
      close();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save your name.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card>
      <CardContent className="pt-6">
        {error && (
          <Alert variant="error" className="mb-4">
            {error}
          </Alert>
        )}

        <div className="flex items-center gap-4 border-b border-border pb-5">
          <Avatar
            src={user.avatar_url}
            name={user.full_name}
            email={user.email}
            className="h-16 w-16 text-xl"
          />
          <div className="min-w-0">
            <p className="truncate font-medium">{user.full_name ?? user.email}</p>
            <p className="mt-0.5 text-sm text-muted-foreground">
              {user.avatar_url
                ? "Synced from your sign-in provider."
                : "Sign in with Google or GitHub to use their picture."}
            </p>
          </div>
        </div>

        <SettingRow label="Full name" value={user.full_name ?? "Not set"}>
          {(close) => (
            <form
              className="flex flex-col gap-2 sm:flex-row"
              onSubmit={(event) => {
                event.preventDefault();
                const value = new FormData(event.currentTarget).get("full_name");
                void saveName(String(value), close);
              }}
            >
              <Input
                name="full_name"
                defaultValue={user.full_name ?? ""}
                placeholder="Ada Lovelace"
                autoComplete="name"
                autoFocus
                maxLength={255}
              />
              <Button type="submit" loading={saving} className="sm:w-32">
                Save
              </Button>
            </form>
          )}
        </SettingRow>

        <SettingRow
          label="Email"
          value={user.email}
          action={
            user.is_verified ? (
              <Badge variant="success">Verified</Badge>
            ) : (
              <Badge variant="warning">Unverified</Badge>
            )
          }
        />
      </CardContent>
    </Card>
  );
}
