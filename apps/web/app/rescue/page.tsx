"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  LifeBuoy,
  PhoneCall,
  Clock,
  ArrowRight,
  AlertTriangle,
  Building2,
  IndianRupee,
  ShieldCheck,
  CheckCircle2,
} from "lucide-react";

export default function RescueTriagePage() {
  const router = useRouter();

  const [timeElapsed, setTimeElapsed] = useState("Under 2 hours (Golden Hour)");
  const [lossAmount, setLossAmount] = useState("45000");
  const [paymentRail, setPaymentRail] = useState("UPI");
  const [bankName, setBankName] = useState("ICICI Bank");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(
      `/rescue/dashboard?amount=${lossAmount}&bank=${encodeURIComponent(bankName)}&rail=${paymentRail}&time=${encodeURIComponent(
        timeElapsed
      )}`
    );
  };

  return (
    <div className="w-full bg-ground py-8 md:py-12">
      <div className="max-w-[1000px] mx-auto px-4 md:px-8">
        {/* Breadcrumb Navigation */}
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-xs text-on-surface-variant font-medium">
            <li>
              <Link href="/" className="hover:text-viz-primary transition-colors">
                ScamGraph
              </Link>
            </li>
            <li className="text-viz-neutral select-none">/</li>
            <li className="text-viz-text font-bold">Emergency Rescue Triage [C08]</li>
          </ol>
        </nav>

        {/* Golden Hour High-Priority Banner */}
        <div className="mb-8 rounded-xl bg-tone-danger-strong-bg p-5 md:p-6 border-2 border-tone-danger-text text-tone-danger-strong-text shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3.5">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-tone-danger-text text-surface shrink-0 shadow-sm">
              <Clock className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[11px] font-bold uppercase tracking-wider bg-tone-danger-text text-surface px-2 py-0.5 rounded">
                  Golden Hour Protocol Active
                </span>
                <span className="text-xs font-semibold text-tone-danger-strong-text">
                  Statutory CFCFRMS Rails
                </span>
              </div>
              <h1 className="text-xl md:text-2xl font-bold tracking-tight text-tone-danger-strong-text">
                Every Minute Counts: Rapid Interbank Freeze Triage
              </h1>
              <p className="text-xs text-tone-danger-text mt-0.5 leading-relaxed">
                Debits reported within 120 minutes achieve an 84% fund salvage rate through automated NPCI lien triggers. After 24 hours, recovery probability drops to 14%.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <a
              href="tel:1930"
              className="inline-flex min-h-[44px] items-center gap-2 rounded-full bg-tone-danger-text text-surface hover:opacity-95 px-5 py-2 text-xs font-bold shadow-sm transition-all whitespace-nowrap"
            >
              <PhoneCall className="h-4 w-4" />
              <span>Call Helpline 1930 Now</span>
            </a>
          </div>
        </div>

        {/* Intake Triage Form Card */}
        <div className="bg-surface rounded-xl border border-border-divider p-6 md:p-8 shadow-sm flex flex-col gap-6">
          <div className="border-b border-border-divider pb-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-viz-primary">
              Immediate Incident Assessment
            </span>
            <h2 className="text-lg md:text-xl font-bold text-on-surface">
              Log Your Loss Event for Instant Lien Dispatch
            </h2>
            <p className="text-xs text-on-surface-variant mt-1">
              We generate formal bank nodal officer escalation letters and pre-fill your National Cybercrime complaint dossier.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            {/* Time Elapsed */}
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-on-surface">
                When was the money debited from your account?
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {[
                  "Under 2 hours (Golden Hour)",
                  "2 to 24 hours ago",
                  "More than 24 hours ago",
                ].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTimeElapsed(t)}
                    className={`min-h-[44px] px-3.5 py-2 rounded-lg text-xs font-semibold border text-left transition-colors flex items-center justify-between ${
                      timeElapsed === t
                        ? "bg-selected-tint border-viz-primary text-viz-primary"
                        : "bg-surface-subtle border-border-control text-on-surface hover:bg-surface"
                    }`}
                  >
                    <span>{t}</span>
                    {timeElapsed === t && <CheckCircle2 className="h-4 w-4 text-viz-primary" />}
                  </button>
                ))}
              </div>
            </div>

            {/* Loss Quantum & Bank */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5">
                <label htmlFor="loss-amount" className="text-xs font-bold text-on-surface flex items-center gap-1">
                  <IndianRupee className="h-3.5 w-3.5 text-viz-primary" />
                  <span>Total Amount Debited (₹):</span>
                </label>
                <input
                  id="loss-amount"
                  type="number"
                  value={lossAmount}
                  onChange={(e) => setLossAmount(e.target.value)}
                  placeholder="e.g. 45000"
                  className="w-full p-3 rounded-lg border border-border-control bg-surface text-on-surface font-mono text-sm font-bold focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label htmlFor="bank-select" className="text-xs font-bold text-on-surface flex items-center gap-1">
                  <Building2 className="h-3.5 w-3.5 text-viz-primary" />
                  <span>Your Bank Name:</span>
                </label>
                <select
                  id="bank-select"
                  value={bankName}
                  onChange={(e) => setBankName(e.target.value)}
                  className="w-full p-3 rounded-lg border border-border-control bg-surface text-on-surface text-xs font-medium focus:border-viz-primary focus:outline-none focus:ring-2 focus:ring-viz-primary/20"
                >
                  <option value="State Bank of India">State Bank of India (SBI)</option>
                  <option value="HDFC Bank">HDFC Bank</option>
                  <option value="ICICI Bank">ICICI Bank</option>
                  <option value="Axis Bank">Axis Bank</option>
                  <option value="Punjab National Bank">Punjab National Bank (PNB)</option>
                  <option value="Bank of Baroda">Bank of Baroda</option>
                  <option value="Canara Bank">Canara Bank</option>
                  <option value="Kotak Mahindra Bank">Kotak Mahindra Bank</option>
                  <option value="Other Bank">Other Scheduled Commercial Bank</option>
                </select>
              </div>
            </div>

            {/* Payment Rail */}
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-bold text-on-surface">
                Payment Channel Used:
              </label>
              <div className="flex flex-wrap gap-2.5">
                {["UPI (GPay / PhonePe / Paytm)", "IMPS Interbank", "NEFT / RTGS", "Debit / Credit Card"].map((rail) => (
                  <button
                    key={rail}
                    type="button"
                    onClick={() => setPaymentRail(rail)}
                    className={`min-h-[38px] px-3.5 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                      paymentRail === rail
                        ? "bg-viz-primary text-on-primary border-viz-primary font-bold"
                        : "bg-surface-subtle text-on-surface border-border-control hover:bg-surface"
                    }`}
                  >
                    {rail}
                  </button>
                ))}
              </div>
            </div>

            {/* Submit Action */}
            <div className="pt-4 border-t border-border-divider flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="text-[11px] text-viz-neutral flex items-center gap-1.5">
                <ShieldCheck className="h-4 w-4 text-viz-primary" />
                <span>All incident reports are sealed with Section 65B BSA cryptographic hashes.</span>
              </div>

              <button
                type="submit"
                className="w-full sm:w-auto inline-flex min-h-[44px] items-center justify-center gap-2 rounded-full bg-viz-primary hover:bg-primary text-on-primary px-8 py-2 text-xs font-bold transition-all shadow-sm"
              >
                <span>Launch Rescue Dashboard &amp; Freeze Actions</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
