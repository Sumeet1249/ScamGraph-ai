# ScamGraph AI — Frontend Architecture

> Status: Phase 1 (foundations) complete. Phases 2–8 build on this layer.
> Applies to: `apps/web/` (Next.js 14 App Router, React 18, TypeScript)

This document defines the production-style frontend architecture for ScamGraph AI.
It is a security/fintech threat-intelligence product, not a hackathon dashboard.
Two product personalities share one backend:

- **ScamGraph Shield** — consumer/simple pre-payment experience (`/`, `/investigate`)
- **ScamGraph Command** — analyst/enterprise threat intelligence (`/incidents`, `/command`, `/campaigns`, `/lab`)

---

## Technology stack

| Concern | Choice | Notes |
|---|---|---|
| Framework | Next.js 14 (App Router) | Already in repo |
| Language | TypeScript (strict) | `tsconfig.json` strict mode |
| Styling | Tailwind CSS 3 | Custom design-token theme |
| UI primitives | Own minimal components | `components/ui/` (no Radix dependency) |
| 3D | three 0.170 + @react-three/fiber v8 + drei v9 | R3F v8 stays on React 18 (v10 is alpha — avoided) |
| Motion | GSAP 3 | Single animation framework — no Framer/Spring overlap |
| Graph | Cytoscape.js | Dynamic-imported, lazy |
| Icons | lucide-react | |
| Server state | TanStack Query v5 | Conservative stale time, no background spam |
| Local state | React useState | Zustand only if genuinely needed (not yet) |
| Charts | Recharts | Added in a later phase when conventional metrics ship |

New dependencies this phase: `three`, `@types/three` (pinned — required R3F peer deps
previously only transitive). No other deps added.

---

## Directory structure

```
apps/web/
├── app/                      # App Router routes
│   ├── layout.tsx            # Root: fonts, AppShell, QueryProvider
│   ├── globals.css           # Design tokens + base layer
│   ├── page.tsx              # Home (hero + Three.js + GSAP comparison)
│   ├── investigate/          # Combined incident composer
│   ├── incidents/
│   │   ├── page.tsx          # Incident list
│   │   └── [id]/page.tsx     # Incident detail (4 tabs)
│   ├── command/              # Command Center
│   ├── campaigns/
│   │   ├── page.tsx          # Campaign list
│   │   └── [id]/page.tsx     # Campaign detail (fingerprint + graph)
│   └── lab/                  # Scenario simulator
├── components/
│   ├── shell/                # AppShell, AppSidebar, TopNav, MobileNav
│   ├── ui/                   # Card, Badge, Button, Tabs, Skeleton (minimal)
│   ├── shared/               # PageHeader, States (Loading/Error/Empty), DemoDataBadge
│   ├── providers/            # QueryProvider
│   ├── motion/               # GsapStagger (reveal primitive)
│   ├── investigation/        # IncidentComposer, inputs, InvestigationProgress
│   ├── journey/              # JourneyTimeline, JourneyNode, CurrentStage, PaymentProximity
│   ├── risk/                 # RiskGauge, ConfidenceIndicator, ReasonCodes, InterventionBanner, RiskBadge
│   ├── evidence/             # EvidenceList, EvidenceCard, EvidenceDrawer, SourceBadge
│   ├── graph/                # EvidenceGraph (Cytoscape), GraphNodeDrawer, GraphLegend
│   ├── three/                # ThreatNetworkScene (+ fallback)
│   ├── campaigns/            # SimilarityBreakdown (CampaignCard, EmergingThreatRadar later)
│   └── lab/                  # ScenarioCard
└── lib/
    ├── api/                  # client.ts (fetch + normalize), types.ts, endpoints
    ├── hooks/                # useReducedMotion, useInvestigationProgress, useJourneyAnimation, useRiskAnimation
    ├── motion/               # gsap.ts (reduced-motion-aware motion system)
    ├── demo/                 # fixtures.ts (synthetic demo data, backend-typed)
    ├── utils/                # cn, risk, format
    └── nav.ts                # Navigation config (two product modes)
```

---

## Separation of concerns (architecture rule)

The codebase strictly separates:

1. **API data** — `lib/api/` owns all network calls and backend type definitions.
2. **Domain models** — TypeScript interfaces in `lib/api/types.ts` mirror the
   FastAPI wire format exactly. No invented frontend models.
3. **Presentation components** — `components/` render data; they do not fetch.
4. **Animation logic** — `lib/hooks/use*Animation` and `lib/motion/gsap.ts`.
   Pages never import GSAP directly or build timelines inline.
5. **3D scenes** — `components/three/`, lazy-loaded via `next/dynamic`.
6. **Graph visualization** — `components/graph/`, Cytoscape dynamic-imported.

---

## API client architecture

`lib/api/client.ts` is the single network entry point.

- **Base URL**: `NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"` + `/api/v1`.
- **Errors**: typed `ApiError` with status + detail. `nullOn404` option for
  graceful "not found" UX.
- **Timeouts**: 12s default, 30s for lab simulation.
- **Normalization**: `GET /incidents/{id}/assessment` returns `risk_score` as a
  float 0.0–1.0; the client multiplies by 100 so the entire UI treats risk_score
  as an integer 0–100 index. `/investigate`, `/lab`, `/assess` already use int.

### Backend contract gotchas (designed around)

1. **risk_score scale mismatch** — normalized in the client (see above).
2. **Two EventType vocabularies** — `packages.schemas.EventType` (ingest/lab)
   vs `services/api/.../enums.EventType` (domain/scenarios). The frontend types
   use the `packages.schemas` set since that's what the live endpoints return.
3. **Two RiskLevel enums** — `packages.schemas` includes `INSUFFICIENT_EVIDENCE`;
   the domain enum has `UNKNOWN`. Frontend unions include both.
4. **`/investigate` runtime bugs** — the endpoint throws on scam-like inputs
   (`correlate_entities` / `matched_stages` / `related_incident_ids` do not
   exist on the referenced classes). The frontend `InvestigateResponse` type
   matches the Pydantic contract; Phase 2 must confirm backend fixes before wiring.
5. **No incidents-list endpoint** — the incidents list uses demo data (labelled).
6. **No OpenAPI spec file** — types are hand-maintained against source. Fetch
   `/openapi.json` from a running backend to reconcile.

---

## Application shell

`components/shell/AppShell.tsx` provides:

- **Desktop**: persistent left sidebar (`AppSidebar`, w-60) with two nav groups
  (Shield / Command) + slim top bar (`TopNav`) with breadcrumb.
- **Mobile**: slide-over nav (`MobileNav`) triggered from the top bar, with
  Esc-to-close and scroll lock. Content is never hidden behind a hamburger on
  desktop.

Navigation is configured in `lib/nav.ts` so the sidebar, mobile nav, and
breadcrumb share one source of truth. Active state is resolved by longest-prefix
match so nested routes (`/incidents/[id]`) highlight their parent.

---

## Incident page (the primary screen)

`/incidents/[id]` is the most important screen. It uses a tabbed layout so
information density stays high without cramming one page:

| Tab | Components |
|---|---|
| Overview | RiskGauge, ConfidenceIndicator, CurrentStage, PaymentProximity, ReasonCodes, Counter Evidence, InterventionBanner |
| Journey | JourneyTimeline (GSAP sequential reveal, "You are here", common next stage) |
| Evidence | EvidenceList (filterable by source) + EvidenceDrawer (provenance) |
| Graph | EvidenceGraph (Cytoscape) + GraphNodeDrawer |

Phase 1 ships this as static component architecture using synthetic demo fixtures
(`lib/demo/fixtures.ts`) that match backend types exactly. Phase 3 replaces
fixtures with real API responses — no component changes needed.

**Key rules enforced in the UI:**
- Risk and Evidence Confidence are always visually separate (Architecture Rule 11).
- Risk is rendered as an index `/100`, never as a probability or `%`.
- Counter evidence is shown but never implies legitimacy.
- Journey predictions say "common next stage for matched workflow," never "attacker will."

---

## Shared states (DoD)

Every data-driven surface handles loading, error, and empty states via
`components/shared/States.tsx`:

- **LoadingState** — skeleton blocks (no flashing spinner).
- **ErrorState** — actionable retry prompt, never crashes the page.
- **EmptyState** — informative placeholder.

Synthetic data is watermarked with `DemoDataBadge` (Architecture Rule 24).

---

## Phased roadmap

| Phase | Scope | Status |
|---|---|---|
| 1 | Design system, shell, nav, route skeletons, API client, shared states, incident page architecture, reduced-motion infra, Three.js + GSAP PoCs | **Done** |
| 2 | `/investigate` real backend connection + GSAP investigation progress | Next |
| 3 | `/incidents/[id]` real data + Risk/Confidence + Journey timeline + Evidence browser | |
| 4 | Cytoscape Evidence Graph (filters, path highlighting, related-incident expansion) | |
| 5 | `/command` enterprise dashboard (live metrics, real incident feeds) | |
| 6 | Three.js Threat Network + Scam Fingerprint scenes | |
| 7 | Emerging Variant comparison animation (identifier vs workflow reveal) | |
| 8 | ScamGraph Lab + complete judge demo (AI-mutated variant hero) | |

Three.js comes relatively late. The product must look like a serious startup
even with all animations disabled; animation and 3D are a premium layer on top.
