import { cn } from "@/lib/utils/cn";
import { humanizeStage } from "@/lib/utils/format";
import type { JourneyStage } from "@/lib/api/types";

const STAGE_ORDER: JourneyStage[] = [
  "INITIAL_CONTACT",
  "IMPERSONATION",
  "URGENCY_PRESSURE",
  "SUSPICIOUS_LINK",
  "CREDENTIAL_OTP_HARVEST",
  "PAYMENT_REQUEST",
  "PAYMENT_INTENT",
];

/** Current journey stage with a progression meter toward payment. */
export function CurrentStage({
  stage,
  paymentProximate,
}: {
  stage: JourneyStage;
  paymentProximate?: boolean;
}) {
  const idx = STAGE_ORDER.indexOf(stage);
  const total = STAGE_ORDER.length;
  const progress = idx >= 0 ? Math.round(((idx + 1) / total) * 100) : 0;

  return (
    <div className="panel p-5">
      <div className="eyebrow mb-3">Current Stage</div>
      <p className="text-base font-semibold text-ink">{humanizeStage(stage)}</p>
      <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-surface-2">
        <div
          className={cn("h-full rounded-full", paymentProximate ? "bg-danger" : "bg-accent")}
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      <p className="mt-2 font-mono text-[11px] text-ink-dim">
        {idx >= 0 ? `${idx + 1} / ${total} progression` : "Stage unknown"}
      </p>
    </div>
  );
}
