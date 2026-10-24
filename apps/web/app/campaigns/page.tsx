"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { Card } from "@/components/ui";
import { humanize, formatDateTime } from "@/lib/utils/format";
import { RotateCw, Share2 } from "lucide-react";

interface CampaignItem {
  id: string;
  name: string;
  pattern_type: string;
  severity: string;
  incidents_count: number;
  shared_infrastructure_count: number;
  first_seen: string;
  last_seen: string;
  tactics?: string[];
  sample_domain?: string;
  sample_vpa?: string;
  description?: string;
}

const DEFAULT_CAMPAIGNS: CampaignItem[] = [
  {
    id: "camp-kyc-freenom",
    name: "State Bank & Aadhaar KYC Suspension Syndicate",
    pattern_type: "KYC_IMPERSONATION",
    severity: "CRITICAL",
    incidents_count: 24,
    shared_infrastructure_count: 7,
    first_seen: "2026-10-15T08:30:00Z",
    last_seen: "2026-10-20T17:45:00Z",
    sample_domain: "sbi-kyc-verify-portal.online",
    description: "Coordinated cluster targeting banking customers using spoofed SMS, KYC warnings, and malicious domains.",
  },
  {
    id: "camp-power-urgent",
    name: "Electricity & Utility Disconnection Phishing Ring",
    pattern_type: "UTILITY_BILL_COERCION",
    severity: "HIGH",
    incidents_count: 18,
    shared_infrastructure_count: 4,
    first_seen: "2026-10-12T10:00:00Z",
    last_seen: "2026-10-20T19:00:00Z",
    sample_domain: "electricity-bill-pay.xyz",
    description: "Urgent electricity shutoff notices redirecting to unauthorized merchant collect requests.",
  },
  {
    id: "camp-work-from-home",
    name: "E-Commerce Rating & Telegram Task Fraud Network",
    pattern_type: "PART_TIME_JOB_FRAUD",
    severity: "HIGH",
    incidents_count: 12,
    shared_infrastructure_count: 5,
    first_seen: "2026-10-16T11:00:00Z",
    last_seen: "2026-10-20T20:15:00Z",
    sample_domain: "task-earning-hub.xyz",
    description: "Deceptive part-time job lures promising daily returns for rating videos.",
  },
  {
    id: "camp-investment-vip",
    name: "High-Yield VIP Crypto & Stock Advisory Syndicate",
    pattern_type: "INVESTMENT_LURE",
    severity: "MEDIUM",
    incidents_count: 10,
    shared_infrastructure_count: 3,
    first_seen: "2026-10-14T09:00:00Z",
    last_seen: "2026-10-22T09:37:00Z",
    sample_domain: "vip-stock-trade.top",
    description: "WhatsApp group pump-and-dump scheme mimicking institutional stock brokerages.",
  },
];

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>(DEFAULT_CAMPAIGNS);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCampaigns = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/campaigns");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setCampaigns(data);
        }
      }
    } catch (err) {
      console.warn("Failed to fetch campaigns:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCampaigns();

    // Auto-poll every 5 seconds for real-time synchronization
    const interval = setInterval(fetchCampaigns, 5000);

    const handleStorage = (e: StorageEvent) => {
      if (e.key === "recent_investigations") {
        fetchCampaigns();
      }
    };
    window.addEventListener("storage", handleStorage);

    return () => {
      clearInterval(interval);
      window.removeEventListener("storage", handleStorage);
    };
  }, [fetchCampaigns]);

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Command"
        title="Emerging Threat Campaigns"
        description="Correlated scam clusters sharing infrastructure, payment VPAs, or deceptive workflows in real time."
        actions={
          <div className="flex items-center gap-3">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-safe/10 border border-safe/30 text-safe text-xs font-medium">
              <span className="h-2 w-2 rounded-full bg-safe animate-pulse" />
              <span>LIVE CLUSTERS</span>
            </div>
            <button
              onClick={fetchCampaigns}
              disabled={isLoading}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full border border-line bg-surface hover:bg-surface-hover text-xs font-medium text-ink transition-all disabled:opacity-50 btn-pop"
              title="Refresh campaigns"
            >
              <RotateCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
              Refresh
            </button>
            <DemoDataBadge />
          </div>
        }
      />

      {/* Section 10.2: Responsive 2-column layout on wide desktop, 1-column on mobile */}
      <div className="grid gap-5 md:grid-cols-2">
        {campaigns.map((c) => {
          const isCritical = c.severity === "CRITICAL";
          const isHigh = c.severity === "HIGH";

          return (
            <Link key={c.id} href={`/campaigns/${c.id}`} className="block h-full group">
              <Card className="h-full flex flex-col justify-between transition-colors border-border bg-surface-1 hover:border-border-strong hover:bg-surface-2/70 p-5 rounded-xl">
                <div>
                  <div className="flex items-start justify-between gap-3">
                    <h3 className="text-sm font-semibold text-text-primary group-hover:text-brand-primary transition-colors line-clamp-2">
                      {c.name}
                    </h3>
                    <span
                      className={`shrink-0 rounded-md border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider2 ${
                        isCritical
                          ? "border-danger/30 bg-danger/10 text-danger"
                          : isHigh
                          ? "border-warning/30 bg-warning/10 text-warning"
                          : "border-signal/30 bg-signal/10 text-signal"
                      }`}
                    >
                      {c.severity}
                    </span>
                  </div>
                  <p className="mt-2 text-xs text-text-muted flex items-center gap-1.5">
                    <Share2 className="h-3 w-3 text-brand-primary" />
                    <span>{humanize(c.pattern_type)}</span>
                  </p>
                  {c.description && (
                    <p className="mt-2.5 text-xs text-text-secondary leading-relaxed line-clamp-2">
                      {c.description}
                    </p>
                  )}
                </div>

                <div className="mt-5 pt-3.5 border-t border-border/80">
                  <dl className="grid grid-cols-2 gap-y-2 text-xs">
                    <div>
                      <dt className="text-text-muted text-[11px]">Correlated Incidents</dt>
                      <dd className="font-mono font-bold text-text-primary tabular-nums mt-0.5">
                        {c.incidents_count}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-text-muted text-[11px]">Shared Infrastructure</dt>
                      <dd className="font-mono text-text-secondary tabular-nums mt-0.5">
                        {c.shared_infrastructure_count}
                      </dd>
                    </div>
                    <div className="col-span-2">
                      <dt className="text-text-muted text-[11px]">Latest Activity</dt>
                      <dd className="font-mono text-text-muted text-[11px] mt-0.5">
                        {formatDateTime(c.last_seen)}
                      </dd>
                    </div>
                  </dl>
                  {c.sample_domain && (
                    <div className="mt-3 overflow-hidden rounded bg-surface-2 px-2.5 py-1.5 border border-border">
                      <p className="truncate font-mono text-[11px] text-text-secondary">
                        Domain: <span className="text-text-primary">{c.sample_domain}</span>
                      </p>
                    </div>
                  )}
                </div>
              </Card>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
