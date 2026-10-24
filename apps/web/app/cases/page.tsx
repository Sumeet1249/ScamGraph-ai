"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Briefcase,
  FileText,
  Shield,
  Gavel,
  Search,
  Filter,
  Download,
  PlusCircle,
  ExternalLink,
  ChevronRight,
  Clock,
  Layers,
  Lock,
  CheckCircle2,
  AlertTriangle,
  Scale,
} from "lucide-react";
import { formatDateTime } from "@/lib/utils/format";

export interface CaseRecord {
  id: string;
  fir_number: string;
  title: string;
  jurisdiction: string;
  police_station: string;
  lead_officer: string;
  legal_sections: string[];
  total_loss: number;
  lien_recovered: number;
  victims_count: number;
  syndicate_cluster: string;
  status: "UNDER_INVESTIGATION" | "CHARGE_SHEET_PREP" | "TRIAL_FILED" | "CLOSED";
  opened_at: string;
  last_updated: string;
}

const CANONICAL_CASES: CaseRecord[] = [
  {
    id: "CASE-2026-KA-0941",
    fir_number: "FIR No. 0142/2026 (Cyber Crime PS Bengaluru)",
    title: "State of Karnataka vs. State Electricity Cutoff Extortion Syndicate",
    jurisdiction: "Bengaluru City Cyber Cell",
    police_station: "Cyber Economic & Narcotics Crime Police Station",
    lead_officer: "Inspector Raghavendra M. (Badge #KA-CY-401)",
    legal_sections: ["§66D IT Act 2000", "§318(4) Bharatiya Nyaya Sanhita 2023", "§111 Organised Crime BNSS"],
    total_loss: 18450000,
    lien_recovered: 4280000,
    victims_count: 142,
    syndicate_cluster: "#UTL-8490",
    status: "UNDER_INVESTIGATION",
    opened_at: "2026-10-21T10:00:00Z",
    last_updated: "2026-10-24T20:46:00Z",
  },
  {
    id: "CASE-2026-MH-0412",
    fir_number: "FIR No. 0089/2026 (BKC Cyber PS Mumbai)",
    title: "State of Maharashtra vs. Impersonated CBI Digital Arrest Ring",
    jurisdiction: "Mumbai Police Cyber Directorate",
    police_station: "BKC Cyber Police Station",
    lead_officer: "ACP Sneha Patil (IPS)",
    legal_sections: ["§66C/66D IT Act", "§204/§308 BNSS", "§319 Extortion"],
    total_loss: 39500000,
    lien_recovered: 12000000,
    victims_count: 34,
    syndicate_cluster: "#DAR-3041",
    status: "CHARGE_SHEET_PREP",
    opened_at: "2026-10-19T14:30:00Z",
    last_updated: "2026-10-24T19:45:00Z",
  },
  {
    id: "CASE-2026-DL-0219",
    fir_number: "FIR No. 0311/2026 (IFSO Special Cell New Delhi)",
    title: "NCT of Delhi vs. Telegram Video Rating Scam Ring",
    jurisdiction: "Delhi Police IFSO",
    police_station: "Special Cell Cyber Hub",
    lead_officer: "Sub-Inspector Pooja Sharma",
    legal_sections: ["§66D IT Act", "§316 BNSS Breach of Trust"],
    total_loss: 11200000,
    lien_recovered: 3100000,
    victims_count: 89,
    syndicate_cluster: "#TSK-1092",
    status: "UNDER_INVESTIGATION",
    opened_at: "2026-10-16T11:00:00Z",
    last_updated: "2026-10-24T16:15:00Z",
  },
];

export default function CasesListPage() {
  const [cases, setCases] = useState<CaseRecord[]>(CANONICAL_CASES);
  const [selectedId, setSelectedId] = useState<string>("CASE-2026-KA-0941");
  const [searchQuery, setSearchQuery] = useState("");

  const selectedCase = cases.find((c) => c.id === selectedId) || cases[0];

  const filteredCases = cases.filter(
    (c) =>
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.fir_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.lead_officer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col w-full -mx-4 -my-6 lg:-mx-8 lg:-my-8 min-h-screen bg-ground text-viz-text">
      {/* 1. Synthetic Demo Banner */}
      <div className="h-7 bg-[#E8DFCF] border-b border-border-divider/50 flex items-center justify-between px-4 lg:px-8 text-[11px] uppercase tracking-wider font-semibold text-[#4A3306] select-none shrink-0">
        <div className="flex items-center gap-2">
          <Lock className="w-3.5 h-3.5 text-viz-warning" />
          <span>SYNTHETIC DEMO DATA — ANALYST WORKSPACE (FIXTURE MODE)</span>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-viz-neutral normal-case font-normal">
          <span>Sprint PG30 · §7 A14 Formal Statutory Cases</span>
          <span>•</span>
          <span>BNSS / §65B Certified</span>
        </div>
      </div>

      {/* 2. Top Header Block */}
      <div className="bg-surface border-b border-border-divider px-4 lg:px-8 py-4 shrink-0 space-y-3">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="w-6 h-6 rounded bg-viz-primary text-white flex items-center justify-center font-bold">
                <Scale className="w-3.5 h-3.5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight text-viz-text">Investigation Cases</h1>
              <span className="text-[11px] bg-surface-subtle text-viz-neutral px-2 py-0.5 rounded uppercase font-semibold border border-border-divider">
                §7 A14
              </span>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-xs font-bold">
                {cases.length} formal dockets
              </span>
            </div>
            <p className="text-xs text-viz-neutral mt-1 max-w-3xl">
              Formal FIR / BNSS statutory prosecution dossiers registered across Law Enforcement Agencies and High Court Jurisdictions with Merkle-backed §65B proof packages.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button className="h-8 px-3 rounded bg-viz-primary text-white text-xs font-semibold flex items-center gap-1.5 hover:bg-[#00483f] transition-colors shadow-xs">
              <PlusCircle className="w-3.5 h-3.5" />
              <span>Register New Case</span>
            </button>
            <button className="h-8 px-3 rounded bg-surface border border-border-control hover:bg-surface-subtle text-xs font-medium text-viz-text flex items-center gap-1.5 transition-colors">
              <Download className="w-3.5 h-3.5 text-viz-neutral" />
              <span>Export Prosecutor Bundle</span>
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative max-w-md">
          <Search className="absolute left-2.5 top-2 w-3.5 h-3.5 text-viz-neutral" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search FIR number, lead officer, jurisdiction..."
            className="w-full h-7 pl-8 pr-2.5 bg-surface-subtle border border-border-divider rounded text-xs text-viz-text placeholder:text-viz-neutral focus:bg-surface focus:outline-none focus:border-viz-primary"
          />
        </div>
      </div>

      {/* 3. Main Split Console */}
      <div className="flex flex-1 w-full overflow-hidden min-h-[calc(100vh-14rem)]">
        {/* Table View */}
        <div className="flex-1 overflow-x-auto bg-surface" data-density="compact">
          <table className="w-full text-left border-collapse select-text min-w-[900px]">
            <thead>
              <tr className="h-9 bg-surface-subtle border-b border-border-divider text-[11px] font-semibold text-viz-neutral uppercase tracking-wider">
                <th className="px-3 font-semibold">FIR Number &amp; Title</th>
                <th className="px-3 font-semibold">Jurisdiction &amp; Station</th>
                <th className="px-3 font-semibold">Lead Officer</th>
                <th className="px-3 font-semibold">Statutory Sections</th>
                <th className="px-3 font-semibold">Loss / Lien</th>
                <th className="px-3 font-semibold">Status</th>
                <th className="px-3 text-right font-semibold">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-xs text-viz-text">
              {filteredCases.map((c) => {
                const isSelected = selectedId === c.id;

                return (
                  <tr
                    key={c.id}
                    onClick={() => setSelectedId(c.id)}
                    className={`h-9 transition-colors cursor-pointer group ${
                      isSelected
                        ? "bg-[#0B6256]/[0.08] border-l-[3px] border-l-viz-primary font-medium"
                        : "hover:bg-surface-container-low border-l-[3px] border-l-transparent"
                    }`}
                  >
                    <td className="px-3">
                      <div className="flex flex-col truncate max-w-[280px]">
                        <span className="font-mono text-[11px] font-bold text-viz-primary">{c.fir_number}</span>
                        <span className="font-semibold text-viz-text truncate">{c.title}</span>
                      </div>
                    </td>
                    <td className="px-3 text-viz-neutral text-[11px] truncate max-w-[180px]">
                      {c.police_station}
                    </td>
                    <td className="px-3 font-medium text-[11px]">{c.lead_officer}</td>
                    <td className="px-3">
                      <div className="flex flex-wrap gap-1">
                        {c.legal_sections.slice(0, 2).map((sec) => (
                          <span key={sec} className="px-1 bg-surface-subtle border border-border-divider rounded text-[10px] font-mono">
                            {sec}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-3">
                      <div className="flex flex-col text-[11px] font-mono">
                        <span className="text-error font-semibold">₹{(c.total_loss / 100000).toFixed(1)} L</span>
                        <span className="text-viz-primary">Lien: ₹{(c.lien_recovered / 100000).toFixed(1)} L</span>
                      </div>
                    </td>
                    <td className="px-3">
                      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[11px] font-medium">
                        {c.status}
                      </span>
                    </td>
                    <td className="px-3 text-right whitespace-nowrap">
                      <Link
                        href={`/cases/${c.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="h-6 px-2 bg-viz-primary hover:bg-[#00483f] text-white rounded text-[11px] font-semibold inline-flex items-center transition-colors"
                      >
                        Open Case
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Right-Hand Docked Detail Inspector (380px) */}
        <aside className="w-80 xl:w-[380px] shrink-0 bg-surface-subtle border-l border-border-divider flex flex-col justify-between overflow-y-auto">
          {selectedCase ? (
            <div className="flex flex-col">
              <div className="px-4 py-3 bg-surface border-b border-border-divider flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded bg-[#0B6256]/10 text-viz-primary flex items-center justify-center font-bold">
                    <Scale className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-viz-neutral font-bold tracking-wider block">
                      Statutory Docket
                    </span>
                    <h2 className="text-xs font-mono font-bold text-viz-text leading-tight">{selectedCase.id}</h2>
                  </div>
                </div>
                <Link
                  href={`/cases/${selectedCase.id}`}
                  className="h-7 px-2.5 bg-viz-primary hover:bg-[#00483f] text-white rounded text-xs font-semibold flex items-center gap-1 transition-colors"
                >
                  <span>Full Workspace</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              {/* Title & Police Station */}
              <div className="p-4 bg-surface border-b border-border-divider space-y-2">
                <h3 className="text-sm font-bold text-viz-text leading-tight">{selectedCase.title}</h3>
                <p className="text-xs text-viz-neutral">{selectedCase.fir_number}</p>
                <div className="p-2.5 rounded bg-surface-subtle border border-border-divider text-xs space-y-1">
                  <span className="font-bold text-viz-text block">Lead Investigating Officer:</span>
                  <span className="text-viz-neutral">{selectedCase.lead_officer}</span>
                </div>
              </div>

              {/* Legal Sections Box */}
              <div className="p-4 space-y-2 text-xs">
                <span className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider block">
                  Applicable Penal Provisions
                </span>
                <div className="space-y-1">
                  {selectedCase.legal_sections.map((sec) => (
                    <div key={sec} className="p-2 rounded bg-surface border border-border-divider font-mono text-[11px] text-viz-text font-semibold">
                      {sec}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Deck */}
              <div className="p-4 mt-auto border-t border-border-divider bg-surface space-y-2">
                <div className="text-[10px] uppercase font-bold text-viz-neutral tracking-wider">
                  Statutory Exports
                </div>
                <button className="w-full h-8 px-3 rounded bg-viz-primary hover:bg-[#00483f] text-white text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors shadow-xs">
                  <Download className="w-3.5 h-3.5" />
                  <span>Export Cryptographic §65B Certificate</span>
                </button>
                <Link
                  href={`/campaigns/${selectedCase.syndicate_cluster}`}
                  className="w-full h-8 px-3 rounded bg-surface-subtle hover:bg-surface-container-high border border-border-control text-xs font-medium text-viz-text flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span>Inspect Linked Campaign ({selectedCase.syndicate_cluster})</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ) : (
            <div className="p-8 text-center text-xs text-viz-neutral">Select a case to inspect formal docket.</div>
          )}
        </aside>
      </div>
    </div>
  );
}
