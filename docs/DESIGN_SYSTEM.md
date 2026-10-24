# ScamGraph AI — Design System

> The product should feel like: enterprise cybersecurity + fintech risk
> intelligence + modern AI startup. Professional, restrained, high information
> density without clutter. Not a hackathon dashboard.

---

## Visual language

**Do:** dark graphite / near-black environment, neutral surfaces, off-white
primary text, muted secondary text, a single controlled blue/cyan accent,
amber for caution, red only for high-risk/intervention, green for verified/low.

**Do NOT:** cyberpunk, Matrix effects, random particles everywhere, huge
gradients, glassmorphism on every card, skulls, hacker imagery, fake terminals,
excessive neon, excessive rounded cards, a glowing 3D lock.

---

## Color tokens

Defined as CSS variables in `app/globals.css` and mapped in `tailwind.config.js`.

### Surfaces (graphite, not blue-tinted)
| Token | Value | Use |
|---|---|---|
| `bg-base` | `#0A0D12` | App background |
| `bg-elevated` | `#11151C` | Sidebar, drawers, raised panels |
| `bg-surface` | `#161B24` | Cards (`.panel`) |
| `bg-surface-hover` | `#1C222D` | Hover state |
| `bg-surface-2` | `#1E2530` | Meters, tracks, secondary fills |

### Borders (opacity-based)
| Token | Value |
|---|---|
| `border-line-subtle` | `rgba(255,255,255,0.06)` |
| `border-line` | `rgba(255,255,255,0.10)` |
| `border-line-strong` | `rgba(255,255,255,0.16)` |

### Text
| Token | Value | Use |
|---|---|---|
| `text-ink` | `#E6EAF0` | Primary (off-white) |
| `text-ink-muted` | `#9AA4B2` | Secondary (muted slate) |
| `text-ink-dim` | `#64748B` | Tertiary / labels |

### Accent + semantic
| Token | Value | Use |
|---|---|---|
| `accent` | `#3B82F6` | Primary actions, links, active nav |
| `accent-hover` | `#60A5FA` | Hover |
| `signal` | `#22D3EE` | Active/live, focus rings |
| `caution` | `#F59E0B` | Caution, medium risk |
| `danger` | `#EF4444` | High-risk, intervention, critical |
| `safe` | `#22C55E` | Verified, low-risk, counter-evidence |

### Risk index bands (0–100)
| Band | Range | Color |
|---|---|---|
| low | 1–34 | `#22C55E` |
| medium | 35–59 | `#F59E0B` |
| high | 60–79 | `#F97316` |
| critical | 80–100 | `#EF4444` |
| insufficient | 0 | `#64748B` |

Risk is an **index**, never a probability. Never render it as "84% scam."

---

## Typography

Loaded via `next/font` (self-hosted, no CDN, no layout shift):

| Role | Family | Tailwind class |
|---|---|---|
| Sans (body + headings) | Inter | `font-sans` / default |
| Mono (data) | JetBrains Mono | `font-mono` |

**Mono is used only for data:** domains, IPs, UPI IDs, evidence IDs,
timestamps, risk signals, code. The whole app is NOT monospace.

Headings use Inter at 600 weight with `-0.018em` letter-spacing.

---

## Component conventions

- **`.panel`** — flat, 1px border, `bg-surface`, `rounded-xl`. No glow by default.
- **`.panel-elevated`** — `bg-elevated`, subtle shadow. Use sparingly for emphasis.
- **`.eyebrow`** — `11px` uppercase, `0.12em` tracking, `text-ink-dim`. Section labels.
- **`.data`** — `13px` mono, `text-ink-muted`. For inline data values.

### UI primitives (`components/ui/`)
- `Card` — variants: `default`, `elevated`, `ghost`; pad: `none`/`sm`/`md`/`lg`.
- `Badge` — tones: `neutral`, `accent`, `signal`, `caution`, `danger`, `safe`.
- `Button` — variants: `primary`, `secondary`, `outline`, `ghost`, `danger`; sizes: `sm`/`md`/`lg`.
- `Tabs` — accessible WAI-ARIA tabs (manual roving, `role=tab`/`tabpanel`).
- `Skeleton` / `TextSkeleton` — loading placeholders (subtle pulse).

All components use `cn()` (clsx + tailwind-merge) for class composition and
expose `focus-visible:outline-signal` for keyboard focus.

---

## Accessibility

- **Focus**: `:focus-visible` draws a 2px `--signal` outline with 2px offset.
- **Color**: text meets contrast on graphite backgrounds. Risk colors are
  reinforced with text labels (never color alone) plus icons.
- **Keyboard**: all interactive elements are real `<button>`/`<a>`/`<label>`
  elements; tabs implement roving tabindex; drawers close on Esc.
- **Reduced motion**: handled globally (see MOTION_SYSTEM.md) — animations
  collapse to instant state changes.
- **3D fallback**: Three.js scenes ship a static 2D SVG fallback for
  environments without WebGL or under reduced motion.
- **Semantics**: roles, aria-labels, aria-live on loading states, aria-current
  on active nav, role="progressbar" on risk meters.

---

## Spacing & layout

- App shell content max-width: `max-w-7xl`, `px-4 lg:px-8`, `py-8 lg:py-10`.
- Card default padding: `p-5`.
- Page vertical rhythm between sections: `space-y-8`.

---

## Responsive behavior

- **Desktop**: full analyst experience — sidebar + 3D + dense layouts.
- **Tablet**: simplified graph layouts, sidebar collapses to slide-over.
- **Mobile**: Shield-first experience. 3D is NOT required; static fallbacks
  render. No horizontal scrolling on content.
