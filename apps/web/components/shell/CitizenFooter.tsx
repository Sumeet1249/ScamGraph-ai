import Link from "next/link";
import { Shield, PhoneCall } from "lucide-react";

export function CitizenFooter() {
  return (
    <footer className="w-full border-t border-blue-100 bg-white/90 backdrop-blur-sm py-4">
      <div className="w-full px-6 sm:px-10 lg:px-16">
        <div className="flex flex-col md:flex-row items-center justify-between gap-3">
          {/* Brand & Mission Tagline */}
          <div className="flex flex-wrap items-center gap-2.5 text-xs text-slate-600">
            <Link href="/" className="flex items-center gap-1.5 font-bold text-blue-900 hover:text-blue-700 transition-colors">
              <span className="flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-white shadow-xs">
                <Shield className="h-3 w-3" />
              </span>
              <span>ScamGraph AI</span>
            </Link>
            <span className="text-slate-300">|</span>
            <span className="text-slate-500 hidden sm:inline">
              Real-time scam &amp; UPI fraud protection
            </span>
            <span className="text-slate-300 hidden sm:inline">|</span>
            <span className="inline-flex items-center gap-1 font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full text-[11px] border border-rose-200/60">
              <PhoneCall className="h-3 w-3" />
              Cyber Helpline: <strong>1930</strong>
            </span>
          </div>

          {/* Quick Clean Navigation Links */}
          <nav aria-label="Footer Navigation" className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs font-medium text-slate-600">
            <Link href="/how-it-works" className="hover:text-blue-600 transition-colors">
              How It Works
            </Link>
            <Link href="/privacy" className="hover:text-blue-600 transition-colors">
              Privacy
            </Link>
            <Link href="/developers" className="hover:text-blue-600 transition-colors">
              API
            </Link>
            <Link href="/rescue" className="text-rose-600 font-semibold hover:text-rose-700 transition-colors">
              Report Fraud
            </Link>
            <Link href="/command" className="hover:text-blue-600 transition-colors">
              Analyst Console
            </Link>
          </nav>

          {/* Minimalist Copyright */}
          <div className="text-[11px] text-slate-400">
            © 2026 ScamGraph AI
          </div>
        </div>
      </div>
    </footer>
  );
}
