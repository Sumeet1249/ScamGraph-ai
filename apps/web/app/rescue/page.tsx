"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  AlertOctagon,
  PhoneCall,
  ShieldAlert,
  FileCheck,
  Download,
  Copy,
  CheckCircle2,
  ExternalLink,
  ChevronRight,
  PlusCircle,
  HelpCircle,
  Smartphone,
  KeyRound,
  FileText,
  AlertTriangle,
  ArrowLeft,
  RefreshCw,
  Clock,
  Send,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui";

interface ActionItem {
  action_id: string;
  category: string;
  priority_order: number;
  title: string;
  description: string;
  action_type: string;
  link_or_dial?: string;
  status: "TODO" | "DONE" | "NOT_APPLICABLE";
  is_immediate_lifeline: boolean;
  official_resource?: {
    display_name: string;
    official_phone?: string;
    official_url?: string;
  };
}

interface LossEvent {
  loss_event_id: string;
  amount: number;
  currency: string;
  payment_method: string;
  recipient_identifier?: string;
  transaction_reference_tokenized?: string;
  occurred_at: string;
}

interface TimelineEvent {
  timeline_event_id: string;
  event_type: string;
  title: string;
  description: string;
  occurred_at: string;
  amount?: number;
  currency?: string;
}

interface OfficialResource {
  resource_id: string;
  resource_type: string;
  display_name: string;
  organization: string;
  official_phone?: string;
  official_url?: string;
  instructions: string[];
}

export default function RescuePage() {
  const [incidentId, setIncidentId] = useState<string>("");
  const [lossType, setLossType] = useState<string>("MONEY_TRANSFER");
  const [selectedEntry, setSelectedEntry] = useState<string>("I ALREADY PAID");
  const [activeTab, setActiveTab] = useState<"actions" | "loss" | "evidence" | "recovery_warning" | "package">("actions");
  const [actions, setActions] = useState<ActionItem[]>([]);
  const [lossEvents, setLossEvents] = useState<LossEvent[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [totalLoss, setTotalLoss] = useState<number>(0);
  const [currency, setCurrency] = useState<string>("INR");
  const [resources, setResources] = useState<OfficialResource[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  // New payment form modal state
  const [newAmount, setNewAmount] = useState<string>("5000");
  const [newMethod, setNewMethod] = useState<string>("UPI");
  const [newVpa, setNewVpa] = useState<string>("fake-rewards@oksbi");
  const [newRef, setNewRef] = useState<string>("123456789012");

  // Recovery scam checker state
  const [suspectMessage, setSuspectMessage] = useState<string>("");
  const [recoveryAnalysis, setRecoveryAnalysis] = useState<any>(null);

  // Initialize rescue session
  useEffect(() => {
    initRescue("MONEY_TRANSFER");
  }, []);

  const initRescue = async (type: string) => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/rescue/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          initial_loss_type: type,
          user_notes: "Emergency Rescue arrival",
          ongoing_contact: false,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setIncidentId(data.incident_id);
        setLossEvents(data.loss_events || []);
        setTotalLoss(data.total_reported_loss || 0);
        setCurrency(data.currency || "INR");
        setTimeline(data.timeline || []);
        setResources(data.official_resources || []);

        const all = [
          ...(data.action_plan.do_now || []),
          ...(data.action_plan.do_next || []),
          ...(data.action_plan.preserve || []),
          ...(data.action_plan.report || []),
          ...(data.action_plan.monitor || []),
        ];
        setActions(all);
      }
    } catch (e) {
      console.error("Rescue init error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!incidentId) return;
    const amt = parseFloat(newAmount);
    if (isNaN(amt) || amt <= 0) return;

    try {
      const res = await fetch(`/api/v1/rescue/${incidentId}/loss-events`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amount: amt,
          currency: "INR",
          payment_method: newMethod,
          recipient_identifier: newVpa,
          transaction_reference: newRef,
          time_granularity: "EXACT",
        }),
      });
      if (res.ok) {
        // Refresh rescue state
        const stateRes = await fetch(`/api/v1/rescue/${incidentId}`);
        if (stateRes.ok) {
          const updated = await stateRes.json();
          setLossEvents(updated.loss_events || []);
          setTotalLoss(updated.total_reported_loss || 0);
          setTimeline(updated.timeline || []);
          const all = [
            ...(updated.action_plan.do_now || []),
            ...(updated.action_plan.do_next || []),
            ...(updated.action_plan.preserve || []),
            ...(updated.action_plan.report || []),
            ...(updated.action_plan.monitor || []),
          ];
          setActions(all);
          setActiveTab("actions");
        }
      }
    } catch (err) {
      console.error("Error recording payment:", err);
    }
  };

  const toggleActionDone = async (actionId: string, currentStatus: string) => {
    const nextStatus = currentStatus === "DONE" ? "TODO" : "DONE";
    try {
      await fetch(`/api/v1/rescue/${incidentId}/actions/${actionId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: nextStatus }),
      });
      setActions((prev) =>
        prev.map((a) => (a.action_id === actionId ? { ...a, status: nextStatus as any } : a))
      );
    } catch (err) {
      console.error("Error updating action:", err);
    }
  };

  const handleCheckRecoveryScam = async () => {
    if (!suspectMessage.trim()) return;
    try {
      const res = await fetch(`/api/v1/rescue/${incidentId}/check-recovery-scam`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message_text: suspectMessage }),
      });
      if (res.ok) {
        const data = await res.json();
        setRecoveryAnalysis(data);
      }
    } catch (err) {
      console.error("Error checking recovery scam:", err);
    }
  };

  const handleCopySummary = async () => {
    try {
      const res = await fetch(`/api/v1/rescue/${incidentId}/case-package`);
      if (res.ok) {
        const pkg = await res.json();
        navigator.clipboard.writeText(pkg.copyable_incident_summary || "");
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const entryOptions = [
    { label: "I Already Paid", type: "MONEY_TRANSFER", icon: AlertOctagon },
    { label: "I Shared an OTP", type: "OTP_DISCLOSURE", icon: Smartphone },
    { label: "I Shared Password/PIN", type: "CREDENTIAL_DISCLOSURE", icon: KeyRound },
    { label: "I Gave Remote Screen Access", type: "REMOTE_ACCESS", icon: ShieldAlert },
    { label: "I Shared ID / Aadhaar", type: "IDENTITY_DOCUMENT_DISCLOSURE", icon: FileText },
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-8">
      {/* ── Top Header ────────────────────────────────────────────── */}
      <div className="flex flex-col gap-4 border-b border-line pb-6 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-red-400">
            <span className="h-2 w-2 rounded-full bg-red-400 animate-pulse" />
            ScamGraph Rescue • Post-Loss Emergency Response
          </div>
          <h1 className="mt-2 text-2xl font-bold tracking-tight text-ink sm:text-3xl">
            You may still have actions you can take.
          </h1>
          <p className="mt-1 text-sm text-ink-muted">
            Tell us what happened so ScamGraph can organize the immediate next steps. Case ID:{" "}
            <code className="text-accent">{incidentId || "Initializing..."}</code>
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link href="/investigate">
            <Button variant="outline" size="sm">
              <ArrowLeft className="mr-1.5 h-3.5 w-3.5" />
              Pre-Payment Check
            </Button>
          </Link>
          <a href="tel:1930">
            <Button variant="danger" size="sm" className="bg-red-600 hover:bg-red-700 text-white font-semibold">
              <PhoneCall className="mr-1.5 h-4 w-4" />
              Call 1930 Helpline
            </Button>
          </a>
        </div>
      </div>

      {/* ── Emergency Situation Selector ──────────────────────────── */}
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-5">
        {entryOptions.map((opt) => {
          const Icon = opt.icon;
          const isSelected = selectedEntry === opt.label;
          return (
            <button
              key={opt.label}
              onClick={() => {
                setSelectedEntry(opt.label);
                setLossType(opt.type);
                initRescue(opt.type);
              }}
              className={`flex flex-col items-center justify-center rounded-xl border p-3 text-center transition-all ${
                isSelected
                  ? "border-red-500/60 bg-red-500/15 text-red-200 shadow-md shadow-red-950/40"
                  : "border-line bg-surface/70 text-ink-muted hover:border-line-hover hover:text-ink"
              }`}
            >
              <Icon className={`h-5 w-5 ${isSelected ? "text-red-400" : "text-ink-dim"}`} />
              <span className="mt-2 text-xs font-semibold leading-tight">{opt.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── Total Loss & Status Banner ────────────────────────────── */}
      <div className="grid gap-4 rounded-2xl border border-line bg-elevated/70 p-5 md:grid-cols-3">
        <div className="space-y-1">
          <div className="text-xs uppercase tracking-wider text-ink-dim">Reported Financial Loss</div>
          <div className="text-2xl font-bold text-red-400">
            {currency} {totalLoss.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-ink-muted">
            {lossEvents.length} recorded transaction(s) • User-Reported
          </div>
        </div>

        <div className="space-y-1">
          <div className="text-xs uppercase tracking-wider text-ink-dim">Immediate Priority</div>
          <div className="inline-flex items-center gap-1.5 text-base font-semibold text-amber-400">
            <AlertTriangle className="h-4 w-4 text-amber-400" />
            Golden Window Active
          </div>
          <div className="text-[11px] text-ink-muted">
            Fastest action with 1930 & bank freeze maximizes freeze probability
          </div>
        </div>

        <div className="flex items-center justify-start gap-2 md:justify-end">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setActiveTab("loss")}
            className="border-dashed text-xs"
          >
            <PlusCircle className="mr-1.5 h-3.5 w-3.5" />
            Add Payment Record
          </Button>
          <Button variant="primary" size="sm" onClick={handleCopySummary} className="text-xs">
            {copied ? <CheckCircle2 className="mr-1.5 h-3.5 w-3.5 text-emerald-400" /> : <Copy className="mr-1.5 h-3.5 w-3.5" />}
            {copied ? "Copied to Clipboard!" : "Copy 1930 Statement"}
          </Button>
        </div>
      </div>

      {/* ── Tab Navigation ────────────────────────────────────────── */}
      <div className="flex border-b border-line text-sm font-medium">
        <button
          onClick={() => setActiveTab("actions")}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 transition-colors ${
            activeTab === "actions"
              ? "border-accent text-accent font-semibold"
              : "border-transparent text-ink-muted hover:text-ink"
          }`}
        >
          <CheckCircle2 className="h-4 w-4" />
          Emergency Action Plan ({actions.filter((a) => a.status === "DONE").length}/{actions.length})
        </button>

        <button
          onClick={() => setActiveTab("loss")}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 transition-colors ${
            activeTab === "loss"
              ? "border-accent text-accent font-semibold"
              : "border-transparent text-ink-muted hover:text-ink"
          }`}
        >
          <Clock className="h-4 w-4" />
          Loss Timeline ({lossEvents.length})
        </button>

        <button
          onClick={() => setActiveTab("recovery_warning")}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 transition-colors ${
            activeTab === "recovery_warning"
              ? "border-red-400 text-red-400 font-semibold"
              : "border-transparent text-ink-muted hover:text-ink"
          }`}
        >
          <ShieldAlert className="h-4 w-4 text-red-400" />
          Recovery Scam Shield
        </button>

        <button
          onClick={() => setActiveTab("package")}
          className={`flex items-center gap-2 border-b-2 px-4 py-2.5 transition-colors ${
            activeTab === "package"
              ? "border-accent text-accent font-semibold"
              : "border-transparent text-ink-muted hover:text-ink"
          }`}
        >
          <FileText className="h-4 w-4" />
          Case Package Export
        </button>
      </div>

      {/* ── TAB 1: ACTION PLAN ────────────────────────────────────── */}
      {activeTab === "actions" && (
        <div className="space-y-6">
          {/* Section: DO NOW */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="rounded bg-red-500/20 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-red-400">
                1. DO NOW (First 15-30 Minutes)
              </span>
              <span className="text-xs text-ink-dim">Stop active extraction and trigger immediate inter-bank holds</span>
            </div>

            <div className="space-y-2">
              {actions
                .filter((a) => a.category === "DO_NOW")
                .map((item) => (
                  <div
                    key={item.action_id}
                    className={`flex items-start justify-between rounded-xl border p-4 transition-all ${
                      item.status === "DONE"
                        ? "border-emerald-500/30 bg-emerald-950/15 opacity-75"
                        : item.is_immediate_lifeline
                        ? "border-red-500/40 bg-red-950/20"
                        : "border-line bg-surface"
                    }`}
                  >
                    <div className="space-y-1.5 pr-4">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-ink text-sm">{item.title}</span>
                        {item.is_immediate_lifeline && (
                          <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-[10px] font-bold text-red-400">
                            CRITICAL
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-ink-muted leading-relaxed">{item.description}</p>
                      {item.link_or_dial && (
                        <div className="pt-1">
                          {item.action_type === "DIRECT_CALL" ? (
                            <a
                              href={`tel:${item.link_or_dial}`}
                              className="inline-flex items-center gap-1.5 text-xs font-bold text-accent hover:underline"
                            >
                              <PhoneCall className="h-3 w-3" />
                              Dial {item.link_or_dial} Directly
                            </a>
                          ) : (
                            <a
                              href={item.link_or_dial}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1.5 text-xs font-bold text-accent hover:underline"
                            >
                              <ExternalLink className="h-3 w-3" />
                              Open Official Portal ({item.link_or_dial})
                            </a>
                          )}
                        </div>
                      )}
                    </div>

                    <button
                      onClick={() => toggleActionDone(item.action_id, item.status)}
                      className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                        item.status === "DONE"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          : "bg-elevated hover:bg-line text-ink-muted border border-line"
                      }`}
                    >
                      {item.status === "DONE" ? "✓ Done" : "Mark Done"}
                    </button>
                  </div>
                ))}
            </div>
          </div>

          {/* Section: DO NEXT */}
          <div className="space-y-3 pt-2">
            <div className="flex items-center gap-2">
              <span className="rounded bg-amber-500/20 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-amber-400">
                2. DO NEXT (First 1-2 Hours)
              </span>
              <span className="text-xs text-ink-dim">Account containment, password resets & emotional support</span>
            </div>

            <div className="space-y-2">
              {actions
                .filter((a) => a.category === "DO_NEXT")
                .map((item) => (
                  <div
                    key={item.action_id}
                    className={`flex items-start justify-between rounded-xl border p-4 ${
                      item.status === "DONE"
                        ? "border-emerald-500/30 bg-emerald-950/15 opacity-75"
                        : "border-line bg-surface"
                    }`}
                  >
                    <div className="space-y-1 pr-4">
                      <div className="font-semibold text-ink text-sm">{item.title}</div>
                      <p className="text-xs text-ink-muted leading-relaxed">{item.description}</p>
                      {item.link_or_dial && (
                        <div className="pt-1">
                          <a
                            href={item.link_or_dial}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center gap-1.5 text-xs font-bold text-accent hover:underline"
                          >
                            <ExternalLink className="h-3 w-3" />
                            Official Link
                          </a>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => toggleActionDone(item.action_id, item.status)}
                      className={`shrink-0 rounded-lg px-3 py-1.5 text-xs font-semibold transition-all ${
                        item.status === "DONE"
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          : "bg-elevated hover:bg-line text-ink-muted border border-line"
                      }`}
                    >
                      {item.status === "DONE" ? "✓ Done" : "Mark Done"}
                    </button>
                  </div>
                ))}
            </div>
          </div>

          {/* Section: PRESERVE & REPORT */}
          <div className="grid gap-6 md:grid-cols-2 pt-2">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="rounded bg-sky-500/20 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-sky-400">
                  3. PRESERVE
                </span>
                <span className="text-xs text-ink-dim">Evidence for legal investigation</span>
              </div>
              <div className="space-y-2">
                {actions
                  .filter((a) => a.category === "PRESERVE")
                  .map((item) => (
                    <div key={item.action_id} className="rounded-xl border border-line bg-surface p-3 space-y-1">
                      <div className="text-xs font-semibold text-ink">{item.title}</div>
                      <p className="text-[11px] text-ink-muted">{item.description}</p>
                    </div>
                  ))}
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-indigo-400">
                  4. REPORT
                </span>
                <span className="text-xs text-ink-dim">Formal cybercrime portal submission</span>
              </div>
              <div className="space-y-2">
                {actions
                  .filter((a) => a.category === "REPORT")
                  .map((item) => (
                    <div key={item.action_id} className="rounded-xl border border-line bg-surface p-3 space-y-1">
                      <div className="text-xs font-semibold text-ink">{item.title}</div>
                      <p className="text-[11px] text-ink-muted">{item.description}</p>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 2: LOSS TIMELINE & MULTIPLE PAYMENTS ──────────────── */}
      {activeTab === "loss" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-line bg-surface p-5">
            <h3 className="text-sm font-semibold text-ink mb-3">Add a Payment Transaction</h3>
            <form onSubmit={handleRecordPayment} className="grid gap-3 sm:grid-cols-2 md:grid-cols-4">
              <div>
                <label className="text-[11px] text-ink-muted">Amount (INR)</label>
                <input
                  type="number"
                  value={newAmount}
                  onChange={(e) => setNewAmount(e.target.value)}
                  className="w-full rounded-lg border border-line bg-elevated px-3 py-2 text-sm text-ink outline-none focus:border-accent"
                  placeholder="e.g. 5000"
                  required
                />
              </div>

              <div>
                <label className="text-[11px] text-ink-muted">Payment Channel</label>
                <select
                  value={newMethod}
                  onChange={(e) => setNewMethod(e.target.value)}
                  className="w-full rounded-lg border border-line bg-elevated px-3 py-2 text-sm text-ink outline-none focus:border-accent"
                >
                  <option value="UPI">UPI</option>
                  <option value="IMPS">IMPS</option>
                  <option value="NEFT">NEFT</option>
                  <option value="CARD">Debit / Credit Card</option>
                  <option value="CRYPTO">Cryptocurrency</option>
                </select>
              </div>

              <div>
                <label className="text-[11px] text-ink-muted">Recipient VPA / Account</label>
                <input
                  type="text"
                  value={newVpa}
                  onChange={(e) => setNewVpa(e.target.value)}
                  className="w-full rounded-lg border border-line bg-elevated px-3 py-2 text-sm text-ink outline-none focus:border-accent"
                  placeholder="e.g. payee@oksbi"
                />
              </div>

              <div>
                <label className="text-[11px] text-ink-muted">12-Digit UTR / Txn Ref</label>
                <input
                  type="text"
                  value={newRef}
                  onChange={(e) => setNewRef(e.target.value)}
                  className="w-full rounded-lg border border-line bg-elevated px-3 py-2 text-sm text-ink outline-none focus:border-accent"
                  placeholder="e.g. 423456789012"
                />
              </div>

              <div className="sm:col-span-2 md:col-span-4 flex justify-end">
                <Button type="submit" variant="primary" size="sm">
                  Record Loss Event
                </Button>
              </div>
            </form>
          </div>

          {/* Payment List */}
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-ink">Recorded Payment Trail</h3>
            {lossEvents.length === 0 ? (
              <div className="rounded-xl border border-dashed border-line p-8 text-center text-xs text-ink-muted">
                No payment events logged yet. Use the form above to record transfers (e.g. ₹500 → ₹5,000 → ₹20,000).
              </div>
            ) : (
              <div className="divide-y divide-line rounded-xl border border-line bg-surface">
                {lossEvents.map((pe, idx) => (
                  <div key={pe.loss_event_id} className="flex items-center justify-between p-4 text-xs">
                    <div className="space-y-1">
                      <div className="font-semibold text-ink">
                        Payment #{idx + 1}: {pe.currency} {pe.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-ink-muted">
                        Method: {pe.payment_method} • Recipient: <code className="text-accent">{pe.recipient_identifier || "N/A"}</code>
                      </div>
                      <div className="text-ink-dim">Ref: {pe.transaction_reference_tokenized || "Masked"}</div>
                    </div>
                    <div className="text-right text-[11px] text-ink-dim">
                      {new Date(pe.occurred_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 3: RECOVERY SCAM SHIELD ────────────────────────────── */}
      {activeTab === "recovery_warning" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-red-500/30 bg-red-950/20 p-6 space-y-4">
            <div className="flex items-start gap-3">
              <ShieldAlert className="h-6 w-6 text-red-400 shrink-0 mt-0.5" />
              <div className="space-y-2">
                <h3 className="text-base font-bold text-red-200">
                  CRITICAL DEFENSE: Beware of Secondary "Recovery Scams"
                </h3>
                <p className="text-xs text-red-300/90 leading-relaxed">
                  Scam victims are frequently targeted a second time by fraudsters posing as &ldquo;ethical hackers&rdquo;,
                  &ldquo;cyber dispute lawyers&rdquo;, or official &ldquo;fund recovery specialists&rdquo;.
                  They will promise to retrieve your lost money if you pay an advance &ldquo;investigation fee&rdquo;,
                  &ldquo;tax release voucher&rdquo;, or &ldquo;unfreeze clearance&rdquo;.
                </p>
                <div className="rounded-lg bg-black/40 p-3 text-xs text-red-200 font-mono">
                  RULE: Legitimate police cyber cells, 1930 nodal officers, and banks NEVER charge any advance fee to
                  investigate or unfreeze funds.
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Recovery Message Checker */}
          <div className="rounded-2xl border border-line bg-surface p-5 space-y-4">
            <h4 className="text-sm font-semibold text-ink">
              Check a Suspicious Recovery Offer or Message
            </h4>
            <p className="text-xs text-ink-muted">
              Did someone contact you offering to get your money back? Paste their message below to verify for fraud patterns:
            </p>
            <div className="space-y-3">
              <textarea
                value={suspectMessage}
                onChange={(e) => setSuspectMessage(e.target.value)}
                placeholder="e.g. 'Hello sir, I am cyber investigator. Pay 5000 fee and we will hack back and unfreeze your 50,000 from the mule account.'"
                rows={3}
                className="w-full rounded-xl border border-line bg-elevated p-3 text-xs text-ink outline-none focus:border-accent"
              />
              <Button variant="danger" size="sm" onClick={handleCheckRecoveryScam}>
                <Send className="mr-1.5 h-3.5 w-3.5" />
                Analyze Recovery Message
              </Button>
            </div>

            {recoveryAnalysis && (
              <div className="mt-4 rounded-xl border border-red-500/40 bg-red-950/30 p-4 space-y-2">
                <div className="flex items-center gap-2 text-xs font-bold text-red-400">
                  <AlertOctagon className="h-4 w-4" />
                  ANALYSIS: {recoveryAnalysis.risk_level} RISK — RECOVERY SCAM DETECTED
                </div>
                <p className="text-xs text-red-200">{recoveryAnalysis.warning_text}</p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {recoveryAnalysis.threat_patterns_detected?.map((p: string) => (
                    <span key={p} className="rounded bg-red-500/30 px-2 py-0.5 text-[10px] font-mono text-red-300">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB 4: CASE PACKAGE EXPORT ────────────────────────────── */}
      {activeTab === "package" && (
        <div className="space-y-6">
          <div className="rounded-2xl border border-line bg-surface p-6 space-y-4">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 className="text-base font-bold text-ink">Incident Information Package</h3>
                <p className="text-xs text-ink-muted">
                  Structured technical document for 1930 / Bank Nodal Officer / NCRP complaint filing.
                </p>
              </div>
              <div className="flex gap-2">
                <Button variant="primary" size="sm" onClick={handleCopySummary}>
                  {copied ? <CheckCircle2 className="mr-1.5 h-3.5 w-3.5 text-emerald-400" /> : <Copy className="mr-1.5 h-3.5 w-3.5" />}
                  {copied ? "Copied!" : "Copy Summary"}
                </Button>
              </div>
            </div>

            <div className="rounded-xl border border-line bg-elevated/80 p-4 text-xs font-mono text-ink-muted space-y-2">
              <div className="text-amber-400 font-semibold">[OFFICIAL NOTICE & DISCLAIMER]</div>
              <p className="leading-relaxed">
                This document is a technical Incident Information Package prepared based on user-provided statements
                and ScamGraph AI automated analysis. It does NOT constitute an official Police FIR, Government
                Cybercrime Registration, or guarantee of fund recovery. It is designed to assist victims in filing
                accurate, structured reports with verified authorities and banking institutions.
              </p>
            </div>

            <div className="space-y-3 pt-2">
              <div className="text-xs font-semibold uppercase tracking-wider text-ink-dim">
                Verified Emergency Channels Included
              </div>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {resources.slice(0, 6).map((res) => (
                  <div key={res.resource_id} className="rounded-xl border border-line bg-surface p-3 space-y-1">
                    <div className="text-xs font-bold text-ink">{res.display_name}</div>
                    <div className="text-[11px] text-ink-muted">{res.organization}</div>
                    {res.official_phone && (
                      <div className="text-xs font-semibold text-accent">Phone: {res.official_phone}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
