"use client";

import { useEffect, useRef } from "react";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";

/** Modal built on the native <dialog> element.
 *
 *  showModal() gives focus trapping, Esc-to-close, background inerting and a
 *  ::backdrop for free — the parts that make a hand-rolled modal inaccessible.
 *  That's why this needs no Radix dependency.
 *
 *  `onClose` fires for every dismissal route (Esc, backdrop, the X), so the
 *  parent's `open` state can never drift out of sync with the element. */
export function Dialog({
  open,
  onClose,
  title,
  description,
  children,
  className,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      // A click landing on the dialog itself (not a child) is a backdrop hit:
      // the element's box covers the whole viewport while modal.
      onClick={(event) => {
        if (event.target === ref.current) onClose();
      }}
      className={cn(
        "m-auto w-[calc(100vw-2rem)] max-w-md rounded-lg border border-border bg-card p-6 text-card-foreground shadow-lg backdrop:bg-foreground/40",
        className,
      )}
    >
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold leading-tight">{title}</h2>
          {description && (
            <p className="mt-1 text-sm text-muted-foreground">{description}</p>
          )}
        </div>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="-m-1 cursor-pointer rounded-md p-1 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
      {children}
    </dialog>
  );
}
