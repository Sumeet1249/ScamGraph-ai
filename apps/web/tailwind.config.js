/** @type {import('tailwindcss').Config}
 *
 * ScamGraph AI — design tokens.
 * Canonical spec names (background, surface-1..3, text-*, border*, brand-*,
 * risk-*) plus backward-compatible aliases (base, surface, ink, line, accent…)
 * so existing pages keep working during the phased rebuild.
 */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // ── Canonical Mocha surfaces (Section 3.1 & 3.2) ──
        background: "var(--sg-bg)",
        "surface-1": "var(--sg-surface)",
        "surface-2": "var(--sg-surface-raised)",
        "surface-3": "var(--sg-surface-hover)",
        "surface-subtle": "var(--sg-bg-subtle)",
        "surface-hover": "var(--sg-surface-hover)",
        "surface-pressed": "var(--sg-surface-pressed)",
        "surface-inset": "var(--sg-surface-inset)",

        // ── Borders ──
        border: "var(--sg-border)",
        "border-strong": "var(--sg-border-strong)",
        "border-input": "var(--sg-input-border)",
        "border-subtle": "rgba(229, 228, 226, 0.05)",

        // ── Platinum & Silver Text ──
        "text-primary": "var(--sg-text)",
        "text-secondary": "var(--sg-text-muted)",
        "text-muted": "var(--sg-text-subtle)",

        // ── Pale Lavender Brand / Action (Section 2 & 3.2) ──
        "brand-primary": "var(--sg-accent)",
        "brand-secondary": "var(--sg-accent-hover)",
        "brand-hover": "var(--sg-accent-hover)",
        "brand-soft": "var(--sg-accent-soft)",
        "brand-line": "var(--sg-accent-line)",
        "on-brand": "var(--sg-on-accent)",

        // ── Mocha structure ──
        structure: "var(--sg-structure)",
        "structure-soft": "var(--sg-structure-soft)",

        // ── Risk index bands ──
        "risk-low": "var(--sg-low)",
        "risk-medium": "var(--sg-medium)",
        "risk-high": "var(--sg-high)",
        "risk-critical": "var(--sg-critical)",
        "risk-insufficient": "var(--sg-neutral)",

        // ── Semantic status ──
        success: "var(--sg-success)",
        warning: "var(--sg-warning)",
        danger: "var(--sg-danger)",
        info: "var(--sg-info)",
        neutral: "var(--sg-neutral)",
        safe: "var(--sg-success)",
        caution: "var(--sg-warning)",

        // ── Direct palette steps (Section 3.1) ──
        "mocha-950": "#120e0c",
        "mocha-900": "#17120f",
        "mocha-800": "#1d1714",
        "mocha-700": "#261e1a",
        "mocha-650": "#2c231f",
        "mocha-600": "#3a2f28",
        "mocha-500": "#6b4f3f",
        "mocha-400": "#8a6a57",
        "mocha-300": "#a98873",
        "mocha-200": "#cdb3a0",

        "platinum-100": "#edebe9",
        "platinum-200": "#e5e4e2",
        "silver-300": "#b9b4b1",
        "silver-400": "#a9a5a9",
        "silver-500": "#948e8a",

        "lavender-300": "#d3c7f0",
        "lavender-400": "#c4b5e8",
        "lavender-500": "#b5a4dd",
        "lavender-ink": "#1a1420",

        // ── Backward-compatible aliases ──
        base: "var(--sg-bg)",
        elevated: "var(--sg-surface-raised)",
        surface: "var(--sg-surface)",
        ink: "var(--sg-text)",
        "ink-muted": "var(--sg-text-muted)",
        "ink-dim": "var(--sg-text-subtle)",
        line: "var(--sg-border)",
        "line-strong": "var(--sg-border-strong)",
        "line-subtle": "rgba(229, 228, 226, 0.05)",
        accent: "var(--sg-accent)",
        "accent-hover": "var(--sg-accent-hover)",
        "accent-soft": "var(--sg-accent-soft)",
        "accent-line": "var(--sg-accent-line)",
        "on-accent": "var(--sg-on-accent)",
        signal: "var(--sg-info)",
        caution: "var(--sg-warning)",
        safe: "var(--sg-success)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "monospace"],
      },
      fontSize: {
        // Typography scale
        "display-lg": ["3.25rem", { lineHeight: "1.05", letterSpacing: "-0.025em", fontWeight: "600" }],
        display: ["2.75rem", { lineHeight: "1.08", letterSpacing: "-0.022em", fontWeight: "600" }],
        "h1-lg": ["2.25rem", { lineHeight: "1.12", letterSpacing: "-0.02em", fontWeight: "600" }],
        h1: ["1.875rem", { lineHeight: "1.15", letterSpacing: "-0.018em", fontWeight: "600" }],
        h2: ["1.5rem", { lineHeight: "1.2", letterSpacing: "-0.016em", fontWeight: "600" }],
        h3: ["1.1875rem", { lineHeight: "1.25", letterSpacing: "-0.012em", fontWeight: "600" }],
        body: ["0.9375rem", { lineHeight: "1.55" }],
        "body-sm": ["0.8125rem", { lineHeight: "1.55" }],
        label: ["0.6875rem", { lineHeight: "1.2", letterSpacing: "0.06em", fontWeight: "600" }],
        caption: ["0.6875rem", { lineHeight: "1.4" }],
        "mono-data": ["0.8125rem", { lineHeight: "1.4" }],
      },
      spacing: {
        "4.5": "1.125rem",
        "13": "3.25rem",
        "15": "3.75rem",
        "18": "4.5rem",
      },
      borderRadius: {
        card: "0.875rem",
      },
      letterSpacing: {
        wider2: "0.08em",
        wider3: "0.12em",
      },
      boxShadow: {
        card: "none",
        floating: "var(--sg-shadow-floating)",
        focus: "0 0 0 2px var(--sg-ring)",
      },
      keyframes: {
        "fade-in": { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        "rise-in": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "pulse-soft": { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.5" } },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.35s ease-out both",
        "rise-in": "rise-in 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
