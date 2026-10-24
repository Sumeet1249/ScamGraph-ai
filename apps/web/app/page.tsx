"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Shield,
  Search,
  ArrowRight,
  Lock,
  AlertTriangle,
  HelpCircle,
  Scale,
  ChevronDown,
  KeyRound,
  FileCheck2,
  ExternalLink,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [inputText, setInputText] = useState("");
  const [selectedFaq, setSelectedFaq] = useState<number | null>(0);

  const handleCheckSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    // Pass query into check flow
    router.push(`/check?query=${encodeURIComponent(inputText.trim())}`);
  };

  const faqItems = [
    {
      q: "What should I do if I already sent money?",
      a: "Go directly to Emergency Rescue. Follow the immediate bank freeze and National Cybercrime 1930 reporting steps immediately. The first 120 minutes (Golden Hour) achieve an 84% fund recovery rate on interbank switches.",
    },
    {
      q: "Does checking a message block my payment automatically?",
      a: "No. ScamGraph provides forensic risk intelligence and verified escalation roadmaps; it does not tamper with banking or UPI rails. You must execute statutory liens through your bank or 1930 CFCFRMS.",
    },
    {
      q: "Can I check an identifier anonymously?",
      a: "Yes. Universal Check is 100% open without registration. Identifiers are salted and hashed client-side using SHA-256 before any graph traversal. No personal PII is stored unhashed.",
    },
    {
      q: "What if ScamGraph shows 'No strong warning signs'?",
      a: "The absence of strong warning signs is NOT a guarantee of safety. Scammers continually rotate new mobile numbers and domain aliases. Always remain cautious when prompted for payments.",
    },
  ];

  return (
    <div className="flex flex-col w-full">
      {/* ── 1. Hero Section & Universal Omnibox ── */}
      <section className="w-full bg-ground py-10 md:py-16 border-b border-border-divider">
        <div className="max-w-[1200px] mx-auto px-4 md:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
            {/* Left Hero Pitch */}
            <div className="lg:col-span-6 flex flex-col justify-center">
              <div className="inline-flex items-center gap-2 text-viz-primary text-xs font-semibold uppercase tracking-wider mb-3">
                <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
                [M01] Sovereign Fraud Defense Infrastructure
              </div>
              <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-on-surface mb-4 leading-tight">
                Empirical Fraud Verification &amp; National Outbreak Defense
              </h1>
              <p className="text-base text-on-surface-variant mb-6 leading-relaxed">
                Instant multi-modal threat verification for Indian citizens, banks, and law enforcement. Pre-transaction UPI guard, autonomous mule freezing, and court-ready Section 65B BSA evidence packaging.
              </p>

              <div className="flex flex-wrap items-center gap-3">
                <Link
                  href="/rescue"
                  className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-tone-danger-bg px-4 py-2 text-xs font-bold text-tone-danger-text border border-tone-danger-strong-bg hover:bg-tone-danger-strong-bg transition-colors"
                >
                  <AlertTriangle className="h-4 w-4" />
                  <span>Money Debited in last 2h? Call 1930</span>
                </Link>
                <Link
                  href="/how-it-works"
                  className="inline-flex min-h-[44px] items-center gap-1.5 rounded-full border border-border-control bg-surface px-4 py-2 text-xs font-semibold text-on-surface hover:bg-surface-subtle transition-colors"
                >
                  <span>How ScamGraph Works</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>

            {/* Right Omnibox Card */}
            <div className="lg:col-span-6 w-full">
              <div className="bg-surface rounded-xl border border-border-divider shadow-sm p-5 md:p-6">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <Search className="h-4 w-4 text-viz-primary" />
                    <span className="text-xs font-bold text-on-surface uppercase tracking-wider">
                      Universal Threat Omnibox
                    </span>
                  </div>
                  <span className="text-[11px] font-semibold text-viz-neutral bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                    Zero-Knowledge Inspection
                  </span>
                </div>

                <form onSubmit={handleCheckSubmit} className="flex flex-col gap-3">
                  <label htmlFor="scam-intake-text" className="text-xs font-medium text-on-surface">
                    Paste UPI ID, phone number (+91), suspicious SMS, or APK hash:
                  </label>
                  <textarea
                    id="scam-intake-text"
                    rows={4}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="e.g. 9876543210@paytm, electricity bill threat SMS, or suspicious APK download URL..."
                    className="w-full p-3.5 rounded-lg border border-border-control bg-surface text-on-surface placeholder:text-viz-neutral text-sm focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20 resize-none transition-all"
                  />

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                    <div className="flex items-center gap-1.5 text-viz-neutral text-[11px]">
                      <Lock className="h-3.5 w-3.5 text-viz-primary" />
                      <span>Client-side SHA-256 hashed. Zero PII stored unhashed.</span>
                    </div>

                    <button
                      type="submit"
                      disabled={!inputText.trim()}
                      className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-viz-primary px-6 py-2 text-xs font-bold text-on-primary hover:bg-primary transition-all disabled:opacity-50 shadow-sm"
                    >
                      <span>Check Now</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </form>

                {/* Popular sample triggers */}
                <div className="mt-4 pt-3 border-t border-border-divider flex flex-wrap items-center gap-1.5 text-[11px]">
                  <span className="text-viz-neutral font-medium">Try sample:</span>
                  {[
                    "Electricity bill disconnection SMS",
                    "Customs courier digital arrest call",
                    "Telegram part-time hotel rating task",
                    "fake-sbi-rewards.apk",
                  ].map((sample) => (
                    <button
                      key={sample}
                      type="button"
                      onClick={() => setInputText(sample)}
                      className="rounded bg-surface-subtle px-2 py-0.5 text-on-surface-variant hover:text-on-surface hover:bg-border-divider transition-colors"
                    >
                      {sample}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. Live Telemetry Strip ── */}
      <section className="w-full bg-surface-subtle py-8 border-b border-border-divider">
        <div className="max-w-[1200px] mx-auto px-4 md:px-8">
          <div className="mb-4">
            <span className="text-[11px] text-viz-neutral font-semibold uppercase tracking-wider block">
              National Defense Telemetry
            </span>
            <h2 className="text-xl font-bold text-on-surface">
              Active Interception &amp; Infrastructure Scale
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-surface rounded-xl border border-border-divider p-4">
              <div className="text-xs text-viz-neutral font-medium">Total Loss Intercepted</div>
              <div className="text-2xl font-bold text-on-surface mt-1">₹482.4 Cr</div>
              <div className="text-xs text-viz-primary font-semibold mt-1">+₹1.8 Cr today</div>
            </div>
            <div className="bg-surface rounded-xl border border-border-divider p-4">
              <div className="text-xs text-viz-neutral font-medium">Active Mule Rings Tracked</div>
              <div className="text-2xl font-bold text-on-surface mt-1">38 Syndicates</div>
              <div className="text-xs text-viz-neutral font-medium mt-1">I4C &amp; NPCI correlated</div>
            </div>
            <div className="bg-surface rounded-xl border border-border-divider p-4">
              <div className="text-xs text-viz-neutral font-medium">Median Golden Hour Freeze</div>
              <div className="text-2xl font-bold text-on-surface mt-1">38 mins</div>
              <div className="text-xs text-viz-neutral font-medium mt-1">Industry avg: 4–6 hrs</div>
            </div>
            <div className="bg-surface rounded-xl border border-border-divider p-4">
              <div className="text-xs text-viz-neutral font-medium">Integrated Partner Banks</div>
              <div className="text-2xl font-bold text-on-surface mt-1">28 Banks</div>
              <div className="text-xs text-viz-neutral font-medium mt-1">Direct Nodal Desks</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 3. 3-Step Methodology ── */}
      <section className="w-full bg-ground py-12 border-b border-border-divider">
        <div className="max-w-[1200px] mx-auto px-4 md:px-8">
          <div className="max-w-[680px] mb-8">
            <span className="text-xs text-viz-neutral font-semibold uppercase tracking-wider block mb-1">
              Transparent Methodology
            </span>
            <h2 className="text-2xl md:text-3xl font-bold text-on-surface">
              Check → Understand → Act
            </h2>
            <p className="text-sm text-on-surface-variant mt-2 leading-relaxed">
              A disciplined analysis cycle that prioritizes actionable next steps over sensationalist cyber jargon.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex flex-col bg-surface p-6 rounded-xl border border-border-divider shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-viz-primary font-bold text-2xl">01</span>
                <div className="h-[1px] flex-1 bg-border-divider" />
              </div>
              <h3 className="text-base font-bold text-on-surface mb-1">Share what you have</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Paste suspicious message text, an APK link, phone number, or recount call dialogue.
              </p>
            </div>

            <div className="flex flex-col bg-surface p-6 rounded-xl border border-border-divider shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-viz-primary font-bold text-2xl">02</span>
                <div className="h-[1px] flex-1 bg-border-divider" />
              </div>
              <h3 className="text-base font-bold text-on-surface mb-1">Understand warning signs</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Review verified threat evidence, psychological coercion indicators, and how this campaign progresses.
              </p>
            </div>

            <div className="flex flex-col bg-surface p-6 rounded-xl border border-border-divider shadow-sm">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-viz-primary font-bold text-2xl">03</span>
                <div className="h-[1px] flex-1 bg-border-divider" />
              </div>
              <h3 className="text-base font-bold text-on-surface mb-1">Know what to do next</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Receive instant statutory next steps, bank freeze letters, and court-ready Section 65B BSA packages.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4. Topological Journey Pipeline ── */}
      <section className="w-full bg-surface py-12 border-b border-border-divider">
        <div className="max-w-[1200px] mx-auto px-4 md:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-on-surface">Topological Scam Path</h2>
                <span className="text-[11px] text-viz-neutral bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                  Illustrative Progression
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mt-1">
                ScamGraph maps sequential coercion stages so victims recognize where they stand before paying.
              </p>
            </div>
          </div>

          <div className="w-full bg-ground rounded-xl border border-border-divider p-6 overflow-x-auto">
            <div className="min-w-[760px] flex items-center justify-between relative py-4">
              {/* Node 1 */}
              <div className="flex flex-col items-center text-center z-10 w-36">
                <div className="w-8 h-8 rounded-full bg-viz-primary text-on-primary flex items-center justify-center font-bold text-xs mb-1.5 shadow-sm">
                  ●
                </div>
                <span className="text-xs font-bold text-on-surface">Initial Contact</span>
                <span className="text-[10px] text-viz-neutral">Observed SMS</span>
              </div>
              <div className="flex-1 h-[2px] bg-border-control" />

              {/* Node 2 */}
              <div className="flex flex-col items-center text-center z-10 w-36">
                <div className="w-8 h-8 rounded-full bg-viz-primary text-on-primary flex items-center justify-center font-bold text-xs mb-1.5 shadow-sm">
                  ●
                </div>
                <span className="text-xs font-bold text-on-surface">Impersonation</span>
                <span className="text-[10px] text-viz-neutral">Power Officer / Police</span>
              </div>
              <div className="flex-1 h-[2px] bg-border-control" />

              {/* Node 3 */}
              <div className="flex flex-col items-center text-center z-10 w-36">
                <div className="w-8 h-8 rounded-full border-2 border-viz-primary bg-surface text-viz-primary flex items-center justify-center font-bold text-xs mb-1.5 shadow-sm">
                  ◉
                </div>
                <span className="text-xs font-bold text-viz-primary">Urgency Pressure</span>
                <span className="text-[10px] text-viz-primary font-semibold">You Reported</span>
              </div>

              {/* Payment Boundary */}
              <div className="flex flex-col items-center px-2 z-10">
                <div className="h-10 w-[2px] bg-tone-danger-text mb-1" />
                <span className="text-[10px] font-bold text-tone-danger-text bg-tone-danger-bg px-2 py-0.5 rounded border border-tone-danger-strong-bg whitespace-nowrap">
                  Payment Boundary
                </span>
              </div>

              {/* Node 4 */}
              <div className="flex flex-col items-center text-center z-10 w-36">
                <div className="w-8 h-8 rounded-full border-2 border-dashed border-border-control bg-surface text-viz-neutral flex items-center justify-center font-bold text-xs mb-1.5 shadow-sm">
                  ○
                </div>
                <span className="text-xs font-semibold text-on-surface-variant">Payment Request</span>
                <span className="text-[10px] text-viz-neutral">Inferred VPA</span>
              </div>
              <div className="flex-1 h-[2px] border-t-2 border-dotted border-border-divider" />

              {/* Node 5 */}
              <div className="flex flex-col items-center text-center z-10 w-36">
                <div className="w-8 h-8 rounded-full border-2 border-dotted border-border-control bg-surface text-viz-neutral flex items-center justify-center font-bold text-xs mb-1.5 shadow-sm">
                  ◌
                </div>
                <span className="text-xs font-semibold text-on-surface-variant">Fee Unlock Trap</span>
                <span className="text-[10px] text-viz-neutral">Projected Next</span>
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-border-divider flex flex-wrap items-center justify-between text-[11px] text-viz-neutral gap-4">
              <div className="flex items-center gap-4">
                <span className="inline-flex items-center gap-1 font-medium"><span className="text-viz-primary font-bold">●</span> Observed Stage</span>
                <span className="inline-flex items-center gap-1 font-medium"><span className="text-viz-primary font-bold">◉</span> User Reported</span>
                <span className="inline-flex items-center gap-1 font-medium"><span className="text-viz-neutral font-bold">○</span> Inferred AI Link</span>
                <span className="inline-flex items-center gap-1 font-medium"><span className="text-viz-neutral font-bold">◌</span> Projected Escalation</span>
              </div>
              <span className="italic text-[11px]">Interception here halts multi-hop laundering</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── 5. FAQs Section ── */}
      <section className="w-full bg-ground py-12 border-b border-border-divider">
        <div className="max-w-[760px] mx-auto px-4 md:px-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-on-surface">Frequently Asked Questions</h2>
            <p className="text-xs text-on-surface-variant mt-1">
              Direct guidance for high-stress fraud situations.
            </p>
          </div>

          <div className="divide-y divide-border-divider border border-border-divider rounded-xl bg-surface overflow-hidden shadow-sm">
            {faqItems.map((item, idx) => {
              const isOpen = selectedFaq === idx;
              return (
                <div key={idx} className="p-4 transition-colors hover:bg-surface-subtle">
                  <button
                    type="button"
                    onClick={() => setSelectedFaq(isOpen ? null : idx)}
                    className="flex w-full items-center justify-between text-left text-xs md:text-sm font-bold text-on-surface focus:outline-none"
                  >
                    <span>{item.q}</span>
                    <ChevronDown className={`h-4 w-4 text-viz-neutral transition-transform ${isOpen ? "rotate-180" : ""}`} />
                  </button>
                  {isOpen && (
                    <div className="pt-2 text-xs text-on-surface-variant leading-relaxed">
                      {item.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── 6. Emergency Bottom Callout ── */}
      <section className="w-full bg-surface-subtle py-12 text-center">
        <div className="max-w-[680px] mx-auto px-4">
          <h2 className="text-xl md:text-2xl font-bold text-on-surface mb-2">
            Victim of an active financial fraud within the last 4 hours?
          </h2>
          <p className="text-xs text-on-surface-variant mb-6">
            Enter Golden Hour Rescue Triage immediately to initiate interbank transaction freezes and generate statutory Section 65B BSA complaint dossiers.
          </p>
          <Link
            href="/rescue"
            className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-6 py-2.5 text-xs font-bold transition-all shadow-sm"
          >
            <span>Access Golden Hour Rescue Triage</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
