'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function GuardDecisionPage() {
  const [declined, setDeclined] = useState<boolean>(false);
  const [resolved, setResolved] = useState<boolean>(false);

  return (
    <div className="w-full bg-ground py-4 sm:py-8">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 pb-16">
        {/* Case Context Bar */}
        <div className="w-full flex flex-wrap items-center justify-between gap-3 py-2 mb-6 border-b border-border-divider">
          <div className="flex items-center gap-2 text-xs">
            <Link
              href="/guard"
              className="inline-flex items-center gap-1 text-viz-neutral hover:text-primary transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Guard</span>
            </Link>
            <span className="text-viz-neutral">·</span>
            <span className="text-on-surface font-semibold">Decision</span>
            <span className="text-viz-neutral">·</span>
            <span className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border-divider text-viz-neutral font-mono">
              Case #SG-84920
            </span>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs text-viz-neutral bg-surface px-2.5 py-1 rounded-full border border-border-divider shadow-sm">
              <span className="w-2 h-2 rounded-full bg-secondary"></span>
              Updated just now
            </span>
          </div>
        </div>

        {/* Hero: Canonical Intervention Output (High Concern / Stop Before Approve) */}
        <section className="w-full mb-8">
          <div className="bg-tone-warning-strong-bg rounded-xl p-6 sm:p-8 shadow-sm border border-tone-warning-strong-text/20 relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-1.5 bg-viz-warning"></div>
            <div className="flex flex-col md:flex-row items-start gap-6 justify-between">
              <div className="flex items-start gap-4 max-w-3xl">
                {/* State 5 Warning Icon */}
                <div className="w-12 h-12 rounded-xl bg-tone-warning-bg border border-tone-warning-text/20 flex items-center justify-center shrink-0 shadow-sm text-viz-warning">
                  <span className="material-symbols-outlined text-[28px]">warning</span>
                </div>
                <div className="flex flex-col gap-1.5">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-warning-bg text-tone-warning-strong-text text-[11px] font-bold uppercase tracking-wider border border-tone-warning-text/20">
                      ▲ Intervention Engine Output
                    </span>
                    <span className="text-xs text-viz-neutral font-mono">Topological Rule #U-3829</span>
                  </div>
                  <h1 className="text-2xl sm:text-3xl font-bold text-tone-warning-strong-text tracking-tight">
                    Stop and verify before you approve
                  </h1>
                  <p className="text-sm text-on-surface leading-relaxed mt-1">
                    Do not approve this collect request. Legitimate state electricity distribution utilities never collect bill arrears via incoming UPI collect requests, third-party payment links, or personal WhatsApp calls.
                  </p>
                </div>
              </div>

              {/* Threat Assessment Badge */}
              <div className="flex flex-col gap-2 shrink-0 self-stretch md:self-auto bg-surface/90 backdrop-blur rounded-lg p-4 border border-border-divider shadow-sm">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-[11px] text-viz-neutral uppercase tracking-wide">Threat Assessment</span>
                  <span className="text-xs font-bold text-tone-danger-text flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-error"></span> High concern
                  </span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs text-viz-neutral">Intervention Node</span>
                  <span className="text-xs text-on-surface font-semibold">Payment boundary safeguard</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="text-xs text-viz-neutral">Inspection Depth</span>
                  <span className="text-xs text-primary font-semibold bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                    Complete inspection (3/3)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Two-Column Primary Body Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Actions & Empirical Lineage (7 cols) */}
          <div className="lg:col-span-7 flex flex-col gap-8">
            {/* Recommended Immediate Actions */}
            <section className="flex flex-col gap-4">
              <div className="flex items-baseline justify-between">
                <h2 className="text-lg font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">checklist</span>
                  <span>Recommended immediate actions</span>
                </h2>
                <span className="text-xs text-viz-neutral">Strict priority sequence</span>
              </div>

              <div className="bg-surface rounded-xl p-6 border border-border-divider shadow-sm flex flex-col gap-5">
                {/* Step 1: Human Grounding & Official Portal */}
                <div className="flex flex-col gap-2 pb-5 border-b border-border-divider">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-primary uppercase tracking-wider">Step 1 · Ground yourself</span>
                    <span className="text-[11px] text-viz-neutral">Zero irreversible risk</span>
                  </div>
                  <p className="text-sm text-on-surface font-medium leading-relaxed">
                    Pause communication immediately. Fraud operators rely on synthetic urgency to isolate you.
                  </p>
                  <div className="flex flex-wrap items-center gap-3 mt-2">
                    <a
                      href="tel:1912"
                      className="inline-flex items-center justify-center gap-1.5 h-10 px-4 rounded-full bg-primary text-white text-xs font-semibold hover:bg-primary-container transition-colors shadow-sm"
                    >
                      <span className="material-symbols-outlined text-[16px]">contact_phone</span>
                      <span>Talk to someone you trust</span>
                    </a>
                    <a
                      className="inline-flex items-center justify-center gap-1.5 h-10 px-4 rounded-lg bg-surface-subtle border border-border-divider text-on-surface text-xs font-semibold hover:bg-surface transition-colors"
                      href="https://1912.co.in"
                      rel="noopener noreferrer"
                      target="_blank"
                    >
                      <span className="material-symbols-outlined text-[16px]">public</span>
                      <span>Verify on official utility portal</span>
                    </a>
                  </div>
                </div>

                {/* Step 2: UPI Action */}
                <div className="flex flex-col gap-2 pb-5 border-b border-border-divider">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-tone-warning-strong-text uppercase tracking-wider">
                      Step 2 · Payment rejection
                    </span>
                    <span className="text-xs text-error font-bold">Do not enter PIN</span>
                  </div>
                  <p className="text-sm text-on-surface font-medium leading-relaxed">
                    Open your UPI app (PhonePe, Google Pay, BHIM, or Paytm) and decline the incoming collect request.
                  </p>
                  <p className="text-xs text-viz-neutral leading-relaxed">
                    Entering your 4-digit or 6-digit UPI PIN authorizes money leaving your account. You never need to enter a UPI PIN to receive money or clear a valid payment receipt.
                  </p>
                  <div className="mt-2 flex items-center gap-3">
                    <button
                      onClick={() => setDeclined(!declined)}
                      type="button"
                      className={`inline-flex items-center gap-2 h-10 px-4 rounded-lg text-xs font-bold transition-all border ${declined
                          ? 'bg-tone-info-bg text-tone-info-text border-tone-info-text/30'
                          : 'bg-surface-subtle text-on-surface border-border-divider hover:bg-surface'
                        }`}
                    >
                      <span className={`material-symbols-outlined text-[18px] ${declined ? 'text-secondary' : 'text-error'}`}>
                        {declined ? 'check_circle' : 'cancel'}
                      </span>
                      <span>{declined ? 'Request confirmed declined' : 'I have declined the request in my app'}</span>
                    </button>
                  </div>
                </div>

                {/* Step 3: Confirmation link */}
                <div className="flex items-center justify-between pt-1">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-secondary text-[20px]">task_alt</span>
                    <span className="text-xs text-on-surface">I paused — no funds or PINs were sent</span>
                  </div>
                  <button
                    onClick={() => setResolved(true)}
                    className="text-xs text-primary font-bold hover:underline"
                    type="button"
                  >
                    {resolved ? '✓ Case resolved' : 'Mark case resolved'}
                  </button>
                </div>
              </div>

              {/* Emergency Affordance Card */}
              <div className="bg-tone-danger-bg rounded-xl p-4 sm:p-5 border border-tone-danger-text/20 shadow-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-tone-danger-text text-[24px] shrink-0 mt-0.5">crisis_alert</span>
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-tone-danger-strong-text">Already paid or shared something?</span>
                    <p className="text-xs text-tone-danger-text mt-0.5 leading-relaxed">
                      Every minute counts. Initiate bank rail freezes and statutory ombudsman reporting immediately.
                    </p>
                  </div>
                </div>
                <Link
                  href="/rescue"
                  className="inline-flex items-center justify-center shrink-0 h-10 px-4 rounded-lg bg-error text-white text-xs font-bold hover:bg-tone-danger-strong-text transition-colors shadow-sm whitespace-nowrap"
                >
                  Go directly to Rescue triage →
                </Link>
              </div>
            </section>

            {/* Why We Recommend Stopping (Topological Reasons) */}
            <section className="flex flex-col gap-4">
              <div className="flex items-baseline justify-between">
                <h2 className="text-lg font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[20px]">account_tree</span>
                  <span>Why we recommend stopping</span>
                </h2>
                <span className="text-xs text-viz-neutral">3 topological indicators flagged</span>
              </div>

              <div className="flex flex-col gap-3">
                {/* Reason Card 1 */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-on-surface flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-viz-warning"></span>
                      Manufactured evening deadline
                    </span>
                    <span className="text-[11px] text-viz-neutral font-mono">TIMING_ANOMALY</span>
                  </div>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    The threat to cut electricity tonight at 9:30 PM violates statutory state electricity regulatory code (§56 Electricity Act 2003), which mandates a written 15-day clear notice period prior to any disconnection.
                  </p>
                  <div className="bg-surface-subtle rounded-lg p-3 mt-1 flex flex-col gap-1 border border-border-divider">
                    <span className="text-[10px] text-viz-neutral uppercase font-mono">Provenance (Original user message snippet)</span>
                    <p className="text-xs text-on-surface font-mono italic leading-relaxed">
                      &ldquo;Dear Consumer, Your electricity power will be disconnected tonight at 9:30 PM from the power sub-division office because your previous month bill was not updated. Immediately call 98******10...&rdquo;
                    </p>
                  </div>
                </div>

                {/* Reason Card 2 */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-on-surface flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-error"></span>
                      Inbound UPI collect request vector
                    </span>
                    <span className="text-[11px] text-viz-neutral font-mono">VECTOR_UPI_COLLECT</span>
                  </div>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    Approving an incoming collect request on PhonePe, Google Pay, or Paytm debits money from your account rather than crediting any funds or settling institutional billing accounts.
                  </p>
                  <div className="bg-surface-subtle rounded-lg p-3 mt-1 flex flex-col gap-1 border border-border-divider">
                    <span className="text-[10px] text-viz-neutral uppercase font-mono">Provenance (Confirmed user interaction telemetry)</span>
                    <div className="flex items-center justify-between text-on-surface font-mono text-xs">
                      <span>Target Action: Approve Collect Request</span>
                      <span className="text-error font-bold">Risk: -₹11,450 debit</span>
                    </div>
                  </div>
                </div>

                {/* Reason Card 3 */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-on-surface flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-viz-warning"></span>
                      Unregistered personal phone contact
                    </span>
                    <span className="text-[11px] text-viz-neutral font-mono">SENDER_SPOOF_RISK</span>
                  </div>
                  <p className="text-xs text-on-surface-variant leading-relaxed">
                    Communications originated from a private prepaid 10-digit mobile number (+91 98******10) instead of a certified governmental utility telecommunication alphanumeric header (e.g., VM-BESCOM or JD-TNEB).
                  </p>
                  <div className="bg-surface-subtle rounded-lg p-3 mt-1 flex flex-col gap-1 border border-border-divider">
                    <span className="text-[10px] text-viz-neutral uppercase font-mono">Provenance (Extracted entity node)</span>
                    <p className="text-xs text-on-surface font-mono leading-relaxed">
                      Caller identifier: +91 98451 98210 · Unverified personal SIM (Reported 14x in National Cybercrime Database within 48h)
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* Reference Evidence Dossier */}
            <section className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-2">
              <h3 className="text-xs font-bold text-on-surface uppercase tracking-wide">Inspection Integrity Hash</h3>
              <div className="flex items-center justify-between py-1 border-b border-border-divider font-mono text-xs text-viz-neutral">
                <span>Engine Model: SovereignGuard-v4.8</span>
                <span>SHA-256: 7d49...a92b</span>
              </div>
              <p className="text-xs text-viz-neutral leading-relaxed">
                The topological rules triggered above represent high-confidence utility bill fraud topologies codified by public interest security research and municipal electricity distribution advisories.
              </p>
            </section>
          </div>

          {/* Right Column: Journey Context & Guardrails (5 cols) */}
          <div className="lg:col-span-5 flex flex-col gap-6 sticky top-24">
            {/* Scam Journey Mini-Track Card */}
            <section className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-4">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <h2 className="text-sm font-bold text-on-surface flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-primary text-[18px]">timeline</span>
                  <span>Where you are on the Scam Journey</span>
                </h2>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                You paused right at the payment boundary before irreversible financial authorization took place.
              </p>

              {/* Visual Topological Mini-Track */}
              <div className="flex flex-col gap-2 py-1">
                {/* Node 1 */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex flex-col items-center">
                    <span className="w-5 h-5 rounded-full bg-primary text-white flex items-center justify-center text-[10px] font-bold shrink-0">●</span>
                    <div className="w-0.5 h-6 bg-primary"></div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-on-surface">1. Contact Initiated</span>
                    <span className="text-[11px] text-viz-neutral">SMS threat received with fake power cut warning (Observed)</span>
                  </div>
                </div>

                {/* Node 2 */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex flex-col items-center">
                    <span className="w-5 h-5 rounded-full bg-primary text-white flex items-center justify-center text-[10px] font-bold shrink-0">●</span>
                    <div className="w-0.5 h-6 bg-primary"></div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-on-surface">2. Trust &amp; Authority Mimicry</span>
                    <span className="text-[11px] text-viz-neutral">Impersonated electricity sub-division officer (Observed)</span>
                  </div>
                </div>

                {/* Node 3 */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex flex-col items-center">
                    <span className="w-5 h-5 rounded-full bg-primary text-white flex items-center justify-center text-[10px] font-bold shrink-0">●</span>
                    <div className="w-0.5 h-6 bg-viz-warning"></div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-on-surface">3. Psychological Urgency Tactic</span>
                    <span className="text-[11px] text-viz-neutral">&quot;Disconnected in 45 minutes&quot; ultimatum (Observed)</span>
                  </div>
                </div>

                {/* Boundary Line: YOU ARE HERE */}
                <div className="my-1 p-3 rounded-lg bg-tone-warning-strong-bg border border-tone-warning-text/30 shadow-sm flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-viz-warning shrink-0 animate-pulse"></div>
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-tone-warning-strong-text uppercase tracking-wide">
                      You are here (Payment Boundary)
                    </span>
                    <span className="text-[11px] text-tone-warning-text">
                      Incoming UPI Collect Request received · Funds safe
                    </span>
                  </div>
                </div>

                {/* Node 4 */}
                <div className="flex items-start gap-3 relative mt-1">
                  <div className="flex flex-col items-center">
                    <span className="w-5 h-5 rounded-full bg-surface-subtle border border-border-divider text-viz-neutral flex items-center justify-center text-[10px] font-bold shrink-0">○</span>
                    <div className="w-0.5 h-6 bg-border-divider border-dashed"></div>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-medium text-viz-neutral">4. Financial Authorization</span>
                    <span className="text-[11px] text-viz-neutral">Approval of collect request / UPI PIN disclosure (Inferred)</span>
                  </div>
                </div>

                {/* Node 5 */}
                <div className="flex items-start gap-3 relative">
                  <div className="flex flex-col items-center">
                    <span className="w-5 h-5 rounded-full bg-surface-subtle border border-border-divider text-viz-neutral flex items-center justify-center text-[10px] font-bold shrink-0">◌</span>
                  </div>
                  <div className="flex flex-col">
                    <span className="text-xs font-medium text-viz-neutral">5. Re-connection Fee / Secondary Loop</span>
                    <span className="text-[11px] text-viz-neutral">Follow-up extortion for &quot;line restoration&quot; (Possible next)</span>
                  </div>
                </div>
              </div>

              <div className="bg-surface-subtle p-3 rounded-lg border border-border-divider flex items-center gap-2 text-primary text-xs font-semibold">
                <span className="material-symbols-outlined text-[18px]">security</span>
                <span>Stopping now breaks this progression cycle permanently.</span>
              </div>
            </section>

            {/* Statutory Truth Guardrail */}
            <section className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-2">
              <div className="flex items-center gap-2 text-on-surface">
                <span className="material-symbols-outlined text-primary text-[18px]">gavel</span>
                <h3 className="text-xs font-bold uppercase tracking-wider">Statutory Truth Guardrail (§2.2 &amp; D13)</h3>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                ScamGraph does not possess direct banking rail integration and cannot automatically freeze interbank UPI transactions on your behalf.
              </p>
              <p className="text-xs text-on-surface font-semibold leading-relaxed">
                Your safest action is to reject the collect request directly inside your payment app and contact the official National Power Helpline.
              </p>
            </section>

            {/* Statutory Helpline Card */}
            <section className="bg-surface-subtle rounded-xl p-5 border border-border-divider shadow-sm flex flex-col gap-3">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <span className="text-xs font-bold text-on-surface flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px] text-primary">verified</span>
                  Verified Statutory Helplines
                </span>
                <span className="text-[11px] text-viz-neutral">Direct Toll-Free</span>
              </div>

              {/* Helpline 1 */}
              <div className="flex items-center justify-between bg-surface rounded-lg p-3 border border-border-divider shadow-sm">
                <div className="flex flex-col">
                  <span className="text-[10px] text-viz-neutral uppercase">Electricity Outage &amp; Billing Discrepancy</span>
                  <span className="text-xs font-bold text-on-surface">National Power Consumer Helpline</span>
                  <span className="text-[11px] text-secondary font-medium">24x7 Government of India Service</span>
                </div>
                <a
                  className="inline-flex items-center justify-center gap-1 h-8 px-3 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors"
                  href="tel:1912"
                >
                  <span className="material-symbols-outlined text-[15px]">call</span>
                  <span>1912</span>
                </a>
              </div>

              {/* Helpline 2 */}
              <div className="flex items-center justify-between bg-surface rounded-lg p-3 border border-border-divider shadow-sm">
                <div className="flex flex-col">
                  <span className="text-[10px] text-viz-neutral uppercase">Cyber Fraud &amp; Financial Loss</span>
                  <span className="text-xs font-bold text-on-surface">National Cyber Crime Helpline</span>
                  <span className="text-[11px] text-viz-neutral">Direct I4C Hotline</span>
                </div>
                <a
                  className="inline-flex items-center justify-center gap-1 h-8 px-3 rounded-full bg-surface-subtle border border-border-divider text-on-surface text-xs font-bold hover:bg-surface transition-colors"
                  href="tel:1930"
                >
                  <span className="material-symbols-outlined text-[15px]">call</span>
                  <span>1930</span>
                </a>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
  );
}
