"use client";

import { useState } from "react";
import Link from "next/link";
import {
  LifeBuoy,
  PhoneCall,
  Search,
  ArrowRight,
  Shield,
  FileCheck2,
  AlertTriangle,
  HelpCircle,
  Building2,
  ChevronRight,
  ExternalLink,
  BookOpen,
} from "lucide-react";

export default function HelpCenterPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [triageStep, setTriageStep] = useState(1);
  const [situation, setSituation] = useState("Lost money via UPI");
  const [elapsed, setElapsed] = useState("< 2 hours (Golden Hour)");

  const categories = [
    {
      title: "UPI & Immediate Banking Fraud",
      desc: "Golden hour step-by-step freeze protocol, NPCI dispute management rails, chargeback window.",
      slug: "upi-banking-freeze",
      tag: "High Priority",
    },
    {
      title: "Digital Arrest & Impersonation Scams",
      desc: "Identifying fake CBI/ED/Police video call threats, Supreme Court warrants, legal safeguards.",
      slug: "digital-arrest-defense",
      tag: "Urgent Advisory",
    },
    {
      title: "Malicious APKs & Phone Takeover",
      desc: "Detection of SMS-forwarding malware, remote access trojans (AnyDesk, TeamViewer), factory reset checklist.",
      slug: "malicious-apk-removal",
      tag: "Device Safety",
    },
    {
      title: "Part-Time Task & Investment Traps",
      desc: "Telegram rating scams, fake crypto/forex yield platforms, recovery triage.",
      slug: "investment-task-scams",
      tag: "Scam Pattern",
    },
    {
      title: "Statutory Evidence & Court Filing (§65B BSA)",
      desc: "Exporting cryptographically verified evidence dossiers under Bharatiya Sakshya Adhiniyam 2023.",
      slug: "section-65b-bsa-filing",
      tag: "Legal Redressal",
    },
    {
      title: "Mule Account Notice & Police Unfreeze",
      desc: "Resolving Section 91 CrPC notices, proving legitimate identity to state cyber crime police branches.",
      slug: "mule-account-remediation",
      tag: "Account Recovery",
    },
  ];

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="max-w-[1200px] mx-auto px-4 md:px-8">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Help Center [M03]</li>
          </ol>
        </nav>

        {/* Emergency Top Banner */}
        <div className="mb-8 rounded-xl bg-tone-danger-strong-bg p-4 md:p-5 border border-tone-danger-text text-tone-danger-strong-text flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-tone-danger-text text-surface shrink-0">
              <PhoneCall className="h-4 w-4" />
            </span>
            <div>
              <p className="text-xs font-bold text-tone-danger-strong-text">
                Active Financial Cyber Emergency?
              </p>
              <p className="text-[11px] text-tone-danger-text">
                Call National Cyber Helpline <strong>1930</strong> immediately or register at cybercrime.gov.in (I4C Golden Hour Triage).
              </p>
            </div>
          </div>
          <a
            href="tel:1930"
            className="inline-flex min-h-[38px] items-center gap-1.5 rounded-full bg-tone-danger-text hover:bg-tone-danger-strong-text text-surface px-4 py-1 text-xs font-bold whitespace-nowrap shadow-sm"
          >
            <span>Call 1930 Now</span>
          </a>
        </div>

        {/* Hero & Search Omnibox */}
        <div className="max-w-[760px] mx-auto text-center mb-10">
          <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
            <span className="w-2 h-2 rounded-full bg-viz-primary" />
            [M03] Citizen Support &amp; Fraud Resolution
          </div>
          <h1 className="text-2xl md:text-4xl font-bold text-on-surface tracking-tight mb-3">
            How can we help resolve your situation?
          </h1>
          <p className="text-xs md:text-sm text-on-surface-variant mb-6">
            Empowering Indian citizens with actionable guides, statutory templates, and instant recovery workflows.
          </p>

          {/* Search Box */}
          <div className="relative w-full max-w-[600px] mx-auto">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-viz-neutral" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by fraud type e.g., 'UPI QR Code scam', 'fake courier APK', 'digital arrest'..."
              className="w-full pl-11 pr-4 py-3 rounded-full border border-border-control bg-surface text-on-surface text-xs md:text-sm shadow-sm focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
            />
          </div>
        </div>

        {/* 6 Core Knowledge & Action Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          {categories.map((cat, idx) => (
            <Link
              key={idx}
              href={`/help-center/${cat.slug}`}
              className="bg-surface rounded-xl border border-border-divider p-5 shadow-sm hover:border-viz-primary transition-all flex flex-col justify-between gap-4 group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary bg-selected-tint px-2 py-0.5 rounded">
                    {cat.tag}
                  </span>
                  <ChevronRight className="h-4 w-4 text-viz-neutral group-hover:text-viz-primary transition-colors" />
                </div>
                <h2 className="text-sm font-bold text-on-surface mb-1.5 group-hover:text-viz-primary transition-colors">
                  {cat.title}
                </h2>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  {cat.desc}
                </p>
              </div>
              <div className="text-[11px] font-bold text-viz-primary flex items-center gap-1">
                <span>View action guide</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </div>
            </Link>
          ))}
        </div>

        {/* Interactive Instant Help Wizard Card */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-6 mb-12">
          <div className="border-b border-border-divider pb-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary">
              Interactive Triage Stepper
            </span>
            <h2 className="text-lg md:text-xl font-bold text-on-surface">
              Instant Action Recommender
            </h2>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Select your exact circumstances to see the mandatory statutory roadmap.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-1.5">
                <span className="text-xs font-bold text-on-surface">1. What happened?</span>
                <div className="flex flex-col gap-2">
                  {[
                    "Lost money via UPI",
                    "Received digital arrest video call",
                    "Installed remote APK",
                    "Bank account frozen by cyber cell",
                  ].map((sit) => (
                    <button
                      key={sit}
                      type="button"
                      onClick={() => setSituation(sit)}
                      className={`text-left p-3 rounded-lg text-xs font-semibold border transition-colors ${
                        situation === sit
                          ? "bg-selected-tint border-viz-primary text-viz-primary"
                          : "bg-surface-subtle border-border-control text-on-surface hover:bg-surface"
                      }`}
                    >
                      {sit}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-1.5">
                <span className="text-xs font-bold text-on-surface">2. Time elapsed since event:</span>
                <div className="flex flex-wrap gap-2">
                  {[
                    "< 2 hours (Golden Hour)",
                    "2–24 hours",
                    "> 24 hours",
                  ].map((el) => (
                    <button
                      key={el}
                      type="button"
                      onClick={() => setElapsed(el)}
                      className={`min-h-[36px] px-3 py-1 rounded-lg text-xs font-medium border transition-colors ${
                        elapsed === el
                          ? "bg-viz-primary text-on-primary border-viz-primary font-bold"
                          : "bg-surface-subtle text-on-surface border-border-control hover:bg-surface"
                      }`}
                    >
                      {el}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Tailored Roadmap Output Card */}
            <div className="bg-surface-subtle rounded-xl border border-border-divider p-5 flex flex-col gap-3.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary">
                Instant Tailored Roadmap:
              </span>
              <h3 className="text-sm font-bold text-on-surface">
                Recommended Action for {situation}:
              </h3>
              <ul className="text-xs text-on-surface-variant space-y-2 list-disc list-inside leading-relaxed">
                {elapsed.includes("Golden Hour") ? (
                  <>
                    <li>
                      <strong>Dial 1930 immediately:</strong> Golden Hour is active (84% salvage rate).
                    </li>
                    <li>
                      <strong>Call Bank Fraud Desk:</strong> Request a lien on the recipient UPI UTR.
                    </li>
                    <li>
                      <strong>Open ScamGraph Rescue:</strong> Generate formal Section 65B annexure for police complaint.
                    </li>
                  </>
                ) : (
                  <>
                    <li>
                      <strong>File Written Notice to Bank Nodal Officer:</strong> Request formal chargeback under RBI guidelines.
                    </li>
                    <li>
                      <strong>Generate Evidence Package:</strong> Export cryptographically signed WhatsApp and debit logs.
                    </li>
                    <li>
                      <strong>Lodge NCRP Complaint:</strong> Register formal cyber crime portal docket.
                    </li>
                  </>
                )}
              </ul>

              <div className="pt-2">
                <Link
                  href="/rescue"
                  className="inline-flex min-h-[40px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
                >
                  <span>Launch Guided Action Flow</span>
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
