"use client";

import { useState } from "react";
import { Users, Shield, UserCheck, Lock, PlusCircle, CheckCircle2 } from "lucide-react";

interface Member {
  id: string;
  name: string;
  email: string;
  role: "CYBER_POLICE_INSPECTOR" | "BANK_FRAUD_ANALYST" | "NODAL_OFFICER" | "SYSTEM_ADMIN";
  org: string;
  badge: string;
  clearance: string;
  status: "ACTIVE" | "PENDING_APPROVAL";
}

const CANONICAL_MEMBERS: Member[] = [
  {
    id: "USR-001",
    name: "Inspector Raghavendra M.",
    email: "raghav.m@ksp.gov.in",
    role: "CYBER_POLICE_INSPECTOR",
    org: "Karnataka State Police (CID Cyber)",
    badge: "KA-CY-401",
    clearance: "Tier-1 Full Statutory Enforcement",
    status: "ACTIVE",
  },
  {
    id: "USR-002",
    name: "Sneha Patil (IPS)",
    email: "sneha.patil@mahapolice.gov.in",
    role: "CYBER_POLICE_INSPECTOR",
    org: "Mumbai Police Cyber Directorate",
    badge: "MH-IPS-108",
    clearance: "Tier-1 Full Statutory Enforcement",
    status: "ACTIVE",
  },
  {
    id: "USR-003",
    name: "Alok Kumar S.",
    email: "alok.s@axisbank.com",
    role: "BANK_FRAUD_ANALYST",
    org: "Axis Bank Ltd (Nodal Fraud Unit)",
    badge: "AX-FRD-991",
    clearance: "Tier-2 Transaction Restraint & Lien",
    status: "ACTIVE",
  },
  {
    id: "USR-004",
    name: "Pooja Sharma",
    email: "pooja.sharma@delhipolice.gov.in",
    role: "CYBER_POLICE_INSPECTOR",
    org: "Delhi Police Special Cell (IFSO)",
    badge: "DL-SI-302",
    clearance: "Tier-1 Full Statutory Enforcement",
    status: "ACTIVE",
  },
];

export default function MembersAccessPage() {
  const [members, setMembers] = useState<Member[]>(CANONICAL_MEMBERS);

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A18 RBAC &amp; Access Governance</span>
        </div>
      </div>

      <div className="p-4 lg:p-8 space-y-5 max-w-[1280px] mx-auto w-full">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
                <Users className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Members &amp; Access Control</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
                §7 A18
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1">
              Statutory Role-Based Access Control (RBAC) governance partitioning Police Cyber Cells, Bank Fraud Desks, and NPCI Officers.
            </p>
          </div>

          <button className="h-8 px-3 rounded bg-viz-primary text-white text-xs font-semibold flex items-center gap-1.5 hover:bg-[#00483f] transition-colors shadow-xs">
            <PlusCircle className="w-3.5 h-3.5" />
            <span>Invite Nodal Officer</span>
          </button>
        </div>

        {/* Members Table */}
        <div className="bg-surface rounded-xl border border-border-divider overflow-hidden shadow-sm">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="px-4 font-semibold">Member &amp; Organization</th>
                <th className="px-4 font-semibold">Role &amp; Badge</th>
                <th className="px-4 font-semibold">Clearance Level</th>
                <th className="px-4 font-semibold">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-viz-text">
              {members.map((m) => (
                <tr key={m.id} className="h-12 hover:bg-surface-subtle transition-colors">
                  <td className="px-4">
                    <div className="flex flex-col">
                      <span className="font-bold text-viz-text">{m.name}</span>
                      <span className="text-[11px] text-viz-neutral">{m.org} · {m.email}</span>
                    </div>
                  </td>
                  <td className="px-4">
                    <div className="flex flex-col">
                      <span className="font-semibold text-viz-primary">{m.role.replace(/_/g, " ")}</span>
                      <span className="text-[10px] font-mono text-viz-neutral">{m.badge}</span>
                    </div>
                  </td>
                  <td className="px-4 font-medium text-viz-neutral">{m.clearance}</td>
                  <td className="px-4">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[11px] font-semibold">
                      <CheckCircle2 className="w-3 h-3 text-viz-primary" />
                      {m.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
