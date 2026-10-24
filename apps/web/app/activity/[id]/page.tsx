'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function ActivityCaseDetailPage() {
  const params = useParams();
  const caseId = (params?.id as string) || 'SG-84920';
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'vault' | 'audit'>('overview');
  const [revealVpa, setRevealVpa] = useState<boolean>(false);
  const [copiedCode, setCopiedCode] = useState<boolean>(false);

  const handleCopyCode = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText('RC-8492-7104-9942');
      setCopiedCode(true);
      setTimeout(() => setCopiedCode(false), 2000);
    }
  };

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      <div className="max-w-[1200px] w-full mx-auto px-4 sm:px-6 flex flex-col gap-6 pb-20">
        {/* Breadcrumbs & Case Chronology Bar */}
        <section className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-surface-subtle p-3.5 rounded-xl border border-border-divider">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <Link
              className="flex items-center gap-1 font-semibold text-primary hover:text-primary-container transition-colors"
              href="/activity"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to My Activity</span>
            </Link>
            <span className="text-border-control">/</span>
            <div className="flex items-center gap-1.5 bg-surface px-2.5 py-0.5 rounded-full border border-border-divider shadow-sm font-mono">
              <span className="font-bold text-on-surface">Case #{caseId}</span>
              <span className="w-1.5 h-1.5 rounded-full bg-viz-primary"></span>
              <span className="text-on-surface-variant text-[11px]">Alok S. (Bengaluru)</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface text-on-surface-variant text-xs border border-border-divider shadow-sm">
              <span className="material-symbols-outlined text-[14px] text-viz-neutral">schedule</span>
              <span>Created 24 Oct 2026, 16:42 IST</span>
              <span className="text-border-control">•</span>
              <span className="font-semibold text-viz-warning">Updated 18m ago</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-tone-warning-bg text-tone-warning-strong-text text-xs font-bold border border-tone-warning-text/20">
              <span className="w-2 h-2 rounded-full bg-viz-warning animate-pulse"></span>
              <span>Status: Active Rescue &amp; Review</span>
            </div>
          </div>
        </section>

        {/* Case Header & Primary Classification Badge */}
        <header className="flex flex-col lg:flex-row lg:items-start justify-between gap-4 bg-surface p-5 sm:p-6 rounded-xl border border-border-divider shadow-sm">
          <div className="flex flex-col gap-1.5 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] uppercase tracking-wider text-viz-neutral font-bold">
                Utility Subcategory · Power Disconnection Scheme
              </span>
              <span className="text-border-control">|</span>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-tone-info-bg text-tone-info-text text-[11px] font-semibold border border-tone-info-text/20">
                <span className="material-symbols-outlined text-[13px]">verified</span>
                <span>Checks complete · 3 sources analyzed</span>
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight">
              BESCOM Power Disconnection Spoof &amp; Mandate Inversion
            </h1>
            <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
              Impersonation assault targeting electricity consumers with SMS urgency cues, deceptive Android application distribution, and automated reverse-mandate UPI account drains.
            </p>
          </div>

          {/* State 6 High Risk Badge */}
          <div className="shrink-0 flex items-center gap-3 bg-tone-danger-bg p-3.5 rounded-xl border border-tone-danger-text/20 self-start shadow-sm">
            <div className="w-10 h-10 rounded-lg bg-tone-danger-strong-bg flex items-center justify-center text-tone-danger-text shrink-0">
              <span className="material-symbols-outlined text-[24px]">shield</span>
            </div>
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="text-base text-tone-danger-text font-bold leading-tight">High Risk</span>
                <span className="w-1.5 h-1.5 rounded-full bg-error"></span>
                <span className="text-[11px] font-bold text-tone-danger-strong-text uppercase tracking-wider font-mono">
                  Level 6
                </span>
              </div>
              <span className="text-xs text-tone-danger-strong-text font-bold">Don&apos;t send money yet</span>
            </div>
          </div>
        </header>

        {/* Primary Action Hero Card */}
        <section className="bg-primary text-white p-5 sm:p-6 rounded-xl shadow-md flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden">
          <div className="flex items-start gap-4 z-10 max-w-2xl">
            <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center shrink-0 text-white">
              <span className="material-symbols-outlined text-[26px]">electric_bolt</span>
            </div>
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2">
                <span className="inline-block w-2 h-2 rounded-full bg-secondary-fixed animate-ping"></span>
                <span className="text-[11px] uppercase tracking-widest text-secondary-fixed font-bold font-mono">
                  Priority Mandate Rescue Pipeline
                </span>
              </div>
              <h2 className="text-lg font-bold text-white">
                Bank mandate reversal request generated
              </h2>
              <p className="text-xs text-white/90 leading-relaxed">
                Your bank mandate reversal request has been generated. Continue to the Rescue Dashboard to place an urgent freeze on the Axis Bank escrow lien before batch clearing at 23:59 IST.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 z-10 shrink-0">
            <Link
              href="/rescue/dashboard"
              className="inline-flex items-center justify-center px-5 h-10 rounded-full bg-white text-primary hover:bg-surface-subtle text-xs font-bold transition-all shadow-sm gap-1.5"
            >
              <span>Continue Rescue Dashboard (C09)</span>
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </Link>
            <Link
              href={`/check/result/${caseId}`}
              className="inline-flex items-center justify-center px-3.5 h-10 rounded-full bg-white/15 hover:bg-white/25 text-white text-xs font-semibold transition-all"
            >
              <span>Summary Result (C03)</span>
            </Link>
            <Link
              href={`/check/journey/${caseId}`}
              className="inline-flex items-center justify-center px-3.5 h-10 rounded-full bg-white/15 hover:bg-white/25 text-white text-xs font-semibold transition-all"
            >
              <span>Full Journey (C04)</span>
            </Link>
          </div>
        </section>

        {/* Interactive Tab Navigation */}
        <nav className="flex items-center gap-1.5 p-1 bg-surface-subtle rounded-xl w-fit border border-border-divider" role="tablist">
          {[
            { id: 'overview', label: 'Case Overview' },
            { id: 'timeline', label: 'Timeline & Journey' },
            { id: 'vault', label: 'Evidence Vault', badge: '3' },
            { id: 'audit', label: 'Activity & Audit History' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              aria-selected={activeTab === tab.id}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === tab.id
                  ? 'bg-surface text-primary shadow-sm border border-border-divider'
                  : 'text-on-surface-variant hover:text-on-surface'
              }`}
              type="button"
            >
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="px-1.5 py-0.2 rounded-full bg-surface-subtle text-[10px] font-bold border border-border-divider">
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* TAB 1: CASE OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full">
            {/* Left Column: Case Intelligence */}
            <div className="lg:col-span-7 flex flex-col gap-6">
              {/* Intelligence Summary Panel */}
              <div className="bg-surface p-6 rounded-xl border border-border-divider shadow-sm flex flex-col gap-4">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-viz-primary text-[20px]">policy</span>
                    <h3 className="text-sm font-bold text-on-surface">Case Intelligence Summary</h3>
                  </div>
                  <span className="text-[11px] bg-surface-subtle text-on-surface-variant px-2 py-0.5 rounded font-mono border border-border-divider">
                    SG-LEI-4491-BLR
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div className="bg-surface-subtle p-3.5 rounded-lg border border-border-divider flex flex-col gap-0.5">
                    <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
                      Scam Family Architecture
                    </span>
                    <span className="text-xs font-bold text-on-surface">Utility Impersonation &amp; APK Dropper</span>
                    <span className="text-[11px] text-viz-neutral mt-0.5">Known Variant: BESCOM-QuickBill v4.1</span>
                  </div>

                  <div className="bg-surface-subtle p-3.5 rounded-lg border border-border-divider flex flex-col gap-0.5">
                    <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
                      Targeted Recipient VPA
                    </span>
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-mono font-bold text-on-surface">
                        {revealVpa ? 'util-power-84920@okaxis' : 'u••••@okaxis'}
                      </span>
                      <button
                        onClick={() => setRevealVpa(!revealVpa)}
                        className="text-primary text-[11px] font-bold hover:underline"
                        type="button"
                      >
                        {revealVpa ? 'Hide' : 'Reveal'}
                      </button>
                    </div>
                    <span className="text-[10px] text-tone-danger-text font-semibold">Flagged in 34 prior reports</span>
                  </div>

                  <div className="bg-surface-subtle p-3.5 rounded-lg border border-border-divider flex flex-col gap-0.5">
                    <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
                      Disputed Loss Event
                    </span>
                    <span className="text-base font-bold text-error font-mono">₹11,450.00</span>
                    <span className="text-[11px] text-on-surface-variant">Paid via Reverse Mandate Inversion</span>
                  </div>

                  <div className="bg-surface-subtle p-3.5 rounded-lg border border-border-divider flex flex-col gap-0.5">
                    <span className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wider">
                      Statutory Escrow Lien Hold
                    </span>
                    <span className="text-base font-bold text-viz-primary font-mono">₹24,350.00</span>
                    <span className="text-[11px] text-on-surface-variant">Axis Bank Koramangala (Form 1930)</span>
                  </div>
                </div>

                {/* Loss Interception Gauge */}
                <div className="p-3.5 bg-ground rounded-lg border border-border-divider flex flex-col gap-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-on-surface font-semibold">Fund Recovery Probability Score</span>
                    <span className="font-bold text-viz-primary">78% (High Recovery Corridor)</span>
                  </div>
                  <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-border-divider">
                    <div className="bg-viz-primary h-full rounded-full w-[78%]"></div>
                  </div>
                  <p className="text-[11px] text-on-surface-variant leading-relaxed">
                    Lien placed within 4 hours of transfer. Mandate queue successfully stalled at intermediary gateway.
                  </p>
                </div>
              </div>

              {/* Why We Flagged This Situation */}
              <div className="bg-surface p-6 rounded-xl border border-border-divider shadow-sm flex flex-col gap-4">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-viz-warning text-[20px]">warning</span>
                  <h3 className="text-sm font-bold text-on-surface">Why We Flagged This Situation</h3>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  ScamGraph&apos;s sovereign rules engine synthesized 3 corroborated signals from Indian telecommunications registries and NPCI UPI gateway logs:
                </p>

                <div className="space-y-3">
                  <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-tone-warning-bg text-tone-warning-text flex items-center justify-center shrink-0 font-bold text-xs border border-tone-warning-text/20">
                      1
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-bold text-on-surface">Spoofed SMS Header impersonating BESCOM</span>
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        Message originated from standard 10-digit prepaid GSM SIM (<code className="font-mono text-primary font-bold">+91 98450 XXXXX</code>) rather than certified DLT utility header (<code className="font-mono text-primary font-bold">BZ-BESCOM</code>). High urgency countdown matches established psychological pressure patterns.
                      </p>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-tone-danger-bg text-tone-danger-text flex items-center justify-center shrink-0 font-bold text-xs border border-tone-danger-text/20">
                      2
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-bold text-on-surface">Weaponized APK Dropper (bescom-quickpay.apk)</span>
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        Sideloaded package requested <code className="font-mono text-error font-bold">RECEIVE_SMS</code>, <code className="font-mono text-error font-bold">READ_SMS</code>, and notification intercept permissions to suppress bank OTP alerts.
                      </p>
                    </div>
                  </div>

                  <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-tone-warning-bg text-tone-warning-text flex items-center justify-center shrink-0 font-bold text-xs border border-tone-warning-text/20">
                      3
                    </div>
                    <div className="flex flex-col gap-0.5">
                      <span className="text-xs font-bold text-on-surface">Reverse Mandate Collect Inversion</span>
                      <p className="text-xs text-on-surface-variant leading-relaxed">
                        Victim was instructed that entering UPI PIN constitutes a &ldquo;₹10 test verification credit&rdquo;. The malicious payload inverted the transaction packet to execute an instantaneous ₹11,450 recurring mandate pull.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Recovery Vault & Lineage */}
            <div className="lg:col-span-5 flex flex-col gap-6 sticky top-24">
              {/* Recovery Code Security Card */}
              <div className="bg-surface p-5 rounded-xl border border-border-divider shadow-sm flex flex-col gap-3">
                <div className="flex items-center gap-2 text-primary">
                  <span className="material-symbols-outlined text-[18px]">key</span>
                  <span className="text-[10px] uppercase font-bold tracking-wider font-mono">
                    Emergency Consumer Recovery Token
                  </span>
                </div>
                <h4 className="text-sm font-bold text-on-surface">Single-Use Dossier Key</h4>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  If you change devices or lose network connectivity, enter this single-use code on any terminal to restore this exact case securely.
                </p>
                <div className="flex items-center justify-between p-3 bg-surface-subtle rounded-lg border border-border-divider mt-1">
                  <code className="font-mono text-sm font-bold text-primary tracking-wider">
                    RC-8492-7104-9942
                  </code>
                  <button
                    onClick={handleCopyCode}
                    className="flex items-center gap-1 px-3 py-1.5 rounded bg-primary text-white hover:bg-primary-container text-xs font-bold transition-all shadow-sm"
                    type="button"
                  >
                    <span className="material-symbols-outlined text-[14px]">content_copy</span>
                    <span>{copiedCode ? 'Copied' : 'Copy'}</span>
                  </button>
                </div>
                <span className="text-[10px] text-viz-neutral">
                  Complies with Indian Digital Personal Data Protection (DPDP) Act 2023.
                </span>
              </div>

              {/* Submitted Evidence Lineage */}
              <div className="bg-surface p-5 rounded-xl border border-border-divider shadow-sm flex flex-col gap-3">
                <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-viz-info text-[20px]">inventory_2</span>
                    <h3 className="text-xs font-bold text-on-surface uppercase tracking-wide">Evidence Lineage</h3>
                  </div>
                  <span className="text-xs text-on-surface-variant">4 Sealed Items</span>
                </div>

                <div className="flex flex-col gap-2.5">
                  <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-on-surface flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-primary text-[16px]">sms</span>
                        <span>Disconnection SMS</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-tone-info-bg text-tone-info-text font-bold">
                        ● Original
                      </span>
                    </div>
                    <span className="text-[10px] text-viz-neutral font-mono">SHA-256: 8f4a...e109 · Logged 16:44 IST</span>
                  </div>

                  <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-on-surface flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-primary text-[16px]">image</span>
                        <span>Officer Chat Screenshot</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-tone-info-bg text-tone-info-text font-bold">
                        ● Original
                      </span>
                    </div>
                    <span className="text-[10px] text-viz-neutral font-mono">Exif verified · Metadata Bengaluru</span>
                  </div>

                  <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-semibold text-on-surface flex items-center gap-1.5">
                        <span className="material-symbols-outlined text-primary text-[16px]">receipt_long</span>
                        <span>Bank Debit SMS &amp; RRN</span>
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-tone-info-bg text-tone-info-text font-bold">
                        ● Original
                      </span>
                    </div>
                    <span className="text-[10px] text-viz-neutral font-mono">NPCI RRN: 429810482910</span>
                  </div>
                </div>

                <Link
                  href="/rescue/evidence"
                  className="mt-2 w-full h-8 rounded bg-surface-subtle hover:bg-surface border border-border-divider text-xs font-semibold text-primary flex items-center justify-center gap-1 transition-colors"
                >
                  <span>Open Full Evidence Workspace (C12)</span>
                  <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TIMELINE & JOURNEY */}
        {activeTab === 'timeline' && (
          <div className="bg-surface p-6 rounded-xl border border-border-divider shadow-sm flex flex-col gap-6 w-full">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div>
                <h3 className="text-base font-bold text-on-surface">Scam Pattern Progression &amp; Citizen Path</h3>
                <p className="text-xs text-on-surface-variant mt-0.5">Topological reconstruction from verified telemetry</p>
              </div>
              <Link
                href="/rescue/timeline"
                className="text-xs text-primary font-bold hover:underline flex items-center gap-1"
              >
                <span>View Full Forensic Timeline (C11)</span>
                <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
              </Link>
            </div>

            <div className="flex flex-col gap-6 relative pl-6 border-l-2 border-border-divider ml-3">
              <div className="flex items-start gap-4 relative">
                <div className="absolute -left-[31px] w-4 h-4 rounded-full bg-viz-primary flex items-center justify-center text-white text-[10px]">●</div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-on-surface">SMS Lure Delivered (15:20 IST)</span>
                  <p className="text-xs text-on-surface-variant leading-relaxed">Sender spoofed local cellular ID. Message created immediate panic regarding nighttime power cutoff.</p>
                  <span className="text-[10px] text-viz-neutral">● Observed Stage (Corroborated by telecom gateway)</span>
                </div>
              </div>

              <div className="flex items-start gap-4 relative">
                <div className="absolute -left-[31px] w-4 h-4 rounded-full bg-primary flex items-center justify-center text-white text-[10px]">◉</div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-on-surface">Victim Contacted Fraudster (15:45 IST)</span>
                  <p className="text-xs text-on-surface-variant leading-relaxed">Victim called number in SMS. Impersonator instructed installation of &apos;BESCOM Quick Update&apos; APK file.</p>
                  <span className="text-[10px] text-primary font-semibold">◉ User-reported Stage</span>
                </div>
              </div>

              <div className="flex items-start gap-4 relative">
                <div className="absolute -left-[31px] w-4 h-4 rounded-full bg-viz-warning flex items-center justify-center text-white text-[10px]">◐</div>
                <div className="flex flex-col gap-0.5 bg-tone-warning-bg p-3.5 rounded-lg border border-tone-warning-text/20">
                  <span className="text-xs font-bold text-tone-warning-strong-text">Mandate Execution &amp; Loss Event (16:30 IST)</span>
                  <p className="text-xs text-tone-warning-text leading-relaxed">Victim authorized inverted ₹11,450 mandate believing it was a ₹10 testing charge.</p>
                  <span className="text-[10px] text-tone-warning-strong-text font-bold">◐ Current Stage (&ldquo;You are here - Action Required&rdquo;)</span>
                </div>
              </div>

              <div className="flex items-start gap-4 relative">
                <div className="absolute -left-[31px] w-4 h-4 rounded-full bg-surface border-2 border-dashed border-border-control flex items-center justify-center text-viz-neutral text-[10px]">○</div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-on-surface">Axis Bank Lien Escalation (In Progress)</span>
                  <p className="text-xs text-on-surface-variant leading-relaxed">Lien form 1930 dispatched to Axis Koramangala Nodal Cyber Desk for secondary beneficiary freeze.</p>
                  <span className="text-[10px] text-viz-neutral">○ Inferred Recovery Stage</span>
                </div>
              </div>

              <div className="flex items-start gap-4 relative">
                <div className="absolute -left-[31px] w-4 h-4 rounded-full bg-surface border-2 border-dotted border-border-control flex items-center justify-center text-viz-neutral text-[10px]">◌</div>
                <div className="flex flex-col gap-0.5">
                  <span className="text-xs font-bold text-on-surface">Statutory Refund Credited</span>
                  <p className="text-xs text-on-surface-variant leading-relaxed">Reversal from frozen recipient escrow back to Alok S. savings account.</p>
                  <span className="text-[10px] text-viz-neutral">◌ Projected Outcome Step</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: EVIDENCE VAULT */}
        {activeTab === 'vault' && (
          <div className="bg-surface p-6 rounded-xl border border-border-divider shadow-sm flex flex-col gap-4 w-full">
            <div className="flex items-center justify-between pb-3 border-b border-border-divider">
              <div>
                <h3 className="text-base font-bold text-on-surface">Cryptographically Sealed Vault Items</h3>
                <span className="text-[11px] text-viz-neutral font-mono">Vault Hash: 991a::d02b</span>
              </div>
              <Link
                href="/rescue/evidence"
                className="text-xs text-primary font-bold hover:underline flex items-center gap-1"
              >
                <span>Manage in Evidence Workspace</span>
                <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 bg-ground rounded-xl border border-border-divider flex flex-col justify-between h-44">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-bold text-viz-primary uppercase tracking-wide">ITEM 01 · SMS DISCONNECTION</span>
                  <span className="text-xs font-bold text-on-surface">Extracted Carrier Payload</span>
                  <p className="text-xs text-on-surface-variant line-clamp-3 mt-1">
                    &ldquo;Dear consumer your electricity power will be cut tonight at 21:30 pm from BESCOM office...&rdquo;
                  </p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-border-divider text-xs">
                  <span className="text-[11px] text-viz-neutral font-mono">Raw Text / CSV</span>
                  <span className="text-primary font-bold">Verified ✓</span>
                </div>
              </div>

              <div className="p-4 bg-ground rounded-xl border border-border-divider flex flex-col justify-between h-44">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-bold text-viz-primary uppercase tracking-wide">ITEM 02 · SCREENSHOT</span>
                  <span className="text-xs font-bold text-on-surface">Fake Officer Persona</span>
                  <p className="text-xs text-on-surface-variant mt-1">
                    WhatsApp Avatar wearing BESCOM utility badge; impersonation intent verified.
                  </p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-border-divider text-xs">
                  <span className="text-[11px] text-viz-neutral font-mono">PNG (3.2 MB)</span>
                  <span className="text-primary font-bold">Verified ✓</span>
                </div>
              </div>

              <div className="p-4 bg-ground rounded-xl border border-border-divider flex flex-col justify-between h-44">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] font-bold text-viz-primary uppercase tracking-wide">ITEM 03 · BANK RECEIPT</span>
                  <span className="text-xs font-bold text-on-surface">UPI Mandate Debit Slip</span>
                  <p className="text-xs text-on-surface-variant mt-1 font-mono">
                    RRN: 638291048291 · ₹11,450 debit via PhonePe collect request.
                  </p>
                </div>
                <div className="flex items-center justify-between pt-2 border-t border-border-divider text-xs">
                  <span className="text-[11px] text-viz-neutral font-mono">PDF (1.1 MB)</span>
                  <span className="text-primary font-bold">Verified ✓</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: AUDIT HISTORY */}
        {activeTab === 'audit' && (
          <div className="bg-surface p-6 rounded-xl border border-border-divider shadow-sm flex flex-col gap-4 w-full text-xs">
            <h3 className="text-sm font-bold text-on-surface">Chronological Case Ledger</h3>
            <div className="divide-y divide-border-divider border border-border-divider rounded-lg">
              {[
                { time: '24 Oct 2026, 16:42 IST', event: 'Case #SG-84920 initialized via Universal Check', actor: 'Citizen (You)' },
                { time: '24 Oct 2026, 16:44 IST', event: 'Disconnection SMS screenshot uploaded and SHA-256 hashed', actor: 'Citizen (You)' },
                { time: '24 Oct 2026, 16:45 IST', event: 'PhonePe collect receipt analyzed with OCR (98% confidence)', actor: 'ScamGraph OCR Engine' },
                { time: '24 Oct 2026, 16:46 IST', event: 'Syndicate #UTL-8490 correlation detected (14 prior matches)', actor: 'Sovereign Graph GNN' },
                { time: '24 Oct 2026, 17:02 IST', event: 'Bank mandate freeze letter generated for Axis Bank Koramangala', actor: 'Citizen (You)' }
              ].map((log, i) => (
                <div key={i} className="p-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-viz-neutral text-[11px]">{log.time}</span>
                    <span className="font-medium text-on-surface">{log.event}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border-divider font-mono text-[10px]">
                    {log.actor}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
