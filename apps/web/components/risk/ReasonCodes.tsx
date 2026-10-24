"use client";

import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils/cn";

/**
 * Why ScamGraph intervened — reason codes.
 * Each code is clickable to open/filter supporting evidence (Phase 3 wires
 * the onClick). Phase 1 renders them as a clear, scannable list.
 */
export function ReasonCodes({
  reasons,
  onSelect,
  className,
}: {
  reasons: string[];
  onSelect?: (code: string) => void;
  className?: string;
}) {
  if (!reasons.length) {
    return (
      <p className="text-sm text-ink-dim">
        No specific risk reasons recorded for this incident.
      </p>
    );
  }

  return (
    <ul className={cn("space-y-1.5", className)}>
      {reasons.map((code, i) => {
        const tag = code.match(/^\[([^\]]+)\]/)?.[1];
        const body = code.replace(/^\[[^\]]+\]\s*/, "");
        return (
          <li key={i}>
            <button
              type="button"
              disabled={!onSelect}
              onClick={() => onSelect?.(code)}
              className={cn(
                "flex w-full items-start gap-2.5 rounded-lg border border-line bg-surface px-3 py-2 text-left text-sm transition-colors",
                onSelect && "hover:border-line-strong hover:bg-surface-hover cursor-pointer",
              )}
            >
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-safe" />
              <span className="min-w-0">
                {tag && (
                  <span className="font-mono text-[10px] uppercase tracking-wider2 text-ink-dim">
                    {tag}
                  </span>
                )}
                <span className="block text-ink-muted">{body}</span>
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
