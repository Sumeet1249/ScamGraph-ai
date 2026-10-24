"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import {
  FileCheck2,
  Download,
  Printer,
  Share2,
  Shield,
  Lock,
  Building2,
  Calendar,
  CheckCircle2,
  Scale,
  ChevronLeft,
} from "lucide-react";

export default function CasePackagePage() {
  const params = useParams();
  const caseId = (params?.id as string) || "SG-2026-89412";

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="max-w-[900px] mx-auto px-4 md:px-8">
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
              <Link href="/rescue/dashboard" className="hover:text-viz-primary transition-colors">
                Rescue Dashboard
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Case Package #{caseId} [C14]</li>
          </ol>
        </nav>

        {/* Section Header */}
        <div className="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-viz-primary" />
              [C14] Statutory Evidence Dossier
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-on-surface">
              Section 65B BSA Digital Evidence Certificate
            </h1>
            <p className="text-xs text-on-surface-variant mt-0.5">
              Cryptographically verified evidence package admissible in Indian Courts under Bharatiya Sakshya Adhiniyam 2023.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => window.print()}
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-4 py-1 text-xs font-semibold shadow-sm transition-colors"
            >
              <Printer className="h-4 w-4 text-viz-neutral" />
              <span>Print Dossier</span>
            </button>
            <button
              type="button"
              onClick={() => alert("Downloading encrypted court package PDF...")}
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-4 py-1 text-xs font-bold shadow-sm transition-colors"
            >
              <Download className="h-4 w-4" />
              <span>Download PDF</span>
            </button>
          </div>
        </div>

        {/* Formal Legal Certificate Surface */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-10 shadow-sm flex flex-col gap-6 text-on-surface">
          {/* Official Seal & Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b-2 border-primary pb-6">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-viz-primary text-on-primary shadow-sm">
                <Shield className="h-6 w-6" />
              </div>
              <div>
                <span className="text-xs font-bold uppercase tracking-widest text-viz-primary">
                  ScamGraph Sovereign Trust Framework
                </span>
                <h2 className="text-lg font-bold">
                  CERTIFICATE UNDER SECTION 65B OF BHARATIYA SAKSHYA ADHINIYAM, 2023
                </h2>
                <span className="text-[11px] text-viz-neutral font-mono">
                  Docket Identifier: {caseId} · Verification Root: 0x7f4b8c...e3b8a1
                </span>
              </div>
            </div>
            <div className="text-right">
              <span className="rounded bg-selected-tint px-2 py-1 text-xs font-bold text-viz-primary border border-viz-primary">
                SEALED &amp; VERIFIED
              </span>
            </div>
          </div>

          {/* Key Incident Parameters Table */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">Complainant Identifier (Masked)</span>
              <span className="font-bold text-on-surface">+91 98•••• ••10</span>
            </div>
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">Total Quantum Debited</span>
              <span className="font-bold font-mono text-base text-tone-danger-text">₹45,000.00 INR</span>
            </div>
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">UPI Transaction UTR Number</span>
              <span className="font-bold font-mono text-on-surface">428901928374</span>
            </div>
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">Recipient Fraudulent VPA</span>
              <span className="font-bold text-on-surface">mule.recovery@ybl</span>
            </div>
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">Victim Debited Bank</span>
              <span className="font-bold text-on-surface">ICICI Bank Limited</span>
            </div>
            <div className="p-3 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <span className="text-viz-neutral font-medium">NTP Stratum-1 Verified Timestamp</span>
              <span className="font-bold font-mono text-on-surface">2026-10-24 18:15:32 IST</span>
            </div>
          </div>

          {/* Statutory Affidavit Body */}
          <div className="text-xs text-on-surface-variant leading-relaxed flex flex-col gap-3 border-t border-border-divider pt-4">
            <p className="font-bold text-on-surface">
              Declaration Pursuant to Section 65B(4) of Bharatiya Sakshya Adhiniyam, 2023:
            </p>
            <p>
              1. This electronic record was produced by the ScamGraph Sovereign Trust System during the ordinary course of regular automated fraud surveillance and incident triage activities.
            </p>
            <p>
              2. Throughout the material period, the system operated with cryptographic integrity. All communications, SMS texts, and payment tokens underwent local client-side salted SHA-256 hashing prior to multi-signal graph correlation.
            </p>
            <p>
              3. The hash digests and timestamps recorded herein match the immutable Merkle tree audit trail anchored in government-empanelled Tier-IV infrastructure within the territory of India.
            </p>
          </div>

          {/* Cryptographic Merkle Seal Block */}
          <div className="p-4 rounded-xl bg-surface-subtle border border-border-divider flex flex-col gap-2">
            <div className="flex items-center justify-between text-xs font-bold text-on-surface">
              <div className="flex items-center gap-1.5 text-viz-primary">
                <Lock className="h-4 w-4" />
                <span>Forensic Digest Verification</span>
              </div>
              <span className="text-[10px] font-mono text-viz-neutral">Algorithm: SHA-256</span>
            </div>
            <div className="font-mono text-[10px] text-viz-neutral bg-surface p-2.5 rounded border border-border-divider break-all">
              MERKLE_ROOT: 0x7f4b8c9d012a4fe3b8a1c6e9d2f4a5b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3
            </div>
          </div>

          {/* Signature & Officer Block */}
          <div className="pt-4 border-t border-border-divider flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs text-on-surface-variant">
            <div>
              <p className="font-bold text-on-surface">ScamGraph Automated Forensic Certifier</p>
              <p className="text-[11px] text-viz-neutral">Empanelled with I4C / Ministry of Home Affairs Protocol</p>
            </div>
            <div className="text-right">
              <p className="font-bold text-on-surface">Certificate ID: CERT-BSA-2026-98124</p>
              <p className="text-[11px] text-viz-neutral">Generated on 24 October 2026, 18:25 IST</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
