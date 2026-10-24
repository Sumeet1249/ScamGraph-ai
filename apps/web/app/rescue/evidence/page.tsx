'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function EvidenceWorkspacePage() {
  const [activeTab, setActiveTab] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [autoRedaction, setAutoRedaction] = useState<boolean>(true);
  const [targetDossier, setTargetDossier] = useState<string>('statutory');

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      <div className="max-w-[1200px] w-full mx-auto px-4 sm:px-6 flex flex-col gap-6">
        {/* Workspace Top Breadcrumb & Status */}
        <div className="bg-surface-subtle p-3 rounded-lg border border-border-divider flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <nav aria-label="Breadcrumb" className="flex items-center gap-2">
            <Link className="text-primary hover:underline flex items-center gap-1 font-semibold" href="/rescue/dashboard">
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to Rescue Dashboard</span>
            </Link>
            <span className="text-border-control">/</span>
            <span className="text-on-surface-variant font-mono">Case #SG-84920</span>
            <span className="text-border-control">/</span>
            <span className="text-on-surface font-bold">Evidence Workspace</span>
          </nav>
          <div className="flex items-center gap-1.5 text-tone-info-text bg-tone-info-bg px-2.5 py-1 rounded font-semibold border border-tone-info-text/20 self-start sm:self-auto">
            <span className="material-symbols-outlined text-[15px]">verified</span>
            <span>Immutable Cryptographic Provenance Active</span>
          </div>
        </div>

        {/* Workspace Header & Actions */}
        <header className="flex flex-col gap-4">
          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
            <div className="max-w-3xl space-y-1">
              <div className="inline-flex items-center gap-1.5 text-tone-info-text text-[11px] font-bold bg-tone-info-bg px-2.5 py-0.5 rounded border border-tone-info-text/20">
                <span className="material-symbols-outlined text-[14px]">inventory_2</span>
                <span>CIVILIAN CUSTODY RECORD • SPRINT PG23</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight">
                Evidence workspace &amp; forensic artifact ledger
              </h1>
              <p className="text-xs sm:text-sm text-on-surface-variant leading-relaxed">
                Centralized repository of submitted and extracted forensic artifacts for Case #SG-84920 (State Electricity Bill Disconnection — UPI Collect Vector). Raw evidence is preserved immutably with SHA-256 cryptographic hashes. Derived extractions and citizen corrections are tracked with explicit evidentiary provenance.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2 self-start shrink-0">
              <Link
                href="/rescue/events/new"
                className="h-10 px-4 rounded bg-surface hover:bg-surface-subtle text-on-surface text-xs font-semibold border border-border-control shadow-sm transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[16px]">add_photo_alternate</span>
                <span>+ Add evidence</span>
              </Link>
              <Link
                href="/rescue/package/SG-84920"
                className="h-10 px-4 rounded bg-primary text-white text-xs font-bold shadow-sm hover:bg-primary-container transition-colors flex items-center gap-1.5"
              >
                <span className="material-symbols-outlined text-[16px]">download_for_offline</span>
                <span>Download verified dossier (PDF)</span>
              </Link>
            </div>
          </div>

          {/* Statutory Caution (§2.2) */}
          <aside aria-label="Statutory Safety Notice" className="bg-tone-warning-bg text-tone-warning-strong-text rounded-xl p-4 border border-tone-warning-text/20 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-tone-warning-strong-bg text-tone-warning-strong-text flex items-center justify-center shrink-0 mt-0.5">
                <span className="material-symbols-outlined text-[18px]">warning</span>
              </div>
              <div className="space-y-0.5">
                <div className="text-xs font-bold text-tone-warning-strong-text flex items-center gap-1.5">
                  <span>Section 2.2 Statutory Caution</span>
                  <span className="text-[10px] px-1.5 py-0.2 rounded bg-surface border border-border-divider font-semibold">
                    Mandatory Honest Assessment
                  </span>
                </div>
                <p className="text-xs text-tone-warning-text max-w-3xl leading-relaxed">
                  The absence of strong warning signs does not guarantee safety. In emergency fraud situations involving imminent monetary loss, notify your bank immediately via national helpline <strong>1930</strong> or your issuing bank&apos;s dedicated emergency cutoff switch.
                </p>
              </div>
            </div>
            <a
              className="h-8 px-3 rounded-full bg-surface text-tone-warning-strong-text text-xs font-bold shrink-0 flex items-center gap-1 shadow-sm hover:bg-surface-subtle border border-border-divider transition-colors"
              href="tel:1930"
            >
              <span className="material-symbols-outlined text-[15px] text-error">call</span>
              <span>Dial 1930 (Toll-Free)</span>
            </a>
          </aside>

          {/* Artifact Filter Strip & View Toggle */}
          <nav aria-label="Evidence Artifact Tabs" className="bg-surface rounded-xl p-2 border border-border-divider shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-1.5" role="tablist">
              {[
                { id: 'all', label: 'All artifacts (4)', icon: 'all_inbox' },
                { id: 'images', label: 'Screenshots & Images (2)', icon: 'image' },
                { id: 'messages', label: 'Messages & Text (1)', icon: 'chat' },
                { id: 'audio', label: 'Audio recordings (0)', icon: 'mic_off' },
                { id: 'receipts', label: 'Receipts & Financial (1)', icon: 'receipt_long' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  aria-selected={activeTab === tab.id}
                  className={`h-9 px-3 rounded text-xs font-medium flex items-center gap-1.5 transition-colors ${
                    activeTab === tab.id
                      ? 'bg-surface-subtle text-primary font-bold border border-border-divider'
                      : 'text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface'
                  }`}
                  role="tab"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[16px]">{tab.icon}</span>
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>
            <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border-divider self-end sm:self-auto">
              <button
                onClick={() => setViewMode('list')}
                aria-pressed={viewMode === 'list'}
                className={`h-7 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  viewMode === 'list' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'
                }`}
                type="button"
              >
                <span className="material-symbols-outlined text-[15px]">format_list_bulleted</span>
                <span>List</span>
              </button>
              <button
                onClick={() => setViewMode('grid')}
                aria-pressed={viewMode === 'grid'}
                className={`h-7 px-2.5 rounded text-xs font-semibold flex items-center gap-1 transition-all ${
                  viewMode === 'grid' ? 'bg-surface text-primary shadow-sm' : 'text-on-surface-variant hover:text-on-surface'
                }`}
                type="button"
              >
                <span className="material-symbols-outlined text-[15px]">grid_view</span>
                <span>Grid</span>
              </button>
            </div>
          </nav>
        </header>

        {/* Main 2-Column Forensic Workspace Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Forensic Artifact Ledger (8 cols) */}
          <section aria-label="Forensic Artifact Ledger" className="lg:col-span-8 flex flex-col gap-6">
            {/* Item 1: Threat Screenshot */}
            <article className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary text-white text-[10px] font-bold">
                      <span className="w-1.5 h-1.5 rounded-full bg-white"></span>
                      Original • Observed
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-surface-subtle text-on-surface text-[10px] font-semibold border border-border-divider">
                      <span className="material-symbols-outlined text-[13px] text-secondary">check_circle</span>
                      Ready • OCR Extracted
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-surface-subtle text-on-surface-variant text-[10px] font-semibold border border-border-divider">
                      <span className="material-symbols-outlined text-[13px]">lock</span>
                      Case dossier &amp; citizen only
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[20px]">image</span>
                    <span>whatsapp_electricity_threat_notice.jpg</span>
                  </h2>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-[11px] text-on-surface-variant font-mono block font-bold">Artifact #AR-01</span>
                  <span className="text-[10px] text-viz-neutral">JPEG • 2.4 MB</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center bg-surface-subtle p-3 rounded-lg border border-border-divider">
                <div className="sm:col-span-4 rounded overflow-hidden shadow-sm relative group bg-surface border border-border-divider">
                  <div className="w-full h-32 bg-surface-subtle flex flex-col items-center justify-center p-3 text-center">
                    <span className="material-symbols-outlined text-primary text-[32px] mb-1">chat</span>
                    <span className="text-[11px] font-bold text-on-surface">Urgent Electricity SMS</span>
                    <span className="text-[10px] text-viz-neutral font-mono mt-0.5">Disconnect at 9:30 PM</span>
                  </div>
                </div>
                <div className="sm:col-span-8 flex flex-col justify-between gap-2">
                  <div className="space-y-1">
                    <div className="text-[10px] text-on-surface-variant uppercase tracking-wider font-bold">Cryptographic Hash Digest</div>
                    <div className="font-mono text-[11px] text-on-surface break-all bg-surface p-2 rounded border border-border-divider select-all">
                      sha256:8f2a991c019bd1e47aa52df092b3c10972688ad2130e550c01
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-1">
                    <span>Ingested: 24 Oct 2026, 19:42 IST</span>
                    <span className="text-secondary font-bold">Immutable Record</span>
                  </div>
                </div>
              </div>

              {/* Extracted Content Card */}
              <div className="bg-surface-subtle rounded-lg p-4 space-y-2 border border-border-divider">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5">
                    <span className="material-symbols-outlined text-secondary text-[16px]">document_scanner</span>
                    <span className="text-xs text-on-surface font-bold">Extracted Threat Notice Text</span>
                    <span className="px-1.5 py-0.2 rounded bg-surface text-tone-info-text text-[10px] font-semibold border border-border-divider">
                      98% OCR Confidence
                    </span>
                  </div>
                  <span className="text-[11px] text-secondary flex items-center gap-1 font-semibold">
                    <span className="material-symbols-outlined text-[13px]">how_to_reg</span>
                    Citizen verified
                  </span>
                </div>
                <blockquote className="bg-surface p-3 rounded border border-border-divider text-xs text-on-surface italic leading-relaxed">
                  &ldquo;Dear Consumer, Your electricity power supply will be disconnected tonight at 9:30 PM from the state power office because your previous month bill was not updated. Please immediately contact our electricity officer Rahul Sharma at +91 98******10 and settle ₹11,450.&rdquo;
                </blockquote>
                <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
                  <div className="flex items-center gap-2 font-semibold text-primary">
                    <button className="hover:underline flex items-center gap-1" type="button">
                      <span className="material-symbols-outlined text-[15px]">visibility</span>
                      <span>Inspect image</span>
                    </button>
                    <span>•</span>
                    <button className="hover:underline flex items-center gap-1" type="button">
                      <span className="material-symbols-outlined text-[15px]">description</span>
                      <span>View full OCR</span>
                    </button>
                  </div>
                  <span className="text-[10px] text-viz-neutral">Language: Hindi/English mixed</span>
                </div>
              </div>
            </article>

            {/* Item 2: Caller Telephony Metadata */}
            <article className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary text-white text-[10px] font-bold">
                      Extracted
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-surface-subtle text-on-surface text-[10px] font-semibold border border-border-divider">
                      <span className="material-symbols-outlined text-[13px]">person</span>
                      You confirmed
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-text text-[10px] font-bold">
                      14 Syndicate Matches
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[20px]">phone_in_talk</span>
                    <span>Caller Telephony Metadata &amp; GSM Node</span>
                  </h2>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-[11px] text-on-surface-variant font-mono block font-bold">Artifact #AR-02</span>
                  <span className="text-[10px] text-viz-neutral">Network Trace</span>
                </div>
              </div>
              <div className="bg-surface-subtle p-4 rounded-lg space-y-3 border border-border-divider">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold">Sender Telephony Ident</span>
                    <p className="text-base font-mono font-bold text-on-surface tracking-wide">
                      +91 98******10
                    </p>
                    <span className="text-[10px] text-viz-neutral">Masked civilian privacy mode</span>
                  </div>
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold">Syndicate Correlation</span>
                    <div className="text-xs text-tone-danger-strong-text font-bold flex items-center gap-1">
                      <span className="material-symbols-outlined text-[15px] text-error">hub</span>
                      <span>Syndicate Campaign #UTL-8490</span>
                    </div>
                    <span className="text-[10px] text-tone-danger-text">Active across Jharkhand &amp; West Bengal nodes</span>
                  </div>
                </div>
                <div className="bg-surface p-2.5 rounded border border-border-divider flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2 text-on-surface">
                    <span className="material-symbols-outlined text-viz-neutral text-[16px]">cell_tower</span>
                    <span>Carrier telemetry: Unregistered personal SIM • Flagged in state electricity phishing cluster</span>
                  </div>
                  <Link href="/radar" className="text-primary hover:underline font-semibold shrink-0">
                    View in Radar →
                  </Link>
                </div>
              </div>
            </article>

            {/* Item 3: PhonePe Payment Receipt */}
            <article className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-secondary text-white text-[10px] font-bold">
                      You confirmed
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-warning-bg text-tone-warning-strong-text text-[10px] font-bold border border-tone-warning-text/20">
                      <span className="material-symbols-outlined text-[13px]">link</span>
                      Loss Event Linked: #LSS-01
                    </span>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-surface-subtle text-on-surface text-[10px] font-semibold border border-border-divider">
                      UPI Collect Trace
                    </span>
                  </div>
                  <h2 className="text-sm font-bold text-on-surface flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary text-[20px]">payments</span>
                    <span>PhonePe_UPI_Collect_Debit_₹11450.png</span>
                  </h2>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-[11px] text-on-surface-variant font-mono block font-bold">Artifact #AR-03</span>
                  <span className="text-[10px] text-viz-neutral">PNG • 1.1 MB</span>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 items-center bg-surface-subtle p-3 rounded-lg border border-border-divider">
                <div className="sm:col-span-4 rounded overflow-hidden shadow-sm relative group bg-surface border border-border-divider">
                  <div className="w-full h-32 bg-surface-subtle flex flex-col items-center justify-center p-3 text-center">
                    <span className="material-symbols-outlined text-error text-[32px] mb-1">payments</span>
                    <span className="text-sm font-bold text-error font-mono">-₹11,450.00</span>
                    <span className="text-[10px] text-viz-neutral font-mono mt-0.5">util-power-84920@okaxis</span>
                  </div>
                </div>
                <div className="sm:col-span-8 flex flex-col justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] text-on-surface-variant uppercase font-bold">Statutory Loss Trace</span>
                      <span className="text-sm font-mono font-bold text-error">-₹11,450.00</span>
                    </div>
                    <div className="font-mono text-xs text-on-surface bg-surface p-2 rounded border border-border-divider space-y-1">
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">Recipient VPA:</span>
                        <span className="font-semibold text-on-surface">util-power-84920@okaxis</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-on-surface-variant">RRN / UTR:</span>
                        <span className="text-on-surface">638291048291</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-on-surface-variant pt-1">
                    <span>Timestamp: 24 Oct 2026, 20:46 IST</span>
                    <span className="text-primary font-bold">Matched with 98% OCR accuracy</span>
                  </div>
                </div>
              </div>

              <div className="bg-surface-subtle p-3 rounded-lg border border-border-divider flex flex-wrap items-center justify-between gap-2 text-xs">
                <p className="text-on-surface">
                  Linked to confirmed statutory loss event <strong>#LSS-01</strong>. Cross-verified with citizen State Bank statement record.
                </p>
                <div className="flex items-center gap-2 font-semibold text-primary">
                  <Link href="/rescue/events/new" className="hover:underline flex items-center gap-1">
                    <span className="material-symbols-outlined text-[15px]">edit</span>
                    <span>Edit loss details</span>
                  </Link>
                </div>
              </div>
            </article>

            {/* Forensic Privacy Guarantee Banner */}
            <section aria-label="Privacy & Security Guarantee" className="bg-primary/5 rounded-xl p-4 border border-primary/20 shadow-sm flex items-start gap-4">
              <div className="w-9 h-9 rounded-full bg-primary text-white flex items-center justify-center shrink-0">
                <span className="material-symbols-outlined text-[18px]">mic_off</span>
              </div>
              <div className="space-y-1">
                <h3 className="text-xs font-bold text-primary flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[15px]">lock</span>
                  <span>Forensic Storage Standards &amp; Audio Privacy Guarantee</span>
                </h3>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  Audio recordings and call records never autoplay and strictly require affirmative citizen permission before transcription. All media binaries are stored on isolated, encrypted sovereign nodes with zero training on public AI models.
                </p>
              </div>
            </section>
          </section>

          {/* Right Column: Lineage & Admissibility Inspector (4 cols) */}
          <aside aria-label="Forensic Inspector" className="lg:col-span-4 flex flex-col gap-5 sticky top-24">
            {/* Card 1: Forensic Lineage (§3.4) */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <h2 className="text-xs font-bold text-on-surface uppercase tracking-wide flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-[18px]">account_tree</span>
                  <span>Forensic Lineage</span>
                </h2>
                <span className="text-[10px] text-viz-neutral font-mono">§3.4 Core Spec</span>
              </div>
              <div className="text-[11px] text-primary bg-primary/10 px-2 py-1 rounded text-center font-bold">
                Reason → Observation → Evidence → Artifact
              </div>

              {/* Structured Provenance Steps */}
              <div className="space-y-3 pl-1">
                <div className="flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-secondary text-white flex items-center justify-center shrink-0 text-[10px] font-bold">1</div>
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold block">REASON</span>
                    <p className="text-xs text-on-surface leading-tight">Fabricated urgency regarding essential public utility disconnection.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-secondary text-white flex items-center justify-center shrink-0 text-[10px] font-bold">2</div>
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold block">OBSERVATION</span>
                    <p className="text-xs text-on-surface leading-tight">Unsolicited WhatsApp message from personal non-business GSM claiming unpaid bill.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-secondary text-white flex items-center justify-center shrink-0 text-[10px] font-bold">3</div>
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold block">EVIDENCE EXTRACTION</span>
                    <p className="text-xs text-on-surface leading-tight">OCR parsed threat text, spoofed seal, and rogue recipient VPA <code className="text-primary font-mono font-bold">util-power-84920@okaxis</code>.</p>
                  </div>
                </div>
                <div className="flex items-start gap-2.5">
                  <div className="w-5 h-5 rounded-full bg-primary text-white flex items-center justify-center shrink-0 text-[10px] font-bold">4</div>
                  <div className="space-y-0.5">
                    <span className="text-[10px] text-on-surface-variant uppercase font-bold block">ORIGINAL ARTIFACT</span>
                    <div className="font-mono text-[10px] text-on-surface break-all bg-surface-subtle p-1.5 rounded border border-border-divider select-all">
                      SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
                    </div>
                  </div>
                </div>
              </div>
              <div className="bg-tone-info-bg text-tone-info-text p-2 rounded border border-tone-info-text/20 flex items-center gap-1.5 justify-center text-[11px] font-semibold">
                <span className="material-symbols-outlined text-[15px]">verified</span>
                <span>Cryptographic provenance intact (Chain verified)</span>
              </div>
            </div>

            {/* Card 2: Privacy & Redaction Controls */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <h2 className="text-xs font-bold text-on-surface uppercase tracking-wide flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-primary text-[18px]">visibility_off</span>
                  <span>Privacy &amp; Redaction</span>
                </h2>
                <span className="px-2 py-0.5 rounded bg-surface-subtle text-on-surface text-[10px] font-bold border border-border-divider">
                  Active
                </span>
              </div>
              <label className="flex items-start gap-2.5 cursor-pointer select-none bg-surface-subtle p-3 rounded border border-border-divider">
                <input
                  checked={autoRedaction}
                  onChange={(e) => setAutoRedaction(e.target.checked)}
                  className="mt-0.5 w-4 h-4 text-primary rounded"
                  type="checkbox"
                />
                <div className="space-y-0.5">
                  <span className="text-xs text-on-surface font-semibold block">Automatic civilian redaction active</span>
                  <p className="text-[11px] text-on-surface-variant leading-relaxed">
                    Phone numbers (+91 98******10) and personal bank account numbers (SBI **** 4902) are automatically masked in exported citizen packets.
                  </p>
                </div>
              </label>
              <div className="space-y-1">
                <label className="text-[10px] text-on-surface-variant font-bold uppercase tracking-wide block">
                  Export Clearance Target:
                </label>
                <select
                  value={targetDossier}
                  onChange={(e) => setTargetDossier(e.target.value)}
                  className="w-full h-10 px-3 rounded bg-surface border border-border-control text-xs text-on-surface shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="statutory">Statutory Dispute Dossier (Form 1930 / Bank Grievance)</option>
                  <option value="police">Law Enforcement Cyber Cell (Full Unmasked Pack)</option>
                  <option value="civilian">Civilian Self-Defense Record (Safe Masked)</option>
                </select>
              </div>
            </div>

            {/* Card 3: Dossier Admissibility Summary */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-border-divider">
                <h2 className="text-xs font-bold text-on-surface uppercase tracking-wide flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-secondary text-[18px]">fact_check</span>
                  <span>Dossier Admissibility Summary</span>
                </h2>
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-on-surface-variant">Verified artifacts</span>
                  <span className="font-bold text-on-surface">4 of 4 verified</span>
                </div>
                <div className="w-full bg-surface-subtle h-2 rounded-full overflow-hidden border border-border-divider">
                  <div className="bg-primary h-full rounded-full w-full"></div>
                </div>
              </div>
              <div className="p-3 rounded bg-surface-subtle border border-border-divider text-xs space-y-1">
                <div className="flex justify-between">
                  <span className="text-viz-neutral">Section 65B BSA Certificate:</span>
                  <span className="font-bold text-secondary">Generated ✓</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-viz-neutral">Merkle Tree Root:</span>
                  <span className="font-mono text-[10px] text-on-surface font-semibold">0x8f2a...c01</span>
                </div>
              </div>
              <Link
                href="/rescue/package/SG-84920"
                className="w-full h-9 rounded bg-primary text-white text-xs font-bold flex items-center justify-center gap-1 hover:bg-primary-container transition-colors shadow-sm"
              >
                <span>View Full Court Package (C14)</span>
                <span className="material-symbols-outlined text-[15px]">arrow_forward</span>
              </Link>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
