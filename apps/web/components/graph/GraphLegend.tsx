import { cn } from "@/lib/utils/cn";
import type { GraphNodeType } from "@/lib/api/types";

const LEGEND: { type: GraphNodeType; color: string; label: string }[] = [
  { type: "incident", color: "var(--sg-node-incident, #C4B5E8)", label: "Incident" },
  { type: "journey_step", color: "var(--sg-node-journey, #A8836B)", label: "Journey Step" },
  { type: "message", color: "var(--sg-node-message, #E5E4E2)", label: "Message" },
  { type: "url", color: "var(--sg-node-url, #7FAFD0)", label: "URL" },
  { type: "domain", color: "var(--sg-node-domain, #7DBFAA)", label: "Domain" },
  { type: "phone", color: "var(--sg-node-phone, #D99DB8)", label: "Phone" },
  { type: "upi_handle", color: "var(--sg-node-upi, #D8C36F)", label: "UPI / VPA" },
  { type: "campaign", color: "var(--sg-node-campaign, #E38E7C)", label: "Campaign" },
];

/** Color legend for the evidence graph. */
export function GraphLegend({ className }: { className?: string }) {
  return (
    <div className={cn("flex flex-wrap gap-x-3 gap-y-1.5", className)}>
      {LEGEND.map((l) => (
        <span key={l.type} className="inline-flex items-center gap-1.5 text-[10px] text-text-muted">
          <span className="h-2 w-2 rounded-full border border-border/40" style={{ backgroundColor: l.color }} />
          {l.label}
        </span>
      ))}
    </div>
  );
}
