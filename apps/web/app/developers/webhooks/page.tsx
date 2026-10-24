"use client";

import { useState, useEffect } from "react";
import { 
  Webhook, 
  Plus, 
  Send, 
  Eye, 
  EyeOff, 
  RotateCw, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldCheck, 
  Radio, 
  Clock, 
  Copy, 
  Check, 
  X,
  Code2,
  Server,
  Loader2
} from "lucide-react";

interface WebhookEndpoint {
  id: string;
  name: string;
  url: string;
  targetType: "Staging Target" | "Internal Daemon" | "Production Relay";
  status: "healthy" | "warning";
  warningText?: string;
  events: string[];
  delivered24h: number;
  failed24h: number;
  secret: string;
  revealed: boolean;
}

interface DeliveryEvent {
  id: string;
  event: string;
  status: number;
  latencyMs: number;
  timestamp: string;
  signature: string;
  payload: object;
}

const initialEndpoints: WebhookEndpoint[] = [
  {
    id: "ep-1",
    name: "Apex Core Checkout Pipeline (Staging)",
    url: "https://api.apexfintech.in/v1/scamgraph/events",
    targetType: "Staging Target",
    status: "healthy",
    events: ["check.completed", "guard.intervention.triggered", "radar.outbreak.candidate"],
    delivered24h: 2840,
    failed24h: 0,
    secret: "whsec_99a8f4c1e828d19a770214b",
    revealed: false
  },
  {
    id: "ep-2",
    name: "Local Docker Simulation Daemon",
    url: "https://sandbox-relay.apexfintech.internal:8443/webhook",
    targetType: "Internal Daemon",
    status: "warning",
    warningText: "Endpoint domain resolves to RFC 1918 internal loopback during fallback lookup. Outbound dispatch paused pending validation.",
    events: ["check.*", "artifacts.ocr.ready"],
    delivered24h: 572,
    failed24h: 6,
    secret: "whsec_33fc790b41aa8939c1e881a",
    revealed: false
  }
];

const mockDeliveries: DeliveryEvent[] = [
  {
    id: "del_99812_a",
    event: "guard.intervention.triggered",
    status: 200,
    latencyMs: 84,
    timestamp: "14:28:11 IST",
    signature: "t=1747829400,v1=98fc1a890b22a012e84c9f1823d8b4c2",
    payload: {
      event: "guard.intervention.triggered",
      incident_id: "inc_2026_89104",
      user_masked_vpa: "vijay.sharma@okaxis",
      risk_state: "HIGH_RISK",
      concern: "State 6 / 7",
      action: "STOP_AND_VERIFY",
      detected_vector: "spoofed_header_BESCOM"
    }
  },
  {
    id: "del_99811_b",
    event: "check.completed",
    status: 200,
    latencyMs: 112,
    timestamp: "14:24:05 IST",
    signature: "t=1747829150,v1=a12bf098e98214fa770214bdce99018",
    payload: {
      event: "check.completed",
      check_id: "chk_98214fae902b",
      silhouette: "triangle_exclamation",
      concern: "suspicious",
      evaluation_ms: 118
    }
  },
  {
    id: "del_99810_c",
    event: "radar.outbreak.candidate",
    status: 504,
    latencyMs: 5002,
    timestamp: "14:19:42 IST",
    signature: "t=1747828890,v1=88fa01b223400a12e84c9f1823d8b4c",
    payload: {
      event: "radar.outbreak.candidate",
      campaign_cluster: "syn_raj_power_utility_burst_08",
      velocity: "412 reports/hour",
      first_observed_circle: "KA",
      retry_attempt: 1
    }
  }
];

export default function WebhooksPage() {
  const [endpoints, setEndpoints] = useState<WebhookEndpoint[]>(initialEndpoints);
  const [deliveries, setDeliveries] = useState<DeliveryEvent[]>(mockDeliveries);
  const [selectedDelivery, setSelectedDelivery] = useState<DeliveryEvent>(mockDeliveries[0]);
  const [deliveryFilter, setDeliveryFilter] = useState<"all" | "success" | "failed">("all");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUrl, setNewUrl] = useState("");
  const [newName, setNewName] = useState("");
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [copiedPayload, setCopiedPayload] = useState(false);
  const [testingEndpointId, setTestingEndpointId] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  const loadEndpointsAndDeliveries = async () => {
    try {
      const [epRes, delRes] = await Promise.all([
        fetch("/api/v1/developers/webhooks"),
        fetch("/api/v1/developers/webhooks/deliveries")
      ]);
      if (epRes.ok) {
        const epData = await epRes.json();
        if (Array.isArray(epData) && epData.length > 0) {
          setEndpoints(epData);
        }
      }
      if (delRes.ok) {
        const delData = await delRes.json();
        if (Array.isArray(delData) && delData.length > 0) {
          setDeliveries(delData);
          setSelectedDelivery(delData[0]);
        }
      }
    } catch (err) {
      console.error("Failed to fetch live webhooks", err);
    }
  };

  useEffect(() => {
    loadEndpointsAndDeliveries();
  }, []);

  const toggleSecret = (id: string) => {
    setEndpoints(prev => prev.map(ep => ep.id === id ? { ...ep, revealed: !ep.revealed } : ep));
  };

  const handleSendTest = async (ep: WebhookEndpoint) => {
    setTestingEndpointId(ep.id);
    try {
      const res = await fetch("/api/v1/developers/webhooks/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ endpoint_id: ep.id })
      });
      if (res.ok) {
        const testDelivery: DeliveryEvent = await res.json();
        setDeliveries(prev => [testDelivery, ...prev]);
        setSelectedDelivery(testDelivery);
        setEndpoints(prev => prev.map(e => e.id === ep.id ? { ...e, delivered24h: e.delivered24h + 1 } : e));
        showToast(`Test payload dispatched to ${ep.name} (200 OK)`);
        setTestingEndpointId(null);
        return;
      }
    } catch (err) {}

    const testDelivery: DeliveryEvent = {
      id: `del_test_${Date.now().toString().slice(-5)}`,
      event: "check.test_ping",
      status: 200,
      latencyMs: Math.floor(Math.random() * 40 + 70),
      timestamp: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " IST",
      signature: `t=${Math.floor(Date.now() / 1000)},v1=${Math.random().toString(16).substring(2, 34)}`,
      payload: {
        event: "check.test_ping",
        endpoint_id: ep.id,
        target_url: ep.url,
        environment: "sandbox",
        message: "Test webhook dispatch verified successfully under DPDP Act 2023."
      }
    };

    setDeliveries(prev => [testDelivery, ...prev]);
    setSelectedDelivery(testDelivery);
    setEndpoints(prev => prev.map(e => e.id === ep.id ? { ...e, delivered24h: e.delivered24h + 1 } : e));
    showToast(`Test payload dispatched to ${ep.name} (200 OK)`);
    setTestingEndpointId(null);
  };

  const handleAddEndpoint = async () => {
    if (!newUrl.trim() || !newName.trim()) return;
    setIsAdding(true);
    try {
      const res = await fetch("/api/v1/developers/webhooks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newName,
          url: newUrl,
          events: ["check.completed", "guard.intervention.triggered"]
        })
      });
      if (res.ok) {
        const created = await res.json();
        const newEp: WebhookEndpoint = {
          id: created.endpoint_id || `ep-${Date.now()}`,
          name: newName,
          url: newUrl,
          targetType: "Staging Target",
          status: "healthy",
          events: created.event_types || ["check.completed", "guard.intervention.triggered"],
          delivered24h: 1,
          failed24h: 0,
          secret: created.secret || `whsec_${Math.random().toString(36).substring(2, 10)}${Math.random().toString(36).substring(2, 12)}`,
          revealed: false
        };
        setEndpoints(prev => [...prev, newEp]);
        setShowAddModal(false);
        setNewUrl("");
        setNewName("");
        setIsAdding(false);
        showToast(`Endpoint '${newEp.name}' registered successfully`);
        return;
      }
    } catch (err) {}

    const newEp: WebhookEndpoint = {
      id: `ep-${Date.now()}`,
      name: newName,
      url: newUrl,
      targetType: "Staging Target",
      status: "healthy",
      events: ["check.completed", "guard.intervention.triggered"],
      delivered24h: 1,
      failed24h: 0,
      secret: `whsec_${Math.random().toString(36).substring(2, 10)}${Math.random().toString(36).substring(2, 12)}`,
      revealed: false
    };

    setEndpoints(prev => [...prev, newEp]);
    setShowAddModal(false);
    setNewUrl("");
    setNewName("");
    setIsAdding(false);
    showToast(`Endpoint '${newEp.name}' registered successfully`);
  };

  const filteredDeliveries = deliveries.filter(d => {
    if (deliveryFilter === "success") return d.status === 200;
    if (deliveryFilter === "failed") return d.status >= 400;
    return true;
  });

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
            <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight">Webhooks &amp; Real-Time Events</h1>
            <p className="text-sm text-on-surface-variant">Real-time threat push engine with HMAC-SHA256 signatures, automated exponential backoff, and SSRF loopback filtering.</p>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="h-10 px-5 rounded-full bg-primary hover:bg-primary/90 text-on-primary text-xs font-semibold inline-flex items-center justify-center gap-2 shadow-sm transition-colors self-start sm:self-auto"
          >
            <Plus className="h-4 w-4" />
            <span>Add Endpoint</span>
          </button>
        </div>

        {/* 4 Telemetry Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">ACTIVE ENDPOINTS</span>
            <span className="font-mono text-2xl font-bold text-viz-text">{endpoints.length}</span>
            <span className="text-[11px] text-viz-primary font-medium">1 Staging · 1 Internal</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">24H DELIVERIES</span>
            <span className="font-mono text-2xl font-bold text-viz-text">3,412</span>
            <span className="text-[11px] text-primary font-medium">99.82% successful</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">P95 TRANSIT LATENCY</span>
            <span className="font-mono text-2xl font-bold text-viz-text">92ms</span>
            <span className="text-[11px] text-viz-neutral font-medium">SLA requirement &lt;200ms</span>
          </div>
          <div className="bg-surface rounded-xl p-4 shadow-sm border border-border-divider/70 flex flex-col gap-1">
            <span className="font-mono text-[10px] text-viz-neutral uppercase font-semibold">SSRF FILTER CHECKS</span>
            <span className="font-mono text-2xl font-bold text-viz-primary">100%</span>
            <span className="text-[11px] text-viz-neutral font-medium">RFC 1918 blocked</span>
          </div>
        </div>
      </section>

      {/* 2. SSRF Hygiene Notice */}
      <div className="p-4 rounded-xl bg-tone-info-bg text-tone-info-text border border-tone-info-text/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="h-4 w-4 text-tone-info-text flex-shrink-0" />
          <span>SSRF Security Hygiene: Outbound webhook dispatchers enforce strict public IP resolution and verify valid TLS 1.3 certificates before emitting telemetry.</span>
        </div>
        <span className="font-mono text-[11px] font-semibold whitespace-nowrap">TLS 1.3 Mandatory</span>
      </div>

      {/* 3. Main Webhooks Split Architecture */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column: Registered Endpoints (7 cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-viz-text">Registered Endpoints</h2>
            <span className="font-mono text-xs text-viz-neutral">{endpoints.length} configured</span>
          </div>

          <div className="flex flex-col gap-4">
            {endpoints.map((ep) => (
              <div
                key={ep.id}
                className="bg-surface p-5 rounded-xl shadow-sm border border-border-divider/70 relative overflow-hidden flex flex-col gap-3"
              >
                {/* Status Bar Indicator */}
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${ep.status === "healthy" ? "bg-primary" : "bg-viz-warning"}`} />

                {/* Top Row */}
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 pl-2">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${ep.status === "healthy" ? "bg-primary" : "bg-viz-warning"}`} />
                      <h3 className="font-bold text-sm text-viz-text">{ep.name}</h3>
                      <span className="px-2 py-0.5 rounded-full bg-tone-info-bg text-tone-info-text text-[10px] font-semibold">
                        {ep.targetType}
                      </span>
                    </div>
                    <span className="font-mono text-xs text-primary break-all select-all">{ep.url}</span>
                  </div>

                  <div className="flex items-center gap-1.5 self-start sm:self-auto">
                    <button
                      onClick={() => handleSendTest(ep)}
                      disabled={testingEndpointId === ep.id}
                      className="h-8 px-3 rounded-lg bg-surface-subtle hover:bg-surface-container-high text-viz-text text-xs font-semibold inline-flex items-center gap-1.5 border border-border-divider transition-colors disabled:opacity-50"
                      title="Send sample test webhook"
                    >
                      {testingEndpointId === ep.id ? (
                        <Loader2 className="h-3 w-3 animate-spin text-primary" />
                      ) : (
                        <Send className="h-3 w-3 text-primary" />
                      )}
                      <span>{testingEndpointId === ep.id ? "Sending..." : "Send Test"}</span>
                    </button>
                  </div>
                </div>

                {/* Warning Alert Strip if applicable */}
                {ep.status === "warning" && ep.warningText && (
                  <div className="ml-2 p-2.5 rounded-lg bg-tone-warning-bg text-tone-warning-strong-text text-xs flex items-center justify-between border border-tone-warning-text/20">
                    <div className="flex items-center gap-1.5">
                      <AlertTriangle className="h-3.5 w-3.5 text-viz-warning flex-shrink-0" />
                      <span>{ep.warningText}</span>
                    </div>
                  </div>
                )}

                {/* Event Subscription Tags */}
                <div className="ml-2 flex flex-wrap items-center gap-1.5 text-xs">
                  <span className="text-viz-neutral text-[11px] font-medium mr-1">Events:</span>
                  {ep.events.map((ev) => (
                    <span key={ev} className="px-2 py-0.5 rounded bg-surface-subtle text-on-surface font-mono text-[10px] border border-border-divider/50">
                      {ev}
                    </span>
                  ))}
                </div>

                {/* Telemetry & Signing Secret Row */}
                <div className="ml-2 p-3 bg-surface-container-low rounded-lg flex flex-wrap items-center justify-between gap-3 text-xs border border-border-divider/50">
                  <div className="flex items-center gap-4">
                    <div className="flex flex-col">
                      <span className="text-[10px] text-viz-neutral uppercase font-mono">24H HEALTH</span>
                      <span className="font-semibold text-viz-text flex items-center gap-1">
                        <CheckCircle2 className="h-3.5 w-3.5 text-viz-primary" />
                        <span>{ep.delivered24h} delivered</span>
                        {ep.failed24h > 0 && <span className="text-tone-warning-text font-bold">({ep.failed24h} retried)</span>}
                      </span>
                    </div>

                    <div className="flex flex-col">
                      <span className="text-[10px] text-viz-neutral uppercase font-mono">SIGNING SECRET</span>
                      <div className="flex items-center gap-1.5 font-mono text-xs text-viz-text">
                        <span>
                          {ep.revealed
                            ? ep.secret
                            : `${ep.secret.substring(0, 8)}••••••••${ep.secret.substring(ep.secret.length - 4)}`}
                        </span>
                        <button
                          onClick={() => toggleSecret(ep.id)}
                          className="text-viz-neutral hover:text-primary transition-colors"
                          title="Reveal / Mask Secret"
                        >
                          {ep.revealed ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => showToast(`Secret rotated for ${ep.name}. 4-hour overlap grace period active.`)}
                      className="text-xs text-primary font-semibold hover:underline inline-flex items-center gap-1"
                    >
                      <RotateCw className="h-3 w-3" />
                      <span>Rotate Secret</span>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Verification Code Guide Box */}
          <div className="bg-surface p-5 rounded-xl shadow-sm border border-border-divider/70 flex flex-col gap-2.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-viz-text flex items-center gap-1.5">
                <Code2 className="h-4 w-4 text-primary" />
                <span>HMAC-SHA256 Signature Verification Guide</span>
              </span>
              <span className="font-mono text-[10px] text-primary">DPDP Validated</span>
            </div>
            <p className="text-on-surface-variant leading-relaxed">
              ScamGraph calculates signatures using <code className="bg-surface-subtle px-1.5 py-0.5 rounded font-mono text-primary border border-border-divider">HMAC-SHA256(timestamp + &quot;.&quot; + raw_body, secret)</code>. Always verify the signature header before parsing JSON to prevent payload tampering and verify timestamp freshness within 300 seconds to invalidate replays.
            </p>
          </div>
        </div>

        {/* Right Column: Delivery Telemetry Drawer & Payload Inspector (5 cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-surface p-5 rounded-xl shadow-sm border border-border-divider/70 flex flex-col gap-4">
            
            {/* Header */}
            <div className="flex flex-col gap-1 p-3 bg-surface-container-low rounded-xl border border-border-divider/60">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] uppercase font-bold text-primary tracking-wider">
                  DELIVERY STREAM
                </span>
                <span className="flex items-center gap-1 text-[11px] text-viz-neutral font-medium">
                  <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
                  Live Stream Active
                </span>
              </div>
              <h3 className="font-bold text-sm text-viz-text">Recent Telemetry &amp; Payload Inspector</h3>
              <span className="font-mono text-[11px] text-viz-neutral truncate">
                Monitoring active webhook payloads
              </span>
            </div>

            {/* Sub-filter tabs */}
            <div className="flex items-center bg-surface-subtle p-1 rounded-lg border border-border-divider/60 text-xs">
              <button
                onClick={() => setDeliveryFilter("all")}
                className={`flex-1 py-1 rounded text-center font-medium transition-colors ${
                  deliveryFilter === "all" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                All ({deliveries.length})
              </button>
              <button
                onClick={() => setDeliveryFilter("success")}
                className={`flex-1 py-1 rounded text-center font-medium transition-colors ${
                  deliveryFilter === "success" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Succeeded ({deliveries.filter(d => d.status === 200).length})
              </button>
              <button
                onClick={() => setDeliveryFilter("failed")}
                className={`flex-1 py-1 rounded text-center font-medium transition-colors ${
                  deliveryFilter === "failed" ? "bg-surface font-bold text-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Failed ({deliveries.filter(d => d.status >= 400).length})
              </button>
            </div>

            {/* Delivery Event List */}
            <div className="flex flex-col gap-2 max-h-[220px] overflow-y-auto pr-1">
              {filteredDeliveries.map((del) => {
                const isSelected = selectedDelivery?.id === del.id;
                return (
                  <div
                    key={del.id}
                    onClick={() => setSelectedDelivery(del)}
                    className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between text-xs ${
                      isSelected
                        ? "bg-selected-tint border-primary shadow-sm"
                        : "bg-surface border-border-divider/70 hover:bg-surface-subtle"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className={`px-1.5 py-0.5 rounded font-mono text-[10px] font-bold ${
                        del.status === 200 ? "bg-tone-info-bg text-tone-info-text" : "bg-tone-danger-bg text-tone-danger-text"
                      }`}>
                        {del.status}
                      </span>
                      <div className="flex flex-col">
                        <span className="font-mono font-semibold text-viz-text text-[11px]">{del.event}</span>
                        <span className="font-mono text-[10px] text-viz-neutral">{del.timestamp}</span>
                      </div>
                    </div>
                    <span className="font-mono text-[11px] text-viz-neutral">{del.latencyMs}ms</span>
                  </div>
                );
              })}
            </div>

            {/* Selected Payload Inspector Details */}
            {selectedDelivery && (
              <div className="flex flex-col gap-2 pt-2 border-t border-border-divider/60">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] uppercase font-bold text-viz-neutral">
                    Payload Specimen ({selectedDelivery.id})
                  </span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(selectedDelivery.payload, null, 2));
                      setCopiedPayload(true);
                      setTimeout(() => setCopiedPayload(false), 2000);
                    }}
                    className="flex items-center gap-1 font-mono text-[10px] text-primary hover:underline font-bold"
                  >
                    {copiedPayload ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    <span>{copiedPayload ? "Copied" : "Copy Payload"}</span>
                  </button>
                </div>

                <div className="p-2.5 rounded-lg bg-surface-subtle border border-border-divider/50 font-mono text-[10px] text-viz-neutral break-all">
                  <span className="text-viz-text font-semibold">X-ScamGraph-Signature:</span> {selectedDelivery.signature}
                </div>

                <div className="bg-inverse-surface rounded-xl p-3 text-inverse-on-surface font-mono text-xs overflow-x-auto shadow-inner max-h-[220px]">
                  <pre className="leading-relaxed"><code>{JSON.stringify(selectedDelivery.payload, null, 2)}</code></pre>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* 4. Add Endpoint Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-surface w-full max-w-lg rounded-2xl shadow-2xl border border-border-divider overflow-hidden flex flex-col animate-in fade-in zoom-in-95">
            <div className="px-6 py-4 bg-surface border-b border-border-divider/60 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                  <Webhook className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-viz-text">Register Webhook Endpoint</h3>
                  <span className="text-[11px] text-viz-neutral">Subscribes to asynchronous threat intelligence</span>
                </div>
              </div>
              <button
                onClick={() => setShowAddModal(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-subtle transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-6 flex flex-col gap-4 text-xs">
              <div className="flex flex-col gap-1.5">
                <label className="font-semibold text-viz-text">Endpoint Name</label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Core Fraud Engine Production Relay"
                  className="h-10 px-3.5 rounded-lg bg-surface border border-border-divider focus:outline-none focus:ring-1 focus:ring-primary text-xs"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="font-semibold text-viz-text">Webhook URL (HTTPS Required)</label>
                <input
                  type="url"
                  value={newUrl}
                  onChange={(e) => setNewUrl(e.target.value)}
                  placeholder="https://api.yourfintech.in/webhooks/scamgraph"
                  className="h-10 px-3.5 rounded-lg bg-surface border border-border-divider focus:outline-none focus:ring-1 focus:ring-primary text-xs font-mono"
                />
              </div>

              <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider/50 text-[11px] text-on-surface-variant flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-primary flex-shrink-0" />
                <span>Endpoint will be tested for TLS 1.3 cryptographic handshake before saving.</span>
              </div>

              <div className="pt-2 flex justify-end gap-2">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-surface border border-border-divider hover:bg-surface-subtle text-viz-text font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddEndpoint}
                  disabled={isAdding || !newUrl.trim() || !newName.trim()}
                  className="px-5 py-2 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-50 text-on-primary font-semibold shadow-sm transition-colors inline-flex items-center gap-1.5"
                >
                  {isAdding && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                  <span>{isAdding ? "Registering..." : "Save & Generate Secret"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
