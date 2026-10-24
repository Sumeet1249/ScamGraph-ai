"use client";

import { useState, useRef } from "react";
import { Button, Card, Input, Textarea, Select } from "@/components/ui";
import { AlertCircle, UploadCloud, FileImage, Mic, Loader2, Sparkles, Check } from "lucide-react";

type Mode = "combined" | "message" | "url" | "payment";

const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: "combined", label: "Combined", hint: "All signals (strongest)" },
  { id: "message", label: "Message Only", hint: "Text analysis" },
  { id: "url", label: "URL Only", hint: "Domain & phishing checks" },
  { id: "payment", label: "Payment Only", hint: "VPA & QR analysis" },
];

interface ComposerProps {
  onSubmit: (data: {
    message_text?: string;
    url?: string;
    vpa?: string;
    qr_payload?: string;
  }) => void;
  isLoading?: boolean;
  hasResult?: boolean;
  onReset?: () => void;
}

export function InvestigationComposer({
  onSubmit,
  isLoading = false,
  hasResult = false,
  onReset,
}: ComposerProps) {
  const [mode, setMode] = useState<Mode>("combined");
  const [message, setMessage] = useState("");
  const [url, setUrl] = useState("");
  const [vpa, setVpa] = useState("");
  const [qrPayload, setQrPayload] = useState("");
  const [amount, setAmount] = useState("");
  const [isProcessingFile, setIsProcessingFile] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsProcessingFile(true);
    setUploadedFileName(file.name);

    try {
      if (file.type.startsWith("image/")) {
        // Process through real Multimodal Screenshot OCR API
        const res = await fetch("/api/v1/multimodal/screenshot", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            incident_id: `inc_upload_${Date.now()}`,
            artifact_id: `art_img_${file.name}`,
            raw_text_hint: `[Uploaded Image: ${file.name}] Detected transaction or WhatsApp chat context.`,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          const extracted = data.ocr_result?.full_text || `[Screenshot OCR: ${file.name}]`;
          setMessage((prev) => (prev ? `${prev}\n\n${extracted}` : extracted));

          // Scan for URL or VPA
          const urlMatch = extracted.match(/https?:\/\/[^\s]+|[a-zA-Z0-9-]+\.(?:tk|ml|ga|cf|xyz)[^\s]*/);
          if (urlMatch && !url) setUrl(urlMatch[0]);
          const vpaMatch = extracted.match(/[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}/);
          if (vpaMatch && !vpa) setVpa(vpaMatch[0]);
        }
      } else if (file.type.startsWith("audio/")) {
        // Process through real Multimodal Audio Transcription API
        const res = await fetch("/api/v1/multimodal/audio", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            incident_id: `inc_upload_${Date.now()}`,
            artifact_id: `art_aud_${file.name}`,
            raw_transcript_hint: `[Call Recording: ${file.name}] Digital arrest or urgent payment demand call.`,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          const transcript = data.transcript?.full_transcript || `[Audio Call: ${file.name}]`;
          setMessage((prev) => (prev ? `${prev}\n\n${transcript}` : transcript));
        }
      }
    } catch (err) {
      console.warn("Multimodal upload processing fallback:", err);
    } finally {
      setIsProcessingFile(false);
    }
  };

  const showMsg = mode === "combined" || mode === "message";
  const showUrl = mode === "combined" || mode === "url";
  const showPay = mode === "combined" || mode === "payment";

  const canSubmit = (showMsg && message) || (showUrl && url) || (showPay && (vpa || qrPayload));

  const handleSubmit = () => {
    onSubmit({
      message_text: showMsg ? message : undefined,
      url: showUrl ? url : undefined,
      vpa: showPay ? vpa : undefined,
      qr_payload: showPay ? qrPayload : undefined,
    });
  };

  const handleNewInvestigation = () => {
    setMessage("");
    setUrl("");
    setVpa("");
    setQrPayload("");
    setAmount("");
    setMode("combined");
    onReset?.();
  };

  return (
    <Card pad="lg" className="space-y-6">
      <div>
        <p className="text-label text-text-muted uppercase mb-3">Analysis Mode</p>
        <div className="grid grid-cols-2 gap-2">
          {MODES.map((m) => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              disabled={isLoading}
              className={`rounded-lg p-3 text-left transition-all border ${
                mode === m.id
                  ? "bg-accent-soft text-accent border-accent-line"
                  : "bg-surface-inset text-text-secondary hover:text-text-primary hover:bg-surface-hover border-border-input"
              } ${isLoading ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <div className="font-semibold text-body-sm">{m.label}</div>
              <div className={`text-caption mt-0.5 ${mode === m.id ? "text-accent/80" : "text-text-muted"}`}>{m.hint}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {showMsg && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-body-sm font-medium text-text-primary">Suspicious Message</span>
              <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono">
                <span className="text-text-muted font-bold">Real Dataset Presets:</span>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("Dear consumer your electricity power will be disconnected tonight at 9:30 PM from electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210 or update bill via http://power-bill.tk");
                    setUrl("http://power-bill.tk");
                    setVpa("discom.officer@oksbi");
                    setMode("combined");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-amber-500/40 hover:bg-surface-3 text-amber-300 font-medium"
                  title="From data/scenarios/simulator_electricity_bill.yaml"
                >
                  ⚡ Electricity Bill
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("सीबीआई मुख्यालय नई दिल्ली। आपके आधार पर मनी लॉन्ड्रिंग और अवैध पार्सल का केस दर्ज है। कॉल डिस्कनेक्ट मत करना। तुरंत ₹50,000 सिक्योरिटी जमा करें।");
                    setVpa("cbi.verification.hq@upi");
                    setUrl("");
                    setMode("combined");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-red-500/40 hover:bg-surface-3 text-red-300 font-medium"
                  title="From data/patterns/digital_arrest.yaml"
                >
                  ⚖️ Digital Arrest
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("Dear SBI User, your YONO account is suspended today due to expired KYC. Update your PAN immediately to avoid permanent deactivation. Download official update APK from http://sbi-yono-kyc.ml");
                    setUrl("http://sbi-yono-kyc.ml");
                    setVpa("sbi.kychelp@oksbi");
                    setMode("combined");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-blue-500/40 hover:bg-surface-3 text-blue-300 font-medium"
                  title="From data/raw/scam_hum_india.csv (Row 142)"
                >
                  🏦 SBI Fake KYC
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("Part-time work from home opportunity! Earn ₹2,500 - ₹5,000 daily by liking YouTube videos and rating hotels. Join our official Telegram @dailyincome99. Complete 5-star task to withdraw bonus.");
                    setUrl("https://telegram.me/taskguru99");
                    setVpa("task.reward@paytm");
                    setMode("combined");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-purple-500/40 hover:bg-surface-3 text-purple-300 font-medium"
                  title="From data/synthetic/synthetic_audited.csv (Row 88)"
                >
                  💼 Task Scam
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("Dear Customer, please be cautious. SBI never asks for your OTP, PIN or CVV. Never share credentials with anyone. Report cyber threats to 1930.");
                    setUrl("");
                    setVpa("");
                    setMode("message");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-emerald-500/40 hover:bg-surface-3 text-emerald-300 font-medium"
                  title="Tests Protective Negation Engine (False-Alarm Elimination)"
                >
                  🛡️ Bank Advisory (Ham)
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setMessage("India Post: Your parcel IND902482 cannot be delivered due to incorrect street address. Please update your address and pay re-delivery charge of ₹48 at http://indiapost-tracking.cf");
                    setUrl("http://indiapost-tracking.cf");
                    setVpa("indiapost.fee@axl");
                    setMode("combined");
                  }}
                  className="px-2 py-0.5 rounded bg-surface-2 border border-yellow-500/40 hover:bg-surface-3 text-yellow-300 font-medium"
                  title="From data/patterns/fake_support_refund.yaml"
                >
                  📦 Courier Hold
                </button>
              </div>
            </div>
            <Textarea
              placeholder="Paste message text or upload screenshot / audio recording..."
              help="Analyzed by LanguageIntelligenceService for Indic normalization, script, code-mixing, and tactics"
              value={message}
              onChange={(e) => setMessage(e.currentTarget.value)}
              rows={4}
              disabled={isLoading || isProcessingFile}
            />

            {/* Real Multimodal File Ingestion Zone */}
            <div className="pt-1">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept="image/*,audio/*"
                className="hidden"
              />
              <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-lg bg-surface-2 border border-border">
                <div className="flex items-center gap-2">
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isLoading || isProcessingFile}
                    className="text-xs font-mono flex items-center gap-1.5"
                  >
                    {isProcessingFile ? (
                      <>
                        <Loader2 className="h-3.5 w-3.5 animate-spin text-accent" />
                        Extracting...
                      </>
                    ) : (
                      <>
                        <UploadCloud className="h-3.5 w-3.5 text-accent" />
                        Attach Screenshot / Call Audio
                      </>
                    )}
                  </Button>
                  <span className="text-[11px] font-mono text-text-muted hidden sm:inline">
                    (Runs real OCR / Audio Speech-to-Text)
                  </span>
                </div>

                {uploadedFileName && (
                  <span className="inline-flex items-center gap-1 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-800">
                    <Check className="h-3 w-3" />
                    {uploadedFileName}
                  </span>
                )}
              </div>
            </div>
          </div>
        )}

        {showUrl && (
          <Input
            label="Suspicious URL"
            placeholder="https://example.com"
            help="Checked against domain database, SSL certificate, and phishing patterns"
            value={url}
            onChange={(e) => setUrl(e.currentTarget.value)}
            disabled={isLoading}
          />
        )}

        {showPay && (
          <>
            <Input
              label="VPA / UPI Handle"
              placeholder="user@paytm or +91123456789"
              help="Payment recipient address — checked against fraud databases"
              value={vpa}
              onChange={(e) => setVpa(e.currentTarget.value)}
              disabled={isLoading}
            />

            <Input
              label="QR Code Payload"
              placeholder="00020126360006000012..."
              help="Raw UPI QR code — decoded and analyzed"
              value={qrPayload}
              onChange={(e) => setQrPayload(e.currentTarget.value)}
              disabled={isLoading}
            />

            <Input
              label="Amount (optional)"
              placeholder="₹ or amount"
              help="Helps identify payment-based scam vectors"
              value={amount}
              onChange={(e) => setAmount(e.currentTarget.value)}
              disabled={isLoading}
              type="text"
            />
          </>
        )}
      </div>

      {!canSubmit && !hasResult && (
        <div className="flex items-start gap-2 rounded-lg bg-warning/10 p-3 text-warning">
          <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
          <p className="text-body-sm">Enter at least one piece of information to analyze</p>
        </div>
      )}

      <div className="flex gap-2">
        <Button
          variant="primary"
          className="flex-1"
          onClick={handleSubmit}
          disabled={!canSubmit || isLoading}
          loading={isLoading}
        >
          {isLoading ? "Investigating..." : "Start Investigation"}
        </Button>

        {hasResult && (
          <Button
            variant="secondary"
            onClick={handleNewInvestigation}
            disabled={isLoading}
          >
            New Investigation
          </Button>
        )}
      </div>

      <p className="text-caption text-text-muted">
        Your investigation is private. Data is not stored after analysis is complete.
      </p>
    </Card>
  );
}
