"use client";

import { usePathname } from "next/navigation";
import { activeItem } from "@/lib/nav";
import { humanize } from "@/lib/utils/format";

/** Slim top bar: breadcrumb + environment indicator. Mobile nav toggle is in MobileNav. */
export function TopNav({ onMenuToggle }: { onMenuToggle?: () => void }) {
  const pathname = usePathname() || "/";
  const active = activeItem(pathname);
  const section = active?.label ?? "ScamGraph";

  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/85 px-4 backdrop-blur-md lg:px-6">
      <button
        type="button"
        onClick={onMenuToggle}
        aria-label="Open menu"
        aria-expanded={false}
        className="lg:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-border text-text-secondary hover:text-text-primary"
      >
        <span className="space-y-1.5">
          <span className="block h-0.5 w-4 bg-current" />
          <span className="block h-0.5 w-4 bg-current" />
          <span className="block h-0.5 w-4 bg-current" />
        </span>
      </button>

      <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm">
        <span className="text-text-secondary">ScamGraph</span>
        <span className="text-text-secondary">/</span>
        <span className="font-medium text-text-primary">{humanize(section).replace(/ /g, " ")}</span>
      </nav>

      <div className="ml-auto flex items-center gap-3">
        <span className="hidden sm:inline-flex items-center gap-1.5 rounded-md border border-border bg-surface-2 px-2.5 py-1 text-[11px] font-mono text-text-muted">
          <span className="h-1.5 w-1.5 rounded-full bg-warning" />
          v0.1 · Demo build
        </span>
      </div>
    </header>
  );
}
