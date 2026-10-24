"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { 
  ShieldCheck, 
  ArrowRight, 
  Building2, 
  ChevronDown, 
  User, 
  FlaskConical,
  Activity,
  Layers,
  CheckCircle2
} from "lucide-react";

export function DeveloperNav() {
  const pathname = usePathname();
  const [orgMenuOpen, setOrgMenuOpen] = useState(false);
  const [env, setEnv] = useState<"sandbox" | "live">("sandbox");

  const navItems = [
    { label: "Overview", href: "/developers" },
    { label: "API docs", href: "/developers/docs" },
    { label: "API keys", href: "/developers/keys" },
    { label: "Webhooks", href: "/developers/webhooks" },
    { label: "Usage", href: "/developers/usage" },
    { label: "Sandbox", href: "/developers/sandbox" },
  ];

  return (
    <>
      {/* 1. Fixed Top Header */}
      <header className="sticky top-0 z-50 w-full bg-surface shadow-[0_1px_8px_rgba(0,0,0,0.04)] border-b border-border-divider/70">
        <div className="h-16 w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between gap-4">
          
          {/* Left Brand & Tabs */}
          <div className="flex items-center gap-6 lg:gap-8 flex-shrink-0">
            <div className="flex items-center gap-2">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-8 h-8 rounded bg-viz-primary flex items-center justify-center text-on-primary shadow-sm">
                  <ShieldCheck className="h-4 w-4" />
                </div>
                <span className="font-semibold text-lg text-viz-text tracking-tight">ScamGraph</span>
              </Link>
              <span className="text-xs font-medium text-viz-neutral pl-0.5">Developers</span>
            </div>

            {/* Sandbox environment indicator badge */}
            <div className="inline-flex items-center px-2 py-0.5 rounded bg-tone-warning-bg text-tone-warning-strong-text font-mono font-medium text-[11px] tracking-wider uppercase border border-tone-warning-text/20">
              [{env.toUpperCase()}]
            </div>

            {/* Sub-nav links */}
            <nav className="hidden xl:flex items-center gap-5 h-16 ml-1">
              {navItems.map((item) => {
                const isActive = item.href === "/developers" 
                  ? pathname === "/developers"
                  : pathname.startsWith(item.href);

                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`h-full inline-flex items-center px-1 text-sm transition-colors border-b-2 ${
                      isActive
                        ? "text-primary font-semibold border-primary"
                        : "border-transparent font-medium text-on-surface-variant hover:text-on-surface"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Action Touchpoints */}
          <div className="flex items-center gap-3.5 flex-shrink-0">
            {/* API Status Indicator */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded bg-surface-subtle text-xs border border-border-divider/50">
              <span className="w-2 h-2 rounded-full bg-viz-primary animate-pulse" />
              <span className="text-on-surface-variant text-[11px]">
                API Status: <strong className="text-viz-text font-medium">Normal (99.98%)</strong>
              </span>
            </div>

            {/* Org Switcher */}
            <div className="relative hidden lg:block">
              <button
                onClick={() => setOrgMenuOpen(!orgMenuOpen)}
                className="flex items-center gap-1.5 text-xs text-viz-neutral bg-surface-subtle px-3 py-1.5 rounded hover:bg-surface-container-high transition-colors border border-border-divider/40"
              >
                <Building2 className="h-3.5 w-3.5 text-viz-neutral" />
                <span className="font-semibold text-viz-text">Apex FinTech India</span>
                <span className="text-viz-neutral/80 text-[11px]">(Dev Org)</span>
                <ChevronDown className="h-3 w-3 text-viz-neutral" />
              </button>
              {orgMenuOpen && (
                <div className="absolute right-0 mt-1 w-56 rounded-md bg-surface p-1 shadow-lg border border-border-divider text-xs z-50">
                  <div className="px-3 py-1.5 font-semibold text-viz-neutral uppercase tracking-wider text-[10px]">
                    Switch Tenant
                  </div>
                  <div className="px-3 py-2 bg-selected-tint rounded font-medium text-primary flex items-center justify-between">
                    <span>Apex FinTech India</span>
                    <CheckCircle2 className="h-3.5 w-3.5 text-primary" />
                  </div>
                  <div className="px-3 py-2 hover:bg-surface-subtle rounded cursor-pointer text-on-surface-variant">
                    <span>Axis UPI Integration Lab</span>
                  </div>
                  <div className="px-3 py-2 hover:bg-surface-subtle rounded cursor-pointer text-on-surface-variant">
                    <span>Razorpay Guard Sandbox</span>
                  </div>
                </div>
              )}
            </div>

            {/* Switch to Live / Analyst Portal link */}
            <button
              onClick={() => setEnv(env === "sandbox" ? "live" : "sandbox")}
              className="hidden md:inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 transition-colors"
            >
              <span>{env === "sandbox" ? "Switch to Live" : "Switch to Sandbox"}</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </button>

            {/* Analyst Console Switcher */}
            <Link
              href="/command"
              className="hidden md:inline-flex items-center gap-1 rounded border border-border-divider bg-surface px-2.5 py-1 text-xs font-semibold text-on-surface-variant hover:border-border-control hover:text-on-surface transition-colors"
            >
              <Layers className="h-3 w-3 text-viz-neutral" />
              <span>Analyst Console</span>
            </Link>

            {/* Citizen Portal Switcher */}
            <Link
              href="/"
              className="inline-flex items-center rounded border border-border-divider bg-surface px-2.5 py-1 text-xs font-semibold text-on-surface-variant hover:border-border-control hover:text-on-surface transition-colors"
            >
              <span>User Mode</span>
            </Link>

            {/* User Profile */}
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-on-primary text-xs font-bold shadow-sm">
              <User className="h-4 w-4" />
            </div>
          </div>
        </div>

        {/* Mobile / Compact Subnav for < xl screens */}
        <div className="xl:hidden w-full overflow-x-auto border-t border-border-divider bg-surface-subtle/80 px-4 py-1.5 flex items-center gap-4 text-xs font-medium no-scrollbar">
          {navItems.map((item) => {
            const isActive = item.href === "/developers" 
              ? pathname === "/developers"
              : pathname.startsWith(item.href);

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`whitespace-nowrap px-2 py-1 rounded transition-colors ${
                  isActive
                    ? "bg-primary text-on-primary font-semibold"
                    : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </header>

      {/* 2. System Status & Environment Telemetry Strip */}
      <section className="w-full bg-surface-container-low py-2 px-4 sm:px-6 lg:px-8 border-b border-border-divider/50">
        <div className="max-w-[1440px] mx-auto flex flex-col lg:flex-row items-start lg:items-center justify-between gap-2">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-viz-neutral">Developers</span>
            <span className="text-border-control">/</span>
            <span className="text-on-surface font-semibold capitalize">
              {pathname === "/developers" ? "Overview" : pathname.replace("/developers/", "")}
            </span>
            <div className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded bg-tone-warning-strong-bg text-tone-warning-strong-text font-mono text-[10px] font-bold tracking-wider">
              <FlaskConical className="h-3 w-3" />
              <span>{env.toUpperCase()} ENVIRONMENT</span>
            </div>
            <span className="hidden sm:inline text-viz-neutral text-[11px]">
              All calls routed through synthetic test models. Zero production intelligence mutation.
            </span>
          </div>

          {/* Telemetry Metrics */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-on-surface-variant">
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-viz-primary" />
              <span>Core REST API: <strong className="text-viz-text font-mono">99.98%</strong> (p95: 142ms)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-viz-primary" />
              <span>Async Queue: <strong className="text-viz-text font-mono">12ms lag</strong></span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-viz-primary" />
              <span>Webhooks: <strong className="text-viz-text">Healthy</strong></span>
            </div>
            <span className="font-mono text-viz-neutral bg-surface px-1.5 py-0.5 rounded text-[11px] border border-border-divider shadow-sm">
              OpenAPI 3.1.0
            </span>
          </div>
        </div>
      </section>
    </>
  );
}
