"use client";

import { useState } from "react";
import { History, ShieldCheck, Lock, Download, CheckCircle2 } from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

interface AuditEntry {
  id: string;
  timestamp: string;
  actor_name: string;
  actor_role: string;
  action: string;
  entity_queried: string;
  justification_statute: string;
  merkle_root_hash: string;
}

const CANONICAL_AUDIT_LOG: AuditEntry[] = [
  {
    id: "AUD-99412",
    timestamp: "2026-10-24T20:46:12Z",
    actor_name: "Inspector Raghavendra M.",
    actor_role: "Karnataka State Police (KA-CY-401)",
    action: "PII Unmask & Section 102 CrPC Lien Notice Served",
    entity_queried: "util-power-84920@okaxis",
    justification_statute: "FIR No. 0142/2026 (Urgent Disconnection Scam)",
    merkle_root_hash: "0x8f2d..91ac",
  },
  {
    id: "AUD-99411",
    timestamp: "2026-10-24T20:15:30Z",
    actor_name: "Alok Kumar S.",
    actor_role: "Axis Bank Nodal Officer",
    action: "Transaction Hold & Account Debit Freeze Execution",
    entity_queried: "util-power-84920@okaxis",
    justification_statute: "1930 NCRP Golden Hour Directive",
    merkle_root_hash: "0x3e1a..bf80",
  },
  {
    id: "AUD-99410",
    timestamp: "2026-10-24T19:48:02Z",
    actor_name: "Pooja Sharma",
    actor_role: "Delhi Police Special Cell",
    action: "Telephony CDR Inspection & Cell Tower Triangulation",
    entity_queried: "+91 98******10",
    justification_statute: "BNSS §94 Telecommunications Preservation",
    merkle_root_hash: "0x77ab..149e",
  },
  {
    id: "AUD-99409",
    timestamp: "2026-10-24T18:20:14Z",
    actor_name: "ACP Sneha Patil (IPS)",
    actor_role: "Mumbai Police Cyber Directorate",
    action: "Formal FIR Evidence Docket Export (§65B BSA)",
    entity_queried: "CASE-2026-MH-0412 (#DAR-3041)",
    justification_statute: "Bharatiya Sakshya Adhiniyam 2023 §65B",
    merkle_root_hash: "0x44cd..00ef",
  },
];

export default function AuditLogPage() {
  const [entries, setEntries] = useState<AuditEntry[]>(CANONICAL_AUDIT_LOG);

  return (
    <div className="w-full space-y-4 text-viz-text">
      <div className="bg-surface border border-border-divider rounded-lg p-5 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
                <History className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Tamper-Evident Audit Log</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
                §7 A19
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-xs font-bold">
                <ShieldCheck className="w-3.5 h-3.5 text-viz-primary" />
                Merkle Root Validated
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1">
              Cryptographically signed append-only ledger tracking all forensic queries, PII audit reveals, bank freezes, and LEA evidence exports.
            </p>
          </div>

          <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
            <Download className="w-3.5 h-3.5 text-viz-neutral" />
            <span>Verify Blockchain Merkle State</span>
          </button>
        </div>

        {/* Audit Log Table */}
        <div className="bg-surface rounded-xl border border-border-divider overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="px-4 font-semibold">Audit Event &amp; Timestamp</th>
                <th className="px-4 font-semibold">Investigator / Actor</th>
                <th className="px-4 font-semibold">Action &amp; Target Node</th>
                <th className="px-4 font-semibold">Statutory Authority</th>
                <th className="px-4 font-semibold">Merkle Root</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-viz-text">
              {entries.map((entry) => (
                <tr key={entry.id} className="h-14 hover:bg-surface-subtle transition-colors">
                  <td className="px-4">
                    <div className="flex flex-col">
                      <span className="font-mono font-bold text-viz-primary text-xs">{entry.id}</span>
                      <span className="text-[11px] text-viz-neutral">{formatDateTime(entry.timestamp)}</span>
                    </div>
                  </td>
                  <td className="px-4">
                    <div className="flex flex-col">
                      <span className="font-bold text-viz-text">{entry.actor_name}</span>
                      <span className="text-[11px] text-viz-neutral">{entry.actor_role}</span>
                    </div>
                  </td>
                  <td className="px-4">
                    <div className="flex flex-col">
                      <span className="font-semibold text-viz-text">{entry.action}</span>
                      <code className="text-[11px] font-mono text-viz-neutral">{entry.entity_queried}</code>
                    </div>
                  </td>
                  <td className="px-4 text-viz-neutral text-[11px]">{entry.justification_statute}</td>
                  <td className="px-4 font-mono text-[11px] text-viz-primary font-bold">{entry.merkle_root_hash}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
