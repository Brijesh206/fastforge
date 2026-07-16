/** Join truthy class names. ponytail: no tailwind-merge — we own every
 *  className passed in, so last-wins source order is enough. Add tailwind-merge
 *  if a consumer ever needs to override a base utility. */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}
