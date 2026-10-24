'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function GuardCheckpointPage() {
  const router = useRouter();
  const [selectedAction, setSelectedAction] = useState<string>('approve_collect');
  const [paused, setPaused] = useState<boolean>(false);

  const handleContinue = () => {
    router.push(`/guard/questions?intent=${encodeURIComponent(selectedAction)}`);
  };

  const options = [
    {
      id: 'send_money',
      title: 'Send money',
      desc: 'UPI transfer, net banking, or instant pay to an individual or QR code',
      icon: 'payments',
      sub: 'Direct debit flow',
      badge: null
    },
    {
      id: 'approve_collect',
      title: 'Approve a payment request',
      desc: 'Accepting a collect request on PhonePe, Google Pay, Paytm, or BHIM',
      icon: 'call_received',
      sub: 'Common impersonation vector',
      badge: 'Target'
    },
    {
      id: 'share_credential',
      title: 'Share OTP or password',
      desc: 'Providing a one-time code, bank PIN, or CVV over call or message',
      icon: 'password',
      sub: 'High irreversible risk',
      badge: null
    },
    {
      id: 'install_app',
      title: 'Install an app',
      desc: 'Downloading an APK file or remote support tool like AnyDesk or TeamViewer',
      icon: 'system_update',
      sub: 'Device compromise vector',
      badge: null
    },
    {
      id: 'share_screen',
      title: 'Share screen or device access',
      desc: 'Allowing an unknown caller to view your smartphone or desktop screen',
      icon: 'screen_share',
      sub: 'Real-time harvest risk',
      badge: null
    },
    {
      id: 'other_action',
      title: 'Other action',
      desc: 'Interacting with unverified customer support or KYC verification links',
      icon: 'contact_support',
      sub: 'General assessment',
      badge: null
    }
  ];

  return (
    <div className="w-full bg-ground py-4 sm:py-8">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        {/* Focused Flow Header Banner */}
        <section className="relative overflow-hidden rounded-xl bg-surface p-6 sm:p-8 border border-border-divider shadow-sm mb-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 relative z-10">
            <div className="max-w-[720px]">
              <div className="flex flex-wrap items-center gap-2 mb-2">
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-semibold">
                  <span className="material-symbols-outlined text-[15px]">security</span>
                  Guard Checkpoint
                </span>
                <span className="text-viz-neutral text-xs">•</span>
                <span className="text-xs text-viz-neutral tracking-normal">Pre-transaction intervention (C05)</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-viz-text mb-2">
                Guard · Before you continue
              </h1>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Pause for 60 seconds. Answering a few quick questions helps prevent unauthorized financial transactions.
              </p>
            </div>
            <div className="flex flex-col items-start md:items-end justify-center shrink-0">
              <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-subtle border border-border-divider">
                <span className="material-symbols-outlined text-viz-primary text-[20px]">inventory_2</span>
                <div className="text-left md:text-right">
                  <p className="text-[11px] text-viz-neutral">Case identifier</p>
                  <p className="text-xs font-bold text-viz-text font-mono">#SG-84920</p>
                </div>
              </div>
              <p className="text-[11px] text-viz-neutral mt-1">Context carried over from Universal Check</p>
            </div>
          </div>
        </section>

        {/* Main Action & Context Split Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Question & Choice Matrix (8 cols) */}
          <main className="lg:col-span-8 flex flex-col gap-6">
            <div className="bg-surface rounded-xl p-6 sm:p-8 border border-border-divider shadow-sm">
              <div className="flex items-center justify-between pb-2 mb-4 border-b border-border-divider">
                <div>
                  <p className="text-xs text-viz-primary font-bold uppercase tracking-wider mb-1">Step 1 of 2</p>
                  <h2 className="text-lg font-bold text-viz-text">What are you about to do?</h2>
                </div>
                <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded bg-tone-warning-bg text-tone-warning-strong-text text-xs font-semibold">
                  <span className="material-symbols-outlined text-[15px]">timer</span>
                  <span>Active deliberation</span>
                </div>
              </div>

              {/* Choice Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4" role="radiogroup" aria-label="Action you are about to perform">
                {options.map((opt) => {
                  const isSelected = selectedAction === opt.id;
                  return (
                    <div
                      key={opt.id}
                      onClick={() => setSelectedAction(opt.id)}
                      className={`group relative flex flex-col justify-between p-4 rounded-xl cursor-pointer min-h-[115px] border transition-all ${isSelected
                          ? 'border-2 border-primary bg-selected-tint shadow-sm'
                          : 'border-border-divider bg-surface-subtle hover:border-border-control'
                        }`}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`w-5 h-5 rounded-full mt-0.5 shrink-0 flex items-center justify-center ${isSelected ? 'bg-primary text-white' : 'border border-border-control bg-surface'}`}>
                          {isSelected ? (
                            <span className="material-symbols-outlined text-[13px] font-bold">check</span>
                          ) : (
                            <div className="w-2 h-2 rounded-full bg-transparent"></div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className={`material-symbols-outlined text-[18px] ${isSelected ? 'text-viz-primary' : 'text-viz-neutral group-hover:text-viz-primary'}`}>
                              {opt.icon}
                            </span>
                            <span className="text-xs font-bold text-viz-text">{opt.title}</span>
                            {opt.badge && (
                              <span className="px-1.5 py-0.2 rounded bg-primary text-white text-[10px] font-bold uppercase tracking-wider">
                                {opt.badge}
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-on-surface-variant mt-1 leading-relaxed">{opt.desc}</p>
                        </div>
                      </div>
                      <div className={`flex items-center justify-between mt-3 pt-2 border-t border-border-divider/50 text-xs ${isSelected ? 'text-viz-primary font-semibold' : 'text-viz-neutral'}`}>
                        <span>{opt.sub}</span>
                        <span className="material-symbols-outlined text-[16px]">
                          {isSelected ? 'check_circle' : 'arrow_forward'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Active Deliberation Helper Box */}
              <div className="mt-6 p-4 rounded-xl bg-tone-info-bg border border-tone-info-text/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <span className="material-symbols-outlined text-tone-info-text text-[22px] shrink-0 mt-0.5">info</span>
                  <div>
                    <h3 className="text-xs font-bold text-tone-info-text">Why does this matter right now?</h3>
                    <p className="text-xs text-tone-info-text/90 leading-relaxed mt-0.5">
                      Approval of collect requests triggers direct debit from your bank account without crediting any funds. Legitimate service providers never send collect requests to resolve utility bills.
                    </p>
                  </div>
                </div>
                <span className="shrink-0 px-2.5 py-1 rounded-full bg-surface text-tone-info-text text-xs font-bold whitespace-nowrap border border-border-divider">
                  Critical point
                </span>
              </div>

              {/* Action Floor Buttons */}
              <div className="mt-8 pt-4 border-t border-border-divider flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
                  {/* Continue Check CTA */}
                  <button
                    onClick={handleContinue}
                    type="button"
                    className="inline-flex items-center justify-center gap-2 min-h-[44px] px-6 rounded-full bg-viz-primary text-white text-xs font-bold hover:bg-primary transition-all shadow-sm focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  >
                    <span>Continue check</span>
                    <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
                  </button>

                  {/* Deliberate Pause Button */}
                  <button
                    onClick={() => setPaused(!paused)}
                    type="button"
                    className="inline-flex items-center justify-center gap-2 min-h-[44px] px-4 rounded-full bg-surface-subtle text-viz-text text-xs font-medium hover:bg-surface border border-border-divider transition-colors focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
                  >
                    <span className="material-symbols-outlined text-[18px] text-viz-neutral">pause_circle</span>
                    <span>{paused ? 'Deliberation Paused' : "I'm not continuing"}</span>
                  </button>
                </div>

                {/* Direct Rescue Route */}
                <Link
                  href="/rescue"
                  className="inline-flex items-center justify-center gap-2 min-h-[44px] px-4 rounded-full bg-tone-danger-bg text-tone-danger-strong-text text-xs font-bold hover:bg-tone-danger-strong-bg border border-tone-danger-text/20 transition-colors focus:outline-none focus:ring-2 focus:ring-error focus:ring-offset-2 whitespace-nowrap"
                >
                  <span className="material-symbols-outlined text-[18px]">report</span>
                  <span>I already paid or shared something →</span>
                </Link>
              </div>

              {paused && (
                <div className="mt-4 p-3 rounded-lg bg-surface-subtle border border-border-divider text-xs text-on-surface">
                  <strong className="text-viz-primary">Good decision to pause.</strong> Taking time breaks the manufactured urgency trap. You can return to inspect this case anytime from Activity.
                </div>
              )}

              {/* Truth & Scope Disclaimer */}
              <div className="mt-6 pt-3 border-t border-border-divider">
                <p className="text-xs text-viz-neutral flex items-center gap-1.5 leading-normal">
                  <span className="material-symbols-outlined text-[16px] text-viz-neutral shrink-0">verified_user</span>
                  <span>Guard provides independent verification assistance. ScamGraph does not process payments or freeze bank accounts on your behalf.</span>
                </p>
              </div>
            </div>
          </main>

          {/* Right: Case Evidence Context Rail (4 cols) */}
          <aside className="lg:col-span-4 flex flex-col gap-4">
            {/* Context Carried Over Card */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-viz-primary text-[18px]">fact_check</span>
                  <h3 className="text-xs font-bold text-viz-text">What we already know from this case</h3>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-surface-subtle border border-border-divider text-viz-neutral text-[10px] font-semibold">
                  Attached
                </span>
              </div>
              <p className="text-xs text-on-surface-variant mb-4 leading-relaxed">
                Your prior evidence is already attached. You won&apos;t need to re-enter this.
              </p>
              <div className="flex flex-col gap-3">
                {/* Evidence Chip 1 */}
                <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                  <div className="flex items-center justify-between text-[11px] text-viz-neutral mb-1">
                    <span className="inline-flex items-center gap-1">
                      <span className="text-[9px] text-primary">●</span>
                      Observed SMS
                    </span>
                    <span className="font-mono text-[10px]">C01 Input</span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <span className="material-symbols-outlined text-viz-warning text-[16px] shrink-0 mt-0.5">warning</span>
                    <p className="text-xs font-semibold text-viz-text">Electricity disconnection threat</p>
                  </div>
                  <p className="text-[11px] text-on-surface-variant mt-1 italic leading-relaxed">
                    &quot;Electricity power will be disconnected tonight at 9:30 PM due to unpaid bill.&quot;
                  </p>
                </div>

                {/* Evidence Chip 2 */}
                <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                  <div className="flex items-center justify-between text-[11px] text-viz-neutral mb-1">
                    <span className="inline-flex items-center gap-1">
                      <span className="text-[9px] text-primary">●</span>
                      Extracted sender
                    </span>
                    <span className="font-mono text-[10px]">Unregistered</span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <span className="material-symbols-outlined text-viz-neutral text-[16px] shrink-0 mt-0.5">phone_iphone</span>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-viz-text font-mono">98******10</p>
                      <p className="text-[11px] text-on-surface-variant">Personal GSM number (Not an official corporate header)</p>
                    </div>
                  </div>
                </div>

                {/* Evidence Chip 3 */}
                <div className="p-3 rounded-lg bg-surface-subtle border border-border-divider">
                  <div className="flex items-center justify-between text-[11px] text-viz-neutral mb-1">
                    <span className="inline-flex items-center gap-1">
                      <span className="text-[9px] text-primary">●</span>
                      Extracted URL
                    </span>
                    <span className="font-mono text-[10px]">Shortened</span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <span className="material-symbols-outlined text-viz-warning text-[16px] shrink-0 mt-0.5">link</span>
                    <div className="min-w-0">
                      <p className="text-xs font-semibold text-viz-text font-mono truncate">bit.ly/elec-bill-update</p>
                      <p className="text-[11px] text-on-surface-variant">Points to fake utility gateway simulation</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Topological Evidence Path */}
              <div className="mt-4 p-3 rounded-lg bg-ground border border-border-divider">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="text-viz-neutral font-semibold">Triage journey status</span>
                  <span className="text-viz-primary font-bold">Checkpoint active</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-viz-neutral font-mono">
                  <span title="Observed SMS">● C01</span>
                  <span>→</span>
                  <span title="Analysis complete">● C03</span>
                  <span>→</span>
                  <span className="px-1.5 py-0.5 rounded bg-viz-primary text-white font-bold" title="Current location">
                    ◐ C05 Guard
                  </span>
                  <span>⇢</span>
                  <span className="text-viz-neutral" title="Next step">◌ C06</span>
                </div>
              </div>
            </div>

            {/* Deliberation Safety Card */}
            <div className="bg-surface rounded-xl p-5 border border-border-divider shadow-sm">
              <h4 className="text-xs font-bold text-viz-text mb-2 flex items-center gap-2">
                <span className="material-symbols-outlined text-viz-primary text-[18px]">psychology</span>
                <span>Psychological pressure check</span>
              </h4>
              <p className="text-xs text-on-surface-variant mb-3 leading-relaxed">
                Scammers rely on manufactured urgency to bypass your normal judgment. Legitimate electricity boards give formal 15-day registered notices before service interruption.
              </p>
              <div className="p-2.5 rounded-lg bg-surface-subtle border border-border-divider flex items-center justify-between text-xs">
                <span className="text-viz-text font-semibold">Official helpline format:</span>
                <span className="font-mono text-viz-primary font-bold">1912 (National Power)</span>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
