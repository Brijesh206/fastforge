import { cloneElement, isValidElement } from "react";

import { cn } from "@/lib/utils";
import { Spinner } from "@/components/ui/spinner";

type Variant =
  | "primary"
  | "accent"
  | "secondary"
  | "outline"
  | "ghost"
  | "destructive";
type Size = "sm" | "md" | "lg" | "icon";

const variants: Record<Variant, string> = {
  primary: "bg-primary text-primary-foreground hover:bg-primary/90",
  accent: "bg-accent text-accent-foreground hover:bg-accent/90",
  secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
  outline: "border border-input bg-card text-foreground hover:bg-muted",
  ghost: "text-foreground hover:bg-muted",
  destructive:
    "bg-destructive text-destructive-foreground hover:bg-destructive/90",
};

const sizes: Record<Size, string> = {
  sm: "h-9 px-3 text-sm",
  md: "h-10 px-4 text-sm",
  lg: "h-11 px-6 text-base",
  icon: "h-10 w-10",
};

const base =
  "inline-flex cursor-pointer items-center justify-center gap-2 rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  /** Render styles onto the single child element (e.g. a Next.js <Link>). */
  asChild?: boolean;
}

export function Button({
  className,
  variant = "primary",
  size = "md",
  loading = false,
  asChild = false,
  disabled,
  children,
  ...props
}: ButtonProps) {
  const classes = cn(base, variants[variant], sizes[size], className);

  if (asChild && isValidElement<{ className?: string }>(children)) {
    return cloneElement(children, {
      className: cn(classes, children.props.className),
    });
  }

  return (
    <button className={classes} disabled={disabled || loading} {...props}>
      {loading && <Spinner className="h-4 w-4" />}
      {children}
    </button>
  );
}
