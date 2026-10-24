"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Briefcase,
  Plus,
  ArrowRight,
  Filter,
  RefreshCw,
  FolderOpen,
  MessageSquare,
  Shield,
  Layers,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/ui";

interface CaseItem {
  case_id: string;
  title: string;
  status: "OPEN" | "INVESTIGATING" | "WAITING" | "RESOLVED" | "ARCHIVED";
  priority: string;
  assigned_analyst?: string;
  linked_incident_ids: string[];
  linked_campaign_ids: string[];
  linked_entities: string[];
  notes: Array<{ author: string; timestamp: string; text: string }>;
  tags: string[];
  created_at: string;
  updated_at: string;
}

export default function CasesPage() {
  const [cases, setCases] = useState<CaseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCase, setSelectedCase] = useState<CaseItem | null>(null);
  const [noteText, setNoteText] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newPriority, setNewPriority] = useState("HIGH");
  const [newAnalyst, setNewAnalyst] = useState("Fraud Ops Lead");
  const [initialNote, setInitialNote] = useState("");

  const fetchCases = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/console/cases");
      if (res.ok) {
        const data = await res.json();
        setCases(data);
        if (data.length > 0 && !selectedCase) {
          setSelectedCase(data[0]);
        }
      }
    } catch (e) {
      console.error("Failed to load cases:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const handleAddNote = async () => {
    if (!selectedCase || !noteText.trim()) return;
    try {
      const res = await fetch(`/api/v1/console/cases/${selectedCase.case_id}/notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: noteText, author: "Fraud Analyst (Active)" }),
      });
      if (res.ok) {
        const updated = await res.json();
        setCases((prev) => prev.map((c) => (c.case_id === updated.case_id ? updated : c)));
        setSelectedCase(updated);
        setNoteText("");
      }
    } catch (e) {
      console.error("Failed to add note:", e);
    }
  };

  const handleCreateCase = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/v1/console/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newTitle,
          priority: newPriority,
          assigned_analyst: newAnalyst,
          initial_note: initialNote,
          tags: ["MANUAL_CASE"],
        }),
      });
      if (res.ok) {
        const created = await res.json();
        setCases((prev) => [created, ...prev]);
        setSelectedCase(created);
        setShowCreateModal(false);
        setNewTitle("");
        setInitialNote("");
      }
    } catch (e) {
      console.error("Failed to create case:", e);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Investigation Casefiles"
          description="Operational case workspaces grouping correlated incidents, cross-channel campaigns, and shared mule accounts."
        />
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchCases} disabled={loading}>
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
          <Button variant="primary" size="sm" onClick={() => setShowCreateModal(true)}>
            <Plus className="h-3.5 w-3.5 mr-1.5" />
            New Case
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Cases List */}
        <div className="lg:col-span-5 space-y-3">
          <div className="text-xs font-semibold text-ink-muted px-1">
            Active Investigations ({cases.length})
          </div>

          <div className="space-y-2">
            {cases.map((c) => (
              <button
                key={c.case_id}
                onClick={() => setSelectedCase(c)}
                className={`w-full p-4 rounded-xl border text-left transition-all ${
                  selectedCase?.case_id === c.case_id
                    ? "border-accent bg-accent/5 shadow-sm"
                    : "border-line bg-surface hover:border-line-strong"
                }`}
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase ${
                      c.priority === "CRITICAL"
                        ? "bg-red-500/15 text-red-400"
                        : "bg-amber-500/15 text-amber-400"
                    }`}
                  >
                    {c.priority}
                  </span>
                  <span className="text-[11px] font-mono text-ink-dim">{c.status}</span>
                </div>

                <div className="text-xs font-semibold text-ink line-clamp-1">{c.title}</div>
                <div className="text-[11px] text-ink-muted mt-1">
                  Assigned: {c.assigned_analyst || "Unassigned"}
                </div>

                <div className="flex items-center gap-4 mt-2 pt-2 border-t border-line/60 text-[10px] text-ink-dim font-mono">
                  <span>{c.linked_incident_ids.length} Incidents</span>
                  <span>{c.linked_campaign_ids.length} Campaigns</span>
                  <span>{c.notes.length} Notes</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Case Detail Workspace */}
        <div className="lg:col-span-7">
          {selectedCase ? (
            <div className="p-6 rounded-2xl border border-line bg-surface space-y-6">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-surface-elevated text-accent">
                      {selectedCase.case_id}
                    </span>
                    <span className="text-xs text-ink-dim">
                      Updated {new Date(selectedCase.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-ink">{selectedCase.title}</h3>
                  <div className="text-xs text-ink-muted mt-1">
                    Lead Analyst:{" "}
                    <span className="text-ink font-semibold">
                      {selectedCase.assigned_analyst || "Unassigned"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Linked Objects Grid */}
              <div className="grid grid-cols-3 gap-3 text-xs font-mono">
                <div className="p-3 rounded-xl border border-line bg-surface-elevated">
                  <div className="text-ink-dim text-[10px] uppercase">Linked Incidents</div>
                  <div className="text-base font-bold text-ink mt-0.5">
                    {selectedCase.linked_incident_ids.length}
                  </div>
                </div>
                <div className="p-3 rounded-xl border border-line bg-surface-elevated">
                  <div className="text-ink-dim text-[10px] uppercase">Correlated Campaigns</div>
                  <div className="text-base font-bold text-accent mt-0.5">
                    {selectedCase.linked_campaign_ids.length}
                  </div>
                </div>
                <div className="p-3 rounded-xl border border-line bg-surface-elevated">
                  <div className="text-ink-dim text-[10px] uppercase">Target Entities</div>
                  <div className="text-base font-bold text-purple-400 mt-0.5">
                    {selectedCase.linked_entities.length}
                  </div>
                </div>
              </div>

              {/* Linked Entities Display */}
              {selectedCase.linked_entities.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs font-bold text-ink-muted uppercase tracking-wider font-mono">
                    Entities Under Investigation
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedCase.linked_entities.map((ent) => (
                      <span
                        key={ent}
                        className="px-2.5 py-1 rounded-lg bg-surface-elevated border border-line text-xs font-mono text-ink"
                      >
                        {ent}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes Stream */}
              <div className="space-y-3 pt-4 border-t border-line">
                <div className="text-xs font-bold text-ink-muted uppercase tracking-wider font-mono">
                  Case Activity & Analyst Notes ({selectedCase.notes.length})
                </div>

                <div className="space-y-2 max-h-56 overflow-y-auto scrollbar-thin">
                  {selectedCase.notes.map((note, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-line bg-surface-elevated text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between text-[10px] text-ink-dim font-mono">
                        <span className="font-semibold text-accent">{note.author}</span>
                        <span>{new Date(note.timestamp).toLocaleString()}</span>
                      </div>
                      <p className="text-xs text-ink leading-relaxed">{note.text}</p>
                    </div>
                  ))}
                </div>

                <div className="pt-2 flex gap-2">
                  <input
                    type="text"
                    value={noteText}
                    onChange={(e) => setNoteText(e.target.value)}
                    placeholder="Add an auditable investigation note..."
                    className="flex-1 rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink outline-none focus:border-accent"
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleAddNote();
                    }}
                  />
                  <Button variant="primary" size="sm" onClick={handleAddNote}>
                    Append Note
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center border border-line rounded-2xl bg-surface text-ink-dim text-sm">
              Select an investigation case to view linked incidents and timeline notes.
            </div>
          )}
        </div>
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl border border-line bg-surface p-6 space-y-4">
            <h3 className="text-base font-bold text-ink">Open New Investigation Case</h3>
            <form onSubmit={handleCreateCase} className="space-y-3">
              <div>
                <label className="text-xs font-semibold text-ink-muted block mb-1">
                  Case Title
                </label>
                <input
                  type="text"
                  required
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Operation FakeKYC Mumbai Ring"
                  className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink outline-none focus:border-accent"
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-muted block mb-1">Priority</label>
                <select
                  value={newPriority}
                  onChange={(e) => setNewPriority(e.target.value)}
                  className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink outline-none focus:border-accent"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold text-ink-muted block mb-1">
                  Initial Investigation Note
                </label>
                <textarea
                  value={initialNote}
                  onChange={(e) => setInitialNote(e.target.value)}
                  placeholder="Reason for opening case and preliminary findings..."
                  className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink outline-none focus:border-accent"
                  rows={3}
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" size="sm" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button variant="primary" size="sm" type="submit">
                  Create Casefile
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
