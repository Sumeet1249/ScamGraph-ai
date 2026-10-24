import { cn } from "@/lib/utils/cn";

/** Single-line URL input. Never fetched from the browser (Architecture Rule 8). */
export function URLInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="space-y-1.5">
      <label htmlFor="url" className="eyebrow">Suspicious URL</label>
      <input
        id="url"
        type="url"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="https://sbi-kyc-verify-portal.online"
        className={cn(
          "w-full rounded-lg border border-line bg-surface px-3.5 py-2.5 font-mono text-sm text-ink placeholder:text-ink-dim",
          "focus:border-accent focus:outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-signal",
        )}
      />
      <p className="text-[11px] text-ink-dim">
        Inspected server-side only. Lexical risk, RDAP, and infrastructure safety.
      </p>
    </div>
  );
}
