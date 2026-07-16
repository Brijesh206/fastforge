import { cn } from "@/lib/utils";

type Variant = "info" | "success" | "error";

const variants: Record<Variant, string> = {
  info: "border-secondary/30 bg-secondary/5 text-secondary",
  success: "border-accent/30 bg-accent/5 text-accent",
  error: "border-destructive/30 bg-destructive/5 text-destructive",
};

export function Alert({
  variant = "info",
  className,
  children,
}: {
  variant?: Variant;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "rounded-md border px-4 py-3 text-sm",
        variants[variant],
        className,
      )}
    >
      {children}
    </div>
  );
}
