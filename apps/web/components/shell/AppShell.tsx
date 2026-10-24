"use client";

import { useState, type ReactNode } from "react";
import { AppSidebar } from "./AppSidebar";
import { TopNav } from "./TopNav";
import { MobileNav } from "./MobileNav";

/**
 * Application shell: persistent sidebar (desktop) + top bar + slide-over mobile
 * nav. Content scrolls; chrome stays fixed. Shared by every route.
 */
export function AppShell({ children }: { children: ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-background text-text-primary">
      <AppSidebar />
      <div className="flex min-w-0 flex-1 flex-col transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]">
        <TopNav onMenuToggle={() => setMenuOpen(true)} />
        <main className="flex-1 overflow-x-hidden">
          <div className="mx-auto w-full max-w-[1440px] px-4 py-8 lg:px-8 lg:py-10">
            {children}
          </div>
        </main>
        <footer className="border-t border-border px-4 py-5 text-xs text-text-muted lg:px-8 bg-surface-subtle/30">
          <div className="mx-auto flex max-w-[1440px] flex-col items-center justify-between gap-2 sm:flex-row">
            <span>
              ScamGraph AI · Scam journey intelligence · Risk is an index, not a probability.
            </span>
            <span className="font-mono text-[11px] text-text-muted">Dual-axis risk · Adaptive friction</span>
          </div>
        </footer>
      </div>
      <MobileNav open={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}
