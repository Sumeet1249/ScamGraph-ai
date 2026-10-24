"use client";

import { useState } from "react";
import { PageHeader } from "@/components/shared/PageHeader";
import { DemoDataBadge } from "@/components/shared/DemoDataBadge";
import { ShieldOverview, ShieldQuickCheck } from "@/components/shield";

export default function ShieldPage() {
  const [activeTab, setActiveTab] = useState<"overview" | "analyze">("overview");

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <PageHeader
        eyebrow="Shield"
        title="Security Hub"
        description="Quick security checks and threat assessment. Verify suspicious activity before taking action."
        actions={<DemoDataBadge />}
      />

      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-border">
        <button
          onClick={() => setActiveTab("overview")}
          className={`px-4 py-2.5 text-body-sm font-semibold transition-colors ${
            activeTab === "overview"
              ? "text-text-primary border-b-2 border-brand-primary -mb-px"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setActiveTab("analyze")}
          className={`px-4 py-2.5 text-body-sm font-semibold transition-colors ${
            activeTab === "analyze"
              ? "text-text-primary border-b-2 border-brand-primary -mb-px"
              : "text-text-secondary hover:text-text-primary"
          }`}
        >
          Quick Check
        </button>
      </div>

      {/* Content */}
      {activeTab === "overview" && <ShieldOverview />}
      {activeTab === "analyze" && <ShieldQuickCheck />}
    </div>
  );
}
