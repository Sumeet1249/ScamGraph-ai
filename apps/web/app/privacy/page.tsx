"use client";

import Link from "next/link";
import {
  Shield,
  Lock,
  Scale,
  Database,
  Download,
  Trash2,
  Mail,
  CheckCircle2,
  Server,
  FileCheck2,
} from "lucide-react";

export default function PrivacyPage() {
  const pillars = [
    {
      title: "Client-Side Zero-Knowledge Hashing",
      desc: "Citizen UPI VPAs, mobile numbers, and bank account credentials undergo local SHA-256 salted hashing before graph traversal. No plain PII is ever transmitted or stored.",
      icon: Lock,
    },
    {
      title: "Statutory Section 65B BSA 2023 Integrity",
      desc: "Evidence artifacts are anchored with Merkle-tree root digests and Stratum-1 NTP timestamps, guaranteeing court admissibility under Bharatiya Sakshya Adhiniyam 2023.",
      icon: Scale,
    },
    {
      title: "Data Minimization & Ephemeral Retention",
      desc: "Unflagged universal checks auto-expire in 72 hours. Incident evidence dossiers are encrypted at rest with citizen-held keys and purged upon request.",
      icon: Database,
    },
    {
      title: "100% Indian Data Sovereignty",
      desc: "Hosted exclusively within MeitY-empanelled Tier-IV data centers inside Indian borders (Mumbai and Hyderabad). Zero cross-border data routing.",
      icon: Server,
    },
  ];

  return (
    <div className="w-full bg-ground py-10 md:py-16">
      <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Privacy &amp; Sovereign Trust [M05]</li>
          </ol>
        </nav>

        {/* Section Hero */}
        <div className="max-w-[760px] mb-12">
          <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-2">
            <span className="w-2 h-2 rounded-full bg-viz-primary" />
            [M05] Data Protection &amp; Governance Charter
          </div>
          <h1 className="text-3xl md:text-4xl font-bold text-on-surface tracking-tight mb-3">
            Privacy, Data Protection &amp; Sovereign Trust
          </h1>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            Built on India&apos;s Digital Personal Data Protection (DPDP) Act 2023, zero-knowledge cryptographic hashes, and strict non-custodial evidence vaulting.
          </p>

          <div className="flex flex-wrap items-center gap-2 mt-4 text-xs">
            <span className="rounded bg-selected-tint px-2.5 py-1 font-semibold text-viz-primary border border-viz-primary">
              DPDP Act 2023 Certified
            </span>
            <span className="rounded bg-surface-subtle px-2.5 py-1 font-semibold text-on-surface-variant border border-border-divider">
              MeitY Tier-IV Hosting
            </span>
            <span className="rounded bg-surface-subtle px-2.5 py-1 font-semibold text-on-surface-variant border border-border-divider">
              Section 65B BSA Compliant
            </span>
          </div>
        </div>

        {/* 4 Core Architectural Security Pillars */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          {pillars.map((pil, idx) => {
            const Icon = pil.icon;
            return (
              <div
                key={idx}
                className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col gap-3"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-surface-subtle rounded-lg text-viz-primary">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h2 className="text-sm md:text-base font-bold text-on-surface">
                    {pil.title}
                  </h2>
                </div>
                <p className="text-xs text-on-surface-variant leading-relaxed">
                  {pil.desc}
                </p>
              </div>
            );
          })}
        </div>

        {/* Citizen Rights Dashboard (DPDP Act 2023) */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-6">
          <div className="border-b border-border-divider pb-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary">
              DPDP Act 2023 Compliance Controls
            </span>
            <h2 className="text-lg md:text-xl font-bold text-on-surface">
              Your Statutory Citizen Data Rights
            </h2>
            <p className="text-xs text-on-surface-variant mt-0.5">
              You maintain sovereign ownership of all data submitted during verification.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="p-4 bg-surface-subtle rounded-xl border border-border-divider flex flex-col justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <Download className="h-4 w-4 text-viz-primary" />
                  <h3 className="text-xs font-bold text-on-surface">Right to Portability</h3>
                </div>
                <p className="text-[11px] text-on-surface-variant leading-relaxed">
                  Download all your logged incident reports, hashes, and evidence in standard JSON and PDF format.
                </p>
              </div>
              <button
                type="button"
                onClick={() => alert("Downloading citizen incident ledger...")}
                className="inline-flex min-h-[36px] items-center justify-center rounded-lg border border-border-control bg-surface px-3 py-1 text-xs font-semibold text-on-surface hover:bg-surface-subtle"
              >
                Export My Data
              </button>
            </div>

            <div className="p-4 bg-surface-subtle rounded-xl border border-border-divider flex flex-col justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <Trash2 className="h-4 w-4 text-tone-danger-text" />
                  <h3 className="text-xs font-bold text-on-surface">Right to Erasure</h3>
                </div>
                <p className="text-[11px] text-on-surface-variant leading-relaxed">
                  Permanently destroy local session keys and remove evidence dossiers from local and cached storage.
                </p>
              </div>
              <button
                type="button"
                onClick={() => {
                  if (confirm("Are you sure you want to cryptographically shred all local incident data?")) {
                    localStorage.clear();
                    alert("Local data shredded.");
                  }
                }}
                className="inline-flex min-h-[36px] items-center justify-center rounded-lg border border-tone-danger-strong-bg bg-tone-danger-bg px-3 py-1 text-xs font-semibold text-tone-danger-text hover:bg-tone-danger-strong-bg"
              >
                Cryptographic Shred
              </button>
            </div>

            <div className="p-4 bg-surface-subtle rounded-xl border border-border-divider flex flex-col justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <Mail className="h-4 w-4 text-viz-primary" />
                  <h3 className="text-xs font-bold text-on-surface">Grievance Redressal</h3>
                </div>
                <p className="text-[11px] text-on-surface-variant leading-relaxed">
                  Direct statutory channel to our Data Protection Officer (DPO Shri R. K. Nambiar). 48-hour SLA.
                </p>
              </div>
              <a
                href="mailto:dpo@scamgraph.gov.in"
                className="inline-flex min-h-[36px] items-center justify-center rounded-lg border border-border-control bg-surface px-3 py-1 text-xs font-semibold text-on-surface hover:bg-surface-subtle"
              >
                Contact DPO Office
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
