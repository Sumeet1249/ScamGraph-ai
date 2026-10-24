"use client";

import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { Card, Badge } from "@/components/ui";
import { SimilarityBreakdown } from "@/components/campaigns/SimilarityBreakdown";
import { EvidenceGraph } from "@/components/graph/EvidenceGraph";
import { ThreatNetworkFallback } from "@/components/three/ThreatNetworkScene";
import { formatDateTime } from "@/lib/utils/format";
import { demoCampaigns, demoGraph } from "@/lib/demo/fixtures";
import type { FingerprintSimilarityResult } from "@/lib/api/types";

const demoSimilarity: FingerprintSimilarityResult = {
  semantic_similarity: 0.91,
  journey_similarity: 0.94,
  infrastructure_similarity: 0.19,
  payment_similarity: 0.22,
  pattern_similarity: 0.86,
  identifier_overlap: 0.0,
  overall_similarity_index: 0.62,
  matched_dimensions: ["Semantic", "Journey", "Pattern"],
  different_dimensions: ["Infrastructure", "Identifier"],
  shared_entities: [],
  shared_patterns: ["KYC_IMPERSONATION"],
  sequence_alignment: {},
  explanation:
    "Identifiers changed across phone, domain, and payment, but the behavioral workflow (impersonation → urgency → credential → OTP → payment) remained similar.",
};

export default function CampaignPage({ params }: { params: { id: string } }) {
  const campaign = demoCampaigns.find((c) => c.id === params.id) ?? demoCampaigns[0];

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Campaign"
        title={campaign.name}
        description="Possible emerging campaign. Shared infrastructure and workflow correlation across incidents."
        actions={<DemoDataBadge />}
      />

      <div className="flex flex-wrap items-center gap-2.5">
        <Badge tone={campaign.severity === "CRITICAL" ? "danger" : "caution"}>{campaign.severity}</Badge>
        <Badge tone="brand">{campaign.pattern_type.replace(/_/g, " ").toLowerCase()}</Badge>
        <Badge tone="neutral">{campaign.incidents_count} incidents</Badge>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card pad="md">
          <div className="eyebrow">Observed incidents</div>
          <p className="mt-2 font-mono text-2xl font-bold text-ink">{campaign.incidents_count}</p>
        </Card>
        <Card pad="md">
          <div className="eyebrow">Shared infrastructure</div>
          <p className="mt-2 font-mono text-2xl font-bold text-ink">{campaign.shared_infrastructure_count}</p>
        </Card>
        <Card pad="md">
          <div className="eyebrow">First observed</div>
          <p className="mt-2 font-mono text-xs text-ink-muted">{formatDateTime(campaign.first_seen)}</p>
        </Card>
        <Card pad="md">
          <div className="eyebrow">Confidence</div>
          <p className="mt-2 text-2xl font-semibold text-caution">Medium</p>
        </Card>
      </div>

      {/* Fingerprint comparison — static placeholder in Phase 1; Three.js morph in Phase 6/7 */}
      <Card pad="none" className="overflow-hidden">
        <div className="flex items-center justify-between border-b border-line px-5 py-3">
          <span className="eyebrow">Fingerprint Comparison</span>
          <span className="font-mono text-[11px] text-ink-dim">Known Campaign vs New Incident · 3D in Phase 6/7</span>
        </div>
        <div className="grid gap-0 lg:grid-cols-[1fr_1fr]">
          <div className="flex h-72 items-center justify-center border-b border-line lg:border-b-0 lg:border-r">
            <ThreatNetworkFallback />
          </div>
          <div className="p-5">
            <SimilarityBreakdown similarity={demoSimilarity} />
          </div>
        </div>
      </Card>

      <div>
        <div className="eyebrow mb-3">Campaign Graph</div>
        <EvidenceGraph graph={demoGraph} />
      </div>
    </div>
  );
}
