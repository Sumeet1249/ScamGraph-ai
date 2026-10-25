"use client";

import { useState, type ReactNode } from "react";
import { usePathname } from "next/navigation";
import { AppSidebar } from "./AppSidebar";
import { TopNav } from "./TopNav";
import { MobileNav } from "./MobileNav";
import { CitizenNav } from "./CitizenNav";
import { CitizenFooter } from "./CitizenFooter";

/**
 * Application shell:
 * - Public / Citizen routes: Renders Sovereign Trust CitizenNav + CitizenFooter
 * - Analyst / Operations routes: Renders persistent sidebar + TopNav
 */
export function AppShell({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  // Determine if this is an internal analyst or operations route
  const isAnalystRoute =
    pathname.startsWith("/command") ||
    pathname.startsWith("/radar") ||
    pathname.startsWith("/campaigns") ||
    pathname.startsWith("/incidents") ||
    pathname.startsWith("/investigate") ||
    pathname.startsWith("/graph") ||
    pathname.startsWith("/mulehunter") ||
    pathname.startsWith("/registry") ||
    pathname.startsWith("/ops") ||
    pathname.startsWith("/lab") ||
    pathname.startsWith("/analyst") ||
    pathname.startsWith("/entities") ||
    pathname.startsWith("/entity") ||
    pathname.startsWith("/alerts") ||
    pathname.startsWith("/review") ||
    pathname.startsWith("/cases") ||
    pathname.startsWith("/search") ||
    pathname.startsWith("/saved") ||
    pathname.startsWith("/access") ||
    pathname.startsWith("/audit") ||
    pathname.startsWith("/tactics") ||
    pathname.startsWith("/arena");

  const isDevRoute = pathname.startsWith("/developers");

  if (isDevRoute) {
    return <div className="min-h-screen bg-ground text-on-surface">{children}</div>;
  }

  if (!isAnalystRoute) {
    return (
      <div className="flex min-h-screen flex-col bg-ground text-on-surface">
        <CitizenNav />
        <main className="flex-1 w-full bg-ground">{children}</main>
        <CitizenFooter />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-ground text-on-surface">
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
        <TopNav onMenuToggle={() => setMenuOpen(true)} />
        <main className="flex-1 overflow-x-hidden bg-ground">
          <div className="mx-auto w-full max-w-[1440px] px-4 py-6 lg:px-8 lg:py-8">
            {children}
          </div>
        </main>
        <footer className="border-t border-border-divider px-4 py-4 text-xs text-viz-neutral lg:px-8 bg-surface-subtle">
          <div className="mx-auto flex max-w-[1440px] flex-col items-center justify-between gap-2 sm:flex-row">
            <span>
              ScamGraph AI · Law Enforcement &amp; Bank Analyst Console · §65B BSA Compliant
            </span>
            <span className="font-mono text-[11px] text-viz-neutral">Dual-axis risk · GNN Mule Traversal</span>
          </div>
        </footer>
      </div>
      <MobileNav open={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}
