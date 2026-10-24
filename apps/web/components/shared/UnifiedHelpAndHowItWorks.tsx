"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Shield,
  Search,
  Scale,
  Network,
  Cpu,
  Database,
  Lock,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Layers,
  FileCheck2,
  LifeBuoy,
  PhoneCall,
  HelpCircle,
  Building2,
  ChevronRight,
  ExternalLink,
  BookOpen,
  Sparkles,
  Smartphone,
  KeyRound,
  FileText,
  Clock,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui";

interface Props {
  initialTab?: "all" | "how-it-works" | "help-center" | "emergency";
}

export default function UnifiedHelpAndHowItWorks({ initialTab = "all" }: Props) {
  const [activeTab, setActiveTab] = useState<"all" | "how-it-works" | "help-center" | "emergency">(initialTab);
  const [searchQuery, setSearchQuery] = useState("");
  const [situation, setSituation] = useState("Lost money via UPI");
  const [elapsed, setElapsed] = useState("< 2 hours (Golden Hour)");

  // 7 Dimensions of ScamGraph Journey Architecture
  const dimensions = [
    {
      num: "01",
      name: "Semantic Urgency & Impersonation NLP",
      desc: "Detects coercive Hindi/Hinglish/English keywords, fake CBI/police threats, electricity cutoff deadlines, and emotional blackmail markers.",
      icon: Search,
      category: "nlp",
    },
    {
      num: "02",
      name: "Web Infrastructure & TinyFish RDAP",
      desc: "Measures domain registration age, DNS clusters, free TLD usage (.tk, .ml), and stealth redirect chains leading to remote APK downloads.",
      icon: Cpu,
      category: "infra",
    },
    {
      num: "03",
      name: "Payment Intent & VPA Discrepancy",
      desc: "Detects mismatches between purported corporate/government entities and the actual beneficiary UPI handle (e.g., electricity bill paid to private individual).",
      icon: Scale,
      category: "payment",
    },
    {
      num: "04",
      name: "Temporal Grooming Velocity",
      desc: "Tracks the elapsed time across contact stages. Attackers applying rapid acceleration to force payment within 30 minutes are flagged.",
      icon: Layers,
      category: "temporal",
    },
    {
      num: "05",
      name: "Reused Infrastructure & Sender Telemetry",
      desc: "Correlates recycled mobile numbers, shared virtual servers, and SIM box clusters across multi-victim datasets.",
      icon: Network,
      category: "telemetry",
    },
    {
      num: "06",
      name: "Historical Incident Graph Traversal",
      desc: "Queries Neo4j and NetworkX property graphs to link incoming identifiers with past 1930 NCRP complaints and police notices.",
      icon: Database,
      category: "graph",
    },
    {
      num: "07",
      name: "High-Dimensional Campaign Similarity",
      desc: "Computes 12D ScamDNA embeddings and multilingual sentence vectors to match tactic variants against active Indian scam syndicate clusters.",
      icon: FileCheck2,
      category: "embeddings",
    },
  ];

  // 6 Help Center Core Knowledge & Action Categories
  const categories = [
    {
      title: "UPI & Immediate Banking Fraud",
      desc: "Golden hour step-by-step freeze protocol, NPCI dispute management rails, bank lien notices under Section 91 CrPC.",
      slug: "upi-banking-freeze",
      tag: "High Priority",
      icon: Zap,
    },
    {
      title: "Digital Arrest & Impersonation Scams",
      desc: "Identifying fake CBI/ED/Police video call threats, forged Supreme Court arrest warrants, and legal safeguards.",
      slug: "digital-arrest-defense",
      tag: "Urgent Advisory",
      icon: Shield,
    },
    {
      title: "Malicious APKs & Phone Takeover",
      desc: "Detection of SMS-forwarding malware, remote access trojans (AnyDesk, TeamViewer QuickSupport), and removal checklist.",
      slug: "malicious-apk-removal",
      tag: "Device Safety",
      icon: Smartphone,
    },
    {
      title: "Part-Time Task & Investment Traps",
      desc: "Telegram rating scams, fake crypto/forex yield platforms, VIP tier traps, and recovery triage.",
      slug: "investment-task-scams",
      tag: "Scam Pattern",
      icon: Layers,
    },
    {
      title: "Statutory Evidence & Court Filing (§65B BSA)",
      desc: "Exporting cryptographically verified SHA-256 evidence dossiers under Bharatiya Sakshya Adhiniyam 2023.",
      slug: "section-65b-bsa-filing",
      tag: "Legal Redressal",
      icon: FileText,
    },
    {
      title: "Mule Account Notice & Police Unfreeze",
      desc: "Resolving Section 91 CrPC / Section 102 BNSS notices, proving legitimate identity to state cyber crime police branches.",
      slug: "mule-account-remediation",
      tag: "Account Recovery",
      icon: Building2,
    },
  ];

  // Bank Helplines
  const bankHelplines = [
    { name: "1930 Cyber Helpline", phone: "1930", note: "National 24x7 Emergency" },
    { name: "State Bank of India (SBI)", phone: "1800-11-1109", note: "Cyber Cell" },
    { name: "HDFC Bank", phone: "1800-266-4332", note: "Fraud Desk" },
    { name: "ICICI Bank", phone: "1800-1080", note: "Emergency Hotline" },
    { name: "Axis Bank", phone: "1860-419-5555", note: "Fraud Operations" },
    { name: "Punjab National Bank", phone: "1800-180-2222", note: "24x7 Help" },
  ];

  // Filter items based on search query
  const filteredCategories = categories.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.desc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredDimensions = dimensions.filter(
    (d) =>
      d.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.desc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="w-full bg-background min-h-screen py-8 md:py-12">
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* ── Breadcrumb ────────────────────────────────────────── */}
        <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-xs text-text-muted font-medium">
          <Link href="/" className="hover:text-brand-primary transition-colors">
            ScamGraph AI
          </Link>
          <span>/</span>
          <span className="text-text-primary font-bold">Unified Knowledge & Help Center</span>
        </nav>

        {/* ── Emergency 1930 Top Banner ─────────────────────────── */}
        <div className="rounded-2xl border border-red-500/40 bg-red-950/20 p-5 text-red-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-md">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-600 text-white shrink-0 shadow-lg shadow-red-950/50">
              <PhoneCall className="h-5 w-5" />
            </span>
            <div>
              <p className="text-sm font-bold text-red-300">
                Active Cyber Financial Fraud or Emergency Loss?
              </p>
              <p className="text-xs text-red-200/90">
                Call National Cyber Crime Helpline <strong>1930</strong> immediately within the Golden Hour (<a href="/rescue" className="underline font-bold text-white hover:text-red-200">or open ScamGraph Emergency Rescue</a>).
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/rescue"
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-lg border border-red-400 bg-red-500/20 hover:bg-red-500/30 text-white px-4 py-1.5 text-xs font-bold transition-all"
            >
              <Zap className="h-3.5 w-3.5" />
              <span>Launch Rescue Portal</span>
            </Link>
            <a
              href="tel:1930"
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-lg bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 text-xs font-bold transition-all shadow-md"
            >
              <PhoneCall className="h-3.5 w-3.5" />
              <span>Dial 1930 Now</span>
            </a>
          </div>
        </div>

        {/* ── Unified Hero & Search Omnibox ──────────────────────── */}
        <div className="max-w-3xl mx-auto text-center space-y-4 pt-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-primary/30 bg-brand-primary/10 px-3 py-1 text-xs font-bold uppercase tracking-wider text-brand-primary">
            <Sparkles className="h-3.5 w-3.5" />
            Combined Knowledge Base & Forensic Verification Engine
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold text-text-primary tracking-tight">
            How ScamGraph Works &amp; Help Center
          </h1>
          <p className="text-sm md:text-base text-text-secondary leading-relaxed">
            Everything you need in one place: Understand the 7-dimensional forensic architecture of ScamGraph AI, or access step-by-step resolution guides for Indian cyber fraud victims.
          </p>

          {/* Search Box */}
          <div className="relative w-full max-w-xl mx-auto pt-2">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search guides or technology (e.g. 'UPI freeze', 'Digital arrest', '12D ScamDNA', 'AnyDesk')..."
              className="w-full pl-11 pr-4 py-3 rounded-full border border-border bg-background-elevated text-text-primary text-xs md:text-sm shadow-sm focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
            />
          </div>
        </div>

        {/* ── Mode / Section Selector Tabs ──────────────────────── */}
        <div className="flex justify-center border-b border-border pb-1">
          <div className="flex flex-wrap gap-2 p-1 rounded-xl bg-background-elevated border border-border">
            <button
              onClick={() => setActiveTab("all")}
              className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "all"
                  ? "bg-brand-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              All-In-One Unified View
            </button>
            <button
              onClick={() => setActiveTab("how-it-works")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "how-it-works"
                  ? "bg-brand-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <Cpu className="h-3.5 w-3.5" />
              How It Works (7 Dimensions)
            </button>
            <button
              onClick={() => setActiveTab("help-center")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "help-center"
                  ? "bg-brand-primary text-white shadow-sm"
                  : "text-text-secondary hover:text-text-primary"
              }`}
            >
              <LifeBuoy className="h-3.5 w-3.5" />
              Help Center &amp; Action Guides
            </button>
            <button
              onClick={() => setActiveTab("emergency")}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                activeTab === "emergency"
                  ? "bg-red-600 text-white shadow-sm"
                  : "text-red-400 hover:text-red-300"
              }`}
            >
              <PhoneCall className="h-3.5 w-3.5" />
              Emergency Helplines &amp; 1930
            </button>
          </div>
        </div>

        {/* ══════════════════════════════════════════════════════════ */}
        {/* SECTION 1: HOW SCAMGRAPH WORKS (FORENSIC ARCHITECTURE)     */}
        {/* ══════════════════════════════════════════════════════════ */}
        {(activeTab === "all" || activeTab === "how-it-works") && (
          <section className="space-y-6 pt-4">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border pb-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-brand-primary">
                  Core Forensic Engine
                </span>
                <h2 className="text-2xl md:text-3xl font-extrabold text-text-primary mt-1">
                  7-Dimensional Scam Journey Recognition
                </h2>
                <p className="text-xs md:text-sm text-text-secondary mt-1 max-w-2xl">
                  Traditional fraud systems check transactions only at the point of settlement. ScamGraph AI reconstructs the psychological, linguistic, and infrastructural journey that precedes financial intent.
                </p>
              </div>

              <Link href="/shield">
                <Button variant="primary" size="sm" className="text-xs font-bold">
                  <span>Try Scam Journey Scanner</span>
                  <ArrowRight className="ml-1.5 h-3.5 w-3.5" />
                </Button>
              </Link>
            </div>

            {/* 7 Dimensions Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredDimensions.map((dim) => {
                const Icon = dim.icon;
                return (
                  <div
                    key={dim.num}
                    className="rounded-2xl border border-border bg-background-elevated p-5 shadow-sm flex flex-col justify-between gap-3 hover:border-brand-primary/60 transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-3">
                        <span className="font-mono text-xl font-black text-brand-primary group-hover:scale-105 transition-transform">
                          {dim.num}
                        </span>
                        <div className="p-2 rounded-xl bg-background border border-border text-brand-primary group-hover:bg-brand-primary group-hover:text-white transition-colors">
                          <Icon className="h-4 w-4" />
                        </div>
                      </div>
                      <h3 className="text-sm font-bold text-text-primary mb-1.5 group-hover:text-brand-primary transition-colors">
                        {dim.name}
                      </h3>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {dim.desc}
                      </p>
                    </div>
                    <div className="text-[10px] font-mono font-semibold uppercase tracking-wider text-text-muted border-t border-border pt-2.5">
                      Subsystem: {dim.category.toUpperCase()}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Dual-Axis Matrix Card */}
            <div className="rounded-2xl border border-border bg-background-elevated p-6 md:p-8 shadow-sm flex flex-col lg:flex-row items-center justify-between gap-8">
              <div className="max-w-xl space-y-3">
                <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-brand-primary">
                  <Scale className="h-3.5 w-3.5" />
                  Core Architecture Rule
                </div>
                <h3 className="text-xl md:text-2xl font-bold text-text-primary">
                  Dual-Axis Risk Assessment &amp; No Single Model
                </h3>
                <p className="text-xs md:text-sm text-text-secondary leading-relaxed">
                  No single machine learning model or LLM is permitted to unilaterally declare fraud. The system independently computes <strong>Risk Level</strong> (Severity of threat) and <strong>Evidence Confidence</strong> (Corroboration certainty). If data points are sparse, we default to <strong>INSUFFICIENT_EVIDENCE</strong> rather than causing false alarms.
                </p>
                <div className="flex gap-3 pt-2">
                  <Link href="/guard">
                    <Button variant="outline" size="sm" className="text-xs">
                      <Shield className="mr-1.5 h-3.5 w-3.5" /> Test Pre-Payment Guard
                    </Button>
                  </Link>
                  <Link href="/radar">
                    <Button variant="outline" size="sm" className="text-xs">
                      <Network className="mr-1.5 h-3.5 w-3.5" /> View Outbreak Radar
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Matrix Badge Display */}
              <div className="w-full lg:w-auto p-5 rounded-xl border border-border bg-background flex flex-col gap-2.5 shrink-0">
                <span className="text-[11px] font-bold uppercase tracking-wider text-text-muted">
                  Evaluation Grid States:
                </span>
                <div className="flex items-center gap-2 text-xs">
                  <span className="rounded-md bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 font-semibold text-emerald-400">
                    State 1 • No strong warning signs (Clean)
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="rounded-md bg-zinc-500/15 border border-zinc-500/30 px-3 py-1 font-semibold text-zinc-300">
                    State 2 • Insufficient evidence (Silent observation)
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="rounded-md bg-amber-500/15 border border-amber-500/30 px-3 py-1 font-semibold text-amber-400">
                    State 4 • Be careful (Contextual advisory banner)
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <span className="rounded-md bg-red-500/20 border border-red-500/40 px-3 py-1 font-bold text-red-400">
                    State 6 • High risk / Act now (15s Cognitive Pause / Block)
                  </span>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════════════════════ */}
        {/* SECTION 2: INTERACTIVE ACTION RECOMMENDER (TRIAGE STEPPER) */}
        {/* ══════════════════════════════════════════════════════════ */}
        {(activeTab === "all" || activeTab === "help-center") && (
          <section className="space-y-6 pt-4">
            <div className="rounded-2xl border border-border bg-background-elevated p-6 md:p-8 shadow-sm space-y-6">
              <div className="border-b border-border pb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-brand-primary">
                  Interactive Triage Stepper
                </span>
                <h2 className="text-xl md:text-2xl font-bold text-text-primary mt-1">
                  Instant Fraud Resolution Action Recommender
                </h2>
                <p className="text-xs text-text-secondary mt-0.5">
                  Select your exact circumstances below to receive your immediate statutory roadmap.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-primary">1. What happened?</label>
                    <div className="grid gap-2 sm:grid-cols-2">
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
                          className={`text-left p-3 rounded-xl text-xs font-semibold border transition-all ${
                            situation === sit
                              ? "bg-brand-primary/15 border-brand-primary text-brand-primary font-bold shadow-sm"
                              : "bg-background border-border text-text-secondary hover:border-brand-primary/40 hover:text-text-primary"
                          }`}
                        >
                          {sit}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-xs font-bold text-text-primary">2. Time elapsed since event:</label>
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
                          className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                            elapsed === el
                              ? "bg-brand-primary text-white border-brand-primary shadow-sm"
                              : "bg-background text-text-secondary border-border hover:border-brand-primary/40"
                          }`}
                        >
                          {el}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Tailored Roadmap Output Card */}
                <div className="rounded-2xl border border-brand-primary/30 bg-brand-primary/5 p-5 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-brand-primary">
                      Instant Tailored Roadmap
                    </span>
                    <span className="rounded-full bg-brand-primary/20 px-2 py-0.5 text-[10px] font-mono text-brand-primary">
                      {elapsed.includes("Golden Hour") ? "84% FREEZE SUCCESS RATE" : "STATUTORY ESCALATION"}
                    </span>
                  </div>

                  <h3 className="text-sm font-bold text-text-primary">
                    Action Plan for: <span className="text-brand-primary">{situation}</span>
                  </h3>

                  <ul className="text-xs text-text-secondary space-y-2 list-disc list-inside leading-relaxed">
                    {elapsed.includes("Golden Hour") ? (
                      <>
                        <li>
                          <strong>Dial 1930 Helpline immediately:</strong> Golden Hour is active. Provide the officer with the 12-digit UTR.
                        </li>
                        <li>
                          <strong>Call Bank Fraud Desk:</strong> Request an administrative debit lien on the recipient VPA under Section 91 CrPC.
                        </li>
                        <li>
                          <strong>Open ScamGraph Rescue:</strong> Auto-generate formal 1930 complaint dossier and statutory bank notice.
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
                          <strong>Lodge NCRP Complaint:</strong> Register formal cybercrime portal complaint docket at cybercrime.gov.in.
                        </li>
                      </>
                    )}
                  </ul>

                  <div className="pt-2">
                    <Link
                      href="/rescue"
                      className="inline-flex items-center gap-2 rounded-xl bg-brand-primary hover:bg-brand-primary-hover text-white px-5 py-2 text-xs font-bold transition-all shadow-md"
                    >
                      <span>Launch Guided Rescue Flow</span>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════════════════════ */}
        {/* SECTION 3: CITIZEN RESOLUTION GUIDES (6 ACTION CARDS)      */}
        {/* ══════════════════════════════════════════════════════════ */}
        {(activeTab === "all" || activeTab === "help-center") && (
          <section className="space-y-6 pt-4">
            <div className="border-b border-border pb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-primary">
                Resolution Knowledge Base
              </span>
              <h2 className="text-2xl md:text-3xl font-extrabold text-text-primary mt-1">
                Citizen Support &amp; Fraud Resolution Guides
              </h2>
              <p className="text-xs md:text-sm text-text-secondary mt-1">
                Detailed step-by-step action manuals covering common cybercrime vectors in India.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredCategories.map((cat, idx) => {
                const Icon = cat.icon;
                return (
                  <Link
                    key={idx}
                    href={`/help-center/${cat.slug}`}
                    className="rounded-2xl border border-border bg-background-elevated p-5 shadow-sm hover:border-brand-primary transition-all flex flex-col justify-between gap-4 group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-brand-primary bg-brand-primary/10 border border-brand-primary/20 px-2 py-0.5 rounded-md">
                          {cat.tag}
                        </span>
                        <ChevronRight className="h-4 w-4 text-text-muted group-hover:text-brand-primary transition-colors" />
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Icon className="h-4 w-4 text-brand-primary" />
                        <h3 className="text-sm font-bold text-text-primary group-hover:text-brand-primary transition-colors">
                          {cat.title}
                        </h3>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        {cat.desc}
                      </p>
                    </div>

                    <div className="text-[11px] font-bold text-brand-primary flex items-center gap-1 border-t border-border pt-3">
                      <span>View step-by-step action guide</span>
                      <ArrowRight className="h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </section>
        )}

        {/* ══════════════════════════════════════════════════════════ */}
        {/* SECTION 4: EMERGENCY HELPLINES & 24x7 BANK DIRECTORY       */}
        {/* ══════════════════════════════════════════════════════════ */}
        {(activeTab === "all" || activeTab === "emergency") && (
          <section className="space-y-6 pt-4">
            <div className="rounded-2xl border border-border bg-background-elevated p-6 md:p-8 shadow-sm space-y-6">
              <div className="border-b border-border pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-red-400">
                    Verified Emergency Channels
                  </span>
                  <h2 className="text-xl md:text-2xl font-bold text-text-primary mt-1">
                    24x7 Bank Fraud Emergency Hotlines &amp; Police Portals
                  </h2>
                  <p className="text-xs text-text-secondary mt-0.5">
                    Official, verified direct helplines to immediately request debit liens and freeze stolen funds.
                  </p>
                </div>
                <a href="tel:1930">
                  <Button variant="danger" size="sm" className="bg-red-600 hover:bg-red-700 text-white font-bold">
                    <PhoneCall className="mr-1.5 h-4 w-4" /> Call 1930 Hotline
                  </Button>
                </a>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {bankHelplines.map((b) => (
                  <div key={b.name} className="rounded-xl border border-border bg-background p-4 flex items-center justify-between gap-3">
                    <div>
                      <div className="text-xs font-bold text-text-primary">{b.name}</div>
                      <div className="text-[11px] text-text-muted">{b.note}</div>
                      <div className="text-xs font-mono font-bold text-brand-primary mt-1">
                        {b.phone}
                      </div>
                    </div>
                    <a
                      href={`tel:${b.phone}`}
                      className="p-2.5 rounded-lg bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white transition-colors"
                      title={`Call ${b.name}`}
                    >
                      <PhoneCall className="h-4 w-4" />
                    </a>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
