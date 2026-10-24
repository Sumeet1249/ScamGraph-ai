import { cn } from "@/lib/utils/cn";

/** Payment proximity indicator — shows how close the journey is to money moving. */
export function PaymentProximity({
  proximate,
}: {
  proximate: boolean;
}) {
  const band = proximate ? "high" : "low";
  return (
    <div className="panel p-5">
      <div className="eyebrow mb-3">Payment Proximity</div>
      <div className="flex items-center justify-between">
        <span
          className={cn(
            "text-lg font-semibold",
            proximate ? "text-danger" : "text-ink-muted",
          )}
        >
          {proximate ? "High" : "Low"}
        </span>
        <span className="font-mono text-xs text-ink-dim">{band}</span>
      </div>
      <div className="mt-3 flex gap-1">
        {Array.from({ length: 10 }).map((_, i) => (
          <span
            key={i}
            className={cn(
              "h-1.5 flex-1 rounded-full",
              proximate && i < 8 ? "bg-danger" : "bg-surface-2",
            )}
          />
        ))}
      </div>
      <p className="mt-2 text-xs text-ink-dim">
        {proximate
          ? "Payment request or intent observed in journey."
          : "No payment request detected yet."}
      </p>
    </div>
  );
}
