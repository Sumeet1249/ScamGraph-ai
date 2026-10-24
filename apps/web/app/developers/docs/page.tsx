
"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Key,
  Copy,
  Check,
  ArrowRight,
  ShieldAlert,
  Shield,
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Octagon,
  CircleDot,
  Server,
  Layers,
  Sparkles,
  ExternalLink
} from "lucide-react";

export default function ApiDocumentationPage() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<string>("/v1/check/universal");
  const [langTab, setLangTab] = useState<"curl" | "ts" | "py">("curl");
  const [responseStatus, setResponseStatus] = useState<200 | 400 | 429>(200);
  const [copied, setCopied] = useState(false);

  const curlReq = `curl -X POST https://api.scamgraph.in/v1/check/universal \\
  -H "Authorization: Bearer sk_test_8942in_98fc02ab" \\
  -H "X-Idempotency-Key: a4c9f182-3d8b-4c22-b9e1-2093e098" \\
  -H "Content-Type: application/json" \\
  -d '{
    "channel": "sms",
    "sender_header": "VM-BESCOM",
    "text": "Dear customer, your electricity power will be disconnected tonight at 9.30 PM from the power office because your previous month bill was not updated. Please immediately contact our electric officer on 9845012345 to update. Thank you.",
    "metadata": {
      "circle": "KA",
      "timestamp_ist": "2026-05-18T19:42:10+05:30",
      "recipient_category": "retail"
    }
  }'`;

  const tsReq = `import { ScamGraphClient } from "@scamgraph/sdk-node";

const client = new ScamGraphClient({
  apiKey: "sk_test_8942in_98fc02ab",
  environment: "sandbox"
});

const response = await client.check.universal({
  channel: "sms",
  senderHeader: "VM-BESCOM",
  text: "Dear customer, your electricity power will be disconnected tonight...",
  metadata: {
    circle: "KA",
    recipientCategory: "retail"
  }
});`;

  const pyReq = `import requests

url = "https://api.scamgraph.in/v1/check/universal"
headers = {
    "Authorization": "Bearer sk_test_8942in_98fc02ab",
    "Content-Type": "application/json",
    "X-Idempotency-Key": "a4c9f182-3d8b-4c22-b9e1-2093e098"
}
payload = {
    "channel": "sms",
    "sender_header": "VM-BESCOM",
    "text": "Dear customer, your electricity power will be disconnected tonight...",
    "metadata": {"circle": "KA", "recipient_category": "retail"}
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()`;

  const resp200 = `{
  "status": "success",
  "evaluation_ms": 118,
  "concern": "high_risk",
  "silhouette": "shield_exclamation",
  "intervention": "STOP_AND_VERIFY",
  "synthetic": false,
  "dlt_registry_match": {
    "header": "VM-BESCOM",
    "authorized_entity": "Bangalore Electricity Supply Co",
    "is_spoofed": true,
    "header_registered_entity_id": "110155291000",
    "traffic_gateway_anomaly_score": 0.94
  },
  "reasons": [
    {
      "id": "rsn_dlt_spoofing",
      "tactic": "spoofed_header",
      "detail": "Alpha-header VM-BESCOM sent via unverified foreign transit aggregator"
    },
    {
      "id": "rsn_coercion_cutoff",
      "tactic": "urgency_threat",
      "detail": "Arbitrary power cut-off threats violate KERC electricity supply regulations"
    }
  ],
  "graph_correlations": {
    "syndicate_cluster": "syn_raj_power_utility_burst_08",
    "confidence_score": 0.994,
    "known_victim_incidents_24h": 412
  },
  "request_id": "req_chk_88201fae902b"
}`;

  const resp400 = `{
  "status": "error",
  "error_code": "INVALID_PAYLOAD_ENCODING",
  "message": "Field 'text' must not be empty and must be valid UTF-8 string up to 4000 characters.",
  "request_id": "req_chk_err_400192a"
}`;

  const resp429 = `{
  "status": "error",
  "error_code": "SANDBOX_QUOTA_EXCEEDED",
  "message": "Burst rate limit of 60 requests/minute exceeded for tenant 'org_apex_98214'.",
  "retry_after_seconds": 14,
  "request_id": "req_chk_err_429188f"
}`;

  const activeSnippet = langTab === "curl" ? curlReq : langTab === "ts" ? tsReq : pyReq;
  const activeResp = responseStatus === 200 ? resp200 : responseStatus === 400 ? resp400 : resp429;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full min-h-[calc(100vh-64px)] bg-ground">
      <div className="w-full max-w-[1536px] mx-auto grid grid-cols-1 lg:grid-cols-12 min-h-[calc(100vh-64px)]">

        {/* 1. Left Column: Endpoint Directory Tree */}
        <nav aria-label="API Endpoint Catalog" className="lg:col-span-3 xl:col-span-2 bg-surface border-r border-border-divider/70 p-4 flex flex-col gap-5 overflow-y-auto text-xs">
          <div className="flex flex-col gap-1">
            <span className="font-mono text-[10px] uppercase font-bold tracking-wider text-viz-neutral px-2">
              API Reference
            </span>
            <span className="text-[11px] text-on-surface-variant px-2">OpenAPI 3.1.0 Spec</span>
          </div>

          {/* Section: Universal Check */}
          <div className="flex flex-col gap-1">
            <span className="px-2 font-mono text-[10px] uppercase tracking-wider font-bold text-viz-neutral">
              Universal Check
            </span>
            <button
              onClick={() => setSelectedEndpoint("/v1/check/universal")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/check/universal"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-primary-container text-on-primary font-bold">
                POST
              </span>
              <span className="truncate">/v1/check/universal</span>
            </button>
            <button
              onClick={() => setSelectedEndpoint("/v1/check/{id}")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/check/{id}"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface font-bold">
                GET
              </span>
              <span className="truncate">/v1/check/&#123;id&#125;</span>
            </button>
          </div>

          {/* Section: Guard & Interception */}
          <div className="flex flex-col gap-1">
            <span className="px-2 font-mono text-[10px] uppercase tracking-wider font-bold text-viz-neutral">
              Guard &amp; Intercept
            </span>
            <button
              onClick={() => setSelectedEndpoint("/v1/guard/intent/eval")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/guard/intent/eval"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-primary-container text-on-primary font-bold">
                POST
              </span>
              <span className="truncate">/v1/guard/intent/eval</span>
            </button>
            <button
              onClick={() => setSelectedEndpoint("/v1/guard/collect/verify")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/guard/collect/verify"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-primary-container text-on-primary font-bold">
                POST
              </span>
              <span className="truncate">/v1/guard/collect/verify</span>
            </button>
          </div>

          {/* Section: Threat Graph & Radar */}
          <div className="flex flex-col gap-1">
            <span className="px-2 font-mono text-[10px] uppercase tracking-wider font-bold text-viz-neutral">
              Threat Graph &amp; Radar
            </span>
            <button
              onClick={() => setSelectedEndpoint("/v1/entities/resolve")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/entities/resolve"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface font-bold">
                GET
              </span>
              <span className="truncate">/v1/entities/resolve</span>
            </button>
            <button
              onClick={() => setSelectedEndpoint("/v1/campaigns/active")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/campaigns/active"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface font-bold">
                GET
              </span>
              <span className="truncate">/v1/campaigns/active</span>
            </button>
            <button
              onClick={() => setSelectedEndpoint("/v1/radar/snapshot")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/radar/snapshot"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface font-bold">
                GET
              </span>
              <span className="truncate">/v1/radar/snapshot</span>
            </button>
          </div>

          {/* Section: System & Health */}
          <div className="flex flex-col gap-1">
            <span className="px-2 font-mono text-[10px] uppercase tracking-wider font-bold text-viz-neutral">
              System &amp; Health
            </span>
            <button
              onClick={() => setSelectedEndpoint("/v1/system/health")}
              className={`w-full text-left px-2.5 py-1.5 rounded flex items-center gap-2 transition-colors ${selectedEndpoint === "/v1/system/health"
                  ? "bg-selected-tint font-bold text-primary border-l-2 border-primary"
                  : "text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                }`}
            >
              <span className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface font-bold">
                GET
              </span>
              <span className="truncate">/v1/system/health</span>
            </button>
          </div>
        </nav>

        {/* 2. Middle Column: Endpoint Documentation Spec */}
        <main className="lg:col-span-5 xl:col-span-6 p-6 sm:p-8 flex flex-col gap-8 bg-ground overflow-y-auto">
          {/* Header Title Area */}
          <section className="flex flex-col gap-3">
            <div className="flex items-center gap-3">
              <span className="px-2.5 py-1 rounded bg-primary-container text-on-primary font-mono text-xs font-bold tracking-wide">
                POST
              </span>
              <h1 className="text-xl sm:text-2xl font-bold text-viz-text tracking-tight font-mono">
                {selectedEndpoint}
              </h1>
            </div>
            <h2 className="text-base font-semibold text-primary">
              Universal Telemetry Verification
            </h2>
            <p className="text-sm text-on-surface leading-relaxed">
              Synchronously ingest raw SMS copy, telephony headers, QR link targets, or UPI VPAs to assess behavioral deception patterns, TRAI DLT registry bindings, and synthetic outbreak campaign correlation in under 140ms.
            </p>

            {/* Authorisation Scope Box */}
            <div className="mt-2 p-4 rounded-xl bg-surface-subtle border border-border-divider/70 flex items-start gap-3">
              <Key className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
              <div className="flex flex-col gap-1 text-xs">
                <span className="font-bold text-on-surface">Authorisation Scope Required</span>
                <span className="text-on-surface-variant leading-relaxed">
                  Requests require a valid Bearer token provided in the <code className="font-mono text-[11px] bg-surface px-1 py-0.5 rounded text-primary border border-border-divider">Authorization</code> header with either <code className="font-mono text-[11px] bg-surface px-1 py-0.5 rounded font-semibold text-on-surface border border-border-divider">check:read</code> or <code className="font-mono text-[11px] bg-surface px-1 py-0.5 rounded font-semibold text-on-surface border border-border-divider">write:telemetry</code> capability flags.
                </span>
              </div>
            </div>
          </section>

          {/* Section: Request Headers */}
          <section className="flex flex-col gap-3">
            <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
              <Server className="h-4 w-4 text-primary" />
              <span>Request Headers</span>
            </h3>
            <div className="overflow-x-auto rounded-xl bg-surface border border-border-divider/70 shadow-sm">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-subtle font-mono text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-border-divider">
                  <tr>
                    <th className="px-4 py-2.5 font-bold">Header</th>
                    <th className="px-4 py-2.5 font-bold">Type</th>
                    <th className="px-4 py-2.5 font-bold">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-divider text-on-surface-variant">
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-semibold text-primary">Authorization</td>
                    <td className="px-4 py-2.5">
                      <span className="px-1.5 py-0.5 rounded bg-surface-subtle font-mono text-[10px] font-semibold">string</span>
                      <span className="text-tone-danger-text text-[10px] ml-1 font-bold">*required</span>
                    </td>
                    <td className="px-4 py-2.5">Standard format: <code className="font-mono bg-surface-subtle px-1 rounded text-on-surface">Bearer sk_test_...</code></td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-semibold text-primary">X-Idempotency-Key</td>
                    <td className="px-4 py-2.5">
                      <span className="px-1.5 py-0.5 rounded bg-surface-subtle font-mono text-[10px] font-semibold">string</span>
                      <span className="text-tone-danger-text text-[10px] ml-1 font-bold">*required</span>
                    </td>
                    <td className="px-4 py-2.5">Unique UUIDv4 trace deduplication key. Avoids duplicate processing during upstream network retries.</td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-semibold text-primary">Content-Type</td>
                    <td className="px-4 py-2.5">
                      <span className="px-1.5 py-0.5 rounded bg-surface-subtle font-mono text-[10px] font-semibold">string</span>
                      <span className="text-tone-danger-text text-[10px] ml-1 font-bold">*required</span>
                    </td>
                    <td className="px-4 py-2.5">Must be explicitly set to <code className="font-mono bg-surface-subtle px-1 rounded text-on-surface">application/json</code>.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          {/* Section: Request Body Schema */}
          <section className="flex flex-col gap-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
                <Layers className="h-4 w-4 text-primary" />
                <span>Request Body</span>
              </h3>
              <span className="font-mono text-[10px] bg-surface-subtle px-2 py-0.5 rounded text-on-surface-variant border border-border-divider">
                application/json
              </span>
            </div>

            <div className="flex flex-col gap-2.5 text-xs">
              {/* Parameter 1: channel */}
              <div className="p-4 rounded-xl bg-surface border border-border-divider/70 shadow-sm flex flex-col gap-1.5">
                <div className="flex items-center justify-between font-mono">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-primary">channel</span>
                    <span className="px-1.5 py-0.5 rounded bg-surface-subtle text-on-surface-variant text-[10px] font-semibold">enum&lt;string&gt;</span>
                    <span className="text-tone-danger-text text-[10px] font-bold">*required</span>
                  </div>
                </div>
                <p className="text-on-surface-variant leading-relaxed">
                  The transmission vector through which the deceptive artifact was presented to the target citizen.
                </p>
                <div className="mt-1 flex flex-wrap gap-1.5 font-mono text-[11px]">
                  {["sms", "whatsapp", "telegram", "qr", "upi_prompt", "web"].map((ch) => (
                    <span key={ch} className="px-2 py-0.5 rounded bg-surface-subtle text-on-surface font-medium border border-border-divider/50">
                      &apos;{ch}&apos;
                    </span>
                  ))}
                </div>
              </div>

              {/* Parameter 2: sender_header */}
              <div className="p-4 rounded-xl bg-surface border border-border-divider/70 shadow-sm flex flex-col gap-1.5">
                <div className="flex items-center gap-2 font-mono">
                  <span className="font-bold text-primary">sender_header</span>
                  <span className="px-1.5 py-0.5 rounded bg-surface-subtle text-on-surface-variant text-[10px] font-semibold">string</span>
                  <span className="text-viz-neutral text-[10px]">optional</span>
                </div>
                <p className="text-on-surface-variant leading-relaxed">
                  SMS sender routing prefix or alphanumeric DLT header (e.g., <code className="font-mono bg-surface-subtle px-1 rounded text-on-surface">VM-BESCOM</code>, <code className="font-mono bg-surface-subtle px-1 rounded text-on-surface">CP-SBIINB</code>). Validated real-time against TRAI DLT Telemarketer records.
                </p>
              </div>

              {/* Parameter 3: text */}
              <div className="p-4 rounded-xl bg-surface border border-border-divider/70 shadow-sm flex flex-col gap-1.5">
                <div className="flex items-center gap-2 font-mono">
                  <span className="font-bold text-primary">text</span>
                  <span className="px-1.5 py-0.5 rounded bg-surface-subtle text-on-surface-variant text-[10px] font-semibold">string</span>
                  <span className="text-tone-danger-text text-[10px] font-bold">*required</span>
                </div>
                <p className="text-on-surface-variant leading-relaxed">
                  The verbatim message payload, call transcript excerpt, or landing copy. Supports up to 4,000 characters. Regional Indic scripts (Hindi, Kannada, Tamil, Bengali, Telugu) are fully preserved in UTF-8.
                </p>
              </div>

              {/* Parameter 4: metadata */}
              <div className="p-4 rounded-xl bg-surface border border-border-divider/70 shadow-sm flex flex-col gap-1.5">
                <div className="flex items-center gap-2 font-mono">
                  <span className="font-bold text-primary">metadata</span>
                  <span className="px-1.5 py-0.5 rounded bg-surface-subtle text-on-surface-variant text-[10px] font-semibold">object</span>
                  <span className="text-viz-neutral text-[10px]">optional</span>
                </div>
                <p className="text-on-surface-variant leading-relaxed">
                  Diagnostic context such as <code className="font-mono text-on-surface">circle</code> (e.g., &apos;KA&apos;, &apos;DL&apos;), ISO timestamp, and <code className="font-mono text-on-surface">recipient_category</code>.
                </p>
              </div>
            </div>
          </section>

          {/* Section: Canonical Response Contract (7-State Ladder) */}
          <section className="flex flex-col gap-3">
            <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary" />
              <span>Canonical 7-State Response Contract (§3.3)</span>
            </h3>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              In compliance with the Sovereign Trust Grammar of Absolute Truth, missing evidence is never marked safe. Responses conform to an unequivocal 7-state silhouette ladder:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-tone-info-bg text-tone-info-text flex items-center gap-2 border border-tone-info-text/20">
                <CircleDot className="h-4 w-4 text-tone-info-text flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">1: no_strong_warning_signs</span>
                  <span className="text-[10px] opacity-80">Circle silhouette · No checkmarks</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-surface-subtle text-on-surface flex items-center gap-2 border border-border-divider">
                <HelpCircle className="h-4 w-4 text-viz-neutral flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">2/3: insufficient_evidence</span>
                  <span className="text-[10px] text-on-surface-variant">Degraded or incomplete trace</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-tone-warning-bg text-tone-warning-text flex items-center gap-2 border border-tone-warning-text/20">
                <AlertTriangle className="h-4 w-4 text-tone-warning-text flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">4: be_careful</span>
                  <span className="text-[10px] opacity-80">Triangle outline · Ambiguous signal</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-tone-warning-strong-bg text-tone-warning-strong-text flex items-center gap-2 border border-tone-warning-strong-text/20">
                <AlertTriangle className="h-4 w-4 text-tone-warning-strong-text flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">5: suspicious</span>
                  <span className="text-[10px] opacity-80">Filled triangle · High anomaly</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-tone-danger-bg text-tone-danger-text flex items-center gap-2 border border-tone-danger-text/20">
                <ShieldAlert className="h-4 w-4 text-tone-danger-text flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">6: high_risk</span>
                  <span className="text-[10px] opacity-80">Shield icon · Proven fraud patterns</span>
                </div>
              </div>

              <div className="p-2.5 rounded-lg bg-tone-danger-strong-bg text-tone-danger-strong-text flex items-center gap-2 border border-tone-danger-strong-text/20">
                <Octagon className="h-4 w-4 text-tone-danger-strong-text flex-shrink-0" />
                <div className="flex flex-col">
                  <span className="font-bold">7: act_now</span>
                  <span className="text-[10px] opacity-80">Octagon · Imminent financial threat</span>
                </div>
              </div>
            </div>
          </section>

          {/* Section: HTTP Error Codes */}
          <section className="flex flex-col gap-3 mb-6">
            <h3 className="text-sm font-bold text-on-surface flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-tone-danger-text" />
              <span>HTTP Canonical Error Codes</span>
            </h3>
            <div className="overflow-x-auto rounded-xl bg-surface border border-border-divider/70 shadow-sm">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-subtle font-mono text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-border-divider">
                  <tr>
                    <th className="px-4 py-2.5 font-bold">Status</th>
                    <th className="px-4 py-2.5 font-bold">Error Code &amp; Semantics</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-divider text-on-surface-variant">
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-bold text-tone-danger-text">400</td>
                    <td className="px-4 py-2.5">
                      <div className="font-mono font-bold text-on-surface">INVALID_PAYLOAD_ENCODING</div>
                      <div className="text-[11px] text-on-surface-variant">Malformed JSON or non-UTF-8 character stream in raw body.</div>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-bold text-tone-danger-text">401</td>
                    <td className="px-4 py-2.5">
                      <div className="font-mono font-bold text-on-surface">MISSING_OR_REVOKED_TOKEN</div>
                      <div className="text-[11px] text-on-surface-variant">Token expired, invalid, revoked, or insufficient org capabilities.</div>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-bold text-tone-danger-text">422</td>
                    <td className="px-4 py-2.5">
                      <div className="font-mono font-bold text-on-surface">UNSUPPORTED_MEDIA_TYPE</div>
                      <div className="text-[11px] text-on-surface-variant">Channel vector does not conform to system accepted transmission taxonomy.</div>
                    </td>
                  </tr>
                  <tr>
                    <td className="px-4 py-2.5 font-mono font-bold text-tone-danger-text">429</td>
                    <td className="px-4 py-2.5">
                      <div className="font-mono font-bold text-on-surface">SANDBOX_QUOTA_EXCEEDED</div>
                      <div className="text-[11px] text-on-surface-variant">Standard burst threshold of 60 req/min exceeded. Upgrade org tier to raise ceiling.</div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </main>

        {/* 3. Right Column: Request Specimen & Interactive Response Explorer */}
        <aside aria-label="Interactive Request & Response Workbench" className="lg:col-span-4 xl:col-span-4 p-5 lg:p-6 flex flex-col gap-5 bg-surface border-l border-border-divider/70 sticky top-16 h-[calc(100vh-64px)] overflow-y-auto">
          {/* Top Request Specimen Header */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider font-bold text-on-surface-variant">
                Request Payload Specimen
              </span>
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 font-mono text-[11px] text-primary hover:underline font-bold transition-colors"
              >
                {copied ? (
                  <>
                    <Check className="h-3 w-3 text-viz-primary" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <Copy className="h-3 w-3 text-viz-neutral" />
                    <span>Copy Snippet</span>
                  </>
                )}
              </button>
            </div>

            {/* Language Selector */}
            <div className="flex items-center gap-1 bg-surface-subtle p-1 rounded-lg border border-border-divider/60 text-xs">
              <button
                onClick={() => setLangTab("curl")}
                className={`px-3 py-1 rounded font-medium transition-colors ${langTab === "curl" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                cURL
              </button>
              <button
                onClick={() => setLangTab("ts")}
                className={`px-3 py-1 rounded font-medium transition-colors ${langTab === "ts" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                TypeScript
              </button>
              <button
                onClick={() => setLangTab("py")}
                className={`px-3 py-1 rounded font-medium transition-colors ${langTab === "py" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                Python
              </button>
            </div>
          </div>

          {/* Request Code Block */}
          <div className="bg-inverse-surface rounded-xl p-4 text-inverse-on-surface font-mono text-xs overflow-x-auto shadow-md">
            <pre className="leading-relaxed"><code>{activeSnippet}</code></pre>
          </div>

          {/* Response Explorer Panel */}
          <div className="flex flex-col gap-2.5 pt-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[10px] uppercase tracking-wider font-bold text-on-surface-variant">
                Response Explorer
              </span>
              <Link
                href="/developers/sandbox"
                className="text-xs text-primary hover:underline font-semibold flex items-center gap-1"
              >
                <span>Open in Sandbox</span>
                <ArrowRight className="h-3 w-3" />
              </Link>
            </div>

            {/* Status Switcher Tabs */}
            <div className="flex items-center gap-1.5 text-xs">
              <button
                onClick={() => setResponseStatus(200)}
                className={`px-2.5 py-1 rounded-md font-mono text-[11px] font-bold flex items-center gap-1.5 transition-colors ${responseStatus === 200
                    ? "bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/30"
                    : "bg-surface-subtle text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                <span className="w-2 h-2 rounded-full bg-viz-primary" />
                <span>200 OK (118ms)</span>
              </button>
              <button
                onClick={() => setResponseStatus(400)}
                className={`px-2.5 py-1 rounded-md font-mono text-[11px] font-medium transition-colors ${responseStatus === 400
                    ? "bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/30"
                    : "bg-surface-subtle text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                400 Bad Request
              </button>
              <button
                onClick={() => setResponseStatus(429)}
                className={`px-2.5 py-1 rounded-md font-mono text-[11px] font-medium transition-colors ${responseStatus === 429
                    ? "bg-tone-danger-bg text-tone-danger-text border border-tone-danger-text/30"
                    : "bg-surface-subtle text-on-surface-variant hover:text-on-surface"
                  }`}
              >
                429 Rate Limit
              </button>
            </div>

            {/* Silhouette Ladder Output Badge for 200 OK */}
            {responseStatus === 200 && (
              <div className="p-3 rounded-xl bg-tone-danger-bg text-tone-danger-text flex items-center justify-between border border-tone-danger-text/20">
                <div className="flex items-center gap-2.5">
                  <ShieldAlert className="h-5 w-5 text-tone-danger-text flex-shrink-0" />
                  <div className="flex flex-col text-xs">
                    <span className="font-bold">HIGH_RISK · State 6 / 7</span>
                    <span className="text-[11px]">Intervention: <strong className="underline">STOP_AND_VERIFY</strong></span>
                  </div>
                </div>
                <span className="text-xs px-2 py-0.5 rounded bg-surface font-mono font-bold text-tone-danger-text border border-border-divider">
                  p = 0.994
                </span>
              </div>
            )}

            {/* JSON Response Code Box */}
            <div className="bg-inverse-surface rounded-xl p-4 text-inverse-on-surface font-mono text-xs overflow-x-auto shadow-md">
              <pre className="leading-relaxed"><code>{activeResp}</code></pre>
            </div>
          </div>
        </aside>

      </div>
    </div>
  );
}
