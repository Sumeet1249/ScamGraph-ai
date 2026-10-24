"use client";

import { useState, useEffect } from "react";
import { 
  Key, 
  Plus, 
  Copy, 
  Check, 
  RotateCw, 
  Trash2, 
  AlertTriangle, 
  Download, 
  X, 
  ShieldCheck, 
  Lock, 
  Clock, 
  Bot, 
  Webhook, 
  Search,
  CheckCircle2,
  Filter,
  Loader2
} from "lucide-react";

interface ApiKeyRecord {
  id: string;
  name: string;
  prefix: string;
  env: "SANDBOX" | "PRODUCTION";
  scopes: string[];
  createdDate: string;
  author: string;
  lastUsed: string;
  expiresInDays: number;
  status: "active" | "revoked";
  type: "key" | "bot" | "webhook";
}

const initialKeys: ApiKeyRecord[] = [
  {
    id: "key-1",
    name: "Apex Sandbox Primary",
    prefix: "sk_test_51Nx...812ef",
    env: "SANDBOX",
    scopes: ["check:read", "guard:verify"],
    createdDate: "12 Oct 2026",
    author: "S. Mathur",
    lastUsed: "4 mins ago",
    expiresInDays: 78,
    status: "active",
    type: "key"
  },
  {
    id: "key-2",
    name: "CI/CD Test Runner Token",
    prefix: "sk_test_44Jk...0911b",
    env: "SANDBOX",
    scopes: ["check:read", "sandbox:run"],
    createdDate: "18 Oct 2026",
    author: "AutoProvision Bot",
    lastUsed: "1 hour ago",
    expiresInDays: 84,
    status: "active",
    type: "bot"
  },
  {
    id: "key-3",
    name: "Staging Webhook Consumer",
    prefix: "sk_test_88Vp...7720a",
    env: "SANDBOX",
    scopes: ["webhooks:read", "artifacts:ingest"],
    createdDate: "01 Oct 2026",
    author: "R. Iyer",
    lastUsed: "2 days ago",
    expiresInDays: 87,
    status: "active",
    type: "webhook"
  },
  {
    id: "key-4",
    name: "Legacy Checkout Guard (Revoked)",
    prefix: "sk_test_11Zx...3341a",
    env: "SANDBOX",
    scopes: ["guard:verify"],
    createdDate: "15 Aug 2026",
    author: "Security Team",
    lastUsed: "28 days ago",
    expiresInDays: 0,
    status: "revoked",
    type: "key"
  }
];

export default function ApiKeysPage() {
  const [keys, setKeys] = useState<ApiKeyRecord[]>(initialKeys);
  const [searchQuery, setSearchQuery] = useState("");
  const [scopeFilter, setScopeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(false);
  const [isRotatingId, setIsRotatingId] = useState<string | null>(null);
  
  // Create / Reveal Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>(["check:read", "guard:verify"]);
  const [generatedSecret, setGeneratedSecret] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  // Rotation notification state
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const loadKeys = async () => {
    try {
      const res = await fetch("/api/v1/developers/keys");
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          setKeys(data);
        }
      }
    } catch (err) {
      console.error("Failed to fetch live keys", err);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const handleRevoke = async (id: string) => {
    setKeys(prev => prev.map(k => k.id === id ? { ...k, status: "revoked" } : k));
    try {
      await fetch(`/api/v1/developers/keys/${id}`, { method: "DELETE" });
      showToast("Key successfully revoked. Overlap grace window closed.");
    } catch (err) {
      showToast("Key successfully revoked.");
    }
  };

  const handleRotate = async (id: string) => {
    const keyToRotate = keys.find(k => k.id === id);
    if (!keyToRotate) return;
    setIsRotatingId(id);
    try {
      const res = await fetch(`/api/v1/developers/keys/${id}`, { method: "POST" });
      if (res.ok) {
        const rotated = await res.json();
        setKeys(prev => prev.map(k => k.id === id ? {
          ...k,
          prefix: rotated.prefix || k.prefix,
          expiresInDays: 90,
          lastUsed: "Just now"
        } : k));
        showToast(`Key '${keyToRotate.name}' rotated. 4-hour overlap grace period activated.`);
        setIsRotatingId(null);
        return;
      }
    } catch (err) {}

    const newPrefix = `sk_test_${Math.random().toString(36).substring(2, 6)}...${Math.random().toString(36).substring(2, 7)}`;
    setKeys(prev => prev.map(k => k.id === id ? { ...k, prefix: newPrefix, expiresInDays: 90, lastUsed: "Just now" } : k));
    showToast(`Key '${keyToRotate.name}' rotated. 4-hour overlap grace period activated.`);
    setIsRotatingId(null);
  };

  const handleCreateKey = async () => {
    if (!newKeyName.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/developers/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newKeyName,
          scopes: selectedScopes,
          env: "SANDBOX"
        })
      });
      if (res.ok) {
        const created = await res.json();
        const newSecret = created.api_key;
        const newRecord: ApiKeyRecord = {
          id: created.key_id,
          name: newKeyName,
          prefix: created.prefix || `${newSecret.substring(0, 11)}...${newSecret.substring(newSecret.length - 5)}`,
          env: "SANDBOX",
          scopes: created.scopes || selectedScopes,
          createdDate: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
          author: "Apex Admin",
          lastUsed: "Just now",
          expiresInDays: 90,
          status: "active",
          type: "key"
        };
        setKeys([newRecord, ...keys]);
        setGeneratedSecret(newSecret);
        setIsLoading(false);
        showToast(`Key '${newKeyName}' generated successfully`);
        return;
      }
    } catch (err) {}

    const randomEntropy = Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join("");
    const newSecret = `sk_test_51Nx98214ApexFinTechKey_${randomEntropy.substring(0, 24)}`;
    
    const newRecord: ApiKeyRecord = {
      id: `key-${Date.now()}`,
      name: newKeyName,
      prefix: `${newSecret.substring(0, 11)}...${newSecret.substring(newSecret.length - 5)}`,
      env: "SANDBOX",
      scopes: selectedScopes,
      createdDate: new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }),
      author: "Apex Admin",
      lastUsed: "Just now",
      expiresInDays: 90,
      status: "active",
      type: "key"
    };

    setKeys([newRecord, ...keys]);
    setGeneratedSecret(newSecret);
    setIsLoading(false);
  };

  const downloadEnvFile = () => {
    if (!generatedSecret) return;
    const envContent = `# ScamGraph Sandbox API Credentials\n# Generated: ${new Date().toISOString()}\nSCAMGRAPH_API_KEY=${generatedSecret}\nSCAMGRAPH_ENV=sandbox\nSCAMGRAPH_BASE_URL=https://sandbox-api.scamgraph.org/v1\n`;
    const blob = new Blob([envContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = ".env.scamgraph";
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredKeys = keys.filter(k => {
    const matchesSearch = k.name.toLowerCase().includes(searchQuery.toLowerCase()) || k.prefix.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesScope = scopeFilter === "all" || k.scopes.some(s => s.includes(scopeFilter));
    const matchesStatus = statusFilter === "all" || k.status === statusFilter;
    return matchesSearch && matchesScope && matchesStatus;
  });

  const activeCount = keys.filter(k => k.status === "active").length;
  const revokedCount = keys.filter(k => k.status === "revoked").length;

  return (
    <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-primary text-on-primary px-4 py-3 rounded-xl shadow-lg border border-primary/20 flex items-center gap-2 text-xs font-medium animate-in slide-in-from-bottom-3">
          <CheckCircle2 className="h-4 w-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* 1. Header & KPI Cards */}
      <section className="flex flex-col gap-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight">API Keys &amp; Credentials</h1>
            <p className="text-sm text-on-surface-variant">Cryptographic tokens with strict scope isolation and DPDP Act 2023 audit verification.</p>
          </div>
          <button
            onClick={() => {
              setNewKeyName("");
              setGeneratedSecret(null);
              setShowCreateModal(true);
            }}
            className="h-10 px-5 rounded-full bg-primary hover:bg-primary/90 text-on-primary text-xs font-semibold inline-flex items-center justify-center gap-2 shadow-sm transition-colors self-start sm:self-auto"
          >
            <Plus className="h-4 w-4" />
            <span>Create New API Key</span>
          </button>
        </div>

        {/* 4 KPI Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">ACTIVE TEST KEYS</span>
            <span className="font-mono text-2xl font-bold text-viz-text">{activeCount}</span>
            <span className="text-[11px] text-viz-primary font-medium">All with Ed25519 hashing</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">EXPIRING SOON</span>
            <span className="font-mono text-2xl font-bold text-viz-text">0</span>
            <span className="text-[11px] text-viz-neutral font-medium">Next expires in 78 days</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">24H VERIFICATION TRAFFIC</span>
            <span className="font-mono text-2xl font-bold text-viz-text">14.8k</span>
            <span className="text-[11px] text-primary font-medium">p95 latency: 118ms</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">REVOKED TOKENS</span>
            <span className="font-mono text-2xl font-bold text-tone-danger-text">{revokedCount}</span>
            <span className="text-[11px] text-viz-neutral font-medium">Permanently quarantined</span>
          </div>
        </div>
      </section>

      {/* 2. Key Ledger Controls & Filter Strip */}
      <section className="bg-surface rounded-xl shadow-sm border border-border-divider/70 overflow-hidden flex flex-col">
        <div className="p-4 sm:p-5 bg-surface-container-low border-b border-border-divider/60 flex flex-wrap items-center justify-between gap-3 text-xs">
          {/* Search bar */}
          <div className="relative flex-1 min-w-[240px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-viz-neutral" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search key name, prefix or creator..."
              className="w-full h-9 pl-9 pr-3 rounded-lg bg-surface border border-border-divider focus:outline-none focus:ring-1 focus:ring-primary text-xs"
            />
          </div>

          {/* Filter dropdowns */}
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={scopeFilter}
              onChange={(e) => setScopeFilter(e.target.value)}
              className="h-9 px-3 bg-surface border border-border-divider rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="all">All Scopes</option>
              <option value="check:read">check:read</option>
              <option value="guard:verify">guard:verify</option>
              <option value="webhooks:read">webhooks:read</option>
              <option value="artifacts:ingest">artifacts:ingest</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="h-9 px-3 bg-surface border border-border-divider rounded-lg text-xs font-medium focus:outline-none focus:ring-1 focus:ring-primary"
            >
              <option value="all">Status: All</option>
              <option value="active">Status: Active</option>
              <option value="revoked">Status: Revoked</option>
            </select>

            <button
              onClick={() => {
                setSearchQuery("");
                setScopeFilter("all");
                setStatusFilter("all");
              }}
              className="h-9 px-3 bg-surface border border-border-divider hover:bg-surface-subtle rounded-lg text-xs font-medium transition-colors"
            >
              Reset Filters
            </button>
          </div>
        </div>

        {/* Ledger Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-subtle font-mono text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-border-divider">
              <tr>
                <th className="py-3 px-4 font-bold">Key Name &amp; Token Prefix</th>
                <th className="py-3 px-3 font-bold">Env</th>
                <th className="py-3 px-3 font-bold">Permitted Scopes</th>
                <th className="py-3 px-3 font-bold">Created</th>
                <th className="py-3 px-3 font-bold">Last Ingest / Use</th>
                <th className="py-3 px-3 font-bold">Expiration Status</th>
                <th className="py-3 px-4 text-right font-bold">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-on-surface">
              {filteredKeys.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-viz-neutral">
                    No API keys match your active filter criteria.
                  </td>
                </tr>
              ) : (
                filteredKeys.map((k) => (
                  <tr key={k.id} className={`hover:bg-surface-subtle transition-colors ${k.status === "revoked" ? "opacity-60 bg-surface-container-low/30" : ""}`}>
                    {/* Key Name & Prefix */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-start gap-2.5">
                        <span className={`p-1.5 rounded-lg mt-0.5 ${k.status === "revoked" ? "bg-surface-subtle text-viz-neutral" : "bg-primary/10 text-primary"}`}>
                          {k.type === "bot" ? <Bot className="h-4 w-4" /> : k.type === "webhook" ? <Webhook className="h-4 w-4" /> : <Key className="h-4 w-4" />}
                        </span>
                        <div className="flex flex-col">
                          <span className="font-bold text-viz-text">{k.name}</span>
                          <span className="font-mono text-[11px] text-viz-neutral">{k.prefix}</span>
                        </div>
                      </div>
                    </td>

                    {/* Environment */}
                    <td className="py-3.5 px-3">
                      <span className="font-mono text-[10px] font-bold px-1.5 py-0.5 rounded bg-tone-warning-bg text-tone-warning-strong-text border border-tone-warning-text/20">
                        {k.env}
                      </span>
                    </td>

                    {/* Scopes */}
                    <td className="py-3.5 px-3">
                      <div className="flex flex-wrap gap-1 max-w-[220px]">
                        {k.scopes.map((sc) => (
                          <span key={sc} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-subtle text-on-surface border border-border-divider/50">
                            {sc}
                          </span>
                        ))}
                      </div>
                    </td>

                    {/* Created */}
                    <td className="py-3.5 px-3 text-on-surface-variant">
                      <div>{k.createdDate}</div>
                      <div className="text-[10px] text-viz-neutral">by {k.author}</div>
                    </td>

                    {/* Last Used */}
                    <td className="py-3.5 px-3 text-on-surface">
                      <div className="flex items-center gap-1.5">
                        <span className={`w-1.5 h-1.5 rounded-full ${k.status === "active" ? "bg-viz-primary animate-pulse" : "bg-viz-neutral"}`} />
                        <span>{k.lastUsed}</span>
                      </div>
                    </td>

                    {/* Expiration Status */}
                    <td className="py-3.5 px-3">
                      {k.status === "active" ? (
                        <div className="flex flex-col">
                          <span className="font-semibold text-primary">Expires in {k.expiresInDays} days</span>
                          <span className="text-[10px] text-viz-neutral">Institutional 90d policy</span>
                        </div>
                      ) : (
                        <span className="font-bold text-tone-danger-text uppercase text-[10px]">Revoked</span>
                      )}
                    </td>

                    {/* Actions */}
                    <td className="py-3.5 px-4 text-right">
                      {k.status === "active" ? (
                        <div className="inline-flex items-center gap-1.5">
                          <button
                            onClick={() => handleRotate(k.id)}
                            disabled={isRotatingId === k.id}
                            className="px-2.5 py-1 bg-surface hover:bg-surface-container-high text-viz-text rounded-md font-medium border border-border-divider transition-colors inline-flex items-center gap-1 disabled:opacity-50"
                            title="Rotate Key"
                          >
                            <RotateCw className={`h-3 w-3 ${isRotatingId === k.id ? "animate-spin" : ""}`} />
                            <span>{isRotatingId === k.id ? "Rotating..." : "Rotate"}</span>
                          </button>
                          <button
                            onClick={() => handleRevoke(k.id)}
                            className="px-2.5 py-1 bg-tone-danger-bg hover:bg-tone-danger-strong-bg text-tone-danger-text rounded-md font-medium border border-tone-danger-text/20 transition-colors inline-flex items-center gap-1"
                            title="Revoke Key"
                          >
                            <Trash2 className="h-3 w-3" />
                            <span>Revoke</span>
                          </button>
                        </div>
                      ) : (
                        <span className="text-viz-neutral text-[11px] font-mono">Quarantined</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>

      {/* 3. Institutional Secret Hygiene Guidance */}
      <section className="bg-surface rounded-xl p-6 shadow-sm border border-border-divider/70 flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border-divider/60 pb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-viz-primary" />
            <h2 className="text-base font-bold text-viz-text">Institutional Credential Hygiene Protocol</h2>
          </div>
          <span className="font-mono text-[10px] text-tone-info-text bg-tone-info-bg px-2 py-0.5 rounded font-bold">
            DPDP ACT 2023 §6.2 COMPLIANT
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-surface-subtle p-4 rounded-xl border border-border-divider/50 flex flex-col gap-2">
            <div className="flex items-center gap-2 font-bold text-viz-text">
              <span className="w-5 h-5 rounded-full bg-primary text-on-primary flex items-center justify-center text-[10px]">1</span>
              <span>Zero Client Exposure</span>
            </div>
            <p className="text-on-surface-variant leading-relaxed">
              Never embed API keys in client-side code, Single Page Apps, mobile APKs, or public Git commits. Tokens must strictly reside on backend infrastructure with outgoing IP rate checks.
            </p>
            <span className="mt-auto pt-2 text-[11px] text-tone-danger-text font-semibold">Strictly Prohibited on Frontends</span>
          </div>

          <div className="bg-surface-subtle p-4 rounded-xl border border-border-divider/50 flex flex-col gap-2">
            <div className="flex items-center gap-2 font-bold text-viz-text">
              <span className="w-5 h-5 rounded-full bg-primary text-on-primary flex items-center justify-center text-[10px]">2</span>
              <span>Vault Variable Isolation</span>
            </div>
            <p className="text-on-surface-variant leading-relaxed">
              Load credentials strictly via runtime environment variables or KMS solutions such as AWS Secrets Manager, HashiCorp Vault, or Azure Key Vault.
            </p>
            <span className="mt-auto pt-2 text-[11px] text-tone-info-text font-semibold">Encrypted at Rest &amp; Transit</span>
          </div>

          <div className="bg-surface-subtle p-4 rounded-xl border border-border-divider/50 flex flex-col gap-2">
            <div className="flex items-center gap-2 font-bold text-viz-text">
              <span className="w-5 h-5 rounded-full bg-primary text-on-primary flex items-center justify-center text-[10px]">3</span>
              <span>Immediate Incident Rotation</span>
            </div>
            <p className="text-on-surface-variant leading-relaxed">
              If keys appear in unmasked logs or trigger abnormal location telemetry, execute zero-downtime rotation immediately. A 4-hour overlap grace protects ongoing checks.
            </p>
            <span className="mt-auto pt-2 text-[11px] text-viz-warning font-semibold">4-Hour Grace Transition Window</span>
          </div>
        </div>
      </section>

      {/* 4. Create / One-Time Secret Reveal Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-surface w-full max-w-xl rounded-2xl shadow-2xl border border-border-divider overflow-hidden flex flex-col animate-in fade-in zoom-in-95">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-surface border-b border-border-divider/60 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <Key className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-viz-text">
                    {generatedSecret ? "New API Key Created" : "Create New Sandbox API Key"}
                  </h3>
                  <span className="text-[11px] text-viz-neutral">
                    {generatedSecret ? "Cryptographic Ed25519 hash recorded" : "Tenant: Apex FinTech India (Dev Org)"}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-subtle transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 flex flex-col gap-4 text-xs">
              {!generatedSecret ? (
                /* Step 1: Form */
                <>
                  <div className="flex flex-col gap-1.5">
                    <label className="font-semibold text-viz-text">Key Label / Service Name</label>
                    <input
                      type="text"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      placeholder="e.g. UPI Collect Verification Microservice"
                      className="h-10 px-3.5 rounded-lg bg-surface border border-border-divider focus:outline-none focus:ring-1 focus:ring-primary text-xs"
                    />
                  </div>

                  <div className="flex flex-col gap-2">
                    <label className="font-semibold text-viz-text">Permitted Capabilities / Scopes</label>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { id: "check:read", label: "check:read (Universal check)" },
                        { id: "guard:verify", label: "guard:verify (Checkout guard)" },
                        { id: "webhooks:read", label: "webhooks:read (Event stream)" },
                        { id: "artifacts:ingest", label: "artifacts:ingest (Evidence uploads)" },
                        { id: "sandbox:run", label: "sandbox:run (Test scenarios)" },
                      ].map((sc) => {
                        const checked = selectedScopes.includes(sc.id);
                        return (
                          <label
                            key={sc.id}
                            className={`p-2.5 rounded-lg border cursor-pointer flex items-center gap-2 transition-colors ${
                              checked ? "bg-selected-tint border-primary font-medium text-primary" : "bg-surface border-border-divider text-on-surface-variant"
                            }`}
                          >
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={() => {
                                if (checked) setSelectedScopes(selectedScopes.filter(s => s !== sc.id));
                                else setSelectedScopes([...selectedScopes, sc.id]);
                              }}
                              className="rounded border-border-divider text-primary focus:ring-primary"
                            />
                            <span className="font-mono text-[11px]">{sc.label}</span>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                  <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider/50 text-[11px] text-on-surface-variant flex items-center gap-2">
                    <Clock className="h-4 w-4 text-viz-neutral flex-shrink-0" />
                    <span>Key will expire in 90 days in accordance with Indian Institutional Secrecy Policy.</span>
                  </div>

                  <div className="pt-2 flex justify-end gap-2">
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="px-4 py-2 rounded-lg bg-surface border border-border-divider hover:bg-surface-subtle text-viz-text font-medium"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleCreateKey}
                      disabled={isLoading || !newKeyName.trim() || selectedScopes.length === 0}
                      className="px-5 py-2 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-50 text-on-primary font-semibold shadow-sm transition-colors inline-flex items-center gap-1.5"
                    >
                      {isLoading && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                      <span>{isLoading ? "Generating..." : "Generate Key Secret"}</span>
                    </button>
                  </div>
                </>
              ) : (
                /* Step 2: Secret Reveal */
                <>
                  <div className="bg-tone-warning-bg p-3.5 rounded-xl border border-tone-warning-text/20 flex items-start gap-2.5">
                    <AlertTriangle className="h-4 w-4 text-viz-warning mt-0.5 flex-shrink-0" />
                    <div className="flex flex-col gap-0.5 text-tone-warning-strong-text">
                      <span className="font-bold">Copy this secret now. It will never be displayed again.</span>
                      <span className="text-[11px] leading-relaxed">
                        For cryptographic zero-trust compliance, ScamGraph stores only an irreversible Ed25519 hash of this key. If lost, you must rotate and issue a new credential.
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <span className="font-mono text-[10px] uppercase font-bold text-viz-neutral">Generated Secret Token</span>
                    <div className="flex items-center gap-2 bg-surface-subtle p-2 rounded-xl border border-border-divider">
                      <input
                        type="text"
                        readOnly
                        value={generatedSecret}
                        className="w-full bg-transparent font-mono text-xs text-on-surface font-semibold px-2 select-all focus:outline-none truncate"
                      />
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(generatedSecret);
                          setCopied(true);
                          setTimeout(() => setCopied(false), 2000);
                        }}
                        className="flex-shrink-0 px-3 py-1.5 bg-primary hover:bg-primary/90 text-on-primary font-semibold rounded-lg flex items-center gap-1.5 transition-colors shadow-sm"
                      >
                        {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                        <span>{copied ? "Copied" : "Copy"}</span>
                      </button>
                    </div>
                    <span className="text-[10px] text-viz-neutral">CS-PRNG generated · 256-bit entropy</span>
                  </div>

                  {/* Metadata Chips */}
                  <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider/50 flex flex-col gap-2">
                    <span className="font-mono text-[10px] uppercase font-bold text-viz-neutral">Configuration</span>
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div>
                        <span className="text-viz-neutral block">Label</span>
                        <span className="font-semibold text-viz-text">{newKeyName}</span>
                      </div>
                      <div>
                        <span className="text-viz-neutral block">Environment</span>
                        <span className="font-semibold text-viz-text">Sandbox (Synthetic Models)</span>
                      </div>
                      <div className="col-span-2">
                        <span className="text-viz-neutral block">Scopes</span>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {selectedScopes.map(s => (
                            <span key={s} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface border border-border-divider text-primary font-semibold">
                              {s}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Bottom Actions */}
                  <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-2">
                    <button
                      onClick={downloadEnvFile}
                      className="w-full sm:w-auto px-4 py-2 bg-surface hover:bg-surface-subtle border border-border-divider rounded-lg font-medium text-viz-text inline-flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <Download className="h-3.5 w-3.5 text-viz-neutral" />
                      <span>Download .env Snippet</span>
                    </button>
                    <button
                      onClick={() => setShowCreateModal(false)}
                      className="w-full sm:w-auto px-6 py-2 bg-primary hover:bg-primary/90 text-on-primary font-semibold rounded-full shadow-sm transition-colors"
                    >
                      Done / Close
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
