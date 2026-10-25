"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, PhoneCall, ArrowRight, User, Terminal, AlertCircle } from "lucide-react";

export function CitizenNav() {
  const pathname = usePathname();

  const navLinks = [
    { label: "Check Scam", href: "/check" },
    { label: "Live Outbreaks", href: "/activity" },
    { label: "Emergency Help", href: "/rescue" },
    { label: "How It Works", href: "/how-it-works" },
  ];

  return (
    <>
      {/* 1. Startup Status & Helpline Strip */}
      <aside aria-label="Status Bar" className="w-full border-b border-blue-100/70 bg-gradient-to-r from-blue-50/70 via-slate-50 to-blue-50/70 text-slate-700">
        <div className="w-full flex items-center justify-between px-6 sm:px-10 lg:px-16 py-1.5 text-xs">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 text-blue-800 px-2 py-0.5 text-[10px] font-bold tracking-wide uppercase border border-blue-200">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
              Active Protection
            </span>
            <span className="text-slate-600 text-[11px] font-medium hidden sm:inline">
              Instant AI Fraud Verification for UPI &amp; Digital Payments
            </span>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-semibold text-rose-700">
            <span className="inline-flex items-center gap-1 bg-white/80 px-2.5 py-0.5 rounded-full border border-rose-200/80 shadow-2xs">
              <PhoneCall className="h-3 w-3 text-rose-600" />
              Cybercrime Helpline: <strong>1930</strong>
            </span>
          </div>
        </div>
      </aside>

      {/* 2. Main Startup Header */}
      <header className="sticky top-0 z-40 w-full border-b border-blue-100/80 bg-white/95 backdrop-blur-md shadow-xs">
        <div className="w-full flex h-16 items-center justify-between gap-4 px-6 sm:px-10 lg:px-16">
          {/* Logo & Navigation */}
          <div className="flex items-center gap-6 lg:gap-8">
            <Link
              href="/"
              className="flex items-center gap-2.5 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 group"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 text-white shadow-sm shadow-blue-500/25 group-hover:scale-105 transition-transform">
                <Shield className="h-4.5 w-4.5" />
              </span>
              <div className="flex flex-col">
                <span className="text-lg font-bold tracking-tight text-slate-900 group-hover:text-blue-700 transition-colors">
                  ScamGraph <span className="text-blue-600 text-xs font-semibold px-1 py-0.2 bg-blue-50 rounded border border-blue-200/60 ml-0.5">AI</span>
                </span>
              </div>
            </Link>

            <nav className="hidden md:flex items-center h-16 gap-1">
              {navLinks.map((link) => {
                const isActive = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`flex h-9 items-center px-3.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? "bg-blue-50 text-blue-700 font-bold shadow-2xs"
                        : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
          </div>

          {/* Right Action Touchpoints */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            {/* Quick Emergency Aid Button */}
            <Link
              href="/rescue"
              className="inline-flex min-h-[36px] items-center gap-1.5 rounded-full border border-rose-200 bg-rose-50/80 px-3 py-1 text-xs font-semibold text-rose-700 shadow-2xs transition-all hover:bg-rose-100 hover:border-rose-300 active:scale-95"
            >
              <AlertCircle className="h-3.5 w-3.5 text-rose-600" />
              <span className="hidden sm:inline">Lost Money?</span>
              <span className="sm:hidden">Help</span>
            </Link>

            {/* Developer Portal */}
            <Link
              href="/developers"
              className="inline-flex min-h-[36px] items-center justify-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 transition-all hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50/50 hidden sm:inline-flex"
            >
              <Terminal className="h-3.5 w-3.5 text-blue-600" />
              <span>API</span>
            </Link>

            {/* Analyst Console */}
            <Link
              href="/command"
              className="inline-flex min-h-[36px] items-center justify-center rounded-lg border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700 transition-all hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50/50 hidden sm:inline-flex"
            >
              Analyst Portal
            </Link>

            {/* Quick Check CTA */}
            <Link
              href="/check"
              className="group inline-flex min-h-[36px] items-center justify-center gap-1.5 rounded-full bg-blue-600 px-4 py-1 text-xs font-bold text-white shadow-sm shadow-blue-600/20 transition-all hover:bg-blue-700 hover:shadow-md hover:scale-[1.02] active:scale-95"
            >
              <span>Scan Now</span>
              <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-0.5" />
            </Link>

            {/* Privacy Settings */}
            <Link
              href="/settings/privacy"
              aria-label="Profile and Privacy Settings"
              className="flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-slate-50 text-slate-600 hover:border-blue-300 hover:text-blue-700 hover:scale-105 transition-all"
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
