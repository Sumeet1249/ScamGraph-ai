import { cn } from "@/lib/utils/cn";

/**
 * Visible watermark for synthetic/demo data (Architecture Rule 24).
 * Every dashboard surface that shows demo numbers must display this clearly.
 */
export function DemoDataBadge({ className }: { className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-md border border-caution/30 bg-caution/10 px-2 py-1",
        "text-[10px] font-bold uppercase tracking-wider2 text-caution",
        className,
      )}
      title="This surface is showing synthetic demonstration data, not live production telemetry."
    >
      <span className="h-1.5 w-1.5 rounded-full bg-caution animate-pulse-soft" />
      Demo Data
    </span>
  );
}
