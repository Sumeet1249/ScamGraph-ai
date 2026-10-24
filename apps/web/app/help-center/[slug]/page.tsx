'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function HelpTopicPage() {
  const params = useParams();
  const slug = (params?.slug as string) || 'power-disconnection-mandate-scams';
  const [copied, setCopied] = useState(false);

  const handleShare = () => {
    if (typeof window !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="w-full max-w-[720px] mx-auto pb-16 flex flex-col gap-6">
      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs text-on-surface-variant pt-2">
        <Link className="hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded" href="/">
          Home
        </Link>
        <span aria-hidden="true" className="text-border-control">/</span>
        <Link className="hover:text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded" href="/help-center">
          Help Center
        </Link>
        <span aria-hidden="true" className="text-border-control">/</span>
        <span aria-current="page" className="text-on-surface font-semibold truncate">
          Power disconnection &amp; Mandate scams
        </span>
      </nav>

      {/* Editorial Header Block */}
      <header className="flex flex-col gap-2 pb-2">
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-tone-danger-bg text-tone-danger-strong-text text-xs font-bold tracking-wide uppercase inline-flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-tone-danger-text inline-block"></span>
            Critical Consumer Advisory · Electricity &amp; Utilities
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface">
          BESCOM &amp; Electricity Bill Disconnection Threats: What You Need to Know
        </h1>
        <div className="p-4 rounded-xl bg-surface-subtle text-on-surface flex flex-col gap-2 border border-border-divider">
          <p className="text-sm text-on-surface leading-relaxed">
            Scammers send urgent SMS messages threatening immediate power disconnection due to pending bills, instructing victims to call a fake official number or approve a ₹10 test verification that secretly drains thousands.
          </p>
          <div className="flex flex-wrap items-center gap-3 pt-1 text-on-surface-variant text-xs">
            <span className="inline-flex items-center gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-[16px] text-primary">verified</span>
              Verified Public Defense Advisory
            </span>
            <span>•</span>
            <span>Updated: Today</span>
            <span>•</span>
            <span>Read time: 3 mins</span>
          </div>
        </div>
      </header>

      {/* Urgent Contextual Intervention Hero Banner */}
      <section aria-labelledby="triage-callout" className="rounded-xl bg-tone-warning-bg p-4 text-tone-warning-strong-text border border-tone-warning-text/20 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-full bg-tone-warning-strong-bg flex items-center justify-center shrink-0 mt-0.5 text-viz-warning">
              <span aria-hidden="true" className="material-symbols-outlined text-[20px]">report_problem</span>
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold text-tone-warning-strong-text" id="triage-callout">
                Are you currently targeted?
              </span>
              <span className="text-xs text-tone-warning-text">
                Immediate guidance for active conversations or completed transactions.
              </span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <Link
              href="/rescue"
              className="h-[40px] px-4 rounded-full bg-tone-danger-strong-text text-white text-xs font-semibold inline-flex items-center justify-center gap-1.5 hover:opacity-95 transition-opacity focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 whitespace-nowrap"
            >
              <span aria-hidden="true" className="material-symbols-outlined text-[16px]">emergency</span>
              <span>I already paid / shared PIN</span>
            </Link>
            <Link
              href="/check"
              className="h-[40px] px-4 rounded-full bg-surface text-viz-text text-xs font-medium inline-flex items-center justify-center gap-1.5 hover:bg-surface-subtle border border-border-divider transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 whitespace-nowrap"
            >
              <span aria-hidden="true" className="material-symbols-outlined text-[16px] text-primary">search_check</span>
              <span>Check SMS text</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Visual Artifact: Anatomy of the Phishing SMS */}
      <section className="flex flex-col gap-2 pt-1">
        <span className="text-xs uppercase tracking-wider text-on-surface-variant font-bold">
          Evidence Simulation · SMS Anatomy
        </span>
        <div className="rounded-xl bg-surface-subtle p-4 flex flex-col gap-3 border border-border-divider">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-error"></span>
              <span className="text-xs font-bold text-tone-danger-text">Spoofed Fraudulent SMS Payload</span>
            </div>
            <span className="text-xs px-2 py-0.5 rounded bg-surface border border-border-divider text-on-surface-variant font-mono">
              From: +91 98450 12391
            </span>
          </div>
          <div className="p-3 rounded-lg bg-surface font-mono text-xs text-on-surface shadow-sm leading-relaxed border border-border-divider">
            “Dear consumer your electricity power will be cut tonight at 9:30 PM due to unpaid bill. Immediately contact officer 9845012391.”
          </div>
          <div className="flex flex-wrap gap-3 text-tone-danger-strong-text text-xs pt-1">
            <span className="inline-flex items-center gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-[15px] text-error">cancel</span>
              Standard 10-digit phone sender (No CP-BESCOM / DLT Header)
            </span>
            <span className="inline-flex items-center gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-[15px] text-error">timer</span>
              Artificial same-day cut-off deadline
            </span>
          </div>
        </div>
      </section>

      {/* Section 1: How It Starts */}
      <section className="flex flex-col gap-2 pt-2">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-primary text-white font-bold text-xs flex items-center justify-center">1</span>
          <h2 className="text-lg font-bold text-on-surface">How It Starts</h2>
        </div>
        <p className="text-sm text-on-surface leading-relaxed">
          High-urgency SMS messages arrive on personal phones claiming imminent power disruption. They intentionally arrive from standard 10-digit mobile numbers rather than legitimate official DLT transactional headers (like <code className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border-divider text-primary font-mono text-xs font-semibold">CP-BESCOM</code> or <code className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border-divider text-primary font-mono text-xs font-semibold">KA-DISCOM</code>).
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="p-3 rounded-xl bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/20 flex flex-col gap-1">
            <span className="text-xs font-bold flex items-center gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-[16px] text-error">close</span>
              Fraudulent Patterns
            </span>
            <span className="text-xs">
              Sent via WhatsApp, Telegram, or personal numbers (+91 9xxxxxxxxx) with immediate threats of same-evening blackouts.
            </span>
          </div>
          <div className="p-3 rounded-xl bg-tone-info-bg text-tone-info-text border border-tone-info-text/20 flex flex-col gap-1">
            <span className="text-xs font-bold flex items-center gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-[16px] text-viz-info">check_circle</span>
              Statutory Protocol
            </span>
            <span className="text-xs">
              Disconnection requires formal 15-day statutory written notice under Section 56 of Electricity Act, 2003. Never sudden SMS threats.
            </span>
          </div>
        </div>
      </section>

      {/* Section 2: What They Ask You to Do */}
      <section className="flex flex-col gap-2 pt-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-primary text-white font-bold text-xs flex items-center justify-center">2</span>
          <h2 className="text-lg font-bold text-on-surface">What They Ask You to Do</h2>
        </div>
        <p className="text-sm text-on-surface leading-relaxed">
          When a frightened consumer calls the listed contact number, the scammer follows an engineered social playbook structured across three sequential manipulations:
        </p>
        <div className="flex flex-col gap-3 pt-1">
          <div className="p-3.5 rounded-xl bg-surface-subtle border border-border-divider flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-surface border border-border-divider flex items-center justify-center shrink-0 text-primary">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px]">support_agent</span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-xs font-bold text-on-surface">1. The “Nodal Officer” Impersonation</span>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                You are connected with a calm, polite actor claiming to represent the power authority&apos;s central billing division. They state that while you may have paid, the central ledger sync failed, requiring an immediate manual reconnect token.
              </p>
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-surface-subtle border border-border-divider flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-surface border border-border-divider flex items-center justify-center shrink-0 text-primary">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px]">download</span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-xs font-bold text-on-surface">2. Sideloading the Utility Helper APK</span>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                They send a direct link via WhatsApp or SMS to download files like <code className="px-1 py-0.5 rounded bg-surface border border-border-divider text-error font-mono text-xs">bescom-quickpay.apk</code>, <code className="px-1 py-0.5 rounded bg-surface border border-border-divider text-error font-mono text-xs">urja-sync.apk</code>, or insist on installing screen-sharing software (AnyDesk, TeamViewer QuickSupport) to “assist you.”
              </p>
            </div>
          </div>
          <div className="p-3.5 rounded-xl bg-surface-subtle border border-border-divider flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-surface border border-border-divider flex items-center justify-center shrink-0 text-primary">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px]">pin</span>
            </div>
            <div className="flex flex-col gap-0.5">
              <span className="text-xs font-bold text-on-surface">3. The “₹10 Verification / Refund” Trap</span>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                The attacker prompts you to open PhonePe, Google Pay, or Paytm and approve a ₹10 test transaction or enter your secret UPI PIN to “authenticate receipt of clearance.” In reality, this executes an unapproved debit or sets an automated recurring mandate.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Key Warning Signs */}
      <section className="flex flex-col gap-2 pt-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-primary text-white font-bold text-xs flex items-center justify-center">3</span>
          <h2 className="text-lg font-bold text-on-surface">Key Warning Signs (Never Ignore These)</h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <div className="p-3.5 rounded-xl bg-tone-danger-strong-bg text-tone-danger-strong-text border border-tone-danger-strong-text/20 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px] text-error">warning</span>
              <span className="text-xs font-bold">Urgency Countdown</span>
            </div>
            <p className="text-xs leading-relaxed">
              Demands compliance with arbitrary deadlines (“Power will be cut at 9:30 PM tonight”). Official state disconnections cannot legally occur after hours or without documented notice.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-tone-danger-strong-bg text-tone-danger-strong-text border border-tone-danger-strong-text/20 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px] text-error">phone_iphone</span>
              <span className="text-xs font-bold">Personal Mobile Helplines</span>
            </div>
            <p className="text-xs leading-relaxed">
              Official electricity utilities (BESCOM, TANGEDCO, MSEDCL, Tata Power) route customer issues through dedicated 4-digit short codes (e.g., 1912), never personal 10-digit mobile numbers.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-tone-danger-strong-bg text-tone-danger-strong-text border border-tone-danger-strong-text/20 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px] text-error">android</span>
              <span className="text-xs font-bold">APK Files via Chat</span>
            </div>
            <p className="text-xs leading-relaxed">
              Any instruction to install an APK file from WhatsApp, Telegram, or unknown web domains grants keylogger and SMS interception rights directly to the attacker.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-tone-danger-strong-bg text-tone-danger-strong-text border border-tone-danger-strong-text/20 flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <span aria-hidden="true" className="material-symbols-outlined text-[18px] text-error">password</span>
              <span className="text-xs font-bold">UPI PIN to “Receive” Money</span>
            </div>
            <p className="text-xs font-semibold leading-relaxed">
              UPI PIN is ONLY entered when deducting money from your bank account. Entering a PIN is NEVER required to receive money, receive verification, or check bill status.
            </p>
          </div>
        </div>
      </section>

      {/* Section 4: What to Do Now */}
      <section className="flex flex-col gap-2 pt-3">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded bg-primary text-white font-bold text-xs flex items-center justify-center">4</span>
          <h2 className="text-lg font-bold text-on-surface">What to Do Now (Step-by-Step)</h2>
        </div>
        <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-3">
          <ol className="flex flex-col gap-3 text-xs text-on-surface">
            <li className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-primary text-white font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">1</span>
              <span className="font-semibold text-sm">Do not approve any UPI collect request or enter your UPI PIN under any circumstance.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-primary text-white font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">2</span>
              <span>Disconnect any ongoing phone call and immediately uninstall any recently sideloaded helper APK or remote-desktop app (AnyDesk, QuickSupport).</span>
            </li>
            <li className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-primary text-white font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">3</span>
              <span>Verify your actual electricity bill status directly by logging into your official state utility website or calling the statutory public helpline <strong className="text-primary font-bold">1912</strong>.</span>
            </li>
            <li className="flex items-start gap-2.5">
              <span className="w-5 h-5 rounded-full bg-primary text-white font-bold text-[11px] flex items-center justify-center shrink-0 mt-0.5">4</span>
              <span className="text-tone-danger-text font-medium">If money was already deducted, immediately call your bank to freeze transaction liens and dial the National Cyber Crime Helpline at <strong className="underline font-bold text-tone-danger-strong-text">1930</strong> (or file at cybercrime.gov.in within the golden hour).</span>
            </li>
          </ol>
        </div>
      </section>

      {/* Contextual Intervention Actions Box */}
      <section className="rounded-xl bg-surface-subtle p-5 flex flex-col gap-4 border border-border-divider">
        <div className="flex flex-col gap-0.5">
          <h3 className="text-base font-bold text-on-surface">Take Immediate Protective Action</h3>
          <p className="text-xs text-on-surface-variant">Use ScamGraph defense tools to analyze incoming messages or trigger immediate recovery protocols.</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <Link
            href="/check"
            className="p-4 rounded-xl bg-surface hover:bg-surface-subtle transition-colors flex flex-col justify-between gap-3 group border border-border-divider shadow-sm"
          >
            <div className="flex flex-col gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-primary text-[24px]">sms</span>
              <span className="text-xs font-bold text-on-surface group-hover:text-primary transition-colors">Check Suspicious Message</span>
              <span className="text-[11px] text-on-surface-variant">Analyze sender DLT headers and phone numbers against the fraud registry.</span>
            </div>
            <span className="text-xs text-primary font-semibold flex items-center gap-1">
              Check message →
            </span>
          </Link>
          <Link
            href="/guard"
            className="p-4 rounded-xl bg-surface hover:bg-surface-subtle transition-colors flex flex-col justify-between gap-3 group border border-border-divider shadow-sm"
          >
            <div className="flex flex-col gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-primary text-[24px]">verified_user</span>
              <span className="text-xs font-bold text-on-surface group-hover:text-primary transition-colors">Check Before I Pay</span>
              <span className="text-[11px] text-on-surface-variant">Verify UPI handles, payment collect links, and beneficiary account risk scores.</span>
            </div>
            <span className="text-xs text-primary font-semibold flex items-center gap-1">
              Check before I pay →
            </span>
          </Link>
          <Link
            href="/rescue"
            className="p-4 rounded-xl bg-tone-danger-bg hover:bg-tone-danger-strong-bg transition-colors flex flex-col justify-between gap-3 group border border-tone-danger-text/20 shadow-sm"
          >
            <div className="flex flex-col gap-1">
              <span aria-hidden="true" className="material-symbols-outlined text-error text-[24px]">emergency_home</span>
              <span className="text-xs font-bold text-tone-danger-strong-text">I Already Paid or Shared</span>
              <span className="text-[11px] text-tone-danger-text">Step-by-step 1930 reporting script, bank lien freeze template, and evidence logs.</span>
            </div>
            <span className="text-xs text-tone-danger-strong-text font-bold flex items-center gap-1">
              Emergency rescue →
            </span>
          </Link>
        </div>
      </section>

      {/* Authority Verification Signature */}
      <div className="p-3.5 rounded-xl bg-surface-subtle text-on-surface-variant flex flex-col sm:flex-row items-center justify-between gap-3 text-xs border border-border-divider">
        <div className="flex items-center gap-2">
          <span aria-hidden="true" className="material-symbols-outlined text-primary text-[18px]">security</span>
          <span>Standardized by ScamGraph Consumer Intelligence Division in coordination with Indian DISCOM alerts.</span>
        </div>
        <button
          onClick={handleShare}
          className="h-[34px] px-3 rounded bg-surface hover:bg-surface-subtle text-on-surface border border-border-divider text-xs font-semibold inline-flex items-center gap-1 transition-colors focus:outline-none focus:ring-2 focus:ring-primary shrink-0"
          type="button"
        >
          <span aria-hidden="true" className="material-symbols-outlined text-[15px]">{copied ? 'check' : 'share'}</span>
          <span>{copied ? 'Link Copied!' : 'Share Alert'}</span>
        </button>
      </div>
    </div>
  );
}
