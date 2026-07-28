import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Join class names, with later Tailwind utilities winning over earlier
 *  conflicting ones.
 *
 *  This used to be a plain filter+join, on the grounds that we owned every
 *  className passed in. shadcn components break that assumption: their
 *  variants emit base utilities a caller is expected to override
 *  (`<Button className="bg-red-500">`), and without tailwind-merge both
 *  classes ship and the winner is whichever rule lands later in the
 *  stylesheet — which is not something the caller controls. */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
