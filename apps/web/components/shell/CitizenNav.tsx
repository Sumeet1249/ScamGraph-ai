"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, PhoneCall, LifeBuoy, ArrowRight, User, Code2 } from "lucide-react";

export function CitizenNav() {
  const pathname = usePathname();

  const navLinks = [
    { label: "Universal Check", href: "/check" },
    { label: "Activity", href: "/activity" },
    { label: "Emergency Recovery", href: "/rescue" },
    { label: "How It Works", href: "/how-it-works" },
    { label: "Help Center", href: "/help-center" },
  ];

  return (
    <>
      {/* 1. Development & Statutory Environment Indicator */}
      <aside aria-label="Development Environment Indicator" className="w-full border-b border-border-divider bg-surface-subtle text-viz-text">
        <div className="w-full flex items-center justify-between px-6 sm:px-10 lg:px-16 py-1 text-xs">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center rounded border border-border-control bg-tone-warning-bg px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-tone-warning-strong-text">
              SYNTHETIC DEMO DATA
            </span>
            <span className="text-on-surface-variant text-[11px] font-medium hidden sm:inline">
              Citizen Protection Prototype · DPDP Act 2023 & Section 65B BSA Compliant
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-semibold text-tone-danger-text">
            <span className="inline-flex items-center gap-1">
              <PhoneCall className="h-3.5 w-3.5" />
              National Cyber Helpline: <strong>1930</strong>
            </span>
          </div>
        </div>
      </aside>

      {/* 2. Main Consumer Header Shell */}
      <header className="sticky top-0 z-50 w-full border-b border-border-divider bg-surface/95 backdrop-blur-md">
        <div className="w-full flex h-16 items-center justify-between gap-4 px-6 sm:px-10 lg:px-16">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-6 lg:gap-8">
            <Link
              href="/"
              className="flex items-center gap-2 rounded focus:outline-none focus:ring-2 focus:ring-viz-primary"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-viz-primary text-on-primary shadow-sm">
                <Shield className="h-4 w-4" />
              </span>
              <span className="text-xl font-bold tracking-tight text-primary">
                ScamGraph
              </span>
            </Link>

            <nav className="hidden md:flex items-center h-16">
              {navLinks.map((link) => {
                const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex h-16 items-center border-b-[3px] px-3.5 text-sm transition-colors ${
                      isActive
                        ? "border-viz-primary bg-selected-tint font-semibold text-viz-primary"
                        : "border-transparent font-medium text-on-surface-variant hover:bg-surface-subtle hover:text-on-surface"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Action Touchpoints */}
          <div className="flex items-center gap-2.5 sm:gap-3.5">
            {/* Direct Rescue Emergency CTA */}
            <Link
              href="/rescue"
              className="inline-flex min-h-[38px] items-center gap-1.5 rounded-full border border-border-control bg-surface px-3.5 py-1 text-xs font-semibold text-viz-text shadow-sm transition-colors hover:bg-surface-subtle"
            >
              <LifeBuoy className="h-3.5 w-3.5 text-viz-primary" />
              <span className="hidden sm:inline">Already paid or shared?</span>
              <span className="sm:hidden">Help</span>
            </Link>

            {/* Developer Portal */}
            <Link
              href="/developers"
              className="inline-flex min-h-[38px] items-center justify-center gap-1.5 rounded border border-border-divider bg-surface px-3 py-1 text-xs font-semibold text-on-surface-variant transition-colors hover:border-border-control hover:text-on-surface hidden sm:inline-flex"
            >
              <Code2 className="h-3.5 w-3.5 text-viz-primary" />
              <span>Dev Console</span>
            </Link>

            {/* Persona Switcher / Analyst Portal */}
            <Link
              href="/command"
              className="inline-flex min-h-[38px] items-center justify-center rounded border border-border-divider bg-surface px-3 py-1 text-xs font-semibold text-on-surface-variant transition-colors hover:border-border-control hover:text-on-surface hidden sm:inline-flex"
            >
              Analyst Console
            </Link>

            {/* Quick Check CTA */}
            <Link
              href="/check"
              className="inline-flex min-h-[38px] items-center justify-center gap-1 rounded-full bg-viz-primary px-4 py-1 text-xs font-bold text-on-primary shadow-sm transition-colors hover:bg-primary"
            >
              <span>Check Free</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>

            {/* Profile & Privacy Settings */}
            <Link
              href="/settings/privacy"
              aria-label="Profile and Privacy Settings"
              className="flex h-8 w-8 items-center justify-center rounded-full border border-border-divider bg-surface-subtle text-on-surface-variant hover:border-border-control hover:text-on-surface transition-colors"
              title="Profile and Privacy Settings"
            >
              <User className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}
