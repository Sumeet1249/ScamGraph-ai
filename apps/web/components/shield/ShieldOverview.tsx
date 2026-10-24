"use client";

import { useEffect, useState } from "react";
import { PageSection, Card, Grid, MetricCard, Badge } from "@/components/ui";
import { Lock, CheckCircle, Clock, Link2 } from "lucide-react";

const THREATS_THIS_WEEK = [
  {
    name: "KYC Verification Scam",
    risk: "HIGH" as const,
    count: 1247,
    pattern: "Fake bank KYC process",
    description: "Scammers pose as banks asking to verify account details or credentials.",
  },
  {
    name: "Investment Opportunity Fraud",
    risk: "MEDIUM" as const,
    count: 892,
    pattern: "Crypto, forex, stock tips",
    description: "Too-good-to-be-true investment opportunities with guaranteed returns.",
  },
  {
    name: "Job Task Scam",
    risk: "MEDIUM" as const,
    count: 654,
    pattern: "Fake remote work jobs",
    description: "Work-from-home jobs that ask for upfront payment or personal data.",
  },
  {
    name: "Fake Refund/Support",
    risk: "HIGH" as const,
    count: 423,
    pattern: "Government/bank impersonation",
    description: "Impersonation of official support asking to verify accounts or make payments.",
  },
];

const PROTECTION_TIPS = [
  {
    title: "Never share OTPs",
    description:
      "Real banks and platforms never ask for OTPs via message or call. An OTP is as valuable as your password.",
    icon: Lock,
  },
  {
    title: "Verify before paying",
    description:
      "Always independently verify bank details. Scammers impersonate official numbers. Use the official app or call the known number.",
    icon: CheckCircle,
  },
  {
    title: "Watch for urgency",
    description:
      'Scammers create false urgency ("act now!", "verify immediately!"). Legitimate institutions give you time to verify.',
    icon: Clock,
  },
  {
    title: "Check domains carefully",
    description:
      'Domains like "facebook-secure.com" or "bank-verify.co" are not the real services. Official domains end in their real name.',
    icon: Link2,
  },
];

export function ShieldOverview() {
  const [metrics, setMetrics] = useState({
    activeThreats: 247,
    patternsTracked: 89,
    userScore: 92,
    lastCheck: "Now",
  });

  // In Phase 3, these would come from the backend
  useEffect(() => {
    // Simulate metric updates
    const interval = setInterval(() => {
      setMetrics((m) => ({
        ...m,
        activeThreats: Math.round(m.activeThreats + (Math.random() - 0.5) * 20),
      }));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <PageSection
        title="Your Protection Status"
        description="Real-time threats detected in your area"
      >
        <Grid columns="4" gap="md">
          <MetricCard
            label="Active Threats"
            value={metrics.activeThreats}
            tone="danger"
            detail="↑ 14 in last 24h"
          />
          <MetricCard
            label="Patterns Tracked"
            value={metrics.patternsTracked}
            tone="caution"
            detail="KYC, Investment, Job scams"
          />
          <MetricCard
            label="Your Score"
            value={metrics.userScore}
            tone="success"
            detail="Protected status"
          />
          <MetricCard
            label="Last Check"
            value={metrics.lastCheck}
            tone="neutral"
            detail="Real-time monitoring"
          />
        </Grid>
      </PageSection>

      {/* Common Threats */}
      <PageSection
        title="Common Threats This Week"
        description="Scam patterns trending in your region"
      >
        <Grid columns="1" gap="md">
          {THREATS_THIS_WEEK.map((threat) => (
            <Card key={threat.name} pad="md" className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <h4 className="font-semibold text-text-primary">{threat.name}</h4>
                <p className="text-body-sm text-text-secondary mt-1">{threat.pattern}</p>
                <p className="text-body-sm text-text-muted mt-2">{threat.description}</p>
                <p className="text-label text-text-muted mt-3 uppercase">
                  {threat.count.toLocaleString()} incidents detected
                </p>
              </div>
              <div className="flex-shrink-0">
                <Badge tone={threat.risk === "HIGH" ? "danger" : "caution"}>
                  {threat.risk}
                </Badge>
              </div>
            </Card>
          ))}
        </Grid>
      </PageSection>

      {/* Protection Tips (Section 13.4) */}
      <PageSection
        title="Stay Protected"
        description="Essential security practices"
      >
        <Grid columns="2" gap="md">
          {PROTECTION_TIPS.map((tip) => {
            const Icon = tip.icon;
            return (
              <Card key={tip.title} pad="md" className="flex flex-col gap-2 bg-surface-1 border border-border">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-inset text-text-muted border border-border-input mb-1">
                  <Icon className="h-4 w-4" />
                </div>
                <h4 className="font-semibold text-text-primary text-sm">{tip.title}</h4>
                <p className="text-xs text-text-secondary leading-relaxed">{tip.description}</p>
              </Card>
            );
          })}
        </Grid>
      </PageSection>

      {/* Resources */}
      <PageSection
        title="More Resources"
        description="Learn about scam prevention and report threats"
      >
        <Grid columns="2" gap="md">
          <Card pad="md" className="flex flex-col gap-3">
            <h4 className="font-semibold text-text-primary">Report a Scam</h4>
            <p className="text-body-sm text-text-secondary">
              Help us identify new threats by reporting suspicious messages, links, or payment requests.
            </p>
            <a
              href="#"
              className="text-brand-primary hover:text-brand-hover font-semibold text-body-sm"
            >
              Open Report Form →
            </a>
          </Card>
          <Card pad="md" className="flex flex-col gap-3">
            <h4 className="font-semibold text-text-primary">Need Help?</h4>
            <p className="text-body-sm text-text-secondary">
              If you&apos;ve already been scammed, follow our guide to minimize damage and protect your accounts.
            </p>
            <a
              href="#"
              className="text-brand-primary hover:text-brand-hover font-semibold text-body-sm"
            >
              Recovery Guide →
            </a>
          </Card>
        </Grid>
      </PageSection>
    </div>
  );
}
