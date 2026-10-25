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
        // ── Sovereign Trust Canonical Light Tokens ──
        ground: "var(--sg-ground, #F6F9FD)",
        "on-surface": "var(--sg-on-surface, #0F172A)",
        "on-surface-variant": "var(--sg-on-surface-variant, #334155)",
        "surface-subtle": "var(--sg-surface-subtle, #EEF4FA)",
        "border-divider": "var(--sg-border-divider, #E2EBF5)",
        "border-control": "var(--sg-border-control, #94A3B8)",
        "viz-primary": "var(--sg-viz-primary, #1D68BD)",
        "viz-text": "var(--sg-viz-text, #0F172A)",
        "viz-neutral": "var(--sg-viz-neutral, #64748B)",
        "viz-warning": "var(--sg-viz-warning, #D97706)",
        "viz-info": "var(--sg-viz-info, #2563EB)",
        "selected-tint": "var(--sg-selected-tint, rgba(29, 104, 189, 0.08))",
        "primary-container": "var(--sg-primary-container, #1D68BD)",
        "on-primary-container": "var(--sg-on-primary-container, #BFDBFE)",
        "on-primary": "var(--sg-on-primary, #FFFFFF)",
        primary: "var(--sg-primary, #134E96)",
        secondary: "var(--sg-secondary, #0284C7)",
        "secondary-container": "var(--sg-secondary-container, #BAE6FD)",

        // 7-State Semantic Status Tones
        "tone-info-bg": "var(--sg-tone-info-bg, #E7EDF4)",
        "tone-info-text": "var(--sg-tone-info-text, #1A446C)",
        "tone-warning-bg": "var(--sg-tone-warning-bg, #F1ECE3)",
        "tone-warning-text": "var(--sg-tone-warning-text, #614714)",
        "tone-warning-strong-bg": "var(--sg-tone-warning-strong-bg, #E8DFCF)",
        "tone-warning-strong-text": "var(--sg-tone-warning-strong-text, #4A3306)",
        "tone-danger-bg": "var(--sg-tone-danger-bg, #F6E7E5)",
        "tone-danger-text": "var(--sg-tone-danger-text, #781C18)",
        "tone-danger-strong-bg": "var(--sg-tone-danger-strong-bg, #F0D6D3)",
        "tone-danger-strong-text": "var(--sg-tone-danger-strong-text, #541210)",

        // ── Canonical surfaces & backward-compat ──
        background: "var(--sg-ground, #FBFBFB)",
        "surface-1": "var(--sg-surface, #FFFFFF)",
        "surface-2": "var(--sg-surface-raised, #FFFFFF)",
        "surface-3": "var(--sg-surface-hover, #F3F4F5)",
        "surface-hover": "var(--sg-surface-hover, #F3F4F5)",
        "surface-pressed": "var(--sg-surface-pressed, #E8E8EA)",
        "surface-inset": "var(--sg-surface-inset, #F3F4F5)",

        // ── Borders ──
        border: "var(--sg-border-divider, #E1E4E8)",
        "border-strong": "var(--sg-border-control, #80858C)",
        "border-input": "var(--sg-border-control, #80858C)",
        "border-subtle": "rgba(225, 228, 232, 0.6)",

        // ── Text ──
        "text-primary": "var(--sg-on-surface, #1A1C1E)",
        "text-secondary": "var(--sg-on-surface-variant, #3F4946)",
        "text-muted": "var(--sg-viz-neutral, #565C65)",

        // ── Brand / Action ──
        "brand-primary": "var(--sg-viz-primary, #0B6256)",
        "brand-secondary": "var(--sg-primary, #00483F)",
        "brand-hover": "var(--sg-primary, #00483F)",
        "brand-soft": "rgba(11, 98, 86, 0.08)",
        "brand-line": "rgba(11, 98, 86, 0.35)",
        "on-brand": "#FFFFFF",

        // ── Structure & Risk ──
        structure: "var(--sg-border-divider, #E1E4E8)",
        "structure-soft": "rgba(225, 228, 232, 0.5)",
        "risk-low": "#205493",
        "risk-medium": "#B86200",
        "risk-high": "#BA1A1A",
        "risk-critical": "#541210",
        "risk-insufficient": "#565C65",

        // ── Semantic status ──
        success: "#0B6256",
        warning: "#B86200",
        danger: "#BA1A1A",
        info: "#205493",
        neutral: "#565C65",
        safe: "#0B6256",
        caution: "#B86200",

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
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "pulse-soft": { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.5" } },
        "emergency-beacon": {
          "0%, 100%": { transform: "scale(1)", boxShadow: "0 0 0 0 rgba(220, 38, 38, 0.4)" },
          "50%": { transform: "scale(1.02)", boxShadow: "0 0 0 8px rgba(220, 38, 38, 0)" },
        },
        "float-subtle": {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-4px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.35s ease-out both",
        "rise-in": "rise-in 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "fade-in-up": "fade-in-up 0.4s cubic-bezier(0.16,1,0.3,1) both",
        "scale-in": "scale-in 0.25s cubic-bezier(0.16,1,0.3,1) both",
        "pulse-soft": "pulse-soft 2.4s ease-in-out infinite",
        "emergency-beacon": "emergency-beacon 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float-subtle": "float-subtle 4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
