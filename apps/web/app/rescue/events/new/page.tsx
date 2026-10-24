"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  IndianRupee,
  Calendar,
  Building2,
  FileText,
  Upload,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  Lock,
} from "lucide-react";

export default function AddLossEventPage() {
  const router = useRouter();

  const [utr, setUtr] = useState("428901928374");
  const [vpa, setVpa] = useState("mule.recovery@ybl");
  const [bank, setBank] = useState("ICICI Bank");
  const [amount, setAmount] = useState("45000");
  const [datetime, setDatetime] = useState("2026-10-24T18:15");
  const [evidenceHash, setEvidenceHash] = useState("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(`/rescue/dashboard?amount=${amount}&bank=${encodeURIComponent(bank)}`);
  };

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="max-w-[760px] mx-auto px-4 md:px-8">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li>
              <Link href="/rescue/dashboard" className="hover:text-viz-primary transition-colors">
                Rescue Dashboard
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Add Loss Event [C10]</li>
          </ol>
        </nav>

        {/* Card Form */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-6">
          <div className="border-b border-border-divider pb-4">
            <div className="inline-flex items-center gap-1.5 text-viz-primary text-xs font-bold uppercase tracking-wider mb-1">
              <span className="w-2 h-2 rounded-full bg-viz-primary" />
              [C10] Transaction Forensic Ingestion
            </div>
            <h1 className="text-xl md:text-2xl font-bold text-on-surface">
              Log Financial Loss &amp; UTR Details
            </h1>
            <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">
              Recording the 12-digit UPI UTR enables NPCI and cybercrime authorities to place real-time interbank liens on recipient mule accounts.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            {/* 12-Digit UTR */}
            <div className="flex flex-col gap-1.5">
              <label htmlFor="utr" className="text-xs font-bold text-on-surface">
                12-Digit UPI Transaction ID / UTR Number:
              </label>
              <input
                id="utr"
                type="text"
                maxLength={12}
                value={utr}
                onChange={(e) => setUtr(e.target.value)}
                placeholder="e.g. 428901928374"
                className="w-full p-3 rounded-lg border border-border-control bg-surface font-mono text-xs md:text-sm font-bold text-on-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                required
              />
              <span className="text-[11px] text-viz-neutral">Found on your bank SMS or GPay/PhonePe/Paytm payment receipt.</span>
            </div>

            {/* Recipient VPA & Amount */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="vpa" className="text-xs font-bold text-on-surface">
                  Recipient UPI ID / VPA:
                </label>
                <input
                  id="vpa"
                  type="text"
                  value={vpa}
                  onChange={(e) => setVpa(e.target.value)}
                  placeholder="e.g. fraudulent.user@okhdfcbank"
                  className="w-full p-3 rounded-lg border border-border-control bg-surface text-xs md:text-sm font-medium text-on-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="amount" className="text-xs font-bold text-on-surface">
                  Amount Debited (₹):
                </label>
                <input
                  id="amount"
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="45000"
                  className="w-full p-3 rounded-lg border border-border-control bg-surface font-mono text-xs md:text-sm font-bold text-on-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                  required
                />
              </div>
            </div>

            {/* Victim Bank & Timestamp */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="bank" className="text-xs font-bold text-on-surface">
                  Your Bank (Debited Account):
                </label>
                <input
                  id="bank"
                  type="text"
                  value={bank}
                  onChange={(e) => setBank(e.target.value)}
                  className="w-full p-3 rounded-lg border border-border-control bg-surface text-xs md:text-sm font-medium text-on-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                  required
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="datetime" className="text-xs font-bold text-on-surface">
                  Exact Debit Date &amp; Time:
                </label>
                <input
                  id="datetime"
                  type="datetime-local"
                  value={datetime}
                  onChange={(e) => setDatetime(e.target.value)}
                  className="w-full p-3 rounded-lg border border-border-control bg-surface text-xs md:text-sm font-medium text-on-surface focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                  required
                />
              </div>
            </div>

            {/* Cryptographic SHA-256 Stamp */}
            <div className="p-3.5 bg-surface-subtle rounded-lg border border-border-divider flex flex-col gap-1">
              <div className="flex items-center gap-1.5 text-viz-primary text-xs font-bold">
                <Lock className="h-3.5 w-3.5" />
                <span>Client-Side §65B BSA Evidence Hash:</span>
              </div>
              <p className="font-mono text-[10px] text-viz-neutral truncate">
                SHA256: {evidenceHash}
              </p>
            </div>

            {/* Form Action */}
            <div className="pt-4 border-t border-border-divider flex items-center justify-between">
              <Link
                href="/rescue/dashboard"
                className="text-xs text-on-surface-variant font-medium hover:text-on-surface"
              >
                Cancel
              </Link>
              <button
                type="submit"
                className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-6 py-2 text-xs font-bold transition-all shadow-sm"
              >
                <span>Save Transaction &amp; Update Docket</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
