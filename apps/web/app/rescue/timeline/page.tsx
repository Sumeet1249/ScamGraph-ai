'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function RescueTimelinePage() {
  const [filter, setFilter] = useState<string>('all');
  const [showDiff, setShowDiff] = useState<boolean>(false);

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6">
        {/* Breadcrumbs / Context Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 pb-3 border-b border-border-divider">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <Link
              href="/rescue/dashboard"
              className="text-primary hover:text-primary-container flex items-center gap-1 font-semibold transition-colors"
            >
              <span className="material-symbols-outlined text-[15px]">arrow_back</span>
              <span>Back to Rescue Dashboard</span>
            </Link>
            <span className="text-viz-neutral">/</span>
            <span className="text-viz-neutral">Timeline Reconstruction</span>
            <span className="text-viz-neutral">/</span>
            <span className="font-bold text-viz-text font-mono">CASE #SG-84920</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-subtle text-viz-text text-xs border border-border-divider">
              <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse"></span>
              <span className="font-medium">Live chronological graph sync active</span>
            </div>
            <div className="px-2 py-0.5 rounded bg-tone-warning-strong-bg text-tone-warning-strong-text text-[11px] font-bold uppercase tracking-wider border border-tone-warning-text/20">
              Mode B: Active Rescue
            </div>
          </div>
        </div>

        {/* Case Context Indicator Bar */}
        <div className="mt-3 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 px-4 py-2.5 rounded bg-surface-subtle border border-border-divider">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[18px] text-viz-primary">account_tree</span>
            <span className="text-xs font-bold text-viz-text uppercase tracking-wide">Incident Context:</span>
            <span className="text-xs text-viz-text font-medium">State Electricity Bill Disconnection — UPI Collect Vector</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-viz-neutral">
            <span className="material-symbols-outlined text-[15px] text-viz-primary">verified</span>
            <span>Cryptographic provenance ledger active</span>
          </div>
        </div>

        {/* Page Title and Overview Header */}
        <div className="mt-6 flex flex-col lg:flex-row lg:items-end justify-between gap-4">
          <div className="max-w-[760px]">
            <span className="text-[11px] uppercase tracking-widest text-viz-neutral font-bold">Forensic Sequence • PG22</span>
            <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight mt-1">
              Rescue timeline &amp; sequence reconstruction
            </h1>
            <p className="mt-1 text-sm text-on-surface-variant leading-relaxed">
              Chronological reconstruction of how the incident unfolded. Every event records source provenance and time confidence. When new evidence alters the timeline, old and new sequences are preserved with complete cryptographic provenance.
            </p>
          </div>

          {/* Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2 self-start lg:self-end">
            <Link
              href="/rescue/events/new"
              className="h-9 px-3.5 rounded bg-surface hover:bg-surface-subtle text-viz-text text-xs font-semibold border border-border-control flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <span className="material-symbols-outlined text-[16px]">add</span>
              <span>Add event</span>
            </Link>
            <button
              onClick={() => setFilter(filter === 'all' ? 'loss_only' : 'all')}
              className="h-9 px-3.5 rounded bg-surface hover:bg-surface-subtle text-viz-text text-xs font-semibold border border-border-control flex items-center gap-1.5 transition-colors shadow-sm"
              type="button"
            >
              <span className="material-symbols-outlined text-[16px]">filter_list</span>
              <span>Filter: {filter === 'all' ? 'All events' : 'Loss events only'}</span>
            </button>
            <button
              onClick={() => alert('Audit log exported: SHA-256 integrity stamped.')}
              className="h-9 px-3.5 rounded bg-surface hover:bg-surface-subtle text-viz-text text-xs font-semibold border border-border-control flex items-center gap-1.5 transition-colors shadow-sm"
              type="button"
            >
              <span className="material-symbols-outlined text-[16px]">ios_share</span>
              <span>Export audit log</span>
            </button>
          </div>
        </div>

        {/* Reconstruction Diff Alert Banner */}
        <div className="mt-4 p-4 rounded-xl bg-tone-warning-bg border border-tone-warning-text/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded bg-tone-warning-strong-bg text-tone-warning-strong-text flex items-center justify-center shrink-0 mt-0.5">
              <span className="material-symbols-outlined text-[20px]">history_toggle_off</span>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-tone-warning-strong-text">Reconstruction updated 12 min ago</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-surface text-viz-text font-bold border border-border-divider">
                  Hypothesis revision v2.3
                </span>
              </div>
              <p className="text-xs text-tone-warning-text mt-0.5 leading-relaxed">
                Recalibrated based on newly added UPI collect receipt (#EVD-04). Earlier hypothesis regarding direct netbanking compromise updated.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowDiff(!showDiff)}
            className="h-8 px-3 rounded bg-surface hover:bg-tone-warning-strong-bg text-tone-warning-strong-text border border-border-control text-xs font-bold shrink-0 transition-colors flex items-center gap-1"
            type="button"
          >
            <span className="material-symbols-outlined text-[15px]">compare_arrows</span>
            <span>{showDiff ? 'Hide reconstruction diff' : 'Review reconstruction diff'}</span>
          </button>
        </div>

        {showDiff && (
          <div className="mt-3 p-4 rounded-xl bg-surface border border-border-divider shadow-sm text-xs">
            <h4 className="font-bold text-on-surface mb-2">Reconstruction Diff v2.2 → v2.3</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 rounded bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/20">
                <span className="font-bold block mb-1">- Previous Hypothesis (v2.2):</span>
                <span>Assumed victim clicked phishing link leading to banking credential credential theft via mock login portal.</span>
              </div>
              <div className="p-3 rounded bg-tone-info-bg text-tone-info-text border border-tone-info-text/20">
                <span className="font-bold block mb-1">+ Updated Reality (v2.3):</span>
                <span>Verified collect request executed on PhonePe for ₹11,450. Device screen-sharing rejected; no credential compromise detected.</span>
              </div>
            </div>
          </div>
        )}

        {/* Main Two-Column Layout */}
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (8 cols): Chronological Timeline Stream */}
          <div className="lg:col-span-8 flex flex-col">
            <div className="flex items-center justify-between pb-2 border-b border-border-divider mb-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-viz-text">Sequence Stream</span>
                <span className="px-2 py-0.5 rounded bg-surface-subtle text-xs text-viz-neutral border border-border-divider font-mono">
                  6 Nodes Documented
                </span>
              </div>
              <span className="text-[11px] text-viz-neutral">Timezone: Asia/Kolkata (IST · UTC+05:30)</span>
            </div>

            <div className="relative pl-6 md:pl-8 space-y-6">
              {/* Vertical Spine */}
              <div className="absolute left-2.5 md:left-3 top-3 bottom-8 w-[2px] bg-border-divider pointer-events-none"></div>

              {/* EVENT 1: Threat SMS */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded-full bg-viz-primary flex items-center justify-center text-white ring-4 ring-ground shadow-sm z-10 text-[10px] font-bold">
                  ●
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider/50 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-viz-text">18:42 IST · 24 Oct 2026</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">lock_clock</span>
                        Exact — from SMS metadata
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral text-[10px] font-semibold border border-border-divider">
                      (Original)
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text">
                    First contact: Threatening utility disconnection SMS
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Received unsolicited SMS from personal 10-digit number (+91 98******10) claiming electricity supply would be immediately discontinued at 9:30 PM due to alleged previous month billing discrepancy.
                  </p>
                  <div className="mt-3 pt-2 border-t border-border-divider/40 flex flex-wrap items-center justify-between gap-2 text-xs">
                    <Link href="/rescue/evidence" className="inline-flex items-center gap-1 text-primary hover:underline font-semibold">
                      <span className="material-symbols-outlined text-[15px]">attachment</span>
                      <span>View SMS screenshot #EVD-01</span>
                    </Link>
                    <span className="px-2 py-0.5 rounded bg-surface-subtle font-mono text-viz-neutral text-[10px]">
                      GSM Mod. Header: TD-STATEPB
                    </span>
                  </div>
                </div>
              </div>

              {/* EVENT 2: Citizen Callback */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded-full bg-surface text-viz-primary border-2 border-viz-primary flex items-center justify-center ring-4 ring-ground shadow-sm z-10 text-[10px] font-bold">
                  ◉
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider/50 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-viz-text">~19:15 IST · 24 Oct 2026</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">help_center</span>
                        User reported — Approximate
                      </span>
                    </div>
                    <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[10px] font-bold">
                      <span className="material-symbols-outlined text-[12px]">person</span>
                      <span>(You confirmed)</span>
                    </div>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text">
                    Incoming voice call: Impersonation of Junior Accounts Officer
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Citizen called back the number provided in the SMS. Fraudster claimed to be &ldquo;Alok Sharma, Junior Accounts Officer, State Electricity Board&rdquo;. Instructed citizen that automated meters require an instant ₹10 clearance token to prevent disconnection order auto-execution.
                  </p>
                  <div className="mt-3 p-2 rounded bg-surface-subtle border border-border-divider flex items-center gap-2 text-xs text-viz-text">
                    <span className="material-symbols-outlined text-[16px] text-viz-neutral">call</span>
                    <span>Duration reported: ~6 mins · Verbal urgency pattern confirmed by citizen</span>
                  </div>
                </div>
              </div>

              {/* EVENT 3: Ultimatum */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded-full bg-viz-primary flex items-center justify-center text-white ring-4 ring-ground shadow-sm z-10 text-[10px] font-bold">
                  ●
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider/50 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-viz-text">20:30 IST · 24 Oct 2026</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">lock_clock</span>
                        Exact — SMS timestamp
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral text-[10px] font-semibold border border-border-divider">
                      (Original)
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text">
                    Pressure tactic: Ultimatum of imminent black-out in 45 minutes
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Follow-up high-urgency WhatsApp alert and SMS received. Fraudster asserted the line dispatch crew was already moving to the local substation transformer. Direct instruction provided to stay on call while opening PhonePe app.
                  </p>
                  <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-tone-warning-bg text-tone-warning-strong-text text-xs border border-tone-warning-text/20">
                    <span className="material-symbols-outlined text-[15px]">timer</span>
                    <span className="font-semibold">Classic artificial countdown vector (Urgency escalation tactic)</span>
                  </div>
                </div>
              </div>

              {/* EVENT 4: Financial Loss Event */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded bg-error text-white flex items-center justify-center ring-4 ring-ground shadow-sm z-10">
                  <span className="material-symbols-outlined text-[13px]">warning</span>
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border-2 border-tone-danger-text/40 shadow-sm relative">
                  <div className="absolute -top-3 right-4 px-2.5 py-0.5 rounded bg-tone-danger-strong-bg text-tone-danger-strong-text text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 border border-tone-danger-strong-text/20">
                    <span className="material-symbols-outlined text-[13px]">error</span>
                    <span>Primary Loss Incident</span>
                  </div>
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-tone-danger-text">20:45 IST · 24 Oct 2026</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">receipt_long</span>
                        Exact — Bank UPI reference
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-xs font-bold">
                      ⚠️ Loss event: Confirmed ₹11,450 debit
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text">
                    Unauthorized transaction: ₹11,450 drained via UPI collect mandate
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Victim was prompted on voice call to enter their UPI PIN to &ldquo;receive the ₹10 zero-balance exemption voucher&rdquo;. Instead, collect mandate #UPI-849201 executed an instant debit of ₹11,450 to beneficiary <span className="font-mono font-bold text-viz-text">util-power-84920@okaxis</span> via PhonePe.
                  </p>
                  <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <div className="p-2 rounded bg-surface-subtle border border-border-divider">
                      <div className="text-[10px] text-viz-neutral uppercase">Bank RRN</div>
                      <div className="font-mono text-xs text-viz-text font-bold mt-0.5">638291048291</div>
                    </div>
                    <div className="p-2 rounded bg-surface-subtle border border-border-divider">
                      <div className="text-[10px] text-viz-neutral uppercase">Destination VPA</div>
                      <div className="font-mono text-xs text-viz-text font-bold mt-0.5 truncate" title="util-power-84920@okaxis">
                        util-power-84920@okaxis
                      </div>
                    </div>
                    <div className="p-2 rounded bg-surface-subtle border border-border-divider">
                      <div className="text-[10px] text-viz-neutral uppercase">Debit Account</div>
                      <div className="font-mono text-xs text-viz-text font-bold mt-0.5">SBI Savings **** 4902</div>
                    </div>
                  </div>
                  <div className="mt-4 pt-2 border-t border-border-divider flex flex-wrap items-center justify-between gap-2">
                    <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-tone-danger-bg text-tone-danger-strong-text text-xs font-bold">
                      <span className="w-2 h-2 rounded-full bg-error animate-ping"></span>
                      <span>Golden Hour reporting window active</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link
                        href="/rescue/events/new"
                        className="h-7 px-2.5 rounded bg-surface text-viz-text border border-border-control text-[11px] font-semibold hover:bg-surface-subtle transition-colors flex items-center gap-1"
                      >
                        <span className="material-symbols-outlined text-[14px]">edit</span>
                        <span>Edit details</span>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>

              {/* EVENT 5: Citizen Termination */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded-full bg-viz-primary flex items-center justify-center text-white ring-4 ring-ground shadow-sm z-10 text-[10px] font-bold">
                  ●
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider/50 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-viz-text">20:58 IST · 24 Oct 2026</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">smartphone</span>
                        Observed — Device log
                      </span>
                    </div>
                    <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[10px] font-bold">
                      <span className="material-symbols-outlined text-[12px]">person</span>
                      <span>(You confirmed)</span>
                    </div>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text">
                    Citizen terminated communication &amp; blocked caller
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Caller attempted second callback requesting an additional ₹5,000 transfer to &ldquo;reverse the mistaken debit&rdquo;. Citizen realized deceit, immediately hung up, blocked the contact, and activated ScamGraph rescue workspace.
                  </p>
                  <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-tone-info-bg text-tone-info-text text-xs font-semibold">
                    <span className="material-symbols-outlined text-[15px]">verified_user</span>
                    <span>Protective action prevented secondary extraction of ₹5,000</span>
                  </div>
                </div>
              </div>

              {/* EVENT 6: Inferred Anticipated Event */}
              <div className="relative group">
                <div className="absolute -left-6 md:-left-8 top-1.5 w-5 h-5 rounded-full bg-surface text-viz-neutral border-2 border-dashed border-viz-neutral flex items-center justify-center ring-4 ring-ground shadow-sm z-10 text-[10px] font-bold">
                  ○
                </div>
                <div className="p-4 sm:p-5 rounded-xl bg-surface border-2 border-dashed border-border-control shadow-sm">
                  <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-border-divider/50 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-viz-neutral">Anticipated next 24–48 hrs</span>
                      <span className="text-viz-neutral">•</span>
                      <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                        <span className="material-symbols-outlined text-[13px]">psychology</span>
                        Inferred — Pattern match
                      </span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-surface-subtle text-viz-neutral text-[10px] font-semibold border border-border-divider">
                      (Inferred)
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-viz-text flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-[16px] text-viz-warning">notification_important</span>
                    <span>Secondary threat: Fake cyber recovery agent contact</span>
                  </h2>
                  <p className="mt-1 text-xs text-on-surface-variant leading-relaxed">
                    Known syndicate cluster #UTL-8490 frequently follows up with fake &ldquo;cyber crime assistance&rdquo; or &ldquo;legal fund retrieval advocate&rdquo; calls demanding advance recovery retainers (typically ₹2,000–₹5,000).
                  </p>
                  <div className="mt-3 p-2.5 rounded bg-surface-subtle border border-border-divider flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-1.5 text-viz-text font-medium">
                      <span className="material-symbols-outlined text-[16px] text-viz-primary">lock</span>
                      <span>Recommended rule: Reject and report any caller claiming to retrieve funds for an upfront fee.</span>
                    </div>
                    <Link href="/help-center" className="text-primary hover:underline font-bold shrink-0">
                      View advisory →
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (4 cols): Sidebar Metadata & Admissibility Guide */}
          <div className="lg:col-span-4 flex flex-col gap-5 sticky top-24">
            {/* Panel 1: Certainty Standards */}
            <div className="p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <h3 className="text-xs font-bold text-viz-text uppercase tracking-wide">Certainty Standards</h3>
                <span className="px-1.5 py-0.5 rounded bg-surface-subtle font-mono text-[10px] text-viz-neutral font-semibold border border-border-divider">
                  §3.4 Core
                </span>
              </div>
              <p className="mt-2 text-xs text-on-surface-variant leading-relaxed">
                Every timeline node is assigned a certainty classification to guarantee institutional audit admissibility:
              </p>
              <div className="mt-3 space-y-2">
                <div className="p-2.5 rounded bg-surface-subtle border border-border-divider flex items-start gap-2.5">
                  <span className="text-viz-primary font-bold text-sm leading-none mt-0.5">●</span>
                  <div>
                    <div className="text-xs font-bold text-viz-text">Observed / Original</div>
                    <div className="text-[11px] text-viz-neutral leading-relaxed">Solid boundary. Unimpeachable telecom/bank system timestamp.</div>
                  </div>
                </div>
                <div className="p-2.5 rounded bg-surface-subtle border border-border-divider flex items-start gap-2.5">
                  <span className="text-viz-primary font-bold text-sm leading-none mt-0.5">◉</span>
                  <div>
                    <div className="text-xs font-bold text-viz-text">User-reported</div>
                    <div className="text-[11px] text-viz-neutral leading-relaxed">Witness account provided by citizen during intake triage.</div>
                  </div>
                </div>
                <div className="p-2.5 rounded bg-surface-subtle border border-border-divider flex items-start gap-2.5">
                  <span className="text-viz-neutral font-bold text-sm leading-none mt-0.5">○</span>
                  <div>
                    <div className="text-xs font-bold text-viz-text">Inferred / Pattern Match</div>
                    <div className="text-[11px] text-viz-neutral leading-relaxed">Dashed outline. Machine predicted step from identical campaigns.</div>
                  </div>
                </div>
              </div>
              <div className="mt-3 pt-2 border-t border-border-divider flex items-center justify-between text-xs">
                <span className="text-viz-neutral">Sequence Integrity Score</span>
                <span className="font-bold text-viz-primary flex items-center gap-1">
                  <span className="material-symbols-outlined text-[14px]">verified</span>
                  High (4 verified anchors)
                </span>
              </div>
            </div>

            {/* Panel 2: Linked Forensic Artifacts */}
            <div className="p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <h3 className="text-xs font-bold text-viz-text uppercase tracking-wide">Forensic Artifacts</h3>
                  <span className="px-1.5 py-0.2 rounded-full bg-surface-subtle text-xs text-viz-neutral font-bold border border-border-divider">
                    3
                  </span>
                </div>
                <Link href="/rescue/evidence" className="text-xs text-primary hover:underline font-semibold">
                  Manage
                </Link>
              </div>
              <div className="mt-3 space-y-2">
                <div className="p-2 rounded bg-surface-subtle border border-border-divider flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="material-symbols-outlined text-[16px] text-viz-neutral">image</span>
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-viz-text truncate">EVD-01_SMS_Screenshot.png</div>
                      <div className="text-[10px] text-viz-neutral">Captured 24 Oct · 18:50 IST</div>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-[16px] text-viz-primary shrink-0">check_circle</span>
                </div>
                <div className="p-2 rounded bg-surface-subtle border border-border-divider flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="material-symbols-outlined text-[16px] text-viz-neutral">picture_as_pdf</span>
                    <div className="min-w-0">
                      <div className="text-xs font-semibold text-viz-text truncate">EVD-04_PhonePe_UPI_Debit.pdf</div>
                      <div className="text-[10px] text-viz-neutral">RRN: 638291048291</div>
                    </div>
                  </div>
                  <span className="material-symbols-outlined text-[16px] text-viz-primary shrink-0">check_circle</span>
                </div>
              </div>
              <Link
                href="/rescue/evidence"
                className="mt-3 w-full h-8 rounded bg-surface hover:bg-surface-subtle text-viz-text border border-border-control text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <span className="material-symbols-outlined text-[14px]">upload_file</span>
                <span>Attach additional proof</span>
              </Link>
            </div>

            {/* Panel 3: Formal Dispute Admissibility */}
            <div className="p-5 rounded-xl bg-surface border border-border-divider shadow-sm">
              <div className="flex items-center gap-2 pb-2 border-b border-border-divider">
                <span className="material-symbols-outlined text-[18px] text-viz-primary">gavel</span>
                <h3 className="text-xs font-bold text-viz-text uppercase tracking-wide">Dispute Admissibility</h3>
              </div>
              <p className="mt-2 text-xs text-on-surface-variant leading-relaxed">
                This chronological reconstruction complies with the Reserve Bank of India (RBI) circular on customer protection for unauthorized electronic banking transactions (RBI/2017-18/15).
              </p>
              <div className="mt-3 p-2.5 rounded bg-surface-subtle border border-border-divider text-xs text-viz-neutral space-y-1">
                <div className="flex justify-between">
                  <span>Zero-Liability Window:</span>
                  <span className="font-bold text-viz-text">Within 3 days</span>
                </div>
                <div className="flex justify-between">
                  <span>Elapsed since incident:</span>
                  <span className="font-bold text-viz-primary">2 hrs 14 mins</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Navigation & Action Bar */}
        <div className="mt-8 pt-4 pb-12 border-t border-border-divider flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <Link
              href="/rescue/dashboard"
              className="h-10 px-4 rounded bg-surface hover:bg-surface-subtle text-viz-text border border-border-control text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors w-full sm:w-auto"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to Rescue dashboard</span>
            </Link>
            <Link
              href="/rescue/events/new"
              className="h-10 px-4 rounded bg-surface hover:bg-surface-subtle text-viz-text border border-border-control text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors w-full sm:w-auto"
            >
              <span className="material-symbols-outlined text-[16px]">add_circle</span>
              <span>Add manual event</span>
            </Link>
          </div>
          <Link
            href="/rescue/report-prep"
            className="h-10 px-6 rounded-full bg-viz-primary hover:bg-primary text-white text-xs font-bold shadow-sm flex items-center justify-center gap-2 transition-all w-full sm:w-auto"
          >
            <span>Prepare reporting summary (C13)</span>
            <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
