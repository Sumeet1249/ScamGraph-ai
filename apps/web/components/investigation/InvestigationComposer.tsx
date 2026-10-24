"use client";

import { useState } from "react";
import { Button, Card, Input, Textarea, Select } from "@/components/ui";
import { AlertCircle } from "lucide-react";

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
          <Textarea
            label="Suspicious Message"
            placeholder="Paste the message text..."
            help="Analyzed for urgency keywords, impersonation, and known scam language"
            value={message}
            onChange={(e) => setMessage(e.currentTarget.value)}
            rows={5}
            disabled={isLoading}
          />
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
