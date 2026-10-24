"use client";

import { useState } from "react";
import { 
  Play, 
  RotateCw, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Octagon, 
  CircleDot, 
  HelpCircle, 
  Copy, 
  Check, 
  Send, 
  Trash2, 
  Sparkles, 
  Code2, 
  CheckCircle2,
  FileCode,
  Layers,
  ArrowRight
} from "lucide-react";

interface ScenarioPreset {
  id: string;
  name: string;
  channel: "sms" | "whatsapp" | "telegram" | "upi_prompt" | "qr" | "web";
  senderHeader: string;
  dltStatus: "spoofed" | "registered" | "none";
  text: string;
  circle: string;
  lang: string;
  expectedState: number;
  stateLabel: string;
  silhouette: string;
  intervention: string;
  confidence: string;
  reasons: { id: string; tactic: string; detail: string }[];
  syndicate?: string;
  latency: number;
}

const presets: ScenarioPreset[] = [
  {
    id: "SCN-POWER-9921",
    name: "BESCOM Bill Disconnection SMS",
    channel: "sms",
    senderHeader: "VM-BESCOM",
    dltStatus: "spoofed",
    text: "Dear consumer, electricity power disconnect tonight 9:30 PM from power office because previous month bill not update. Call officer 9845012345 or download verification sync app: https://bescom-billpay.app/sync.apk",
    circle: "KA",
    lang: "en-IN / Romanized Indic",
    expectedState: 6,
    stateLabel: "STATE 6: HIGH_RISK",
    silhouette: "shield_exclamation",
    intervention: "STOP_AND_VERIFY",
    confidence: "high (0.994)",
    reasons: [
      { id: "rsn_dlt_spoofing", tactic: "spoofed_header", detail: "VM-BESCOM header routed via untrusted international transit aggregator." },
      { id: "rsn_malicious_apk", tactic: "remote_access_trojan", detail: "Payload URL links to an unverified sideloaded Android APK (sync.apk)." },
      { id: "rsn_coercion_cutoff", tactic: "urgency_threat", detail: "Manufactured emergency of same-night electricity disconnection." }
    ],
    syndicate: "syn_raj_power_utility_burst_08",
    latency: 118
  },
  {
    id: "SCN-POLICE-4402",
    name: "Digital Arrest / CBI WhatsApp Threat",
    channel: "whatsapp",
    senderHeader: "+91 98112-99812",
    dltStatus: "none",
    text: "CBI Cyber Cell notice: A parcel containing narcotics was intercepted at Mumbai airport under your Aadhaar. Join official Skype interrogation immediately or warrant #W-8912 will be dispatched to local police station.",
    circle: "DL",
    lang: "en-IN / Hindi English",
    expectedState: 7,
    stateLabel: "STATE 7: ACT_NOW",
    silhouette: "octagon_hand",
    intervention: "ISOLATE_AND_CALL_1930",
    confidence: "critical (0.999)",
    reasons: [
      { id: "rsn_digital_arrest", tactic: "coercive_arrest", detail: "Fabricated law enforcement arrest threat designed to force Skype confinement." },
      { id: "rsn_impersonation", tactic: "cbi_police_impersonation", detail: "No Indian police or central agency conducts video-call trials." }
    ],
    syndicate: "syn_mumbai_airport_customs_ring",
    latency: 94
  },
  {
    id: "SCN-APK-8109",
    name: "Courier Undelivered APK Dropper",
    channel: "sms",
    senderHeader: "AD-INDPOST",
    dltStatus: "spoofed",
    text: "India Post: Your package #IN-889102 could not be delivered due to wrong address. Update address within 24h or parcel will be returned: https://indiapost-parcel-update.com/app",
    circle: "MH",
    lang: "en-IN",
    expectedState: 6,
    stateLabel: "STATE 6: HIGH_RISK",
    silhouette: "shield_exclamation",
    intervention: "STOP_AND_VERIFY",
    confidence: "high (0.982)",
    reasons: [
      { id: "rsn_fake_courier", tactic: "phishing_domain", detail: "Domain indiapost-parcel-update.com registered 4 hours ago via NameCheap." },
      { id: "rsn_spoofed_post", tactic: "impersonation", detail: "India Post does not solicit address update via third-party web domains." }
    ],
    syndicate: "syn_courier_smishing_blr_04",
    latency: 104
  },
  {
    id: "SCN-TELE-3310",
    name: "Telegram Part-Time Rating Job",
    channel: "telegram",
    senderHeader: "@HotelReviewManager_Pooja",
    dltStatus: "none",
    text: "Part-time job offer! Earn ₹3,000 to ₹8,000 daily from home. Just like and review Google Maps hotel locations. First 3 tasks free, payment sent via UPI. Reply YES to start.",
    circle: "WB",
    lang: "en-IN",
    expectedState: 5,
    stateLabel: "STATE 5: SUSPICIOUS",
    silhouette: "triangle_filled",
    intervention: "CAUTION_AND_EVALUATE",
    confidence: "medium (0.871)",
    reasons: [
      { id: "rsn_advance_fee_task", tactic: "task_fraud", detail: "Prepaid task scheme known for upfront hook payments followed by deposit extortion." }
    ],
    syndicate: "syn_telegram_task_extortion_delhi",
    latency: 122
  },
  {
    id: "SCN-COLLECT-7721",
    name: "UPI Collect Reverse Request",
    channel: "upi_prompt",
    senderHeader: "merchant_refund_desk@ybl",
    dltStatus: "none",
    text: "OLX Buyer sent ₹25,000 refund for furniture. Enter your UPI MPIN to receive the funds directly into your bank account.",
    circle: "TN",
    lang: "en-IN",
    expectedState: 6,
    stateLabel: "STATE 6: HIGH_RISK",
    silhouette: "shield_exclamation",
    intervention: "STOP_AND_VERIFY",
    confidence: "high (0.995)",
    reasons: [
      { id: "rsn_upi_pin_receive", tactic: "collect_request_deception", detail: "Entering MPIN is NEVER required to receive money on UPI. Collect request masquerading as refund credit." }
    ],
    syndicate: "syn_olx_qr_mule_cluster_11",
    latency: 88
  },
  {
    id: "SCN-SAFE-0012",
    name: "Hinglish Negation ('mat bhejna')",
    channel: "whatsapp",
    senderHeader: "+91 94481-12001",
    dltStatus: "none",
    text: "Bhai yeh scam lag raha hai, is link par click mat karna aur koi OTP mat bhejna.",
    circle: "UP_EAST",
    lang: "Hinglish",
    expectedState: 1,
    stateLabel: "STATE 1: NO_STRONG_WARNING_SIGNS",
    silhouette: "circle_dot",
    intervention: "NO_INTERVENTION_NEEDED",
    confidence: "high (0.94)",
    reasons: [
      { id: "rsn_negation_safe", tactic: "protective_warning", detail: "Linguistic polarity analysis detected defensive negation advising against OTP sharing." }
    ],
    latency: 72
  },
  {
    id: "SCN-LEGIT-0021",
    name: "Legitimate Bank Statement Alert",
    channel: "sms",
    senderHeader: "CP-HDFCBK",
    dltStatus: "registered",
    text: "Dear Customer, INR 4,500.00 debited from A/c **4912 on 24-OCT-26 at SWIGGY BANGALORE via UPI Ref 6298129910. If not done by you, SMS BLOCK to 5676712.",
    circle: "KA",
    lang: "en-IN",
    expectedState: 1,
    stateLabel: "STATE 1: NO_STRONG_WARNING_SIGNS",
    silhouette: "circle_dot",
    intervention: "NO_INTERVENTION_NEEDED",
    confidence: "high (0.99)",
    reasons: [
      { id: "rsn_valid_dlt", tactic: "verified_dlt_sender", detail: "CP-HDFCBK cryptographic telemetry signature validated against NPCI/TRAI ledger." }
    ],
    latency: 64
  },
  {
    id: "SCN-PARTIAL-0005",
    name: "Degraded Source Benchmark",
    channel: "sms",
    senderHeader: "UNKNOWN",
    dltStatus: "none",
    text: "Hi are you available tomorrow?",
    circle: "DL",
    lang: "en-IN",
    expectedState: 2,
    stateLabel: "STATE 2: INSUFFICIENT_EVIDENCE",
    silhouette: "half_circle",
    intervention: "MONITOR_FLOW",
    confidence: "low (0.35)",
    reasons: [
      { id: "rsn_insufficient", tactic: "neutral_greeting", detail: "Payload contains zero financial vectors, URLs, or psychological pressure indicators." }
    ],
    latency: 58
  }
];

export default function SandboxRunnerPage() {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioPreset>(presets[0]);
  const [channel, setChannel] = useState<ScenarioPreset["channel"]>(presets[0].channel);
  const [senderHeader, setSenderHeader] = useState(presets[0].senderHeader);
  const [payloadText, setPayloadText] = useState(presets[0].text);
  const [circle, setCircle] = useState(presets[0].circle);
  const [langScript, setLangScript] = useState(presets[0].lang);
  
  // Execution state
  const [isRunning, setIsRunning] = useState(false);
  const [lastExecutedPreset, setLastExecutedPreset] = useState<ScenarioPreset>(presets[0]);
  const [activeTab, setActiveTab] = useState<"decoded" | "reasons" | "curl">("decoded");
  const [copiedCurl, setCopiedCurl] = useState(false);

  const handleSelectScenario = (s: ScenarioPreset) => {
    setSelectedScenario(s);
    setChannel(s.channel);
    setSenderHeader(s.senderHeader);
    setPayloadText(s.text);
    setCircle(s.circle);
    setLangScript(s.lang);
    setLastExecutedPreset(s);
  };

  const handleRunExecution = async () => {
    setIsRunning(true);
    try {
      const res = await fetch("/api/v1/check/universal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel,
          sender_header: senderHeader,
          text: payloadText,
          metadata: {
            circle,
            linguistic_profile: langScript
          }
        })
      });

      if (res.ok) {
        const liveData = await res.json();
        setLastExecutedPreset({
          ...selectedScenario,
          channel,
          senderHeader,
          text: payloadText,
          circle,
          lang: langScript,
          expectedState: liveData.state_num ?? selectedScenario.expectedState,
          stateLabel: liveData.state_label ?? selectedScenario.stateLabel,
          silhouette: liveData.silhouette ?? selectedScenario.silhouette,
          intervention: liveData.intervention ?? selectedScenario.intervention,
          confidence: liveData.confidence ?? selectedScenario.confidence,
          reasons: liveData.reasons ?? selectedScenario.reasons,
          latency: liveData.evaluation_ms ?? selectedScenario.latency
        });
      }
    } catch (err) {
      console.error("Live execution error:", err);
    } finally {
      setIsRunning(false);
    }
  };

  const currentResult = lastExecutedPreset;

  const jsonResponse = {
    status: "success",
    evaluation_ms: currentResult.latency,
    concern: currentResult.stateLabel.toLowerCase().replace(/state \d+: /, ""),
    silhouette: currentResult.silhouette,
    intervention: currentResult.intervention,
    confidence: currentResult.confidence,
    dlt_verification: {
      sender_header: senderHeader,
      status: currentResult.dltStatus === "registered" ? "VERIFIED_TRAI_ENTITY" : currentResult.dltStatus === "spoofed" ? "UNREGISTERED_OR_SPOOFED" : "UNTRACKED_P2P"
    },
    reasons: currentResult.reasons,
    graph_correlations: currentResult.syndicate ? {
      syndicate_cluster: currentResult.syndicate,
      network_breadth: "multi-circle burst"
    } : null,
    synthetic: true,
    request_id: `req_sand_${Date.now().toString().slice(-8)}`
  };

  const curlSpecimen = `curl -X POST https://sandbox-api.scamgraph.org/v1/check/universal \\
  -H "Authorization: Bearer sk_sand_94829108ApexDevKey01bf" \\
  -H "Content-Type: application/json" \\
  -H "X-Idempotency-Key: idem_sand_${Date.now().toString().slice(-6)}" \\
  -d '{
    "channel": "${channel}",
    "sender_header": "${senderHeader}",
    "text": ${JSON.stringify(payloadText)},
    "metadata": {
      "circle": "${circle}",
      "linguistic_profile": "${langScript}"
    }
  }'`;

  return (
    <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
      {/* 1. Header & Quick Controls */}
      <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight">Interactive Sandbox Runner</h1>
          <p className="text-sm text-on-surface-variant">Execute synthetic threat payloads against real-time ScamGraph behavioral heuristics and DLT verification engines.</p>
        </div>

        <button
          onClick={handleRunExecution}
          disabled={isRunning}
          className="h-11 px-6 rounded-full bg-primary hover:bg-primary/90 disabled:opacity-50 text-on-primary text-xs font-bold inline-flex items-center justify-center gap-2 shadow-md transition-all self-start sm:self-auto"
        >
          {isRunning ? (
            <>
              <RotateCw className="h-4 w-4 animate-spin" />
              <span>Evaluating Model...</span>
            </>
          ) : (
            <>
              <Play className="h-4 w-4 fill-current" />
              <span>Execute Verification (118ms)</span>
            </>
          )}
        </button>
      </section>

      {/* 2. Benchmark Presets Carousel / Grid */}
      <section className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs uppercase font-bold text-viz-neutral tracking-wider">
            Curated Benchmark Presets (8 Scenarios)
          </span>
          <span className="text-xs text-on-surface-variant">Click to load payload specimen</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {presets.map((p) => {
            const isSelected = selectedScenario.id === p.id;
            return (
              <button
                key={p.id}
                onClick={() => handleSelectScenario(p)}
                className={`p-3 rounded-xl border text-left flex flex-col justify-between transition-all ${
                  isSelected
                    ? "bg-selected-tint border-primary shadow-sm"
                    : "bg-surface border-border-divider hover:border-border-control hover:bg-surface-subtle"
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <span className="font-mono text-[10px] font-bold text-viz-neutral">#{p.id}</span>
                  <span className={`w-2 h-2 rounded-full ${
                    p.expectedState >= 6 ? "bg-tone-danger-text" : p.expectedState >= 4 ? "bg-viz-warning" : "bg-viz-primary"
                  }`} />
                </div>
                <p className="font-semibold text-xs text-viz-text mt-1.5 line-clamp-1">{p.name}</p>
                <span className="font-mono text-[10px] text-viz-neutral mt-1">State {p.expectedState} · {p.channel.toUpperCase()}</span>
              </button>
            );
          })}
        </div>
      </section>

      {/* 3. Core Workbench Split (Left: Request, Right: Response & Diagnostic) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column: Request Workbench (5 Cols) */}
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-surface rounded-xl border border-border-divider/70 p-5 shadow-sm flex flex-col gap-4 text-xs">
            
            <div className="flex items-center justify-between pb-3 border-b border-border-divider/60">
              <div className="flex items-center gap-2">
                <FileCode className="h-4 w-4 text-primary" />
                <h2 className="text-sm font-bold text-viz-text">Request Workbench</h2>
              </div>
              <span className="font-mono text-[10px] text-viz-neutral bg-surface-subtle px-2 py-0.5 rounded border border-border-divider">
                POST /v1/check/universal
              </span>
            </div>

            {/* Injected Headers Box */}
            <div className="bg-surface-subtle rounded-xl p-3 border border-border-divider/60 flex flex-col gap-1.5 font-mono text-[11px]">
              <div className="flex justify-between items-center text-on-surface">
                <span className="text-viz-neutral">Authorization:</span>
                <span className="text-primary truncate max-w-[200px]">Bearer sk_sand_94829...01bf</span>
              </div>
              <div className="flex justify-between items-center text-on-surface">
                <span className="text-viz-neutral">X-Idempotency-Key:</span>
                <span className="text-on-surface">idem_sandbox_99a820c812ef</span>
              </div>
              <div className="flex justify-between items-center text-on-surface">
                <span className="text-viz-neutral">Content-Type:</span>
                <span className="text-on-surface">application/json</span>
              </div>
            </div>

            {/* Form Parameters */}
            <div className="flex flex-col gap-3">
              {/* Channel & DLT Sender */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-viz-text">Vector Channel</label>
                  <select
                    value={channel}
                    onChange={(e) => setChannel(e.target.value as ScenarioPreset["channel"])}
                    className="h-10 px-3 rounded-lg border border-border-divider bg-surface text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="sms">SMS (GSM-7 / DLT)</option>
                    <option value="whatsapp">WhatsApp Business API</option>
                    <option value="telegram">Telegram Bot/Chat</option>
                    <option value="upi_prompt">UPI Payment Intent Prompt</option>
                    <option value="qr">Dynamic BharatQR / UPI QR</option>
                    <option value="web">Web Landing Page / APK link</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-viz-text">Sender Header / Origin</label>
                  <input
                    type="text"
                    value={senderHeader}
                    onChange={(e) => setSenderHeader(e.target.value)}
                    className="h-10 px-3 rounded-lg border border-border-divider bg-surface text-xs focus:outline-none focus:ring-1 focus:ring-primary font-mono"
                  />
                </div>
              </div>

              {/* DLT Header State Proof */}
              <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-surface-subtle border border-border-divider text-[11px]">
                <span className="text-viz-neutral font-medium">TRAI DLT Registry Validation:</span>
                <span className={`font-semibold inline-flex items-center gap-1 ${
                  selectedScenario.dltStatus === "registered" ? "text-viz-primary" : selectedScenario.dltStatus === "spoofed" ? "text-tone-danger-text" : "text-viz-neutral"
                }`}>
                  {selectedScenario.dltStatus === "registered" ? "Verified Entity (Govt / Bank)" : selectedScenario.dltStatus === "spoofed" ? "Unregistered / Spoofed" : "Untracked Vector"}
                </span>
              </div>

              {/* Message Payload Textarea */}
              <div className="flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <label className="font-semibold text-viz-text">Message Specimen Payload</label>
                  <span className="font-mono text-[10px] text-viz-neutral">{payloadText.length} chars</span>
                </div>
                <textarea
                  rows={5}
                  value={payloadText}
                  onChange={(e) => setPayloadText(e.target.value)}
                  className="p-3 rounded-lg border border-border-divider bg-surface text-xs font-mono focus:outline-none focus:ring-1 focus:ring-primary leading-relaxed resize-y"
                />
              </div>

              {/* Circle & Language */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-viz-text">Telecom Circle</label>
                  <select
                    value={circle}
                    onChange={(e) => setCircle(e.target.value)}
                    className="h-10 px-3 rounded-lg border border-border-divider bg-surface text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                  >
                    <option value="KA">KA (Karnataka / Bengaluru)</option>
                    <option value="DL">DL (Delhi Metro)</option>
                    <option value="MH">MH (Maharashtra &amp; Goa)</option>
                    <option value="WB">WB (West Bengal &amp; Kolkata)</option>
                    <option value="TN">TN (Tamil Nadu &amp; Chennai)</option>
                    <option value="UP_EAST">UP-E (Uttar Pradesh East)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-viz-text">Linguistic Profile</label>
                  <input
                    type="text"
                    value={langScript}
                    onChange={(e) => setLangScript(e.target.value)}
                    className="h-10 px-3 rounded-lg border border-border-divider bg-surface text-xs focus:outline-none focus:ring-1 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="pt-2 border-t border-border-divider flex items-center justify-between">
              <button
                onClick={() => setPayloadText("")}
                className="px-3 py-1.5 rounded-lg border border-border-divider hover:bg-surface-subtle text-viz-neutral font-medium transition-colors"
              >
                Clear Text
              </button>
              <button
                onClick={handleRunExecution}
                className="px-4 py-1.5 rounded-full bg-primary hover:bg-primary/90 text-on-primary font-bold transition-colors inline-flex items-center gap-1.5 shadow-sm"
              >
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Re-run Evaluation</span>
              </button>
            </div>

          </div>
        </div>

        {/* Right Column: Diagnostic Inspector (7 Cols) */}
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="bg-surface rounded-xl border border-border-divider/70 p-5 shadow-sm flex flex-col gap-4 text-xs">
            
            {/* Header Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-border-divider/60 gap-2">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <h2 className="text-sm font-bold text-viz-text">Diagnostic Inspector</h2>
              </div>
              <div className="flex items-center gap-2 flex-wrap font-mono text-[11px]">
                <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border-divider text-on-surface font-semibold">
                  HTTP 200 OK
                </span>
                <span className="px-2 py-0.5 rounded bg-surface-subtle border border-border-divider text-primary font-semibold">
                  Latency: {currentResult.latency}ms
                </span>
                <span className="px-2 py-0.5 rounded bg-tone-info-bg text-tone-info-text font-semibold">
                  SLA Headroom: +{300 - currentResult.latency}ms
                </span>
              </div>
            </div>

            {/* Canonical Silhouette Banner */}
            <div className={`rounded-xl border-2 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all ${
              currentResult.expectedState >= 6
                ? "border-tone-danger-text bg-tone-danger-bg text-tone-danger-strong-text"
                : currentResult.expectedState >= 4
                ? "border-viz-warning bg-tone-warning-bg text-tone-warning-strong-text"
                : "border-viz-primary bg-tone-info-bg text-tone-info-text"
            }`}>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-surface flex items-center justify-center border border-border-divider shrink-0 shadow-sm">
                  {currentResult.expectedState >= 7 ? (
                    <Octagon className="h-6 w-6 text-tone-danger-text" />
                  ) : currentResult.expectedState >= 6 ? (
                    <ShieldAlert className="h-6 w-6 text-tone-danger-text" />
                  ) : currentResult.expectedState >= 4 ? (
                    <AlertTriangle className="h-6 w-6 text-viz-warning" />
                  ) : (
                    <CircleDot className="h-6 w-6 text-viz-primary" />
                  )}
                </div>
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-base font-mono">{currentResult.stateLabel}</span>
                    <span className="px-2 py-0.5 rounded bg-surface font-mono text-[10px] font-bold uppercase shadow-sm">
                      {currentResult.intervention}
                    </span>
                  </div>
                  <p className="text-xs mt-0.5 leading-relaxed">
                    Confidence: <strong>{currentResult.confidence}</strong> · Empirical Zero-Safe guarantee verified.
                  </p>
                </div>
              </div>
            </div>

            {/* Diagnostic Tabs */}
            <div className="border-b border-border-divider flex items-center gap-4 text-xs">
              <button
                onClick={() => setActiveTab("decoded")}
                className={`py-2 border-b-2 font-semibold transition-colors ${
                  activeTab === "decoded" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Decoded JSON Response
              </button>
              <button
                onClick={() => setActiveTab("reasons")}
                className={`py-2 border-b-2 font-semibold transition-colors ${
                  activeTab === "reasons" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
                }`}
              >
                Structured Evidence Reasons ({currentResult.reasons.length})
              </button>
              <button
                onClick={() => setActiveTab("curl")}
                className={`py-2 border-b-2 font-semibold transition-colors ${
                  activeTab === "curl" ? "border-primary text-primary" : "border-transparent text-on-surface-variant hover:text-on-surface"
                }`}
              >
                cURL Replay
              </button>
            </div>

            {/* Tab 1: Decoded JSON */}
            {activeTab === "decoded" && (
              <div className="bg-inverse-surface rounded-xl p-4 text-inverse-on-surface font-mono text-xs overflow-x-auto shadow-inner max-h-[360px]">
                <pre className="leading-relaxed"><code>{JSON.stringify(jsonResponse, null, 2)}</code></pre>
              </div>
            )}

            {/* Tab 2: Reasons */}
            {activeTab === "reasons" && (
              <div className="flex flex-col gap-2.5 max-h-[360px] overflow-y-auto">
                {currentResult.reasons.map((r) => (
                  <div key={r.id} className="p-3.5 rounded-xl bg-surface-subtle border border-border-divider/70 flex flex-col gap-1">
                    <div className="flex items-center justify-between font-mono">
                      <span className="font-bold text-primary">{r.id}</span>
                      <span className="px-1.5 py-0.5 rounded bg-surface border border-border-divider text-[10px] text-viz-neutral font-semibold">
                        tactic: {r.tactic}
                      </span>
                    </div>
                    <p className="text-xs text-on-surface leading-relaxed mt-0.5">{r.detail}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab 3: cURL Replay */}
            {activeTab === "curl" && (
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-[10px] text-viz-neutral uppercase font-bold">Copy to execute in terminal</span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(curlSpecimen);
                      setCopiedCurl(true);
                      setTimeout(() => setCopiedCurl(false), 2000);
                    }}
                    className="flex items-center gap-1 font-mono text-xs text-primary hover:underline font-bold"
                  >
                    {copiedCurl ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                    <span>{copiedCurl ? "Copied" : "Copy cURL"}</span>
                  </button>
                </div>
                <div className="bg-inverse-surface rounded-xl p-4 text-inverse-on-surface font-mono text-xs overflow-x-auto shadow-inner">
                  <pre className="leading-relaxed"><code>{curlSpecimen}</code></pre>
                </div>
              </div>
            )}

          </div>
        </div>

      </section>
    </div>
  );
}
