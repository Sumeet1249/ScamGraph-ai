"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Card, PageSection, Badge } from "@/components/ui";
import { Brain, ShieldAlert, AlertTriangle, Eye, ShieldCheck, Filter, Search, Zap, Cpu, FlaskConical } from "lucide-react";

interface TacticItem {
  name: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  languages: string[];
  primary_actions: string[];
}

const TACTIC_DESCRIPTIONS: Record<string, { desc: string; example: string }> = {
  AUTHORITY: {
    desc: "Adversary mimics police, CBI, customs, or bank officials to compel obedience through institutional fear.",
    example: "'CBI Officer Sharma speaking. Your Aadhaar is flagged for illegal parcel trafficking in Mumbai.'",
  },
  URGENCY: {
    desc: "Forces immediate emotional reaction by imposing short deadlines (<2 hours) to bypass rational thought.",
    example: "'Your electricity connection will be disconnected tonight at 9:30 PM due to unpaid bill.'",
  },
  FEAR: {
    desc: "Threatens imminent arrest, bank account freeze, SIM blocking, or police raid unless compliance is given.",
    example: "'A non-bailable arrest warrant has been issued in your name. Do not cut the call.'",
  },
  ISOLATION: {
    desc: "Commands the victim to remain alone, stay on a continuous call, and not consult family, friends, or local police.",
    example: "'Stay in a closed room. Keep video on. Disclosing this to anyone violates the National Security Act.'",
  },
  PAYMENT_PRESSURE: {
    desc: "Demands immediate fund transfer, security deposit, or collect request approval disguised as verification.",
    example: "'Transfer ₹50,000 security deposit to the RBI verification account. Funds will be refunded in 30 mins.'",
  },
  CREDENTIAL_PRESSURE: {
    desc: "Coerces the victim into sharing OTP, PIN, NetBanking password, or CVV under the guise of an update.",
    example: "'Share the 6-digit verification code sent to your mobile to prevent immediate account block.'",
  },
  REMOTE_ACCESS_PRESSURE: {
    desc: "Instructs victim to install remote-desktop applications (AnyDesk, TeamViewer, RustDesk) or rogue APKs.",
    example: "'Download the official support helper app from this link to assist with your KYC reactivation.'",
  },
  GREED: {
    desc: "Exploits desire for quick, effortless financial gain through fake high-yield investments or daily tasks.",
    example: "'Earn ₹5,000 daily by liking YouTube videos. Deposit ₹1,000 to unlock VIP Tier.'",
  },
  LOSS_AVERSION: {
    desc: "Preys on fear of losing accumulated investments or courier shipments unless a nominal clearance fee is paid.",
    example: "'Your international parcel is held at customs. Pay ₹48 re-delivery fee or it will be destroyed.'",
  },
  SECRECY: {
    desc: "Demands complete confidentiality, warning that informing third parties will worsen criminal charges.",
    example: "'This is a secret investigation. If you inform bank staff, you will be arrested on the spot.'",
  },
};

export default function LabTacticsPage() {
  const [tactics, setTactics] = useState<TacticItem[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchTactics();
  }, []);

  const fetchTactics = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/tactics");
      if (res.ok) {
        const data = await res.json();
        setTactics(data.tactics || []);
      }
    } catch (e) {
      console.warn("Could not fetch tactics:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTactics = tactics.filter((t) => {
    const matchesSeverity = filterSeverity === "ALL" || t.severity === filterSeverity;
    const matchesSearch =
      t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (TACTIC_DESCRIPTIONS[t.name]?.desc || "").toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSeverity && matchesSearch;
  });

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return <Badge tone="danger">CRITICAL</Badge>;
      case "HIGH":
        return <Badge tone="caution">HIGH</Badge>;
      case "MEDIUM":
        return <Badge tone="info">MEDIUM</Badge>;
      default:
        return <Badge tone="neutral">{sev}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Unified Lab Sub-Navigation Bar */}
      <div className="flex items-center gap-2 border-b border-blue-100 pb-3">
        <Link
          href="/lab"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        >
          <FlaskConical className="h-3.5 w-3.5 text-slate-500" />
          <span>Attack Simulator</span>
        </Link>
        <Link
          href="/lab/arena"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
        >
          <Cpu className="h-3.5 w-3.5 text-slate-500" />
          <span>AI Model Arena</span>
        </Link>
        <Link
          href="/lab/tactics"
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-bold text-blue-700 bg-blue-50 border border-blue-200/80 shadow-2xs"
        >
          <Brain className="h-3.5 w-3.5 text-blue-600" />
          <span>Tactics Matrix</span>
        </Link>
      </div>

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono font-bold tracking-wider text-blue-700 uppercase">
            Simulation &amp; Defense Lab • Persuasion Vectors
          </span>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-900 mt-1">
            Psychological Scam Tactics Matrix
          </h1>
          <p className="text-xs text-slate-600 mt-1 max-w-2xl leading-relaxed">
            The 10 canonical coercion tactics mapped to multi-lingual regex dictionaries, Indic dialect patterns, and NLP semantic classifiers.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3.5 rounded-xl bg-white border border-blue-100 shadow-sm">
        <div className="flex items-center gap-2 flex-1 min-w-[240px]">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search tactic by name, keyword, or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-transparent border-none text-xs text-slate-900 placeholder:text-slate-400 focus:outline-none"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="h-3.5 w-3.5 text-slate-400" />
          <span className="text-[11px] font-semibold text-slate-500 uppercase">Severity:</span>
          {["ALL", "CRITICAL", "HIGH", "MEDIUM"].map((sev) => (
            <button
              key={sev}
              onClick={() => setFilterSeverity(sev)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                filterSeverity === sev
                  ? "bg-blue-600 text-white shadow-2xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Tactics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredTactics.map((t) => {
          const info = TACTIC_DESCRIPTIONS[t.name] || {
            desc: "Tactical persuasion vector utilized in psychological manipulation.",
            example: "Generic coercion template.",
          };

          return (
            <div
              key={t.name}
              className="p-5 rounded-xl bg-white border border-blue-100 shadow-sm hover:border-blue-300 transition-all flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-extrabold text-slate-900 tracking-tight">
                      {t.name.replace(/_/g, " ")}
                    </span>
                  </div>
                  {getSeverityBadge(t.severity)}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-3">
                  {info.desc}
                </p>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/70 text-xs font-mono text-slate-700 italic">
                  {info.example}
                </div>
              </div>

              <div className="pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-500">
                  <span>Languages:</span>
                  <div className="flex gap-1">
                    {t.languages?.map((lang) => (
                      <span key={lang} className="px-1.5 py-0.2 bg-blue-50 text-blue-700 border border-blue-100 rounded text-[10px] font-bold">
                        {lang}
                      </span>
                    )) || <span className="text-slate-400">hin, eng</span>}
                  </div>
                </div>

                <div className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded font-semibold text-[10px] border border-emerald-200/60">
                  ✓ Active Classifier Rule
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
