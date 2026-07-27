"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";

/** One labelled row that swaps into an inline form when edited.
 *
 *  This is the whole settings idiom: a page of read-only values where exactly
 *  one row opens at a time, instead of a wall of always-live inputs. Rows
 *  without an `children` render function are display-only. */
export function SettingRow({
  label,
  value,
  action,
  children,
}: {
  label: string;
  /** Current value, shown when the row is closed. */
  value: React.ReactNode;
  /** Replaces the Edit button — for rows that link out or aren't editable. */
  action?: React.ReactNode;
  /** Edit form. Called with a closer so it can dismiss itself on success. */
  children?: (close: () => void) => React.ReactNode;
}) {
  const [editing, setEditing] = useState(false);

  return (
    <div className="border-b border-border py-5 last:border-b-0">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="text-sm font-medium">{label}</p>
          {!editing && (
            <div className="mt-1 text-sm text-muted-foreground">{value}</div>
          )}
        </div>
        {action ??
          (children && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => setEditing((open) => !open)}
            >
              {editing ? "Cancel" : "Edit"}
            </Button>
          ))}
      </div>

      {editing && children && (
        <div className="mt-4">{children(() => setEditing(false))}</div>
      )}
    </div>
  );
}
