import { gsap } from "gsap";

export function revealStagger(
  targets: gsap.TweenTarget,
  vars: gsap.TweenVars = {},
  stagger = 0.08
) {
  if (typeof window === "undefined") return;
  return gsap.from(targets, {
    opacity: 0,
    y: 12,
    duration: 0.45,
    ease: "power2.out",
    stagger,
    ...vars,
  });
}
