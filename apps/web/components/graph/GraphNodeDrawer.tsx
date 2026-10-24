"use client";

import { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { humanize, shortId } from "@/lib/utils/format";
import { severityBgToken } from "@/lib/utils/risk";
import type { CytoscapeNodeData } from "@/lib/api/types";

/** Slide-over showing details for a selected graph node. */
export function GraphNodeDrawer({
  node,
  onClose,
}: {
  node: CytoscapeNodeData | null;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!node) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [node, onClose]);

  if (!node) return null;

  const props = node.properties ?? {};
  const entries = Object.entries(props);

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} aria-hidden />
      <aside
        role="dialog"
        aria-label="Graph node details"
        aria-modal="true"
        className="absolute inset-y-0 right-0 flex w-full max-w-sm flex-col border-l border-line bg-elevated animate-fade-in"
      >
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-line px-4">
          <span className="text-sm font-semibold text-ink">Node</span>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-8 w-8 items-center justify-center rounded-lg border border-line text-ink-muted hover:text-ink"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto scrollbar-thin p-5">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="rounded border border-line bg-surface px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wider2 text-ink-dim">
                {humanize(node.node_type)}
              </span>
              {node.severity && (
                <span className={cn("rounded border px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider2", severityBgToken(node.severity))}>
                  {node.severity}
                </span>
              )}
            </div>
            <h3 className="mt-3 break-all text-lg font-semibold text-ink">{node.label}</h3>
            {node.subtext && <p className="mt-1 font-mono text-xs text-ink-dim">{node.subtext}</p>}
          </div>

          {entries.length > 0 && (
            <div>
              <div className="eyebrow mb-2">Properties</div>
              <dl className="panel space-y-2 p-4 text-sm">
                {entries.map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-3">
                    <dt className="text-ink-dim">{humanize(k)}</dt>
                    <dd className="font-mono text-xs text-ink-muted">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          <div className="font-mono text-[11px] text-ink-dim">ID: {shortId(node.id, 10, 6)}</div>
        </div>
      </aside>
    </div>
  );
}
