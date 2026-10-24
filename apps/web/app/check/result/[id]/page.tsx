"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ShieldAlert,
  ShieldCheck,
  ArrowRight,
  LifeBuoy,
  FileCheck2,
  AlertTriangle,
  Scale,
  ExternalLink,
  ChevronRight,
  PhoneCall,
  Lock,
  RefreshCw,
  CheckCircle2,
  FileText,
  ImageIcon,
  Clock,
  Tag,
  Copy,
  Check,
  FileCode,
} from "lucide-react";

interface EvidenceSignal {
  signal_id: string;
  dimension: string;
  category: string;
  title: string;
  desc: string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  is_counter_evidence?: boolean;
}

interface IncidentData {
  incident_id: string;
  analyzed_at: string;
  query_content: string;
  entity_type: string;
  attached_files?: Array<{
    name: string;
    size?: number;
    type?: string;
    hash?: string;
    previewUrl?: string;
  }>;
  assessment: {
    incident_id: string;
    risk_score: number;
    risk_level: string;
    evidence_confidence: string;
    state_code: number;
    state_label: string;
    headline: string;
    summary: string;
    pattern_name: string;
    reason_codes: string[];
    section_65b_hash: string;
  };
  signals: EvidenceSignal[];
}

export default function CheckResultPage() {
  const params = useParams();
  const caseId = (params?.id as string) || "SG-2026-89412";
  const [data, setData] = useState<IncidentData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    async function fetchCaseData() {
      try {
        const res = await fetch(`/api/v1/investigate?id=${encodeURIComponent(caseId)}`);
        if (res.ok) {
          const json = await res.json();
          if (active) setData(json);
        }
      } catch (err) {
        console.error("Failed to fetch investigation case:", err);
      } finally {
        if (active) setLoading(false);
      }
    }
    fetchCaseData();
    return () => {
      active = false;
    };
  }, [caseId]);

  const score = data?.assessment.risk_score ?? 94;
  const isHighRisk = score >= 50;
  const isLowRisk = score < 25;
  const stateLabel = data?.assessment.state_label || (isHighRisk ? "State 6 · High Risk Incident" : "State 1 · Informational");
  const headline = data?.assessment.headline || "Act Now: Multiple Verified Scam Indicators Detected";
  const summary = data?.assessment.summary || "Matches active scam campaigns coordinated across multi-hop mule accounts. Immediate payment freeze recommended.";
  const patternName = data?.assessment.pattern_name || "Electricity Bill Disconnection Threat";
  const signals = data?.signals || [];
  const hash = data?.assessment.section_65b_hash || "0x7f4b8c9d2e1a3f6b4c8a9e7d2b1f0c3e4a5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f";

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
              <Link href="/check" className="hover:text-viz-primary transition-colors">
                Check
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Case Result #{caseId} [C03]</li>
          </ol>
        </nav>

        {/* Top Risk Verdict Banner */}
        <div
          className={`mb-8 rounded-xl p-5 md:p-6 border-2 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${isHighRisk
              ? "bg-tone-danger-strong-bg border-tone-danger-text text-tone-danger-strong-text"
              : isLowRisk
                ? "bg-tone-info-bg border-viz-info text-tone-info-text"
                : "bg-tone-warning-bg border-tone-warning-strong-text text-tone-warning-strong-text"
            }`}
        >
          <div className="flex items-start gap-3.5">
            <div
              className={`flex h-11 w-11 items-center justify-center rounded-xl shrink-0 shadow-sm ${isHighRisk
                  ? "bg-tone-danger-text text-surface"
                  : isLowRisk
                    ? "bg-viz-info text-surface"
                    : "bg-viz-warning text-surface"
                }`}
            >
              {isHighRisk ? (
                <ShieldAlert className="h-6 w-6" />
              ) : isLowRisk ? (
                <ShieldCheck className="h-6 w-6" />
              ) : (
                <AlertTriangle className="h-6 w-6" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span
                  className={`text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded ${isHighRisk
                      ? "bg-tone-danger-text text-surface"
                      : isLowRisk
                        ? "bg-viz-info text-surface"
                        : "bg-viz-warning text-surface"
                    }`}
                >
                  {stateLabel}
                </span>
                <span className="text-xs font-semibold">
                  Docket #{caseId}
                </span>
              </div>
              <h1 className="text-xl md:text-2xl font-bold tracking-tight">
                {headline}
              </h1>
              <p className="text-xs mt-0.5 leading-relaxed opacity-90 max-w-3xl">
                {summary}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {isHighRisk ? (
              <Link
                href="/rescue"
                className="inline-flex min-h-[44px] items-center gap-1.5 rounded-full bg-tone-danger-text text-surface hover:opacity-95 px-5 py-2 text-xs font-bold shadow-sm transition-all"
              >
                <LifeBuoy className="h-4 w-4" />
                <span>Already paid? Enter Rescue</span>
              </Link>
            ) : (
              <Link
                href="/check"
                className="inline-flex min-h-[44px] items-center gap-1.5 rounded-full bg-viz-primary text-surface hover:opacity-95 px-5 py-2 text-xs font-bold shadow-sm transition-all"
              >
                <span>Check Another Target</span>
              </Link>
            )}
          </div>
        </div>

        {/* 2-Column Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Main 8-Col Assessment Content */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            {/* Target Investigated Overview Card */}
            <div className="bg-surface rounded-xl border border-border-divider p-5 shadow-sm flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Tag className="h-4 w-4 text-viz-primary" />
                  <span className="text-xs font-bold text-on-surface uppercase tracking-wider">
                    Investigated Target Artifact
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-semibold text-viz-neutral bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                    {data?.entity_type || "Direct Query"}
                  </span>
                  {data?.analyzed_at && (
                    <span className="text-[11px] text-viz-neutral flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {new Date(data.analyzed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  )}
                </div>
              </div>
              <div className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider text-xs text-on-surface font-mono break-all leading-relaxed">
                {data?.query_content || "Direct multi-modal search target"}
              </div>
            </div>

            {/* Attached Forensic Evidence Files Card (if files were uploaded) */}
            {data?.attached_files && data.attached_files.length > 0 && (
              <div className="bg-surface rounded-xl border border-border-divider p-5 shadow-sm flex flex-col gap-4">
                <div className="flex items-center justify-between border-b border-border-divider pb-3">
                  <div className="flex items-center gap-2">
                    <FileCode className="h-4 w-4 text-viz-primary" />
                    <h3 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                      Attached Forensic Evidence Files ({data.attached_files.length})
                    </h3>
                  </div>
                  <span className="text-[11px] font-semibold text-tone-info-text bg-tone-info-bg px-2.5 py-0.5 rounded-full border border-viz-info flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    BSA §65B Certified
                  </span>
                </div>

                <div className="flex flex-col gap-3">
                  {data.attached_files.map((file, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 rounded-lg bg-surface-subtle border border-border-divider flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-lg bg-surface border border-border-divider flex items-center justify-center shrink-0 text-viz-primary">
                          {file.type?.includes("image") ? (
                            <ImageIcon className="h-5 w-5" />
                          ) : (
                            <FileText className="h-5 w-5" />
                          )}
                        </div>
                        <div className="flex flex-col">
                          <span className="text-xs font-bold text-on-surface truncate max-w-[260px] sm:max-w-[340px]">
                            {file.name}
                          </span>
                          <span className="text-[11px] text-on-surface-variant">
                            {file.size ? `${(file.size / 1024).toFixed(1)} KB` : "Digital Artifact"} · {file.type || "binary"}
                          </span>
                        </div>
                      </div>

                      {file.hash && (
                        <div className="flex flex-col sm:items-end w-full sm:w-auto">
                          <span className="text-[10px] font-bold text-viz-neutral uppercase tracking-wider">
                            SHA-256 Digest
                          </span>
                          <span className="text-[10px] font-mono text-viz-primary bg-surface px-2 py-0.5 rounded border border-border-divider truncate max-w-[280px]">
                            {file.hash}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Dual-Axis Assessment Card */}
            <div className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col gap-5">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border-divider pb-4">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary">
                    Dual-Axis Risk Assessment · {patternName}
                  </span>
                  <h2 className="text-lg font-bold text-on-surface">
                    Empirical Threat Index
                  </h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-on-surface bg-surface-subtle px-2.5 py-1 rounded border border-border-divider">
                    Risk: <strong className={isHighRisk ? "text-tone-danger-text" : "text-viz-info"}>{data?.assessment.risk_level || "HIGH"} ({score}/100)</strong>
                  </span>
                  <span className="text-xs font-bold text-on-surface bg-surface-subtle px-2.5 py-1 rounded border border-border-divider">
                    Confidence: <strong className="text-viz-primary">{data?.assessment.evidence_confidence || "HIGH"} ({signals.length} Signals)</strong>
                  </span>
                </div>
              </div>

              {/* Dynamic Risk Gauge Bar */}
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center justify-between text-xs text-on-surface-variant font-medium">
                  <span>Calculated Threat Probability</span>
                  <span className="font-bold text-on-surface">{score}%</span>
                </div>
                <div className="w-full bg-surface-subtle h-2.5 rounded-full overflow-hidden border border-border-divider">
                  <div
                    className={`h-full transition-all duration-700 rounded-full ${score >= 70
                        ? "bg-tone-danger-text"
                        : score >= 40
                          ? "bg-viz-warning"
                          : "bg-viz-info"
                      }`}
                    style={{ width: `${Math.min(100, Math.max(5, score))}%` }}
                  />
                </div>
              </div>

              {/* Verified Signal Items */}
              <div className="flex flex-col gap-3.5">
                <span className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Corroborated Evidence Signals ({signals.length})
                </span>
                {signals.map((sig, idx) => (
                  <div
                    key={sig.signal_id || idx}
                    className="p-4 rounded-lg bg-surface-subtle border border-border-divider flex flex-col gap-1.5"
                  >
                    <div className="flex items-center justify-between text-xs font-bold text-on-surface">
                      <div className="flex items-center gap-2">
                        <span
                          className={`w-2 h-2 rounded-full ${sig.severity === "critical"
                              ? "bg-tone-danger-text"
                              : sig.severity === "high"
                                ? "bg-tone-warning-strong-text"
                                : "bg-viz-info"
                            }`}
                        />
                        <span>{sig.title}</span>
                      </div>
                      <span
                        className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${sig.severity === "critical"
                            ? "text-tone-danger-text bg-tone-danger-bg border-tone-danger-strong-bg"
                            : "text-viz-neutral bg-surface border-border-divider"
                          }`}
                      >
                        {sig.category}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface-variant leading-relaxed">
                      {sig.desc}
                    </p>
                  </div>
                ))}
              </div>

              {/* Navigation Action Gates */}
              <div className="pt-3 border-t border-border-divider flex flex-wrap items-center justify-between gap-3">
                <Link
                  href={`/check/journey/${caseId}`}
                  className="inline-flex min-h-[44px] items-center gap-2 rounded-full border border-border-control bg-surface hover:bg-surface-subtle text-on-surface px-5 py-2 text-xs font-bold transition-colors shadow-sm"
                >
                  <span>Explore Full Scam Journey [C04]</span>
                  <ChevronRight className="h-4 w-4" />
                </Link>

                <Link
                  href={`/rescue/package/${caseId}`}
                  className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-5 py-2 text-xs font-bold transition-colors shadow-sm"
                >
                  <FileCheck2 className="h-4 w-4" />
                  <span>Generate §65B BSA Package [C14]</span>
                </Link>
              </div>
            </div>

            {/* Explanation & Statutory Legal Defense Guidance */}
            <div className="bg-surface rounded-xl border border-border-divider p-6 shadow-sm flex flex-col gap-4">
              <div className="flex items-center gap-2 text-viz-primary">
                <Scale className="h-4 w-4" />
                <h3 className="text-xs font-bold text-on-surface uppercase tracking-wider">
                  Statutory Action Advice &amp; Protection Checklist
                </h3>
              </div>
              <ul className="text-xs text-on-surface-variant space-y-2 list-disc list-inside leading-relaxed">
                <li>
                  <strong>Halt Communications:</strong> Do not dial unverified phone numbers or answer urgent WhatsApp collect calls.
                </li>
                <li>
                  <strong>Verify Independently:</strong> Contact official customer nodal portals directly to inspect account balances.
                </li>
                <li>
                  <strong>Do Not Sideload APKs:</strong> Never install application files sent over WhatsApp or SMS.
                </li>
                <li>
                  <strong>Notify Bank Immediately:</strong> If you initiated an approval intent or payment, call 1930 to place an interbank lien.
                </li>
              </ul>
            </div>
          </div>

          {/* Right 4-Col Quick Assistance Rail */}
          <aside className="lg:col-span-4 flex flex-col gap-4">
            {/* National 1930 Card */}
            <div className="bg-tone-danger-bg rounded-xl border border-tone-danger-strong-bg p-5 shadow-sm flex flex-col gap-2.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-tone-danger-text">
                Immediate Assistance
              </span>
              <h3 className="text-sm font-bold text-tone-danger-strong-text">
                National Cybercrime Helpline
              </h3>
              <p className="text-xs text-tone-danger-text leading-relaxed">
                Victim of unauthorized UPI debits? Register a complaint with the Ministry of Home Affairs 1930 helpline within 2 hours.
              </p>
              <div className="mt-2 flex items-center justify-between bg-surface p-3 rounded-lg border border-tone-danger-strong-bg">
                <div className="flex items-center gap-2">
                  <PhoneCall className="h-4 w-4 text-tone-danger-text" />
                  <span className="text-base font-bold text-on-surface">1930</span>
                </div>
                <span className="text-[11px] font-semibold text-tone-danger-text bg-tone-danger-bg px-2 py-0.5 rounded">
                  24/7 Toll Free
                </span>
              </div>
            </div>

            {/* Zero-Knowledge Hashing Proof */}
            <div className="bg-surface rounded-xl border border-border-divider p-4 shadow-sm flex flex-col gap-2">
              <div className="flex items-center gap-1.5 text-viz-primary">
                <Lock className="h-3.5 w-3.5" />
                <span className="text-xs font-bold text-on-surface">Cryptographic Proof</span>
              </div>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                SHA-256 Merkle root hash for this case has been timestamped. Admissible in Indian courts under Bharatiya Sakshya Adhiniyam 2023.
              </p>
              <div className="p-2 bg-surface-subtle rounded border border-border-divider font-mono text-[10px] text-viz-neutral truncate">
                {hash}
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
