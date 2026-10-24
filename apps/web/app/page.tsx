"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import {
  ArrowRight,
  Search,
  PlayCircle,
  X,
  Check,
  Fingerprint,
  Network,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui";
import { PageHeader } from "@/components/shared/PageHeader";
import { GsapStagger } from "@/components/motion/GsapStagger";

// Lazy-load the Three.js scene so it never blocks hero interaction.
// SSR disabled — Canvas needs the DOM/window.
const ThreatNetworkScene = dynamic(() => import("@/components/three/ThreatNetworkScene"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center text-ink-dim text-xs">
      Loading threat network…
    </div>
  ),
});

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* ── Hero ────────────────────────────────────────────────────── */}
      <section className="grid gap-10 lg:grid-cols-[1.1fr_1fr] lg:items-center">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1 text-[11px] font-semibold uppercase tracking-wider2 text-ink-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-signal animate-pulse-soft" />
            ScamGraph AI
          </div>

          <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl lg:text-6xl">
            AI Scam Journey
            <br />
            <span className="text-accent">Intelligence</span>
          </h1>

          <p className="text-xl font-medium text-ink">
            Understand the scam before you pay.
          </p>

          <p className="max-w-xl text-sm leading-relaxed text-ink-muted">
            ScamGraph connects messages, websites, payment requests, and infrastructure
            to identify the workflow behind suspicious activity — even when attackers
            rotate every identifier.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Link href="/investigate">
              <Button size="lg" variant="primary">
                <Search className="h-4 w-4" />
                Analyze an Incident
              </Button>
            </Link>
            <Link href="/rescue">
              <Button size="lg" variant="danger" className="border border-red-500/40 bg-red-500/15 text-red-300 hover:bg-red-500/25">
                <span className="h-2 w-2 rounded-full bg-red-400 animate-pulse mr-1" />
                I Already Paid (Rescue)
              </Button>
            </Link>
            <Link href="/lab">
              <Button size="lg" variant="outline">
                <PlayCircle className="h-4 w-4" />
                Explore Demo
              </Button>
            </Link>
          </div>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 pt-4 text-xs text-ink-dim">
            <span className="inline-flex items-center gap-1.5">
              <Fingerprint className="h-3.5 w-3.5" /> Scam fingerprinting
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Network className="h-3.5 w-3.5" /> Graph correlation
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Activity className="h-3.5 w-3.5" /> Journey detection
            </span>
          </div>
        </div>

        {/* Three.js Threat Intelligence Network — desktop only */}
        <div className="order-first h-72 w-full overflow-hidden rounded-2xl border border-line bg-elevated lg:order-last lg:h-96">
          <ThreatNetworkScene />
        </div>
      </section>

      {/* ── Product story: identifiers change, workflow survives ────── */}
      <section className="space-y-6">
        <div className="space-y-2 text-center">
          <div className="eyebrow">Why ScamGraph</div>
          <h2 className="text-2xl font-semibold tracking-tight text-ink sm:text-3xl">
            Attackers change identifiers.
            <br />
            <span className="text-ink-muted">The workflow survives.</span>
          </h2>
        </div>

        <GsapStagger className="grid gap-4 md:grid-cols-[1fr_auto_1fr] md:items-center">
          {/* Campaign A */}
          <div className="panel p-5">
            <div className="eyebrow mb-3">Known Campaign A</div>
            <dl className="space-y-2 text-sm">
              {[
                ["Brand", "SBI"],
                ["Phone", "+9198XXXXXX01"],
                ["Domain", "sbi-kyc-portal.online"],
                ["UPI", "scammer.ops@oksbi"],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4">
                  <dt className="text-ink-dim">{k}</dt>
                  <dd className="font-mono text-ink-muted">{v}</dd>
                </div>
              ))}
            </dl>
          </div>

          {/* vs divider */}
          <div className="flex flex-col items-center justify-center px-2 py-2">
            <span className="text-ink-dim text-xs font-mono uppercase tracking-wider2 bg-surface-2 border border-border px-2 py-1 rounded">
              vs
            </span>
          </div>

          {/* New incident */}
          <div className="panel p-5">
            <div className="eyebrow mb-3">New Incident</div>
            <dl className="space-y-2 text-sm">
              {[
                ["Brand", "HDFC"],
                ["Phone", "+9177XXXXXX99"],
                ["Domain", "hdfc-secure-validate.xyz"],
                ["UPI", "ops.verify@yb..."],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4">
                  <dt className="text-ink-dim">{k}</dt>
                  <dd className="font-mono text-ink-muted">{v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </GsapStagger>

        <GsapStagger className="grid gap-4 sm:grid-cols-2">
          <div className="panel-elevated p-5">
            <div className="flex items-center justify-between">
              <span className="eyebrow">Identifier overlap</span>
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-danger/10 text-danger border border-danger/20">
                <X className="h-4 w-4" />
              </span>
            </div>
            <p className="mt-3 text-2xl font-semibold text-ink font-mono">0 matches</p>
            <p className="mt-1 text-sm text-ink-dim">Phone, domain, payment, brand — all different.</p>
          </div>
          <div className="panel-elevated p-5">
            <div className="flex items-center justify-between">
              <span className="eyebrow">Workflow similarity</span>
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-safe/10 text-safe border border-safe/20">
                <Check className="h-4 w-4" />
              </span>
            </div>
            <p className="mt-3 text-2xl font-semibold text-safe">High</p>
            <p className="mt-1 text-sm text-ink-dim">Same grooming sequence behind new identifiers.</p>
          </div>
        </GsapStagger>

        <p className="text-center text-sm font-medium text-ink-muted pt-2">
          ScamGraph recognizes the journey behind the identifiers.
        </p>
      </section>
    </div>
  );
}
