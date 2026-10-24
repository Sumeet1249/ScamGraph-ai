import Link from "next/link";
import { Shield, Lock } from "lucide-react";

export function CitizenFooter() {
  return (
    <footer className="mt-auto w-full border-t border-border-divider bg-surface py-10">
      <div className="w-full px-6 sm:px-10 lg:px-16">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-8 pb-8 border-b border-border-divider">
          <div className="max-w-[620px]">
            <div className="flex items-center gap-2 mb-2">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-viz-primary text-on-primary">
                <Shield className="h-3 w-3" />
              </span>
              <span className="text-base font-bold text-primary">ScamGraph</span>
              <span className="rounded border border-border-divider bg-surface-subtle px-1.5 py-0.5 text-[10px] font-semibold uppercase text-viz-neutral">
                DPDP Act 2023 · Section 65B BSA Compliant
              </span>
            </div>
            <p className="text-xs leading-relaxed text-on-surface-variant">
              ScamGraph is a sovereign financial fraud intelligence platform. We reconstruct psychological coercion journeys and correlate interbank mule trails before financial intent is executed. No citizen credentials or passwords are ever requested or stored unhashed.
            </p>
          </div>

          <nav aria-label="Footer Navigation" className="flex flex-wrap gap-x-6 gap-y-2 text-xs font-semibold text-on-surface-variant">
            <Link href="/how-it-works" className="hover:text-viz-primary transition-colors">
              Help &amp; How It Works
            </Link>
            <Link href="/privacy" className="hover:text-viz-primary transition-colors">
              Privacy &amp; Data Rights
            </Link>
            <Link href="/developers" className="hover:text-viz-primary transition-colors">
              Bank &amp; Fintech API
            </Link>
            <Link href="/command" className="hover:text-viz-primary transition-colors">
              Law Enforcement Access
            </Link>
          </nav>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-[11px] text-viz-neutral">
          <div className="flex items-center gap-2">
            <Lock className="h-3.5 w-3.5 text-viz-primary shrink-0" />
            <span>
              <strong>Honest Assessment Notice:</strong> The absence of strong warning signs is not a certificate of safety. If funds have been transferred under duress, notify your bank immediately or dial <strong>1930</strong>.
            </span>
          </div>
          <span className="whitespace-nowrap font-mono text-[10px]">
            © 2026 ScamGraph AI · All rights reserved
          </span>
        </div>
      </div>
    </footer>
  );
}
