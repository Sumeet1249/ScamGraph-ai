"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  LifeBuoy,
  PhoneCall,
  Clock,
  ArrowRight,
  AlertTriangle,
  Building2,
  IndianRupee,
  ShieldCheck,
  CheckCircle2,
  FileText,
  FileCheck2,
  Download,
  Plus,
  Share2,
} from "lucide-react";

export default function RescueDashboardPage() {
  const searchParams = useSearchParams();

  const amount = searchParams.get("amount") || "45000";
  const bank = searchParams.get("bank") || "ICICI Bank";
  const rail = searchParams.get("rail") || "UPI";
  const time = searchParams.get("time") || "Under 2 hours";

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
            <li>
              <Link href="/rescue" className="hover:text-viz-primary transition-colors">
                Rescue Triage
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Case #SG-2026-89412 [C09]</li>
          </ol>
        </nav>

        {/* Section Header */}
        <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
              <span className="w-2 h-2 rounded-full bg-viz-primary" />
              [C09] Citizen Financial Rapid Recovery Hub
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-on-surface tracking-tight">
              Emergency Action &amp; Interbank Freeze Dashboard
            </h1>
            <p className="text-xs md:text-sm text-on-surface-variant mt-1 leading-relaxed">
              Active case docket for ₹{parseInt(amount).toLocaleString("en-IN")} loss via {rail} ({bank}). Follow the immediate statutory actions below to intercept funds.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/rescue/events/new"
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-4 py-1.5 text-xs font-bold transition-colors shadow-sm"
            >
              <Plus className="h-4 w-4" />
              <span>Log Loss Event [C10]</span>
            </Link>
            <Link
              href="/rescue/package/SG-2026-89412"
              className="inline-flex min-h-[40px] items-center gap-1.5 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-4 py-1.5 text-xs font-bold transition-colors shadow-sm"
            >
              <FileCheck2 className="h-4 w-4" />
              <span>Case Package [C14]</span>
            </Link>
          </div>
        </div>

        {/* Top Recovery KPI Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm">
            <div className="text-xs text-viz-neutral font-medium">Logged Loss Amount</div>
            <div className="text-2xl font-bold text-on-surface mt-1 font-mono">
              ₹{parseInt(amount).toLocaleString("en-IN")}
            </div>
            <div className="text-xs text-tone-danger-text font-semibold mt-1">1 Debit Recorded</div>
          </div>
          <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm">
            <div className="text-xs text-viz-neutral font-medium">Estimated Recovery Probability</div>
            <div className="text-2xl font-bold text-viz-primary mt-1">84%</div>
            <div className="text-xs text-viz-primary font-semibold mt-1">Golden Hour window active</div>
          </div>
          <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm">
            <div className="text-xs text-viz-neutral font-medium">Victim Bank Escalation</div>
            <div className="text-2xl font-bold text-on-surface mt-1 truncate">{bank}</div>
            <div className="text-xs text-viz-neutral font-medium mt-1">Fraud Desk Connected</div>
          </div>
          <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm">
            <div className="text-xs text-viz-neutral font-medium">Statutory Compliance Status</div>
            <div className="text-2xl font-bold text-viz-primary mt-1">§65B BSA</div>
            <div className="text-xs text-viz-neutral font-medium mt-1">Merkle Proof Sealed</div>
          </div>
        </div>

        {/* 4 Core Action Workbenches */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Action 1: 1930 Helpline */}
          <div className="bg-surface rounded-xl border-2 border-tone-danger-strong-bg p-6 shadow-sm flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-tone-danger-text uppercase tracking-wider bg-tone-danger-bg px-2 py-0.5 rounded">
                  Priority 1 · Immediate Freeze
                </span>
                <span className="text-xs font-mono text-viz-neutral">SLA: Under 15m</span>
              </div>
              <h2 className="text-base font-bold text-on-surface">
                1. Dial National Cyber Helpline 1930
              </h2>
              <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                Connect directly to the National Cyber Crime Reporting Portal (NCRP) CFCFRMS switch. Give your 12-digit UPI UTR number so police can freeze all subsequent mule accounts in real time.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-border-divider">
              <a
                href="tel:1930"
                className="inline-flex min-h-[40px] items-center gap-2 rounded-full bg-tone-danger-text hover:bg-tone-danger-strong-text text-surface px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <PhoneCall className="h-4 w-4" />
                <span>Call 1930 Toll Free</span>
              </a>
              <span className="text-[11px] text-viz-neutral">Open 24/7 all India</span>
            </div>
          </div>

          {/* Action 2: Bank Escalation Letter */}
          <div className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-viz-primary uppercase tracking-wider bg-selected-tint px-2 py-0.5 rounded">
                  Priority 2 · Bank Lien
                </span>
                <span className="text-xs font-mono text-viz-neutral">RBI Circular 2017/18</span>
              </div>
              <h2 className="text-base font-bold text-on-surface">
                2. Formal {bank} Nodal Escalation
              </h2>
              <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                Pre-filled formal letter addressed to the Principal Nodal Officer of {bank} demanding immediate reversal and lien placement under Section 65B of Bharatiya Sakshya Adhiniyam 2023.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-border-divider">
              <a
                href="#download"
                onClick={(e) => {
                  e.preventDefault();
                  alert("Formal Bank Escalation Letter generated and saved to case docket.");
                }}
                className="inline-flex min-h-[40px] items-center gap-2 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <Download className="h-4 w-4 text-viz-primary" />
                <span>Download Letter (.DOCX)</span>
              </a>
              <span className="text-[11px] text-viz-neutral">Pre-filled with case details</span>
            </div>
          </div>

          {/* Action 3: Loss Event Logger */}
          <div className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-viz-neutral uppercase tracking-wider bg-surface-subtle px-2 py-0.5 rounded">
                  Priority 3 · Evidence Audit
                </span>
                <span className="text-xs font-mono text-viz-neutral">12-Digit UTR</span>
              </div>
              <h2 className="text-base font-bold text-on-surface">
                3. Log Transaction Hashes &amp; UTRs
              </h2>
              <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                Record exact bank debit SMS timestamps, recipient VPA handles (e.g. `mule@ybl`), and screenshot hashes so banks can trace second and third-hop accounts.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-border-divider">
              <Link
                href="/rescue/events/new"
                className="inline-flex min-h-[40px] items-center gap-2 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <Plus className="h-4 w-4 text-viz-primary" />
                <span>Add Loss Transaction [C10]</span>
              </Link>
              <Link
                href="/rescue/timeline"
                className="text-xs text-viz-primary font-semibold hover:underline"
              >
                View Timeline [C11]
              </Link>
            </div>
          </div>

          {/* Action 4: Case Package */}
          <div className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col justify-between gap-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-viz-primary uppercase tracking-wider bg-selected-tint px-2 py-0.5 rounded">
                  Priority 4 · Legal Redressal
                </span>
                <span className="text-xs font-mono text-viz-neutral">Court Admissible</span>
              </div>
              <h2 className="text-base font-bold text-on-surface">
                4. Court-Admissible Case Package
              </h2>
              <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                Export an immutable forensic evidence dossier with Merkle root verification, SHA-256 digests, and statutory certificate ready for your local Cyber Crime Police Station.
              </p>
            </div>

            <div className="flex items-center gap-3 pt-2 border-t border-border-divider">
              <Link
                href="/rescue/package/SG-2026-89412"
                className="inline-flex min-h-[40px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-5 py-1.5 text-xs font-bold transition-all shadow-sm"
              >
                <FileCheck2 className="h-4 w-4" />
                <span>Generate Case Package [C14]</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
