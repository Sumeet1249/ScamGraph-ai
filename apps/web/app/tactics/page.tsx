"use client";

import { useState, useEffect } from "react";
import { Card, PageSection, Badge } from "@/components/ui";
import { Brain, ShieldAlert, AlertTriangle, Eye, ShieldCheck, Filter, Search, Zap } from "lucide-react";

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
    desc: "Forces immediate emotional reaction by imposing short deadlines (&lt;2 hours) to bypass rational thought.",
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

export default function TacticsPage() {
  const [tactics, setTactics] = useState<TacticItem[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadTactics() {
      try {
        const res = await fetch("/api/v1/tactics");
        if (res.ok) {
          const data = await res.json();
          setTactics(data.tactics_taxonomy?.tactics || []);
        }
      } catch (e) {
        console.warn("Could not load tactics:", e);
      } finally {
        setIsLoading(false);
      }
    }
    loadTactics();
  }, []);

  const filtered = tactics.filter((t) => {
    const matchesSev = filterSeverity === "ALL" || t.severity === filterSeverity;
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSev && matchesSearch;
  });

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return <Badge tone="danger">CRITICAL SEVERITY</Badge>;
      case "HIGH":
        return <Badge tone="caution">HIGH RISK</Badge>;
      case "MEDIUM":
        return <Badge tone="neutral">MEDIUM RISK</Badge>;
      default:
        return <Badge tone="success">LOW RISK</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <span className="text-xs font-mono font-bold tracking-wider text-accent uppercase">Psychological Intelligence</span>
          <h1 className="text-3xl font-black font-mono tracking-tight text-text-primary mt-1">
            Canonical Manipulation Tactics Matrix
          </h1>
          <p className="text-body-sm text-text-secondary mt-1">
            20 standardized social-engineering psychological coercion techniques extracted across multi-turn Indic audio calls, WhatsApp chats, and SMS messages.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-2 border border-border text-xs font-mono text-text-primary font-bold">
            <Brain className="h-4 w-4 text-purple-400" />
            20 CANONICAL TACTICS LOADED
          </span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-4 rounded-xl bg-surface-2 border border-border shadow-sm">
        <div className="flex flex-wrap items-center gap-2">
          <Filter className="h-4 w-4 text-text-muted" />
          <span className="text-xs font-mono text-text-muted">Severity:</span>
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => (
            <button
              key={s}
              onClick={() => setFilterSeverity(s)}
              className={`px-2.5 py-1 rounded text-xs font-mono transition-all border ${
                filterSeverity === s
                  ? "bg-accent-soft text-accent border-accent-line font-bold"
                  : "bg-surface-1 text-text-secondary hover:text-text-primary border-border"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="h-3.5 w-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
          <input
            type="text"
            placeholder="Search tactic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-8 pr-3 py-1.5 text-xs font-mono rounded-lg bg-surface-1 border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent"
          />
        </div>
      </div>

      {/* Grid of 20 Tactics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((t) => {
          const meta = TACTIC_DESCRIPTIONS[t.name] || {
            desc: `Psychological manipulation exploiting ${t.name.toLowerCase().replace(/_/g, " ")} mechanics to override victim decision-making.`,
            example: `Adversary triggers ${t.name.toLowerCase().replace(/_/g, " ")} cues demanding immediate action.`,
          };

          return (
            <div
              key={t.name}
              className="p-5 rounded-xl bg-surface-2 border border-border hover:border-accent/50 transition-all space-y-3"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-accent" />
                  <h3 className="font-bold font-mono text-text-primary text-base">
                    {t.name}
                  </h3>
                </div>
                {getSeverityBadge(t.severity)}
              </div>

              <p className="text-xs font-mono text-text-secondary leading-relaxed">
                {meta.desc}
              </p>

              {/* Realistic Example */}
              <div className="p-2.5 rounded bg-surface-inset border border-border/60 text-[11px] font-mono text-amber-300/90 italic">
                &ldquo;{meta.example}&rdquo;
              </div>

              {/* Action Vectors & Locales */}
              <div className="pt-2 border-t border-border/60 flex flex-wrap items-center justify-between gap-2 text-[10px] font-mono text-text-muted">
                <div className="flex items-center gap-1.5 flex-wrap">
                  <span className="font-bold text-text-secondary">Action Triggers:</span>
                  {t.primary_actions.map((act) => (
                    <span
                      key={act}
                      className="px-1.5 py-0.5 rounded bg-surface-1 border border-border text-text-secondary"
                    >
                      {act}
                    </span>
                  ))}
                </div>
                <div>
                  Locales: <span className="text-text-secondary">{t.languages.join(", ")}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
