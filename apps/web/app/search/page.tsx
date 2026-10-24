"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  ArrowRight,
  Database,
  Building,
  Phone,
  Globe,
  FileText,
  Lock,
  Layers,
  ChevronRight,
  ShieldAlert,
} from "lucide-react";

interface SearchHit {
  type: "VPA" | "PHONE" | "DOMAIN" | "INCIDENT" | "CAMPAIGN" | "FIR";
  title: string;
  subtitle: string;
  score: number;
  link: string;
  tags: string[];
}

const SAMPLE_HITS: SearchHit[] = [
  {
    type: "VPA",
    title: "util-power-84920@okaxis",
    subtitle: "Axis Bank · Linked to 14 corroborated extortion cases in #UTL-8490",
    score: 98,
    link: "/entity/ENT-UPI-AXIS-84920",
    tags: ["High Risk", "Mule Node", "Axis Bank"],
  },
  {
    type: "CAMPAIGN",
    title: "State Electricity Instant Cutoff Syndicate (#UTL-8490)",
    subtitle: "Active pan-regional coercive payment extortion campaign · 142 cases",
    score: 94,
    link: "/campaigns/camp-power-urgent",
    tags: ["Surging", "+340% / 4h", "Outbreak Candidate"],
  },
  {
    type: "PHONE",
    title: "+91 98******10 Pool",
    subtitle: "Telephony Anchor · 14 observed incoming SIMs, common LAC 404-45",
    score: 92,
    link: "/graph",
    tags: ["Telephony", "GSM Rotation"],
  },
  {
    type: "DOMAIN",
    title: "bescom-bill-renew.in",
    subtitle: "DNS Sinkholed · 14 referrals mimicking state electricity portal",
    score: 89,
    link: "/graph",
    tags: ["Domain", "Phishing"],
  },
  {
    type: "INCIDENT",
    title: "#SG-84920 — BESCOM Immediate Disconnection & Mandate",
    subtitle: "Victim loss: ₹11,450 · High urgency (<45m window)",
    score: 98,
    link: "/incidents/SG-2026-84920",
    tags: ["High Risk", "Active"],
  },
  {
    type: "FIR",
    title: "FIR No. 0142/2026 (Cyber Crime PS Bengaluru)",
    subtitle: "State of Karnataka vs. State Electricity Cutoff Extortion Syndicate",
    score: 95,
    link: "/cases/CASE-2026-KA-0941",
    tags: ["§66D IT Act", "BNSS §318(4)"],
  },
];

export default function GlobalSearchPage() {
  const [query, setQuery] = useState("");
  const [activeFilter, setActiveFilter] = useState<string>("ALL");

  const filteredHits = SAMPLE_HITS.filter((hit) => {
    if (activeFilter !== "ALL" && hit.type !== activeFilter) return false;
    if (!query.trim()) return true;
    const q = query.toLowerCase();
    return (
      hit.title.toLowerCase().includes(q) ||
      hit.subtitle.toLowerCase().includes(q) ||
      hit.tags.some((t) => t.toLowerCase().includes(q))
    );
  });

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* 1. Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A16 Global Intelligence Search</span>
          <span>•</span>
          <span>1.4M Entity Nodes Indexed</span>
        </div>
      </div>

      <div className="p-4 lg:p-8 space-y-5 max-w-[1280px] mx-auto w-full">
        {/* Title */}
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
              <Search className="w-3.5 h-3.5" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-viz-text">Global Intelligence Search</h1>
            <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
              §7 A16
            </span>
          </div>
          <p className="text-xs text-viz-neutral mt-1">
            Search across 1.4M graph nodes, NPCI transaction references, beneficiary VPAs, GSM phone hashes, spoofed URLs, and formal police FIRs.
          </p>
        </div>

        {/* Omnibar */}
        <div className="relative w-full">
          <Search className="absolute left-4 top-3.5 w-5 h-5 text-viz-primary" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by VPA handle, phone hash, domain, campaign ID, FIR number, UTR..."
            className="w-full h-12 pl-12 pr-4 bg-surface rounded-xl border border-border-divider text-sm text-viz-text placeholder:text-viz-neutral focus:outline-none focus:border-viz-primary shadow-sm"
          />
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          {["ALL", "VPA", "PHONE", "DOMAIN", "CAMPAIGN", "INCIDENT", "FIR"].map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`h-7 px-3 rounded-full font-medium transition-colors ${
                activeFilter === f
                  ? "bg-viz-primary text-white font-semibold"
                  : "bg-surface hover:bg-surface-subtle text-viz-text border border-border-divider"
              }`}
            >
              {f === "ALL" ? "All Results (1.4M)" : f}
            </button>
          ))}
        </div>

        {/* Results List */}
        <div className="space-y-3">
          <div className="text-xs font-bold uppercase tracking-wider text-viz-neutral">
            Showing {filteredHits.length} verified graph matches
          </div>

          <div className="space-y-2">
            {filteredHits.map((hit, idx) => (
              <Link
                key={idx}
                href={hit.link}
                className="block p-4 rounded-xl bg-surface border border-border-divider hover:border-viz-primary hover:bg-[#0B6256]/[0.02] transition-all group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-1.5 py-0.2 rounded bg-surface-subtle border border-border-divider font-mono text-[10px] uppercase font-bold text-viz-neutral">
                        {hit.type}
                      </span>
                      <h3 className="text-sm font-bold text-viz-text group-hover:text-viz-primary transition-colors">
                        {hit.title}
                      </h3>
                    </div>
                    <p className="text-xs text-viz-neutral">{hit.subtitle}</p>
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {hit.tags.map((t) => (
                        <span key={t} className="px-2 py-0.5 rounded bg-surface-subtle text-[10px] text-viz-text">
                          {t}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs font-mono font-bold text-viz-primary">{hit.score}% Match</span>
                    <ChevronRight className="w-4 h-4 text-viz-neutral group-hover:text-viz-primary group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
