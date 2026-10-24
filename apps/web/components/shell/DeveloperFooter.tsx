"use client";

import Link from "next/link";

export function DeveloperFooter() {
  return (
    <footer className="w-full bg-surface py-6 border-t border-border-divider/70 shadow-[0_-1px_4px_rgba(0,0,0,0.02)] mt-auto">
      <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs">
        <div className="flex flex-wrap items-center gap-4 text-viz-neutral">
          <span className="font-mono text-viz-neutral font-semibold">v2.4.0-spec</span>
          <Link href="/developers/docs" className="text-on-surface-variant hover:text-primary transition-colors">
            OpenAPI 3.1 Specification
          </Link>
          <Link href="/developers/usage" className="text-on-surface-variant hover:text-primary transition-colors">
            Latency SLAs (&lt;120ms P99)
          </Link>
          <Link href="/developers" className="text-on-surface-variant hover:text-primary transition-colors">
            Status Page (99.98%)
          </Link>
          <Link href="/help-center" className="text-on-surface-variant hover:text-primary transition-colors">
            Security &amp; Vulnerability Disclosure
          </Link>
        </div>
        <div className="text-viz-neutral text-[11px]">
          © {new Date().getFullYear()} ScamGraph Infrastructure. All cryptographic guarantees certified under §65B BSA &amp; DPDP Act 2023.
        </div>
      </div>
    </footer>
  );
}
