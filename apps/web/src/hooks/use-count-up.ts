"use client";

import { useEffect, useRef, useState } from "react";

const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";

/** Animate a number up to `target` on mount and whenever it changes.
 *
 *  The CSS in globals.css can't do this one — there's no text-content
 *  keyframe — so it's the one piece of motion that needs JS. It honours
 *  prefers-reduced-motion itself for the same reason: the global CSS guard
 *  can't reach a requestAnimationFrame loop.
 *
 *  Counts from the previous value rather than zero, so a range switch reads
 *  as the number moving, not resetting.
 */
export function useCountUp(target: number, durationMs = 900): number {
  const [value, setValue] = useState(target);
  const fromRef = useRef(target);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const from = fromRef.current;
    fromRef.current = target;

    if (from === target || window.matchMedia(REDUCED_MOTION).matches) {
      setValue(target);
      return;
    }

    let frame = 0;
    const start = performance.now();

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / durationMs);
      // easeOutCubic — fast start, gentle settle.
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(from + (target - from) * eased);
      if (t < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}
