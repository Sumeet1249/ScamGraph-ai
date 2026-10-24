import gsap from "gsap";

export function revealStagger(
  elements: HTMLElement[],
  options?: { stagger?: number; y?: number; duration?: number }
) {
  if (typeof window === "undefined" || !elements || elements.length === 0) return;
  const { stagger = 0.08, y = 12, duration = 0.5 } = options || {};
  return gsap.fromTo(
    elements,
    { opacity: 0, y },
    { opacity: 1, y: 0, duration, stagger, ease: "power2.out" }
  );
}
