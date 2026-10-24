import { cn } from "@/lib/utils/cn";

/** Multi-line message input for SMS / WhatsApp / email text. */
export function MessageInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor="msg" className="eyebrow">Suspicious message</label>
      <textarea
        id="msg"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={5}
        placeholder="Paste SMS, WhatsApp, or email text…"
        className={cn(
          "w-full resize-y rounded-lg border border-line bg-surface px-3.5 py-3 text-sm text-ink placeholder:text-ink-dim",
          "focus:border-accent focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-signal",
        )}
      />
      <p className="text-[11px] text-ink-dim">
        Semantic analysis extracts urgency, impersonation, and intent markers.
      </p>
    </div>
  );
}
