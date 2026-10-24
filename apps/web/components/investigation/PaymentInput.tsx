import { cn } from "@/lib/utils/cn";

/** UPI / QR / payment context input. */
export function PaymentInput({
  vpa,
  onVpaChange,
  amount,
  onAmountChange,
  qrPayload,
  onQrChange,
}: {
  vpa: string;
  onVpaChange: (v: string) => void;
  amount: string;
  onAmountChange: (v: string) => void;
  qrPayload: string;
  onQrChange: (v: string) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor="vpa" className="eyebrow">UPI / Payment information</label>
      <input
        id="vpa"
        type="text"
        value={vpa}
        onChange={(e) => onVpaChange(e.target.value)}
        placeholder="merchant@upi or individual@oksbi"
        className={cn(
          "w-full rounded-lg border border-line bg-surface px-3.5 py-2.5 font-mono text-sm text-ink placeholder:text-ink-dim",
          "focus:border-accent focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-signal",
        )}
      />
      <div className="grid grid-cols-2 gap-3">
        <input
          type="number"
          inputMode="decimal"
          value={amount}
          onChange={(e) => onAmountChange(e.target.value)}
          placeholder="Amount (₹)"
          className={cn(
            "rounded-lg border border-line bg-surface px-3.5 py-2.5 text-sm text-ink placeholder:text-ink-dim",
            "focus:border-accent focus:outline-none",
          )}
        />
        <input
          type="text"
          value={qrPayload}
          onChange={(e) => onQrChange(e.target.value)}
          placeholder="or paste QR payload (upi://…)"
          className={cn(
            "rounded-lg border border-line bg-surface px-3.5 py-2.5 font-mono text-xs text-ink placeholder:text-ink-dim",
            "focus:border-accent focus:outline-none",
          )}
        />
      </div>
      <p className="text-[11px] text-ink-dim">
        Validates payee type and detects institutional-impersonation VPAs.
      </p>
    </div>
  );
}
