# ScamGraph AI — Frontend Redesign Audit

> Audit of the current `apps/web/` presentation layer, conducted before the
> Phase 1 visual rebuild. This documents what exists, what works, what looks
> wrong, and what must change — without touching backend logic or API contracts.

---

## 1. Current routes

| Route | Type | Status |
|---|---|---|
| `/` | Landing (hero + comparison) | Exists. Needs polish. |
| `/investigate` | Combined incident composer | Exists. Form inputs look weak/default. |
| `/incidents` | Incident list | Exists. Hardcoded demo rows, no table/filters. |
| `/incidents/[id]` | Incident detail (4 tabs) | Exists. Architecture good; presentation sparse. |
| `/command` | Command Center | Exists. Metrics + static graph placeholder. |
| `/campaigns` | Campaign list | Exists. Cards. |
| `/campaigns/[id]` | Campaign detail | Exists. Fingerprint breakdown + graph. |
| `/lab` | Scenario simulator | Exists. Scenario cards; no live simulation. |
| `/shield` | Consumer pre-payment | **Missing.** Required by spec. |

**Backend contracts preserved (do not touch):** `lib/api/client.ts` exposes a
typed `api` object hitting `/api/v1/*`. Endpoints: incidents (create/get/
timeline/evidence/journey/assessment/graph/assess), investigate, campaigns
(list/graph), lab (scenarios/simulate), analyze/url. Risk-score normalization
(float 0–1 on `/assessment` → int 0–100) is handled in the client. **All of this
stays.**

---

## 2. Current components

Working layer (preserve logic):
- `lib/api/*` — centralized client + types. **Keep.**
- `lib/hooks/*` — useReducedMotion, useInvestigationProgress, useJourneyAnimation, useRiskAnimation. **Keep.**
- `lib/motion/gsap.ts` — reduced-motion-aware GSAP system. **Keep.**
- `lib/demo/fixtures.ts` — synthetic, backend-typed demo data (deterministic IDs). **Keep.**
- `lib/utils/*` — cn, risk, format. **Keep.**
- `components/risk/*` — RiskBadge, RiskGauge, ConfidenceIndicator, ReasonCodes, InterventionBanner. **Keep; restyle later.**
- `components/journey/*`, `components/evidence/*`, `components/graph/*` — domain components. **Keep; restyle in Phase 3/4.**
- `components/three/ThreatNetworkScene` — R3F PoC + SVG fallback. **Keep; enhance in Phase 6.**
- `components/investigation/*` — composer + inputs. **Keep; rewire to new form system in Phase 2.**
- `components/motion/GsapStagger` — reveal primitive. **Keep.**

---

## 3. Current design problems (the reason for this rebuild)

1. **Browser-default-looking controls.** Inputs/textareas use a thin border + bg
   but lack a real form system: no Select, SegmentedControl, Checkbox, Switch,
   FileUpload, validation, or help-text primitives. Buttons have no loading/icon
   states. Touch targets are inconsistent.
2. **Weak spacing & hierarchy.** No defined typography scale (Display → Caption).
   Section spacing relies on ad-hoc `space-y-8`. Headings don't differentiate
   strongly from body.
3. **Almost no card/surface system.** A single `.panel` class. No MetricCard,
   AssessmentCard, or elevated surface variants for dashboard density.
4. **Poor use of screen width.** Content capped at `max-w-7xl` with generous
   padding leaves wide empty gutters on large monitors. No responsive width
   strategy for data-dense vs landing pages.
5. **Excessive empty space.** Vertical padding `py-8 lg:py-10` + sparse content
   makes pages feel empty rather than dense/technical.
6. **Weak product navigation.** Sidebar groups exist but the Shield/Command/Lab
   separation is soft. No system-status / TinyFish-status / demo-mode / version
   indicators in the sidebar footer. Active route is a subtle dot, not obvious.
7. **Insufficient consumer/analyst separation.** Shield (consumer) and Command
   (analyst) share visual weight; `/shield` route doesn't exist, so the consumer
   pre-payment experience is missing entirely.
8. **Badge system is generic.** A `tone` prop, not semantic risk/variant/status
   badges (LOW/MEDIUM/HIGH/COMPLETE/PARTIAL/MUTATED_VARIANT/DEMO_DATA…).
9. **No named loading skeletons.** Generic `LoadingState` only. No
   IncidentSkeleton / EvidenceSkeleton / GraphLoadingState / CampaignSkeleton /
   CommandSkeleton.
10. **Token naming diverges from spec.** Uses `base/surface/ink/line/accent`
    instead of `background/surface-1..3/text-*/border*/brand-*/risk-*`.

---

## 4. Current API integrations (preserved)

- `api.getIncident`, `getTimeline`, `getEvidence`, `getJourney`, `getAssessment`
  (normalized), `getGraph` — incident surface.
- `api.investigate` — POST /investigate (note: backend has a known runtime bug
  on scam-like inputs; flagged, not fixed by frontend).
- `api.getCampaigns`, `getCampaignGraph`.
- `api.getLabScenarios`, `api.runSimulation`.
- `api.analyzeUrl`.
- TanStack Query provider is wired in `layout.tsx`.

**Rule:** the rebuild does not replace any of these with mocks. Demo fixtures
are used only where no backend endpoint exists (incident list, campaigns list)
and are explicitly labelled DEMO DATA.

---

## 5. Components worth preserving (as-is)

`lib/api/*`, `lib/hooks/*`, `lib/motion/*`, `lib/demo/*`, `lib/utils/*`,
`components/three/ThreatNetworkScene`, `components/motion/GsapStagger`,
`components/graph/EvidenceGraph` (Cytoscape wiring), the four-tab incident
architecture, the Tabs primitive (accessible), the API client risk-score
normalization.

---

## 6. Components requiring redesign (Phase 1 foundation)

- `tailwind.config.js` + `app/globals.css` — token system + typography scale.
- `components/ui/*` — full primitive rebuild (Button, Badge, Card, Input,
  Textarea, Select, SegmentedControl, Checkbox, Switch, FileUpload,
  ValidationMessage, HelpText, MetricCard).
- `components/shell/*` — sidebar (new structure + status footer), top bar
  (breadcrumb + env), mobile nav, app shell (width/density).
- `components/shared/States.tsx` — named skeletons + partial-result states.
- `lib/nav.ts` — add `/shield`, strengthen group separation.

---

## 7. Missing loading/error/empty states

- Named skeletons: IncidentSkeleton, EvidenceSkeleton, GraphLoadingState,
  CampaignSkeleton, CommandSkeleton — **none exist.**
- Partial-result state (COMPLETE/PARTIAL/UNAVAILABLE/FAILED per provider) — **none.**
- Provider-failure error (TinyFish timeout graceful message) — generic only.
- Empty states exist generically but lack route-specific copy + CTAs.

---

## 8. Responsive problems

- Sidebar is `hidden md:flex` — drops at `md`, but the only mobile option is a
  slide-over. No tablet "collapsible" behavior; no bottom navigation. Graph-heavy
  analyst pages are not adapted for narrow widths (no stacked-card fallback for
  the incidents table on mobile).
- Content max-width is uniform across landing and data pages.

---

## 9. Accessibility problems

- Reduced-motion infra exists (hook + GSAP) — **good, keep.**
- Focus-visible outline exists — **good.**
- Gaps: risk encoded partly by color in a few places; node-list textual
  alternative for Cytoscape not provided; some icon-only buttons lack aria-labels;
  sidebar status indicators are decorative without text.

---

## 10. Phase 1 scope (this pass)

Design tokens · Typography · Buttons · Inputs · Badges · Cards · Sidebar ·
Top bar · Application shell · Responsive navigation · Loading/error/empty states.
**Not** rebuilding page interiors (Shield/Investigate/Incidents/Command/Lab
interiors are Phase 2+). Pages inherit the new foundation automatically through
the shell + tokens, then get rebuilt in later phases.
