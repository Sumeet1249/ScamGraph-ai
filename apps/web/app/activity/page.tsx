"use client";

import Link from "next/link";
import {
  FileText,
  Clock,
  ArrowRight,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  FileCheck2,
  Plus,
} from "lucide-react";

export default function MyActivityPage() {
  const activities = [
    {
      id: "SG-2026-89412",
      type: "UPI Financial Dispute",
      entity: "mule.recovery@ybl",
      bank: "ICICI Bank",
      amount: "₹45,000",
      status: "Lien Escalation Active",
      date: "24 Oct 2026, 18:15 IST",
      risk: "HIGH",
    },
    {
      id: "SG-2026-87103",
      type: "Fake Courier Digital Arrest Call",
      entity: "+91-9876543210",
      bank: "N/A (Pre-Transaction Blocked)",
      amount: "₹0 (Intercepted)",
      status: "Resolved & Reported",
      date: "22 Oct 2026, 11:30 IST",
      risk: "CRITICAL",
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
            <li className="text-viz-text font-bold">My Activity &amp; Cases [C15]</li>
          </ol>
        </nav>

        {/* Section Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-viz-primary" />
              [C15] Citizen Incident Ledger
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-on-surface">
              My Verified Activity &amp; Dispute Dockets
            </h1>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Track status of interbank freeze requests, Section 65B court packages, and verified incident checks.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/check"
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-4 py-1 text-xs font-semibold shadow-sm transition-colors"
            >
              <span>New Check [C01]</span>
            </Link>
            <Link
              href="/rescue"
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-tone-danger-text text-surface hover:bg-tone-danger-strong-text px-4 py-1 text-xs font-bold shadow-sm transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Log Incident [C08]</span>
            </Link>
          </div>
        </div>

        {/* Activity Cards Table */}
        <div className="bg-surface rounded-xl border border-border-divider shadow-sm overflow-hidden flex flex-col divide-y divide-border-divider">
          {activities.map((act) => (
            <div
              key={act.id}
              className="p-5 md:p-6 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-surface-subtle transition-colors"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-selected-tint rounded-xl text-viz-primary shrink-0 mt-0.5">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold text-on-surface">{act.type}</span>
                    <span className="text-[10px] font-mono text-viz-neutral bg-surface-subtle px-1.5 py-0.5 rounded border border-border-divider">
                      #{act.id}
                    </span>
                    <span className="text-[10px] font-bold text-tone-danger-text bg-tone-danger-bg px-2 py-0.5 rounded">
                      Risk: {act.risk}
                    </span>
                  </div>
                  <p className="text-xs text-on-surface-variant">
                    Target: <strong className="font-mono text-on-surface">{act.entity}</strong> · Bank: {act.bank}
                  </p>
                  <div className="flex items-center gap-3 text-[11px] text-viz-neutral mt-2">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {act.date}
                    </span>
                    <span className="font-semibold text-viz-primary">
                      {act.status}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row sm:items-center gap-3 shrink-0">
                <div className="text-right sm:pr-4 sm:border-r border-border-divider">
                  <span className="text-[10px] text-viz-neutral uppercase font-bold block">
                    Quantum
                  </span>
                  <span className="font-mono font-bold text-base text-on-surface">
                    {act.amount}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    href={`/check/result/${act.id}`}
                    className="inline-flex min-h-[36px] items-center gap-1 rounded-full border border-border-control bg-surface px-3 py-1 text-xs font-semibold text-on-surface hover:bg-surface-subtle transition-colors"
                  >
                    <span>View Result</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>

                  <Link
                    href={`/rescue/package/${act.id}`}
                    className="inline-flex min-h-[36px] items-center gap-1.5 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-4 py-1 text-xs font-bold transition-colors shadow-sm"
                  >
                    <FileCheck2 className="h-3.5 w-3.5" />
                    <span>§65B Package</span>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
