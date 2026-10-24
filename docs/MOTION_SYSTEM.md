# ScamGraph AI — Motion System

> GSAP creates information choreography, not random animation. Three.js is
> used only where spatial visualization communicates threat relationships,
> fingerprints, campaigns, or emerging variants. Never decorative.

---

## Principles

1. **Motion explains a decision.** The risk score animates as evidence arrives
   to answer "why did ScamGraph intervene now?" — directly combatting alert fatigue.
2. **Animation lives in hooks, not pages.** Pages compose `lib/hooks/use*Animation`
   or `components/motion/GsapStagger`. They never import `gsap` directly or build
   timelines inline. This keeps GSAP logic reusable and testable.
3. **Reduced motion is non-negotiable.** Every animation helper checks
   `prefers-reduced-motion` and collapses to an instant `set()`. The CSS base
   layer also zeroes animation/transition durations under the media query.
4. **Content is never gated behind motion.** All important information remains
   available without animation. 3D supplements numeric/text data; it never
   replaces it.
5. **One framework.** GSAP is the only animation library. No Framer Motion,
   Anime.js, React Spring, or Motion are installed.

---

## Reduced-motion infrastructure

`lib/hooks/useReducedMotion.ts`
- `useReducedMotion()` — React hook; SSR-safe (false on server + first paint to
  avoid hydration mismatch), subscribes to the media query and re-renders on
  change.
- `prefersReducedMotion()` — non-hook helper for use inside effects/timeline
  setup.

`lib/motion/gsap.ts` — the single GSAP entry point:
- `createTimeline(vars)` — timeline whose durations collapse to ~0 under
  reduced motion.
- `animateTo(targets, vars)` — tween, instant under reduced motion.
- `setProps(targets, vars)` — instant set (no animation).
- `revealStagger(targets, opts)` — fade+rise stagger for lists (journey, evidence,
  investigation steps). Under reduced motion, all visible instantly.
- `animateNumber(from, to, onUpdate, opts)` — numeric tween (risk progression).
  Under reduced motion, jumps to target.

CSS fallback (`globals.css`):
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
}
```

---

## Where GSAP is used (by phase)

| Phase | Animation | Hook / primitive |
|---|---|---|
| 1 (PoC) | Hero comparison reveal | `GsapStagger` (IntersectionObserver-triggered) |
| 2 | Investigation progress — steps light up as engine confirms each stage | `useInvestigationProgress` |
| 3 | Journey node sequential reveal + "You are here" | `useJourneyAnimation` |
| 3 | Risk score progression (evidence-arrival deltas) | `useRiskAnimation` |
| 3 | Evidence list reveal | `GsapStagger` |
| 7 | Emerging variant reveal: identifiers → semantic → journey → graph → verdict | staged `createTimeline` |
| 8 | Lab event arrival over time | `useInvestigationProgress`-style timeline |

**Rule:** only mark a stage complete when the API confirms it. Never fabricate
backend completion for a smoother animation.

---

## Three.js usage (exactly 4 places)

3D is NOT decoration. One Three.js canvas per major visualization, lazy-loaded
via `next/dynamic` with `ssr: false`, with a static 2D fallback.

| # | Scene | Location | Phase |
|---|---|---|---|
| 1 | Threat Intelligence Network (abstract orbiting nodes, NOT geography) | Home / Command | 1 (PoC), 6 (full) |
| 2 | Scam Fingerprint Orb (5 dimensions) | Incident / Campaign | 6 |
| 3 | Emerging Variant Reveal (fingerprint morph) | Campaign | 7 |
| 4 | Campaign Constellation | Campaign detail | 6 |

### Phase 1 proof-of-concept
`components/three/ThreatNetworkScene.tsx`
- R3F v8 Canvas + drei `Line` for connections, `<mesh>` spheres for nodes.
- ~14 deterministic nodes (no per-render random churn), no post-processing.
- Rotation pauses under reduced motion; `Canvas` `fallback` prop renders the
  static SVG `ThreatNetworkFallback`.
- Lazy-loaded on the homepage only (`next/dynamic`, `ssr: false`).

---

## Performance rules

- Never more than one Three.js canvas per major visualization; lazy-load it.
- Do not block initial page rendering on 3D — the hero is interactive before the
  Canvas resolves.
- Cap particle/node counts. Avoid post-processing.
- Pause/reduce animation when not visible. Use `IntersectionObserver` to defer
  reveals until on-screen.
- GSAP timelines are created per-component and cleaned up (`.kill()` in effects)
  to prevent leaks.
- Static scenes do not continuously re-render.

---

## Accessibility for motion

- All 3D visualizations have a textual/numeric alternative rendered alongside.
  Judges are never forced to interpret the 3D graphic alone.
- `prefers-reduced-motion` disables camera/particle motion and GSAP tweens.
- WebGL failure degrades to the 2D SVG fallback rather than a blank screen.
