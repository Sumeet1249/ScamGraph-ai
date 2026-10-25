"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Shield,
  Search,
  ArrowRight,
  Lock,
  AlertTriangle,
  ChevronDown,
  ExternalLink,
  CheckCircle2,
  Zap,
} from "lucide-react";
import { ScamJourneyMotion } from "@/components/home/ScamJourneyMotion";

export default function HomePage() {
  const router = useRouter();
  const [inputText, setInputText] = useState("");
  const [selectedFaq, setSelectedFaq] = useState<number | null>(0);

  const handleCheckSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim()) return;
    router.push(`/check?query=${encodeURIComponent(inputText.trim())}`);
  };

  const faqItems = [
    {
      q: "What should I do if I already sent money to a scammer?",
      a: "Act immediately: Call the National Cybercrime Helpline at 1930 and contact your bank to freeze the payment. Reporting within the first 2 hours ('Golden Hour') gives the highest chance of freezing and recovering funds across interbank networks.",
    },
    {
      q: "Does checking a message block my payment automatically?",
      a: "No. ScamGraph AI provides safety analysis, scam warnings, and step-by-step guidance. It does not touch your bank account or block transactions automatically. You maintain full control.",
    },
    {
      q: "Is it safe and anonymous to check a message or UPI ID?",
      a: "Yes, 100%. ScamGraph is completely free and requires no account. Your input is encrypted client-side and never shared, sold, or stored with any personal identifying details.",
    },
    {
      q: "What if ScamGraph shows 'No strong scam indicators'?",
      a: "Even if no obvious scam patterns are found, always stay alert. Scammers frequently create new phone numbers and fake UPI IDs. Never share OTPs, passwords, or download unknown remote-access apps.",
    },
  ];

  return (
    <div className="flex flex-col w-full animate-fade-in-up">
      {/* ── 1. Hero Section & Quick Scanner ── */}
      <section className="w-full py-10 md:py-16 border-b border-blue-100/80">
        <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            {/* Left Hero Pitch */}
            <div className="lg:col-span-6 flex flex-col justify-center">
              <div className="inline-flex items-center gap-2 text-blue-700 bg-blue-50 border border-blue-200/80 rounded-full px-3 py-1 text-xs font-semibold w-fit mb-4 shadow-2xs">
                <span className="w-2 h-2 rounded-full bg-blue-600 animate-pulse" />
                <span>Next-Gen Scam &amp; UPI Fraud Shield</span>
              </div>
              <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight text-slate-900 mb-4 leading-[1.18]">
                Stop Scams Before You <span className="text-blue-600 bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">Send Money</span>
              </h1>
              <p className="text-base text-slate-600 mb-6 leading-relaxed">
                Paste any suspicious message, UPI ID, phone number, or payment link to check for fraud signals in seconds. Powered by AI journey recognition that detects threats before transactions occur.
              </p>

              <div className="flex flex-wrap items-center gap-3">
                <Link
                  href="/rescue"
                  className="inline-flex min-h-[42px] items-center gap-2 rounded-full bg-rose-600 px-5 py-2 text-xs font-bold text-white shadow-md shadow-rose-600/20 transition-all hover:bg-rose-700 hover:shadow-lg active:scale-95"
                >
                  <AlertTriangle className="h-4 w-4" />
                  <span>Lost Money? Dial 1930 / Quick Recovery</span>
                </Link>
                <Link
                  href="/how-it-works"
                  className="inline-flex min-h-[42px] items-center gap-1.5 rounded-full border border-slate-200 bg-white/90 px-5 py-2 text-xs font-semibold text-slate-700 shadow-2xs transition-all hover:border-blue-300 hover:text-blue-600 hover:bg-blue-50/40 active:scale-95"
                >
                  <span>How It Works</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>

            {/* Right Omnibox Card */}
            <div className="lg:col-span-6 w-full">
              <div className="bg-white rounded-2xl border border-blue-100 shadow-xl shadow-blue-500/5 p-5 md:p-7 relative overflow-hidden backdrop-blur-sm">
                <div className="flex items-center justify-between pb-3 mb-4 border-b border-slate-100">
                  <div className="flex items-center gap-2">
                    <Search className="h-4 w-4 text-blue-600" />
                    <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                      Quick Scam Scanner
                    </span>
                  </div>
                  <span className="text-[11px] font-semibold text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
                    100% Free &amp; Private
                  </span>
                </div>

                <form onSubmit={handleCheckSubmit} className="flex flex-col gap-3">
                  <label htmlFor="scam-intake-text" className="text-xs font-medium text-slate-700">
                    Paste a UPI ID, phone number, SMS message, or website link:
                  </label>
                  <textarea
                    id="scam-intake-text"
                    rows={4}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="e.g. 9876543210@paytm, electricity bill threat SMS, or suspicious APK download URL..."
                    className="w-full p-3.5 rounded-xl border border-slate-200 bg-slate-50/50 text-slate-900 placeholder:text-slate-400 text-sm focus:border-blue-500 focus:bg-white focus:outline-none focus:ring-3 focus:ring-blue-500/15 resize-none transition-all"
                  />

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                    <div className="flex items-center gap-1.5 text-slate-500 text-[11px]">
                      <Lock className="h-3.5 w-3.5 text-blue-600" />
                      <span>Private &amp; Secure. No personal data is ever saved.</span>
                    </div>

                    <button
                      type="submit"
                      disabled={!inputText.trim()}
                      className="inline-flex min-h-[42px] items-center justify-center gap-2 rounded-full bg-blue-600 px-6 py-2 text-xs font-bold text-white hover:bg-blue-700 transition-all disabled:opacity-50 shadow-md shadow-blue-600/20 active:scale-95"
                    >
                      <span>Check for Scams</span>
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  </div>
                </form>

                {/* Popular sample triggers */}
                <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center gap-1.5 text-[11px]">
                  <span className="text-slate-500 font-medium">Try example:</span>
                  {[
                    "Electricity bill disconnection threat",
                    "Fake courier & digital arrest call",
                    "Telegram part-time job offer",
                    "fake-sbi-rewards.apk",
                  ].map((sample) => (
                    <button
                      key={sample}
                      type="button"
                      onClick={() => setInputText(sample)}
                      className="rounded-lg bg-slate-100/80 px-2.5 py-1 text-slate-600 hover:text-blue-700 hover:bg-blue-50 border border-slate-200/60 transition-colors"
                    >
                      {sample}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. Live Platform Impact ── */}
      <section className="w-full bg-white/70 py-8 border-b border-blue-100/80 backdrop-blur-xs">
        <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <span className="text-[11px] text-blue-700 font-bold uppercase tracking-wider block">
                Live Protection Network
              </span>
              <h2 className="text-xl font-bold text-slate-900">
                Community Impact &amp; Threat Detection
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-blue-100/90 p-4 shadow-sm hover:border-blue-300 transition-colors">
              <div className="text-xs text-slate-500 font-medium">Scam Money Prevented</div>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">₹482+ Cr</div>
              <div className="text-xs text-emerald-600 font-semibold mt-1 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Across UPI &amp; Net Banking
              </div>
            </div>
            <div className="bg-white rounded-xl border border-blue-100/90 p-4 shadow-sm hover:border-blue-300 transition-colors">
              <div className="text-xs text-slate-500 font-medium">Active Scam Networks Tracked</div>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">38+ Syndicates</div>
              <div className="text-xs text-slate-500 font-medium mt-1">Cross-bank linked clusters</div>
            </div>
            <div className="bg-white rounded-xl border border-blue-100/90 p-4 shadow-sm hover:border-blue-300 transition-colors">
              <div className="text-xs text-slate-500 font-medium">Average Scan Speed</div>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">&lt; 1.2 Sec</div>
              <div className="text-xs text-blue-600 font-semibold mt-1 flex items-center gap-1">
                <Zap className="w-3.5 h-3.5" /> Real-time threat matching
              </div>
            </div>
            <div className="bg-white rounded-xl border border-blue-100/90 p-4 shadow-sm hover:border-blue-300 transition-colors">
              <div className="text-xs text-slate-500 font-medium">Supported Payment Systems</div>
              <div className="text-2xl font-extrabold text-slate-900 mt-1">All UPI &amp; Banks</div>
              <div className="text-xs text-slate-500 font-medium mt-1">GPay, PhonePe, Paytm &amp; Banks</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 3. Simple 3-Step Guide ── */}
      <section className="w-full py-12 border-b border-blue-100/80">
        <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
          <div className="max-w-[700px] mb-8">
            <span className="text-xs text-blue-700 font-bold uppercase tracking-wider block mb-1">
              Easy 3-Step Process
            </span>
            <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900">
              Check → Understand → Protect
            </h2>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Clear, practical advice in plain language without complicated cybersecurity terms.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex flex-col bg-white p-6 rounded-2xl border border-blue-100/80 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-blue-600 font-extrabold text-2xl">01</span>
                <div className="h-px flex-1 bg-slate-100" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">Paste what you received</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Copy and paste the suspicious text message, phone number, UPI ID, or website link into the scanner.
              </p>
            </div>

            <div className="flex flex-col bg-white p-6 rounded-2xl border border-blue-100/80 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-blue-600 font-extrabold text-2xl">02</span>
                <div className="h-px flex-1 bg-slate-100" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">See the warning signs</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Our AI highlights high-risk urgency tactics, impersonation flags, and known scam patterns.
              </p>
            </div>

            <div className="flex flex-col bg-white p-6 rounded-2xl border border-blue-100/80 shadow-sm hover:shadow-md transition-shadow">
              <div className="flex items-center gap-3 mb-4">
                <span className="font-mono text-blue-600 font-extrabold text-2xl">03</span>
                <div className="h-px flex-1 bg-slate-100" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-1">Take safe action</h3>
              <p className="text-xs text-slate-600 leading-relaxed">
                Get immediate instructions on how to block, report, or freeze your payment before financial loss occurs.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4. Visual Scam Stages ── */}
      <section className="w-full bg-white/70 py-12 border-b border-blue-100/80">
        <div className="w-full px-6 sm:px-10 lg:px-16 xl:px-20">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-slate-900">How Scammers Trick Victims (4 Stages)</h2>
                <span className="text-[11px] text-blue-700 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-200/80 font-semibold">
                  Recognize The Tactics
                </span>
              </div>
              <p className="text-xs text-slate-600 mt-1">
                Scams follow predictable psychological steps. Spotting them early keeps your money safe.
              </p>
            </div>
          </div>

          <ScamJourneyMotion />
        </div>
      </section>

      {/* ── 5. FAQs Section ── */}
      <section className="w-full py-12 border-b border-blue-100/80">
        <div className="w-full max-w-4xl mx-auto px-6 sm:px-10">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-extrabold text-slate-900">Frequently Asked Questions</h2>
            <p className="text-xs text-slate-600 mt-1">
              Direct guidance for common scam situations and fraud concerns.
            </p>
          </div>

          <div className="divide-y divide-slate-100 border border-blue-100 rounded-2xl bg-white overflow-hidden shadow-sm">
            {faqItems.map((item, idx) => {
              const isOpen = selectedFaq === idx;
              return (
                <div key={idx} className="p-4 transition-colors hover:bg-slate-50/60">
                  <button
                    type="button"
                    onClick={() => setSelectedFaq(isOpen ? null : idx)}
                    className="flex w-full items-center justify-between text-left text-xs md:text-sm font-bold text-slate-900 focus:outline-none"
                  >
                    <span>{item.q}</span>
                    <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
                  </button>
                  {isOpen && (
                    <div className="pt-2.5 text-xs text-slate-600 leading-relaxed">
                      {item.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── 6. Compact Emergency Assistance Bar ── */}
      <section className="w-full py-8 text-center bg-gradient-to-r from-blue-50/60 via-indigo-50/40 to-blue-50/60">
        <div className="w-full max-w-3xl mx-auto px-6 sm:px-10">
          <h2 className="text-lg md:text-xl font-bold text-slate-900 mb-1.5">
            Lost money in a scam recently?
          </h2>
          <p className="text-xs text-slate-600 mb-4">
            Call the Cybercrime Helpline at <strong>1930</strong> immediately, or follow our step-by-step recovery guide to freeze unauthorized transfers.
          </p>
          <Link
            href="/rescue"
            className="inline-flex min-h-[40px] items-center gap-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 text-xs font-bold transition-all shadow-md shadow-blue-600/20 active:scale-95"
          >
            <span>Start Quick Recovery Guide</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>
    </div>
  );
}
