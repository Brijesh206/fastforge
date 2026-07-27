"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { SettingRow } from "@/components/setting-row";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ApiError, api } from "@/lib/api";
import { useSession } from "@/providers/session-provider";

export default function SecuritySettingsPage() {
  const { user, refresh, signOut } = useSession();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [confirmingDelete, setConfirmingDelete] = useState(false);

  if (!user) return null;

  async function changePassword(form: FormData, close: () => void) {
    setError(null);
    setDone(null);
    setSaving(true);
    try {
      await api.changePassword({
        // Omitted entirely for an OAuth-only account, which has none to prove.
        current_password: user!.has_password
          ? String(form.get("current_password"))
          : undefined,
        new_password: String(form.get("new_password")),
      });
      await refresh();
      setDone(
        user!.has_password
          ? "Password changed. Other devices have been signed out."
          : "Password set. You can now log in with your email too.",
      );
      close();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not change your password.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteAccount(form: FormData) {
    setError(null);
    setSaving(true);
    try {
      await api.deleteAccount(
        user!.has_password ? String(form.get("password")) : undefined,
      );
      signOut();
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not delete your account.");
      setSaving(false);
      setConfirmingDelete(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardContent className="p-6">
          {error && (
            <Alert variant="error" className="mb-4">
              {error}
            </Alert>
          )}
          {done && (
            <Alert variant="success" className="mb-4">
              {done}
            </Alert>
          )}

          <SettingRow
            label="Password"
            value={
              user.has_password
                ? "••••••••••••"
                : "No password set — you sign in with Google or GitHub."
            }
          >
            {(close) => (
              <form
                className="max-w-sm space-y-3"
                onSubmit={(event) => {
                  event.preventDefault();
                  void changePassword(new FormData(event.currentTarget), close);
                }}
              >
                {user.has_password && (
                  <div>
                    <Label htmlFor="current_password">Current password</Label>
                    <Input
                      id="current_password"
                      name="current_password"
                      type="password"
                      required
                      autoComplete="current-password"
                      autoFocus
                    />
                  </div>
                )}
                <div>
                  <Label htmlFor="new_password">
                    {user.has_password ? "New password" : "Password"}
                  </Label>
                  <Input
                    id="new_password"
                    name="new_password"
                    type="password"
                    required
                    minLength={12}
                    autoComplete="new-password"
                    placeholder="At least 12 characters"
                    autoFocus={!user.has_password}
                  />
                </div>
                <Button type="submit" loading={saving}>
                  {user.has_password ? "Change password" : "Set password"}
                </Button>
              </form>
            )}
          </SettingRow>
        </CardContent>
      </Card>

      <Card className="border-destructive/30">
        <CardContent className="p-6">
          <SettingRow
            label="Delete account"
            value="Permanently removes your account, subscription and API keys. This cannot be undone."
            action={
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setConfirmingDelete(true)}
              >
                Delete
              </Button>
            }
          />
        </CardContent>
      </Card>

      <Dialog
        open={confirmingDelete}
        onClose={() => setConfirmingDelete(false)}
        title="Delete your account?"
        description="Your subscription is cancelled and all your data is removed. This cannot be undone."
      >
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            void deleteAccount(new FormData(event.currentTarget));
          }}
        >
          {user.has_password && (
            <div>
              <Label htmlFor="password">Confirm your password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
              />
            </div>
          )}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setConfirmingDelete(false)}
            >
              Cancel
            </Button>
            <Button type="submit" variant="destructive" loading={saving}>
              Delete account
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
}
