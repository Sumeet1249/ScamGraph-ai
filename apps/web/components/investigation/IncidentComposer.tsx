"use client";

import { useState } from "react";
import { Button } from "@/components/ui";
import { MessageInput } from "./MessageInput";
import { URLInput } from "./URLInput";
import { PaymentInput } from "./PaymentInput";

type Mode = "combined" | "message" | "url" | "payment";

const MODES: { id: Mode; label: string }[] = [
  { id: "combined", label: "Combined Incident" },
  { id: "message", label: "Message" },
  { id: "url", label: "URL" },
  { id: "payment", label: "QR / Payment" },
];

/**
 * Multi-signal incident composer. Defaults to Combined Incident so analysts can
 * submit message + URL + payment together for stronger analysis.
 * Phase 2 wires onSubmit to POST /investigate + the progress screen.
 */
export function IncidentComposer({
  onSubmit,
}: {
  onSubmit?: (data: {
    message_text: string;
    url: string;
    vpa: string;
    qr_payload: string;
    amount: string;
  }) => void;
}) {
  const [mode, setMode] = useState<Mode>("combined");
  const [message, setMessage] = useState("");
  const [url, setUrl] = useState("");
  const [vpa, setVpa] = useState("");
  const [amount, setAmount] = useState("");
  const [qr, setQr] = useState("");

  const showMsg = mode === "combined" || mode === "message";
  const showUrl = mode === "combined" || mode === "url";
  const showPay = mode === "combined" || mode === "payment";

  function handleSubmit() {
    onSubmit?.({ message_text: message, url, vpa, qr_payload: qr, amount });
  }

  return (
    <div className="space-y-6">
      <div role="tablist" aria-label="Input mode" className="flex flex-wrap gap-1">
        {MODES.map((m) => (
          <button
            key={m.id}
            role="tab"
            aria-selected={mode === m.id}
            onClick={() => setMode(m.id)}
            className={
              "rounded-full px-3.5 py-1.5 text-xs font-medium transition-all btn-pop " +
              (mode === m.id
                ? "bg-surface text-ink border border-line"
                : "text-ink-dim hover:text-ink-muted")
            }
          >
            {m.label}
          </button>
        ))}
      </div>

      <div className="space-y-5">
        {showMsg && <MessageInput value={message} onChange={setMessage} />}
        {showUrl && <URLInput value={url} onChange={setUrl} />}
        {showPay && (
          <PaymentInput
            vpa={vpa}
            onVpaChange={setVpa}
            amount={amount}
            onAmountChange={setAmount}
            qrPayload={qr}
            onQrChange={setQr}
          />
        )}
      </div>

      <Button size="lg" variant="primary" onClick={handleSubmit} className="w-full sm:w-auto">
        Start Investigation
      </Button>
      <p className="text-[11px] text-ink-dim">
        Only mark a stage complete when the engine confirms it. No fabricated results.
      </p>
    </div>
  );
}
