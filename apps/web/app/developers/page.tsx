"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { 
  Key, 
  BookOpen, 
  PlayCircle, 
  ArrowRight, 
  Check, 
  Copy, 
  Shield, 
  ShieldAlert, 
  Cpu, 
  Zap, 
  Share2, 
  Radar, 
  Fingerprint, 
  CheckCircle2, 
  Info,
  Clock,
  Sparkles,
  ChevronRight
} from "lucide-react";

export default function DeveloperOverviewPage() {
  const [activeTab, setActiveTab] = useState<"curl" | "ts" | "py">("curl");
  const [copied, setCopied] = useState(false);
  const [activeKeysCount, setActiveKeysCount] = useState<number>(3);
  const [usageStats, setUsageStats] = useState<any>(null);
  const [deliveriesCount, setDeliveriesCount] = useState<number>(2840);

  useEffect(() => {
    const fetchOverviewData = async () => {
      try {
        const [keysRes, usageRes, delRes] = await Promise.all([
          fetch("/api/v1/developers/keys"),
          fetch("/api/v1/developers/usage"),
          fetch("/api/v1/developers/webhooks/deliveries")
        ]);
        if (keysRes.ok) {
          const keysData = await keysRes.json();
          if (Array.isArray(keysData)) {
            setActiveKeysCount(keysData.filter((k: any) => k.status === "active").length);
          }
        }
        if (usageRes.ok) {
          const uData = await usageRes.json();
          setUsageStats(uData);
        }
        if (delRes.ok) {
          const dData = await delRes.json();
          if (Array.isArray(dData)) {
            setDeliveriesCount(dData.length);
          }
        }
      } catch (e) {
        console.error("Overview data fetch failed", e);
      }
    };
    fetchOverviewData();
  }, []);

  const curlSnippet = `curl -X POST https://sandbox-api.scamgraph.org/v1/check/universal \\
  -H "Authorization: Bearer sk_test_51Nx98214ApexFinTechKey" \\
  -H "Content-Type: application/json" \\
  -H "X-Idempotency-Key: idemp_99a820c812ef" \\
  -d '{
    "channel": "sms",
    "sender_header": "VM-BESCOM",
    "text": "Dear consumer, electric power disconnect tonight 9:30PM due unpaid bill. Call officer 9845012345 or download update: https://bescom-billpay.app/sync.apk",
    "metadata": {
      "telecom_circle": "KA",
      "recipient_category": "retail_subscriber"
    }
  }'`;

  const tsSnippet = `import { ScamGraphClient } from "@scamgraph/sdk-node";

const client = new ScamGraphClient({
  apiKey: "sk_test_51Nx98214ApexFinTechKey",
  environment: "sandbox"
});

const evaluation = await client.check.universal({
  channel: "sms",
  senderHeader: "VM-BESCOM",
  text: "Dear consumer, electric power disconnect tonight 9:30PM...",
  metadata: { telecomCircle: "KA" }
});`;

  const pySnippet = `from scamgraph import ScamGraph

sg = ScamGraph(api_key="sk_test_51Nx98214ApexFinTechKey", env="sandbox")

result = sg.check.universal(
    channel="sms",
    sender_header="VM-BESCOM",
    text="Dear consumer, electric power disconnect tonight 9:30PM...",
    metadata={"telecom_circle": "KA"}
)`;

  const activeSnippet = activeTab === "curl" ? curlSnippet : activeTab === "ts" ? tsSnippet : pySnippet;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(activeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2200);
  };

  return (
    <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
      {/* 1. Welcome & Org Profile Card */}
      <section className="w-full bg-surface rounded-xl shadow-sm border border-border-divider/70 p-6 md:p-8 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        <div className="flex flex-col gap-2.5 max-w-[820px]">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded bg-surface-subtle font-mono text-[11px] text-viz-neutral border border-border-divider/50">
              TENANT: org_apex_98214
            </span>
            <span className="px-2.5 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[11px] font-semibold">
              Enterprise Sandbox
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight">
            Developer Portal &amp; API Gateway
          </h1>
          <p className="text-sm text-on-surface-variant leading-relaxed">
            Integrate real-time behavioral scam heuristics, SMS header verification, and topological outbreak signals directly into consumer checkout and banking apps.
          </p>
          <div className="flex items-center gap-1.5 text-xs text-viz-neutral pt-1">
            <CheckCircle2 className="h-4 w-4 text-viz-primary" />
            <span>Organization: <strong className="text-viz-text font-medium">Apex FinTech India Private Limited</strong></span>
          </div>
        </div>

        {/* Quick Action Controls */}
        <div className="flex flex-wrap lg:flex-col items-stretch gap-2.5 w-full lg:w-auto flex-shrink-0">
          <Link
            href="/developers/keys"
            className="h-10 px-5 rounded-full bg-primary hover:bg-primary/90 text-on-primary text-xs font-semibold inline-flex items-center justify-center gap-2 shadow-sm transition-colors"
          >
            <Key className="h-4 w-4" />
            <span>Create Test Key</span>
          </Link>
          <Link
            href="/developers/docs"
            className="h-10 px-5 rounded-lg bg-surface-subtle hover:bg-surface-container-high text-viz-text text-xs font-semibold inline-flex items-center justify-center gap-2 border border-border-divider/70 transition-colors"
          >
            <BookOpen className="h-4 w-4 text-viz-neutral" />
            <span>Explore Interactive Docs</span>
          </Link>
          <Link
            href="/developers/sandbox"
            className="h-10 px-5 rounded-lg bg-surface-subtle hover:bg-surface-container-high text-viz-text text-xs font-semibold inline-flex items-center justify-center gap-2 border border-border-divider/70 transition-colors"
          >
            <PlayCircle className="h-4 w-4 text-viz-primary" />
            <span>Open Sandbox Runner</span>
          </Link>
        </div>
      </section>

      {/* 2. 4-Step Developer Quickstart Pipeline */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-viz-text">Integration Quickstart</h2>
            <p className="text-xs text-on-surface-variant">Follow the canonical pipeline to wire synchronous intent verification into your payments flow.</p>
          </div>
          <span className="font-mono text-[11px] text-viz-neutral hidden md:inline">spec: p95 &lt; 150ms verification</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Step 1 */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-7 h-7 rounded-full bg-surface-subtle text-primary font-mono text-xs font-bold flex items-center justify-center border border-border-divider">
                  01
                </span>
                <span className="font-mono text-[10px] uppercase font-semibold text-viz-neutral">AUTH</span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Create a test key</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Generate a scoped sandbox API token with <code className="font-mono text-[11px] bg-surface-subtle px-1 py-0.5 rounded text-primary">read:check</code> and <code className="font-mono text-[11px] bg-surface-subtle px-1 py-0.5 rounded text-primary">write:telemetry</code> permissions.
              </p>
            </div>
            <Link href="/developers/keys" className="pt-4 inline-flex items-center gap-1 text-xs text-primary font-semibold hover:underline">
              <span>Get API Key</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>

          {/* Step 2 */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-7 h-7 rounded-full bg-surface-subtle text-primary font-mono text-xs font-bold flex items-center justify-center border border-border-divider">
                  02
                </span>
                <span className="font-mono text-[10px] uppercase font-semibold text-viz-neutral">INGEST</span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Make one check call</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Post a suspicious message payload or UPI handle to <code className="font-mono text-[11px] bg-surface-subtle px-1 py-0.5 rounded text-primary">/v1/check/universal</code> and evaluate the returned concern state.
              </p>
            </div>
            <span className="pt-4 font-mono text-[11px] text-viz-neutral">HTTP POST · JSON</span>
          </div>

          {/* Step 3 */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-7 h-7 rounded-full bg-surface-subtle text-primary font-mono text-xs font-bold flex items-center justify-center border border-border-divider">
                  03
                </span>
                <span className="font-mono text-[10px] uppercase font-semibold text-viz-neutral">SILHOUETTE</span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Inspect risk &amp; certainty</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Parse canonical seven-state risk silhouettes, evidence reasons, and ScamDNA correlation vectors with empirical zero-safe-guarantees.
              </p>
            </div>
            <span className="pt-4 font-mono text-[11px] text-viz-neutral">7 Canonical States</span>
          </div>

          {/* Step 4 */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="w-7 h-7 rounded-full bg-surface-subtle text-primary font-mono text-xs font-bold flex items-center justify-center border border-border-divider">
                  04
                </span>
                <span className="font-mono text-[10px] uppercase font-semibold text-viz-neutral">EVENTS</span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Add webhook endpoint</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Subscribe to async analysis completion and emerging outbreak campaign alerts via signed HMAC-SHA256 payloads.
              </p>
            </div>
            <Link href="/developers/webhooks" className="pt-4 inline-flex items-center gap-1 text-xs text-primary font-semibold hover:underline">
              <span>Configure URLs</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* 3. Interactive Quickstart Code Panel */}
      <section className="bg-surface rounded-xl shadow-sm border border-border-divider/70 overflow-hidden flex flex-col">
        <div className="px-5 py-3 bg-surface-container-low border-b border-border-divider/60 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <span className="text-xs font-bold text-viz-text">Live Sandbox Runner: Specimen #IN-BESCOM-9921</span>
            <div className="flex items-center bg-surface rounded p-0.5 border border-border-divider text-xs">
              <button
                onClick={() => setActiveTab("curl")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  activeTab === "curl" ? "bg-primary text-on-primary font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                cURL
              </button>
              <button
                onClick={() => setActiveTab("ts")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  activeTab === "ts" ? "bg-primary text-on-primary font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                TypeScript
              </button>
              <button
                onClick={() => setActiveTab("py")}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  activeTab === "py" ? "bg-primary text-on-primary font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Python
              </button>
            </div>
          </div>

          <button
            onClick={copyToClipboard}
            className="h-8 px-3 rounded bg-surface hover:bg-surface-subtle text-viz-text text-xs font-medium inline-flex items-center gap-1.5 border border-border-divider shadow-sm transition-all"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-viz-primary" />
                <span className="text-viz-primary font-semibold">Copied snippet</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5 text-viz-neutral" />
                <span>Copy {activeTab.toUpperCase()} Snippet</span>
              </>
            )}
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 bg-surface">
          {/* Request Window */}
          <div className="p-5 flex flex-col gap-2 bg-ground border-b lg:border-b-0 lg:border-r border-border-divider/60">
            <div className="flex items-center justify-between font-mono text-[11px] text-viz-neutral">
              <span>REQUEST · /v1/check/universal</span>
              <span>HTTP/1.1 POST</span>
            </div>
            <pre className="font-mono text-xs text-on-surface bg-surface p-4 rounded-lg border border-border-divider/60 overflow-x-auto leading-relaxed shadow-inner">
              <code>{activeSnippet}</code>
            </pre>
            <div className="flex items-center gap-1.5 text-[11px] text-viz-neutral pt-1">
              <Shield className="h-3.5 w-3.5 text-viz-primary" />
              <span>DLT entity headers cross-referenced against TRAI register</span>
            </div>
          </div>

          {/* Response Window */}
          <div className="p-5 flex flex-col gap-2 bg-surface">
            <div className="flex items-center justify-between font-mono text-xs">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-viz-primary" />
                <span className="text-on-surface font-semibold">200 OK</span>
                <span className="text-viz-neutral font-normal">(118ms)</span>
              </div>
              <div className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-info-bg text-tone-info-text text-[10px] font-semibold">
                <span>SYNTHETIC_DATA</span>
              </div>
            </div>

            <pre className="font-mono text-xs text-on-surface bg-surface-container-low p-4 rounded-lg border border-border-divider/60 overflow-x-auto leading-relaxed shadow-inner">
              <code>{`{
  "status": "success",
  "concern": "high_risk",
  "silhouette": "shield_exclamation",
  "intervention": "stop_and_verify",
  "confidence": "medium",
  "reasons": [
    {
      "id": "rsn_dlt_mismatch",
      "tactic": "spoofed_header",
      "detail": "VM-BESCOM not registered to Bangalore Electricity Supply Co Ltd"
    },
    {
      "id": "rsn_apk_dropper",
      "tactic": "remote_access_trojan",
      "url": "https://bescom-billpay.app/sync.apk"
    }
  ],
  "graph_correlations": {
    "syndicate_cluster": "syn_raj_power_utility_burst_08",
    "known_victim_incidents_24h": 412
  },
  "synthetic": true,
  "request_id": "req_chk_88201fae902b"
}`}</code>
            </pre>

            {/* Concern Silhouette Banner Preview */}
            <div className="mt-1 p-2.5 rounded-lg bg-tone-danger-bg text-tone-danger-strong-text flex items-center justify-between border border-tone-danger-text/20">
              <div className="flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-tone-danger-text" />
                <span className="text-xs font-medium">State 6: High Risk (Stop and verify)</span>
              </div>
              <span className="font-mono text-[10px] uppercase text-tone-danger-text font-bold">
                Action Recommended
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* 4. ScamGraph API Surfaces Matrix (5 core cards) */}
      <section className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
          <div>
            <h2 className="text-lg font-bold text-viz-text">ScamGraph API Surfaces Matrix</h2>
            <p className="text-xs text-on-surface-variant">Core primitives for synchronous checkouts, asynchronous forensics, and threat syndicates.</p>
          </div>
          <Link href="/developers/docs" className="text-xs text-primary font-semibold hover:underline inline-flex items-center gap-1">
            <span>View all 28 endpoints</span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* 1. Check API */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-lg bg-primary-container text-on-primary flex items-center justify-center">
                  <Shield className="h-4 w-4" />
                </span>
                <span className="font-mono text-xs text-viz-primary bg-secondary-container/40 px-2 py-0.5 rounded font-semibold">
                  v1/check
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Check API</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Synchronous &amp; async evaluation of text, telephony headers, and raw payment strings. Returns canonical 7-tier risk state with full correlation chains.
              </p>
            </div>
            <div className="pt-4 flex items-center justify-between text-xs text-viz-neutral border-t border-border-divider/40 mt-3">
              <span>Latency: &lt;140ms</span>
              <span className="font-mono font-semibold text-viz-text">POST /universal</span>
            </div>
          </div>

          {/* 2. Guard API */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-lg bg-primary-container text-on-primary flex items-center justify-center">
                  <Zap className="h-4 w-4" />
                </span>
                <span className="font-mono text-xs text-viz-primary bg-secondary-container/40 px-2 py-0.5 rounded font-semibold">
                  v1/guard
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Guard API</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Pre-transaction checkpoint for checkout forms, collect requests, and UPI mandate approvals. Evaluates user psychological coercion signals before debit.
              </p>
            </div>
            <div className="pt-4 flex items-center justify-between text-xs text-viz-neutral border-t border-border-divider/40 mt-3">
              <span>Latency: &lt;95ms</span>
              <span className="font-mono font-semibold text-viz-text">POST /intent/eval</span>
            </div>
          </div>

          {/* 3. Entity & Network API */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-lg bg-primary-container text-on-primary flex items-center justify-center">
                  <Share2 className="h-4 w-4" />
                </span>
                <span className="font-mono text-xs text-viz-primary bg-secondary-container/40 px-2 py-0.5 rounded font-semibold">
                  v1/entities
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Entity &amp; Network API</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Query known malicious VPAs, IFSC routing nodes, and suspicious domain lifecycles with strict cryptographic masking and bank secrecy compliance.
              </p>
            </div>
            <div className="pt-4 flex items-center justify-between text-xs text-viz-neutral border-t border-border-divider/40 mt-3">
              <span>Graph queries</span>
              <span className="font-mono font-semibold text-viz-text">GET /resolve</span>
            </div>
          </div>

          {/* 4. Campaign & Radar API */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <span className="w-9 h-9 rounded-lg bg-primary-container text-on-primary flex items-center justify-center">
                  <Radar className="h-4 w-4" />
                </span>
                <span className="font-mono text-xs text-viz-primary bg-secondary-container/40 px-2 py-0.5 rounded font-semibold">
                  v1/campaigns
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Campaign &amp; Radar API</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Ingest regional threat spikes, trending syndicates, and velocity bursts directly into internal SIEM, SOAR, and fraud prevention engines.
              </p>
            </div>
            <div className="pt-4 flex items-center justify-between text-xs text-viz-neutral border-t border-border-divider/40 mt-3">
              <span>Streaming &amp; Batch</span>
              <span className="font-mono font-semibold text-viz-text">GET /radar/active</span>
            </div>
          </div>

          {/* 5. Async Artifacts & Lineage */}
          <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between md:col-span-2 lg:col-span-2">
            <div className="flex flex-col gap-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="w-9 h-9 rounded-lg bg-primary-container text-on-primary flex items-center justify-center">
                    <Fingerprint className="h-4 w-4" />
                  </span>
                  <span className="font-mono text-xs text-viz-primary bg-secondary-container/40 px-2 py-0.5 rounded font-semibold">
                    v1/artifacts
                  </span>
                </div>
                <span className="font-mono text-[10px] text-viz-neutral font-semibold">
                  AUTOMATED REDACTION
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Async Artifacts &amp; Lineage API</h3>
              <p className="text-xs text-on-surface-variant leading-relaxed max-w-[720px]">
                Multi-part evidence ingestion (audio recordings, payment receipts, screenshots) with automatic OCR, PII redacting, and topological vector anchoring for criminal evidence dossiers.
              </p>
            </div>
            <div className="pt-4 flex flex-wrap items-center justify-between gap-2 text-xs text-viz-neutral border-t border-border-divider/40 mt-3">
              <span>Supports: PDF, PNG, WAV, MP3 (&lt;25MB)</span>
              <span className="font-mono font-semibold text-viz-text">POST /artifacts/ingest</span>
            </div>
          </div>
        </div>
      </section>

      {/* 5. Bento Grid: Quotas, Webhooks & SDKs */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Usage & Quotas */}
        <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-viz-text">Sandbox Quota</h3>
              <span className="font-mono text-xs text-primary font-bold">
                {Math.round(((usageStats?.quota_used ?? 1420) / (usageStats?.quota_limit ?? 50000)) * 100)}% USED
              </span>
            </div>
            <p className="text-xs text-on-surface-variant">Monthly synthetic verification call allocation for Apex FinTech org.</p>
            <div className="pt-2 flex flex-col gap-1.5">
              <div className="flex justify-between font-mono text-xs text-viz-text">
                <span className="font-bold">{(usageStats?.quota_used ?? 1420).toLocaleString()} calls</span>
                <span className="text-viz-neutral">{(usageStats?.quota_limit ?? 50000).toLocaleString()} limit</span>
              </div>
              <div className="w-full h-2 rounded-full bg-surface-subtle overflow-hidden border border-border-divider/50">
                <div 
                  className="h-full bg-viz-primary rounded-full" 
                  style={{ width: `${Math.min(Math.round(((usageStats?.quota_used ?? 1420) / (usageStats?.quota_limit ?? 50000)) * 100), 100)}%` }} 
                />
              </div>
              <span className="text-[11px] text-viz-neutral">Cycles reset in 18 days (Midnight UTC)</span>
            </div>
          </div>
          <div className="pt-4 flex items-center justify-between text-xs border-t border-border-divider/40 mt-3">
            <span className="text-viz-neutral">Active Test Keys: <strong className="text-viz-text">{activeKeysCount} active</strong></span>
            <Link href="/developers/keys" className="text-primary font-semibold hover:underline">Manage Keys</Link>
          </div>
        </div>

        {/* Webhook Delivery & Reliability */}
        <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-viz-text">Webhook Reliability</h3>
              <span className="font-mono text-xs text-viz-primary font-bold">99.8%</span>
            </div>
            <p className="text-xs text-on-surface-variant">Delivery telemetry across all sandbox subscriber endpoints.</p>
            <div className="pt-1.5 grid grid-cols-2 gap-2">
              <div className="p-2.5 rounded-lg bg-surface-subtle border border-border-divider/50 flex flex-col">
                <span className="font-mono text-[10px] text-viz-neutral uppercase">24H DELIVERIES</span>
                <span className="font-mono text-lg text-viz-text font-bold">{deliveriesCount.toLocaleString()}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-surface-subtle border border-border-divider/50 flex flex-col">
                <span className="font-mono text-[10px] text-viz-neutral uppercase">RETRIED (AUTO)</span>
                <span className="font-mono text-lg text-tone-warning-text font-bold">0</span>
              </div>
            </div>
          </div>
          <div className="pt-4 flex items-center justify-between text-xs border-t border-border-divider/40 mt-3">
            <span className="text-viz-neutral">HMAC SHA-256 Signatures active</span>
            <Link href="/developers/webhooks" className="text-primary font-semibold hover:underline">View Event Logs</Link>
          </div>
        </div>

        {/* SDKs & Libraries */}
        <div className="bg-surface rounded-xl p-5 shadow-sm border border-border-divider/70 flex flex-col justify-between">
          <div className="flex flex-col gap-2">
            <h3 className="font-bold text-sm text-viz-text">SDKs &amp; Libraries</h3>
            <p className="text-xs text-on-surface-variant">Official client libraries maintaining thread safety and automatic connection pooling.</p>
            <div className="grid grid-cols-2 gap-1.5 font-mono text-xs pt-1">
              <div className="p-2 rounded bg-surface-subtle border border-border-divider/50 flex items-center justify-between">
                <span>TypeScript</span>
                <span className="text-viz-neutral text-[11px]">v2.4.1</span>
              </div>
              <div className="p-2 rounded bg-surface-subtle border border-border-divider/50 flex items-center justify-between">
                <span>Python</span>
                <span className="text-viz-neutral text-[11px]">v2.4.0</span>
              </div>
              <div className="p-2 rounded bg-surface-subtle border border-border-divider/50 flex items-center justify-between">
                <span>Go Lang</span>
                <span className="text-viz-neutral text-[11px]">v1.9.2</span>
              </div>
              <div className="p-2 rounded bg-surface-subtle border border-border-divider/50 flex items-center justify-between">
                <span>Java Spring</span>
                <span className="text-viz-neutral text-[11px]">v3.1.0</span>
              </div>
            </div>
          </div>
          <div className="pt-4 flex items-center gap-1.5 text-[11px] text-on-surface-variant border-t border-border-divider/40 mt-3">
            <CheckCircle2 className="h-3.5 w-3.5 text-primary" />
            <span>Zero storage of passwords or MPINs. Strictly TLS 1.3.</span>
          </div>
        </div>
      </section>

      {/* Institutional Disclaimer Strip */}
      <div className="p-4 rounded-xl bg-surface-subtle text-on-surface-variant flex flex-col md:flex-row items-start md:items-center justify-between gap-2 text-xs border border-border-divider/60">
        <div className="flex items-center gap-2">
          <Info className="h-4 w-4 text-viz-neutral flex-shrink-0" />
          <span>Developer sandbox instances run isolated from live sovereign reporting relays to avoid false regulatory filings.</span>
        </div>
        <span className="font-mono text-viz-neutral text-[11px]">Apex FinTech Org Token Expires in 89 days</span>
      </div>
    </div>
  );
}
