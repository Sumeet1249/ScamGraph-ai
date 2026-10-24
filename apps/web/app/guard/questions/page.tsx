'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function GuardContextQuestionsPage() {
  const router = useRouter();
  const [selectedUrgency, setSelectedUrgency] = useState<string>('strict_deadline');

  const handleContinue = () => {
    router.push('/guard/decision');
  };

  const urgencyOptions = [
    {
      id: 'strict_deadline',
      title: 'Yes — They gave a strict deadline',
      desc: 'Demanding payment within hours, warning of immediate shutoff, or insisting you must remain connected on the phone call.'
    },
    {
      id: 'no_pressure',
      title: 'No — There is no immediate deadline or time pressure',
      desc: 'Communication follows standard informational timing with no ultimatum or threatening immediate punitive consequences.'
    },
    {
      id: 'routine_penalty',
      title: 'Not sure — Mentioned a penalty, but no exact cutoff',
      desc: 'Vague mention of overdue dues or routine late charges without specific threat of immediate same-day cut-off or seizure.'
    }
  ];

  return (
    <div className="w-full bg-ground py-4 sm:py-8">
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6">
        {/* Top Navigation & Progress Header */}
        <section className="w-full pb-6 border-b border-border-divider">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-2">
              <Link
                href="/guard"
                className="inline-flex items-center gap-1 text-xs text-primary hover:text-primary-container font-semibold transition-colors"
              >
                <span className="material-symbols-outlined text-[16px]">arrow_back</span>
                <span>Guard · Question 2 of about 4</span>
              </Link>
            </div>
            <div className="flex items-center gap-2 self-start sm:self-auto">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-surface-subtle text-on-surface text-xs font-medium border border-border-divider">
                <span className="material-symbols-outlined text-[15px] text-viz-neutral">folder_open</span>
                <span className="font-mono">Case #SG-84920</span>
                <span className="text-viz-neutral">·</span>
                <span className="text-on-surface-variant">Pre-transaction intervention</span>
              </div>
            </div>
          </div>

          {/* Adaptive Progress Stepper */}
          <div className="w-full max-w-xl">
            <div className="flex items-center justify-between mb-1.5 text-xs">
              <span className="font-semibold text-primary">Step 2 of about 4</span>
              <span className="text-viz-neutral flex items-center gap-1 text-[11px]">
                <span className="material-symbols-outlined text-[14px]">tune</span>
                Adaptive cue: questions adjust based on your answers
              </span>
            </div>
            <div className="w-full h-1.5 bg-surface-subtle border border-border-divider rounded-full overflow-hidden flex">
              <div className="h-full bg-primary rounded-full transition-all duration-300 w-[50%]"></div>
            </div>
          </div>
        </section>

        {/* Two-Column Workspace Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mt-6 items-start pb-24">
          {/* Left Column: Deliberation Context Question (7 cols) */}
          <main className="lg:col-span-7 flex flex-col gap-6">
            <div className="flex flex-col gap-2">
              <div className="inline-flex items-center gap-1.5 self-start px-2.5 py-0.5 rounded bg-surface-subtle text-primary text-xs font-semibold border border-border-divider">
                <span className="material-symbols-outlined text-[15px]">priority_high</span>
                <span>Question 2 of ~4: Urgency &amp; Coercion Check</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-on-surface mt-1">
                Are they pressuring you to act right now?
              </h1>
              <p className="text-sm text-on-surface-variant leading-relaxed">
                Scammers frequently fabricate extreme urgency—like immediate power disconnections, legal warrants, or frozen assets—to prevent you from verifying claims independently.
              </p>
            </div>

            {/* Deliberation Interactive Options */}
            <div className="flex flex-col gap-3" role="radiogroup" aria-label="Urgency level options">
              {urgencyOptions.map((opt) => {
                const isSelected = selectedUrgency === opt.id;
                return (
                  <div
                    key={opt.id}
                    onClick={() => setSelectedUrgency(opt.id)}
                    className={`group relative flex items-start p-4 sm:p-5 rounded-xl cursor-pointer transition-all ${
                      isSelected
                        ? 'border-2 border-primary bg-selected-tint shadow-sm'
                        : 'border border-border-divider bg-surface hover:border-border-control hover:bg-surface-subtle'
                    }`}
                  >
                    <div
                      className={`flex items-center justify-center w-6 h-6 rounded-full mr-4 shrink-0 mt-0.5 ${
                        isSelected ? 'bg-primary text-white' : 'border border-border-control bg-surface'
                      }`}
                    >
                      {isSelected ? (
                        <span className="material-symbols-outlined text-[15px] font-bold">check</span>
                      ) : (
                        <div className="w-2.5 h-2.5 rounded-full bg-transparent"></div>
                      )}
                    </div>
                    <div className="flex flex-col min-w-0 pr-2 flex-1">
                      <span className={`text-sm font-semibold transition-colors ${isSelected ? 'text-primary' : 'text-on-surface group-hover:text-primary'}`}>
                        {opt.title}
                      </span>
                      <span className="text-xs text-on-surface-variant mt-1 leading-relaxed">
                        {opt.desc}
                      </span>
                    </div>
                    <span className={`inline-flex items-center shrink-0 self-center ${isSelected ? 'text-primary' : 'text-viz-neutral'}`}>
                      <span className="material-symbols-outlined text-[18px]">chevron_right</span>
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Dynamic Explainer Banner */}
            <section className="p-4 sm:p-5 rounded-xl bg-tone-warning-bg text-tone-warning-text border border-tone-warning-text/20 flex items-start gap-4">
              <div className="shrink-0 mt-0.5 w-6 h-6 rounded-full bg-viz-warning/20 flex items-center justify-center text-viz-warning">
                <span className="material-symbols-outlined text-[16px]">info</span>
              </div>
              <div className="flex flex-col gap-1">
                <h2 className="text-xs font-bold text-tone-warning-strong-text uppercase tracking-wide">
                  Why this matters in electricity &amp; utility notices
                </h2>
                <p className="text-xs text-tone-warning-text leading-relaxed">
                  In legitimate utility disputes, state electricity boards are legally bound to deliver a formal 15-day statutory notice by registered physical dispatch or scheduled billing cycle (§56 Electricity Act 2003). Demanding an instant same-day resolution via personal messaging apps is a signature coercion pattern designed to short-circuit analytical thinking.
                </p>
              </div>
            </section>

            {/* Secondary Navigation Helpers */}
            <div className="flex flex-wrap items-center justify-between gap-4 pt-2 text-xs">
              <button
                onClick={handleContinue}
                className="text-viz-neutral hover:text-on-surface underline underline-offset-4 decoration-border-control transition-colors"
                type="button"
              >
                Skip this question (keeps existing evidence)
              </button>
              <Link
                href="/rescue"
                className="inline-flex items-center gap-1 font-semibold text-tone-danger-text hover:text-tone-danger-strong-text transition-colors"
              >
                <span className="material-symbols-outlined text-[16px]">report_problem</span>
                <span>I already paid or shared something →</span>
              </Link>
            </div>
          </main>

          {/* Right Sidebar: Preserved Case Evidence & Assessment Preview (5 cols) */}
          <aside className="lg:col-span-5 flex flex-col gap-5 sticky top-28">
            {/* Preserved Case Evidence Card */}
            <div className="bg-surface rounded-xl border border-border-divider p-5 flex flex-col gap-4 shadow-sm">
              <div className="flex items-center justify-between pb-3 border-b border-border-divider">
                <div className="flex items-center gap-2">
                  <span className="material-symbols-outlined text-primary text-[18px]">shield_with_heart</span>
                  <h2 className="text-xs font-bold text-on-surface">Case context carried forward</h2>
                </div>
                <span className="text-xs text-viz-neutral">3 Signals</span>
              </div>
              <ul className="flex flex-col gap-3 list-none m-0 p-0">
                {/* Evidence Item 1 */}
                <li className="flex flex-col gap-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-viz-neutral uppercase tracking-wider">Observed SMS</span>
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-surface-subtle text-on-surface-variant border border-border-divider">
                      Original source
                    </span>
                  </div>
                  <p className="text-xs text-on-surface bg-surface-subtle p-2.5 rounded border border-border-divider leading-relaxed">
                    &ldquo;Electricity disconnection tonight at 9:30 PM due to unpaid previous month bill. Call officer immediately.&rdquo;
                  </p>
                </li>

                {/* Evidence Item 2 */}
                <li className="flex flex-col gap-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-viz-neutral uppercase tracking-wider">Target Action (Step 1)</span>
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-primary/10 text-primary">
                      You confirmed
                    </span>
                  </div>
                  <div className="flex items-center gap-2 p-2.5 rounded bg-surface-subtle border border-border-divider text-xs text-on-surface">
                    <span className="material-symbols-outlined text-primary text-[18px]">contactless</span>
                    <span className="font-medium">Approve payment request (UPI collect via PhonePe)</span>
                  </div>
                </li>

                {/* Evidence Item 3 */}
                <li className="flex flex-col gap-1 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-viz-neutral uppercase tracking-wider">Observed Contact</span>
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-surface-subtle text-on-surface-variant border border-border-divider">
                      System extracted
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-2.5 rounded bg-surface-subtle border border-border-divider text-xs">
                    <span className="font-mono text-xs text-on-surface font-semibold">98******10</span>
                    <span className="text-viz-neutral text-[11px]">Unregistered personal GSM</span>
                  </div>
                </li>
              </ul>
            </div>

            {/* Dynamic Assessment Preview Card */}
            <div className="bg-tone-warning-bg rounded-xl border border-tone-warning-text/20 p-5 flex flex-col gap-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex flex-col gap-0.5">
                  <span className="text-[10px] font-bold text-tone-warning-strong-text uppercase tracking-wider">
                    Signal Deliberation
                  </span>
                  <h3 className="text-xs font-bold text-tone-warning-strong-text">
                    Dynamic Assessment Posture
                  </h3>
                </div>
                <div className="w-7 h-7 rounded bg-tone-warning-strong-bg flex items-center justify-center text-viz-warning">
                  <span className="material-symbols-outlined text-[18px]">warning</span>
                </div>
              </div>
              <div className="p-3 rounded-lg bg-surface/90 border border-tone-warning-text/20 flex items-start gap-2">
                <span className="material-symbols-outlined text-viz-warning text-[18px] shrink-0 mt-0.5">change_circle</span>
                <p className="text-xs text-on-surface font-medium leading-relaxed">
                  Warning sign amplified: Psychological pressure confirmed with pending UPI collect request.
                </p>
              </div>
              <p className="text-[11px] text-on-surface-variant leading-relaxed">
                Assessment adjusts adaptively as signals are evaluated. ScamGraph evaluates behavioral topologies against known fraud playbooks.
              </p>
              <div className="pt-2 border-t border-tone-warning-text/20 flex items-start gap-2 text-viz-neutral">
                <span className="material-symbols-outlined text-[14px] shrink-0 mt-0.5">balance</span>
                <p className="text-[10px] leading-tight">
                  Guard provides independent deliberation assistance. ScamGraph does not process payments or freeze bank accounts on your behalf.
                </p>
              </div>
            </div>
          </aside>
        </div>

        {/* Sticky Bottom Action Bar */}
        <aside aria-label="Deliberation submission controls" className="fixed bottom-0 left-0 right-0 z-30 bg-surface/95 backdrop-blur-md border-t border-border-divider py-3.5 shadow-lg">
          <div className="max-w-[1200px] mx-auto px-4 sm:px-6 flex items-center justify-between gap-4">
            <Link
              href="/guard"
              className="inline-flex items-center justify-center h-10 px-4 rounded-lg border border-border-control text-xs font-medium text-on-surface hover:bg-surface-subtle transition-colors"
            >
              <span className="material-symbols-outlined text-[16px] mr-1">arrow_back</span>
              <span>Back</span>
            </Link>

            <div className="flex items-center gap-3">
              <Link
                href="/activity"
                className="hidden sm:inline-flex items-center justify-center h-10 px-4 text-xs font-medium text-viz-neutral hover:text-on-surface transition-colors"
              >
                I&apos;m not continuing
              </Link>
              <button
                onClick={handleContinue}
                className="inline-flex items-center justify-center h-10 px-6 rounded-full bg-primary text-white text-xs font-bold hover:bg-primary-container focus:ring-2 focus:ring-primary focus:ring-offset-2 transition-all shadow-sm"
                type="button"
              >
                <span>Continue</span>
                <span className="material-symbols-outlined text-[16px] ml-1">arrow_forward</span>
              </button>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
