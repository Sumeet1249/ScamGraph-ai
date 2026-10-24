"use client";

import { useEffect, useRef, type ReactNode } from "react";
import { revealStagger } from "@/lib/motion/gsap";

/**
 * GSAP compatibility proof-of-concept.
 *
 * Wraps a list of children and reveals them with a staggered fade+rise when
 * scrolled into view. Under reduced motion, all children appear instantly.
 *
 * This is the shared choreography primitive used by the investigation progress,
 * journey timeline, evidence list, and campaign comparison in later phases.
 * Pages never call GSAP directly — they compose this or the motion hooks.
 */
export function GsapStagger({
  children,
  className,
  stagger = 0.08,
}: {
  children: ReactNode;
  className?: string;
  stagger?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const nodes = Array.from(el.children) as HTMLElement[];
    if (!nodes.length) return;

    // Reveal when scrolled into view (IntersectionObserver), not on mount,
    // so the animation is meaningful rather than firing off-screen.
    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            revealStagger(nodes, { stagger, y: 12 });
            io.disconnect();
          }
        }
      },
      { rootMargin: "-10% 0px" },
    );
    io.observe(el);

    return () => io.disconnect();
  }, [stagger]);

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  );
}
