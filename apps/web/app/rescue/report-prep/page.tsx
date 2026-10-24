'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function ReportingPreparationPage() {
  const [statement, setStatement] = useState<string>(
    'On 24 Oct 2026 at ~19:15 IST, citizen received an unsolicited threatening message and subsequent call claiming state electricity supply would be severed at 9:30 PM due to unpaid arrears of ₹11,450. Under verbal duress and intimidation of immediate utility cutoff, citizen opened PhonePe and authorized an unverified UPI collect mandate.'
  );
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [copiedSummary, setCopiedSummary] = useState<boolean>(false);
  const [copiedBankHalt, setCopiedBankHalt] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [ackNumber, setAckNumber] = useState<string>('');
  const [submittedStatus, setSubmittedStatus] = useState<boolean>(false);
  const [draftSaved, setDraftSaved] = useState<boolean>(false);

  const handleCopySummary = () => {
    const textToCopy = `[INCIDENT COMPLAINT DOSSIER - SCAMGRAPH PREPARED]
Case Reference: #SG-84920
Category: High Risk (Electricity Utility Impersonation / UPI Collect Fraud)
Debited Amount: INR 11,450.00
Bank UTR/RRN: 638291048291
Beneficiary UPI VPA: util-power-84920@okaxis
Suspect GSM Phone: +91 98******10
Incident Timestamp: 24 Oct 2026, 20:45:12 IST
Citizen Statement: ${statement}
Forensic SHA-256 Digest: d7a8fbb307d7809469ca9abcb0082e4f8d5651e46d3cdb762d02d0bf37c9e592
Prepared via ScamGraph Citizen Safety Prototype. Verification Section 65B BSA compliant.`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(textToCopy);
      setCopiedSummary(true);
      setTimeout(() => setCopiedSummary(false), 2500);
    }
  };

  const handleCopyHalt = () => {
    const haltSMS = 'HALT 638291048291';
    if (navigator.clipboard) {
      navigator.clipboard.writeText(haltSMS);
      setCopiedBankHalt(true);
      setTimeout(() => setCopiedBankHalt(false), 2500);
    }
  };

  const handleSaveDraft = () => {
    setDraftSaved(true);
    setTimeout(() => setDraftSaved(false), 2000);
  };

  return (
    <div className="w-full bg-ground py-4 sm:py-8 min-h-screen">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 pb-20">
        {/* Breadcrumb Nav */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-border-divider">
          <div className="flex items-center gap-2 text-xs">
            <Link
              href="/rescue/evidence"
              className="text-primary hover:text-primary-container font-semibold flex items-center gap-1 transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">arrow_back</span>
              <span>Back to Evidence Workspace</span>
            </Link>
            <span className="text-border-control">/</span>
            <span className="text-on-surface-variant font-mono">Case #SG-84920</span>
            <span className="text-border-control">/</span>
            <span className="text-on-surface font-bold">Reporting Preparation</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-surface-subtle font-mono text-[11px] text-on-surface font-bold tracking-wider uppercase rounded border border-border-divider">
              <span className="material-symbols-outlined text-[14px] text-viz-primary">gavel</span>
              STATUTORY DOSSIER GENERATION
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-tone-danger-bg text-tone-danger-strong-text text-[11px] font-bold rounded border border-tone-danger-text/20">
              <span className="material-symbols-outlined text-[14px]">timer</span>
              Golden Hour: ~2 hrs 14m remaining
            </span>
          </div>
        </div>

        {/* Page Title */}
        <div className="mt-6 max-w-3xl">
          <h1 className="text-2xl sm:text-3xl font-bold text-on-surface tracking-tight">
            Reporting preparation &amp; statutory complaint dossier
          </h1>
          <p className="text-sm text-on-surface-variant mt-1.5 leading-relaxed">
            Structure verified incident facts, transaction references, and forensic evidence for immediate submission to the National Cyber Crime Reporting Portal (NCRP) or your bank&apos;s fraud grievance desk.
          </p>
        </div>

        {/* Critical Truth Guardrail Banner */}
        <div className="my-6 p-4 sm:p-5 bg-tone-warning-bg rounded-xl border border-tone-warning-text/20 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-10 h-10 rounded-lg bg-tone-warning-strong-bg flex items-center justify-center shrink-0 text-tone-warning-strong-text">
              <span className="material-symbols-outlined text-[24px]">warning</span>
            </div>
            <div className="space-y-1">
              <div className="text-sm font-bold text-tone-warning-strong-text">
                IMPORTANT: Prepared Does Not Equal Submitted
              </div>
              <p className="text-xs text-tone-warning-text max-w-3xl leading-relaxed">
                ScamGraph prepares and verifies factual summaries for institutional submission. Opening an official link or downloading a dossier does <strong>NOT</strong> automatically lodge a police FIR or bank dispute. You must present these facts directly to the official authority.
              </p>
            </div>
          </div>
          <div className="shrink-0 self-end md:self-center">
            <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded bg-surface text-tone-warning-strong-text text-xs font-bold uppercase tracking-wider border border-border-divider shadow-sm">
              <span className={`w-2.5 h-2.5 rounded-full ${submittedStatus ? 'bg-secondary' : 'bg-viz-warning'}`}></span>
              <span>Status: {submittedStatus ? 'User-Marked Submitted' : 'Prepared (Pending Submission)'}</span>
            </span>
          </div>
        </div>

        {/* Two-Column Workspace Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column (8 cols): Primary Workspace */}
          <div className="lg:col-span-8 flex flex-col gap-8">
            {/* Official Statutory Reporting Destinations */}
            <section className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-viz-primary text-[20px]">account_balance</span>
                  <span>Official Statutory Reporting Destinations</span>
                </h2>
                <span className="text-xs text-on-surface-variant font-mono">Verified Gateways §4.7</span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Destination 1: National Cyber Crime Helpline */}
                <div className="bg-surface p-5 rounded-xl border border-border-divider shadow-sm flex flex-col justify-between gap-4">
                  <div>
                    <div className="flex items-center justify-between pb-2 border-b border-border-divider/50">
                      <span className="text-xs font-bold text-on-surface">National Cyber Crime Helpline</span>
                      <span className="px-2 py-0.5 rounded bg-surface-subtle font-mono text-[10px] text-on-surface-variant font-bold border border-border-divider">
                        MHA / 1930
                      </span>
                    </div>
                    <div className="mt-3 space-y-2 text-xs text-on-surface-variant">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-primary">call</span>
                        <span className="font-bold text-on-surface">Dial 1930 (Toll-Free, 24x7)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-primary">public</span>
                        <span className="text-on-surface font-mono">cybercrime.gov.in</span>
                      </div>
                      <div className="text-[11px] text-viz-neutral pt-1">
                        Last Verified: Today, 06:00 IST by Legal Defense Desk
                      </div>
                    </div>
                  </div>
                  <div>
                    <a
                      className="inline-flex items-center justify-center w-full h-10 px-4 rounded-lg bg-surface-subtle hover:bg-surface border border-border-divider text-on-surface text-xs font-bold transition-colors"
                      href="https://cybercrime.gov.in"
                      rel="noopener noreferrer"
                      target="_blank"
                    >
                      <span>Open National Cyber Crime Portal</span>
                      <span className="material-symbols-outlined text-[16px] ml-1.5">open_in_new</span>
                    </a>
                    <p className="text-[10px] text-on-surface-variant mt-1.5 text-center">
                      Opens in new tab. Opening will NOT change status to submitted.
                    </p>
                  </div>
                </div>

                {/* Destination 2: State Bank of India */}
                <div className="bg-surface p-5 rounded-xl border border-border-divider shadow-sm flex flex-col justify-between gap-4">
                  <div>
                    <div className="flex items-center justify-between pb-2 border-b border-border-divider/50">
                      <span className="text-xs font-bold text-on-surface">SBI Cyber Fraud Cell</span>
                      <span className="px-2 py-0.5 rounded bg-surface-subtle font-mono text-[10px] text-on-surface-variant font-bold border border-border-divider">
                        Debited Bank
                      </span>
                    </div>
                    <div className="mt-3 space-y-2 text-xs text-on-surface-variant">
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-primary">power_settings_new</span>
                        <span className="font-bold text-on-surface font-mono">SMS HALT to 9223008333</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="material-symbols-outlined text-[16px] text-primary">support_agent</span>
                        <span className="text-on-surface font-mono">Call 1800 11 1109</span>
                      </div>
                      <div className="text-[11px] text-viz-neutral pt-1">
                        Targeting UTR #638291048291 / SBI Account ending **4902
                      </div>
                    </div>
                  </div>
                  <div>
                    <button
                      onClick={handleCopyHalt}
                      className="inline-flex items-center justify-center w-full h-10 px-4 rounded-lg bg-surface-subtle hover:bg-surface border border-border-divider text-on-surface text-xs font-bold transition-colors"
                      type="button"
                    >
                      <span className="material-symbols-outlined text-[16px] mr-1.5">
                        {copiedBankHalt ? 'check' : 'content_copy'}
                      </span>
                      <span>{copiedBankHalt ? 'SMS Copied to Clipboard!' : 'Copy Emergency Freeze SMS'}</span>
                    </button>
                    <p className="text-[10px] text-on-surface-variant mt-1.5 text-center">
                      Sends immediate lien freeze request to SBI card switch.
                    </p>
                  </div>
                </div>
              </div>
            </section>

            {/* 4-Part Structured Summary Breakdown */}
            <section className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-on-surface flex items-center gap-2">
                  <span className="material-symbols-outlined text-viz-primary text-[20px]">assignment</span>
                  <span>Structured Incident Dossier Breakdown</span>
                </h2>
                <span className="text-xs text-on-surface-variant font-mono">Provenance Split Architecture §3.4</span>
              </div>

              <div className="space-y-4">
                {/* SECTION 1: Citizen Statement */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
                  <div className="flex items-center justify-between pb-3 border-b border-border-divider/50 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">Section 1: Facts You Provided</span>
                      <span className="px-2 py-0.5 rounded bg-surface-subtle text-[10px] font-bold text-on-surface border border-border-divider">
                        (You confirmed)
                      </span>
                    </div>
                    <button
                      onClick={() => setIsEditing(!isEditing)}
                      className="text-xs font-semibold text-primary hover:underline flex items-center gap-1"
                      type="button"
                    >
                      <span className="material-symbols-outlined text-[14px]">edit</span>
                      <span>{isEditing ? 'Save edits' : 'Edit statement'}</span>
                    </button>
                  </div>
                  <textarea
                    value={statement}
                    onChange={(e) => setStatement(e.target.value)}
                    readOnly={!isEditing}
                    rows={4}
                    className={`w-full text-xs text-on-surface p-3 rounded-lg border transition-all resize-y ${
                      isEditing
                        ? 'bg-surface border-primary ring-2 ring-primary/20 outline-none'
                        : 'bg-surface-subtle border-border-divider'
                    }`}
                  />
                  <p className="text-[11px] text-on-surface-variant mt-2">
                    This statement will be exported verbatim under the victim testimony section of the Form 1930 submission.
                  </p>
                </div>

                {/* SECTION 2: Extracted Technical Facts */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
                  <div className="flex items-center justify-between pb-3 border-b border-border-divider/50 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">Section 2: Extracted Technical Facts</span>
                      <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[10px] font-bold">
                        (Extracted from original artifacts)
                      </span>
                    </div>
                    <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                      <span className="material-symbols-outlined text-[13px] text-primary">lock</span>
                      Cryptographically Verified
                    </span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <tbody className="divide-y divide-border-divider">
                        <tr className="h-10">
                          <td className="text-on-surface-variant font-medium w-1/3">Debited Amount</td>
                          <td className="py-2 flex items-center justify-between gap-2">
                            <span className="text-tone-danger-text font-bold text-sm">₹11,450.00</span>
                            <span className="text-[10px] text-on-surface-variant bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                              Matched 98% OCR from PhonePe screenshot
                            </span>
                          </td>
                        </tr>
                        <tr className="h-10">
                          <td className="text-on-surface-variant font-medium">Beneficiary VPA</td>
                          <td className="py-2 flex items-center justify-between gap-2">
                            <span className="font-mono text-on-surface font-semibold">util-power-84920@okaxis</span>
                            <span className="text-[10px] text-on-surface-variant bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                              Masked in public summaries
                            </span>
                          </td>
                        </tr>
                        <tr className="h-10">
                          <td className="text-on-surface-variant font-medium">Bank UTR / RRN</td>
                          <td className="py-2 flex items-center justify-between gap-2">
                            <span className="font-mono text-on-surface font-bold">638291048291</span>
                            <span className="text-[10px] text-on-surface-variant bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                              NPCI Settlement Trace
                            </span>
                          </td>
                        </tr>
                        <tr className="h-10">
                          <td className="text-on-surface-variant font-medium">Fraudulent GSM Node</td>
                          <td className="py-2 flex items-center justify-between gap-2">
                            <span className="font-mono text-on-surface font-semibold">+91 98******10</span>
                            <span className="text-[10px] text-on-surface-variant bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                              Telecom record verified
                            </span>
                          </td>
                        </tr>
                        <tr className="h-10">
                          <td className="text-on-surface-variant font-medium">Date &amp; Timestamp</td>
                          <td className="py-2 flex items-center justify-between gap-2">
                            <span className="text-on-surface">24 Oct 2026, 20:45:12 IST</span>
                            <span className="text-[10px] text-on-surface-variant bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                              Exact from SMS/Receipt
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* SECTION 3: ScamGraph Assessment & Syndicate Context */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
                  <div className="flex items-center justify-between pb-3 border-b border-border-divider/50 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">Section 3: ScamGraph Assessment &amp; Syndicate Context</span>
                      <span className="px-2 py-0.5 rounded bg-surface-subtle text-[10px] font-bold text-viz-info border border-border-divider">
                        (ScamGraph Forensic Assessment)
                      </span>
                    </div>
                  </div>
                  <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider space-y-1.5 text-xs text-on-surface">
                    <div className="flex items-center gap-2 font-bold text-tone-danger-text">
                      <span className="material-symbols-outlined text-[18px]">policy</span>
                      <span>Categorized as High Risk (Utility Impersonation &amp; Time-Pressure Vector)</span>
                    </div>
                    <p className="text-on-surface-variant leading-relaxed">
                      Pattern correlation indicates syndicate campaign <strong>#UTL-8490</strong> active across 14 matched regional incidents. Modality involves spoofed junior officer persona requesting emergency token clearing before evening grid lockout.
                    </p>
                  </div>
                </div>

                {/* SECTION 4: Evidence & Dossier Checklist */}
                <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
                  <div className="flex items-center justify-between pb-3 border-b border-border-divider/50 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-on-surface">Section 4: Evidence &amp; Dossier Checklist</span>
                      <span className="px-2 py-0.5 rounded bg-primary text-white text-[10px] font-bold">
                        7 of 7 Ready
                      </span>
                    </div>
                    <span className="text-xs text-secondary font-bold">Ready for C14 Packaging</span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-on-surface">
                    {[
                      'Transaction UTR / RRN confirmed',
                      'Confirmed statutory debit amount (₹11,450)',
                      'Fraudulent beneficiary UPI VPA',
                      'Impersonator telephony node & call timestamp',
                      'Original WhatsApp threat screenshot with SHA-256 hash',
                      'Normalized chronological sequence timeline',
                      'Citizen identity & personal account redaction mask active'
                    ].map((item, idx) => (
                      <div key={idx} className="flex items-center gap-2 py-1">
                        <span className="material-symbols-outlined text-secondary text-[18px]">check_circle</span>
                        <span>{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* Right Column (4 cols): Sidebar Console */}
          <div className="lg:col-span-4 flex flex-col gap-6 sticky top-24">
            {/* Statutory Admissibility */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-on-surface pb-2 border-b border-border-divider">
                <span className="material-symbols-outlined text-viz-primary text-[20px]">verified</span>
                <h3 className="text-xs font-bold uppercase tracking-wide">Statutory Admissibility</h3>
              </div>
              <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider space-y-1">
                <div className="text-xs font-bold text-on-surface">Section 65B Bharatiya Sakshya Adhiniyam 2023</div>
                <p className="text-[11px] text-on-surface-variant leading-relaxed">
                  All cryptographic hash digests (SHA-256) and raw device metadata are timestamped in UTC+05:30 to satisfy electronic evidence admissibility in Indian courts.
                </p>
              </div>
              <div className="pt-1">
                <div className="text-[10px] font-bold text-on-surface uppercase tracking-wider mb-1.5">Redaction Status</div>
                <div className="flex items-center gap-2 text-tone-info-text bg-tone-info-bg p-2.5 rounded border border-tone-info-text/20 text-xs font-semibold">
                  <span className="material-symbols-outlined text-[16px]">security</span>
                  <span>Active — Phone (+91 98******10) and Bank Acc (SBI ****4902) masked.</span>
                </div>
              </div>
            </div>

            {/* Dossier Actions */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-on-surface pb-2 border-b border-border-divider">
                <span className="material-symbols-outlined text-viz-primary text-[20px]">output</span>
                <h3 className="text-xs font-bold uppercase tracking-wide">Dossier Actions</h3>
              </div>
              <div className="flex flex-col gap-2.5">
                <button
                  onClick={handleCopySummary}
                  className="inline-flex items-center justify-center min-h-[42px] px-4 rounded-lg bg-surface-subtle hover:bg-surface border border-border-divider text-on-surface text-xs font-bold transition-colors"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[16px] mr-1.5">
                    {copiedSummary ? 'check' : 'content_copy'}
                  </span>
                  <span>{copiedSummary ? 'Summary Copied to Clipboard!' : 'Copy summary for 1930 / Portal'}</span>
                </button>

                <Link
                  href="/rescue/package/SG-84920"
                  className="inline-flex items-center justify-center min-h-[42px] px-4 rounded-full bg-primary text-white hover:bg-primary-container text-xs font-bold transition-colors shadow-sm"
                >
                  <span>Review &amp; Prepare case package (C14)</span>
                  <span className="material-symbols-outlined text-[16px] ml-1.5">arrow_forward</span>
                </Link>

                <button
                  onClick={() => setShowModal(true)}
                  className="inline-flex items-center justify-center min-h-[42px] px-4 rounded-lg bg-surface-subtle hover:bg-surface border border-border-divider text-on-surface text-xs font-semibold transition-colors"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[16px] mr-1.5">check_box</span>
                  <span>Mark: I submitted this report</span>
                </button>
              </div>
              <p className="text-[11px] text-on-surface-variant text-center pt-1 leading-relaxed">
                Dossier package compiles into Section 65B compliant forensic bundle.
              </p>
            </div>
          </div>
        </div>

        {/* Sticky Bottom Navigation Bar */}
        <div className="mt-8 p-4 bg-surface rounded-xl border border-border-divider flex flex-col sm:flex-row items-center justify-between gap-4">
          <Link
            href="/rescue/evidence"
            className="inline-flex items-center h-10 px-4 rounded hover:bg-surface-subtle text-on-surface-variant text-xs font-semibold transition-colors"
          >
            <span className="material-symbols-outlined text-[16px] mr-1">arrow_back</span>
            <span>Back to Evidence workspace</span>
          </Link>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              onClick={handleSaveDraft}
              className="flex-1 sm:flex-none inline-flex items-center justify-center h-10 px-4 rounded-lg bg-surface-subtle hover:bg-surface border border-border-divider text-on-surface text-xs font-semibold transition-colors"
              type="button"
            >
              <span className="material-symbols-outlined text-[16px] mr-1">
                {draftSaved ? 'check' : 'save'}
              </span>
              <span>{draftSaved ? 'Draft Saved Locally' : 'Save draft summary'}</span>
            </button>
            <Link
              href="/rescue/package/SG-84920"
              className="flex-1 sm:flex-none inline-flex items-center justify-center h-10 px-6 rounded-full bg-primary text-white hover:bg-primary-container text-xs font-bold transition-colors shadow-sm"
            >
              <span>Proceed to Case Package (C14)</span>
              <span className="material-symbols-outlined text-[16px] ml-1">arrow_forward</span>
            </Link>
          </div>
        </div>

        {/* Citizen Submission Clarification Modal */}
        {showModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-inverse-surface/40 backdrop-blur-sm">
            <div className="bg-surface max-w-lg w-full rounded-2xl p-6 border border-border-divider shadow-xl flex flex-col gap-4">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2 text-on-surface font-bold text-base">
                  <span className="material-symbols-outlined text-viz-primary text-[22px]">flag</span>
                  <h4>Confirm Self-Submission Status</h4>
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-on-surface-variant hover:text-on-surface p-1 rounded"
                >
                  <span className="material-symbols-outlined text-[20px]">close</span>
                </button>
              </div>
              <div className="space-y-3 text-xs text-on-surface-variant">
                <p>
                  You are marking this statutory dossier as submitted by you to an external institution (NCRP Portal 1930 or State Bank of India).
                </p>
                <div className="p-3 bg-tone-warning-bg rounded-lg border border-tone-warning-text/20 text-tone-warning-strong-text text-[11px] leading-relaxed">
                  <strong>Mandatory Disclosure:</strong> ScamGraph does not maintain an automated dispatch pipeline to law enforcement. Marking this case as &ldquo;User-Marked Submitted&rdquo; will update your personal activity timeline, but does not certify institutional police processing or acknowledge receipt from state authorities.
                </div>
                <div className="flex flex-col gap-1.5 pt-1">
                  <label className="font-semibold text-on-surface">
                    Official Ack / Complaint Number (Optional):
                  </label>
                  <input
                    value={ackNumber}
                    onChange={(e) => setAckNumber(e.target.value)}
                    placeholder="e.g. 210202619308492"
                    type="text"
                    className="h-10 px-3 bg-surface-subtle border border-border-divider rounded-lg outline-none focus:bg-surface focus:ring-2 focus:ring-primary text-on-surface font-mono text-xs"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end gap-3 pt-3 border-t border-border-divider">
                <button
                  onClick={() => setShowModal(false)}
                  className="h-9 px-4 rounded text-on-surface-variant text-xs font-semibold hover:bg-surface-subtle"
                  type="button"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    setSubmittedStatus(true);
                    setShowModal(false);
                  }}
                  className="h-9 px-5 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container transition-colors shadow-sm"
                  type="button"
                >
                  Confirm Mark as Submitted
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
