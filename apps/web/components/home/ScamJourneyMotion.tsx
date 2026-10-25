"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Play,
  Pause,
  RotateCcw,
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  PhoneCall,
  MessageSquare,
  CreditCard,
  UserCheck,
  Sparkles,
} from "lucide-react";

interface StageInfo {
  id: number;
  title: string;
  subtitle: string;
  category: "observed" | "coercion" | "barrier" | "fraud";
  badge: string;
  badgeTone: string;
  icon: any;
  exampleSnippet: {
    type: "sms" | "call" | "threat" | "barrier" | "upi";
    sender: string;
    text: string;
    warning?: string;
  };
  attackerTactic: string;
  psychologicalTrigger: string;
  defenseAction: string;
}

const STAGES: StageInfo[] = [
  {
    id: 1,
    title: "First Contact",
    subtitle: "SMS / WhatsApp / Call",
    category: "observed",
    badge: "Observed Stage • Entry Vector",
    badgeTone: "bg-blue-50 text-blue-700 border-blue-200",
    icon: MessageSquare,
    exampleSnippet: {
      type: "sms",
      sender: "SMS · +91 99999 99999",
      text: "Your electricity connection will be disconnected today at 9:30 PM due to unpaid dues. Update payment immediately: http://city-power-bill.test",
      warning: "Unverified sender, suspicious domain (.test)",
    },
    attackerTactic: "Mass automated broadcast with spoofed utility or bank pretext to cast a wide net.",
    psychologicalTrigger: "Curiosity and routine compliance — victim assumes a genuine billing oversight.",
    defenseAction: "Do NOT click links in unsolicited messages. Check bill status via official provider app.",
  },
  {
    id: 2,
    title: "Fake Identity",
    subtitle: "Posing as Bank / Police",
    category: "observed",
    badge: "Observed Stage • Authority Spoofing",
    badgeTone: "bg-blue-50 text-blue-700 border-blue-200",
    icon: UserCheck,
    exampleSnippet: {
      type: "call",
      sender: "Voice Call · Officer Rahul Sharma",
      text: "I am Inspector Sharma from the Cyber Crime Cell. A SIM registered under your Aadhaar is flagged in a 2.4 Crore laundering syndicate.",
      warning: "Fake badge copy & background radio siren effects",
    },
    attackerTactic: "Impersonates TRAI, CBI, or bank manager using official legal jargon and forged departmental seals.",
    psychologicalTrigger: "Authority bias — natural impulse to respect official law enforcement orders.",
    defenseAction: "Hang up immediately. Government agencies never interrogate or issue warrants over phone or video calls.",
  },
  {
    id: 3,
    title: "Panic & Urgency",
    subtitle: '"Act in 2 Hours!"',
    category: "coercion",
    badge: "Coercion Point • Cognitive Overload",
    badgeTone: "bg-amber-50 text-amber-800 border-amber-200",
    icon: AlertTriangle,
    exampleSnippet: {
      type: "threat",
      sender: "High-Pressure Demand",
      text: "Stay on the call. Do NOT speak to family members or consult anyone. You have 15 minutes to clear your name before our tactical arrest team arrives.",
      warning: "Artificial deadline + enforced isolation",
    },
    attackerTactic: "Fabricates emergency deadlines and insists on strict secrecy to prevent independent verification.",
    psychologicalTrigger: "Fight-or-flight panic — fear of public arrest or immediate service disruption blocks rational analysis.",
    defenseAction: "Breathe and break the spell. Urgency + isolation is the #1 telltale hallmark of criminal fraud.",
  },
  {
    id: 4,
    title: "Payment Request",
    subtitle: "UPI / QR / Phishing Link",
    category: "fraud",
    badge: "Fraud Intent • Irreversible Loss",
    badgeTone: "bg-rose-50 text-rose-800 border-rose-200",
    icon: CreditCard,
    exampleSnippet: {
      type: "upi",
      sender: "Simulated UPI Transfer Mandate",
      text: "Transfer ₹1,840 to 'escrow.clearance@okhdfcbank' to verify account. Refundable in 10 minutes upon clearance.",
      warning: "⚠️ Personal mule VPA with irreversible instant debit",
    },
    attackerTactic: "Directs victim to approve instant UPI debits or enter UPI PIN into a fake escrow account.",
    psychologicalTrigger: "Sunk-cost relief — victim pays believing it resolves the manufactured emergency.",
    defenseAction: "Never enter UPI PIN to receive money or clear legal threats. UPI payments cannot be reversed once authorized.",
  },
];

export function ScamJourneyMotion() {
  const [activeStageId, setActiveStageId] = useState<number>(1);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [showBarrierHighlight, setShowBarrierHighlight] = useState<boolean>(false);
  const [progressPercent, setProgressPercent] = useState<number>(0);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Auto-play state machine
  useEffect(() => {
    if (!isPlaying) {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    setProgressPercent(0);
    const duration = 4500; // 4.5 seconds per stage
    const tick = 50;

    progressIntervalRef.current = setInterval(() => {
      setProgressPercent((prev) => {
        if (prev >= 100) return 100;
        return prev + (tick / duration) * 100;
      });
    }, tick);

    timerRef.current = setTimeout(() => {
      setActiveStageId((curr) => {
        if (curr === 3 && !showBarrierHighlight) {
          // Pause briefly at the barrier
          setShowBarrierHighlight(true);
          return 3;
        }
        setShowBarrierHighlight(false);
        return curr >= 4 ? 1 : curr + 1;
      });
    }, duration);

    return () => {
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isPlaying, activeStageId, showBarrierHighlight]);

  const handleSelectStage = (id: number) => {
    setActiveStageId(id);
    setShowBarrierHighlight(false);
    setProgressPercent(0);
  };

  const handleTogglePlay = () => {
    setIsPlaying((prev) => !prev);
  };

  const handleRestart = () => {
    setActiveStageId(1);
    setShowBarrierHighlight(false);
    setProgressPercent(0);
    setIsPlaying(true);
  };

  const currentStage = STAGES.find((s) => s.id === activeStageId) || STAGES[0];

  return (
    <div className="w-full bg-white rounded-2xl border border-blue-100 p-6 sm:p-8 shadow-sm overflow-hidden">
      {/* ── 1. Header & Live Motion Controls ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-600 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-600" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-blue-700">
              Interactive Attack Sequence Reconstruction
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Watch how psychological coercion escalates from inbound message to irreversible transaction.
          </p>
        </div>

        {/* Player Controls */}
        <div className="flex items-center gap-2 self-start sm:self-auto bg-slate-50 p-1.5 rounded-xl border border-slate-200/80">
          <button
            type="button"
            onClick={handleTogglePlay}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-slate-700 hover:text-blue-700 hover:bg-white transition-all shadow-none hover:shadow-sm"
            title={isPlaying ? "Pause journey playback" : "Resume journey playback"}
          >
            {isPlaying ? (
              <>
                <Pause className="h-3.5 w-3.5 text-blue-600" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 text-blue-600 fill-current" />
                <span>Play Motion</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={handleRestart}
            className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-white transition-all"
            title="Restart from Stage 1"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* ── 2. The Stepper Track with Traveling Motion Beam ── */}
      <div className="relative py-8 overflow-x-auto">
        <div className="min-w-[760px] flex items-center justify-between relative px-4">
          {/* Animated Connecting Track 1 to 2 */}
          <div className="absolute top-[28px] left-[13%] right-[66%] h-[3px] bg-slate-100 -z-0">
            <div
              className={`h-full bg-gradient-to-r from-blue-600 to-blue-500 transition-all duration-700 ${
                activeStageId >= 2 ? "w-full" : "w-0"
              }`}
            />
            {isPlaying && activeStageId === 1 && (
              <div className="absolute top-1/2 -translate-y-1/2 h-2 w-2 rounded-full bg-blue-600 shadow-[0_0_8px_rgba(37,99,235,0.8)] animate-pulse" />
            )}
          </div>

          {/* Animated Connecting Track 2 to 3 */}
          <div className="absolute top-[28px] left-[37%] right-[42%] h-[3px] bg-slate-100 -z-0">
            <div
              className={`h-full bg-gradient-to-r from-blue-500 to-amber-500 transition-all duration-700 ${
                activeStageId >= 3 ? "w-full" : "w-0"
              }`}
            />
          </div>

          {/* Animated Connecting Track 3 to 4 (Crosses Intervention Boundary) */}
          <div className="absolute top-[28px] left-[61%] right-[14%] h-[3px] bg-slate-100 -z-0">
            <div
              className={`h-full bg-gradient-to-r from-amber-500 via-rose-400 to-rose-600 transition-all duration-700 ${
                activeStageId >= 4 ? "w-full" : "w-0"
              }`}
            />
          </div>

          {/* Stage 1 Node */}
          <button
            type="button"
            onClick={() => handleSelectStage(1)}
            className={`flex flex-col items-center text-center z-10 w-36 transition-all group focus:outline-none ${
              activeStageId === 1 ? "scale-105" : "opacity-80 hover:opacity-100"
            }`}
          >
            <div className="relative mb-2">
              {activeStageId === 1 && (
                <span className="absolute -inset-1.5 rounded-full bg-blue-600/20 animate-ping" />
              )}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shadow-sm transition-all ${
                  activeStageId === 1
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : activeStageId > 1
                    ? "bg-blue-600 text-white"
                    : "bg-blue-600 text-white"
                }`}
              >
                1
              </div>
            </div>
            <span
              className={`text-xs font-bold transition-colors ${
                activeStageId === 1 ? "text-blue-700" : "text-slate-900"
              }`}
            >
              First Contact
            </span>
            <span className="text-[10px] text-slate-500 mt-0.5">SMS / WhatsApp / Call</span>
          </button>

          {/* Stage 2 Node */}
          <button
            type="button"
            onClick={() => handleSelectStage(2)}
            className={`flex flex-col items-center text-center z-10 w-36 transition-all group focus:outline-none ${
              activeStageId === 2 ? "scale-105" : "opacity-80 hover:opacity-100"
            }`}
          >
            <div className="relative mb-2">
              {activeStageId === 2 && (
                <span className="absolute -inset-1.5 rounded-full bg-blue-600/20 animate-ping" />
              )}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shadow-sm transition-all ${
                  activeStageId === 2
                    ? "bg-blue-600 text-white ring-4 ring-blue-100"
                    : activeStageId > 2
                    ? "bg-blue-600 text-white"
                    : "bg-blue-600/80 text-white"
                }`}
              >
                2
              </div>
            </div>
            <span
              className={`text-xs font-bold transition-colors ${
                activeStageId === 2 ? "text-blue-700" : "text-slate-900"
              }`}
            >
              Fake Identity
            </span>
            <span className="text-[10px] text-slate-500 mt-0.5">Posing as Bank / Police</span>
          </button>

          {/* Stage 3 Node */}
          <button
            type="button"
            onClick={() => handleSelectStage(3)}
            className={`flex flex-col items-center text-center z-10 w-36 transition-all group focus:outline-none ${
              activeStageId === 3 ? "scale-105" : "opacity-80 hover:opacity-100"
            }`}
          >
            <div className="relative mb-2">
              {activeStageId === 3 && (
                <span className="absolute -inset-1.5 rounded-full bg-amber-500/25 animate-ping" />
              )}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shadow-sm transition-all ${
                  activeStageId === 3
                    ? "border-2 border-amber-500 bg-amber-500 text-white ring-4 ring-amber-100"
                    : "border-2 border-amber-500 bg-amber-50 text-amber-700"
                }`}
              >
                3
              </div>
            </div>
            <span
              className={`text-xs font-bold transition-colors ${
                activeStageId === 3 ? "text-amber-700 font-extrabold" : "text-amber-700"
              }`}
            >
              Panic &amp; Urgency
            </span>
            <span className="text-[10px] text-amber-600 font-semibold mt-0.5">&ldquo;Act in 2 Hours!&rdquo;</span>
          </button>

          {/* ── Protection Boundary Barrier with Interactive Shield ── */}
          <div className="flex flex-col items-center px-2 z-20 relative">
            <div
              className={`h-11 w-[3px] rounded-full transition-all duration-300 ${
                showBarrierHighlight || activeStageId === 3
                  ? "bg-rose-500 shadow-[0_0_12px_rgba(244,63,94,0.9)] scale-y-110"
                  : "bg-rose-400"
              }`}
            />
            <div className="mt-1 relative">
              <span
                className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border whitespace-nowrap transition-all duration-300 flex items-center gap-1 ${
                  showBarrierHighlight || activeStageId === 3
                    ? "text-rose-800 bg-rose-100 border-rose-300 shadow-md ring-2 ring-rose-200 animate-pulse"
                    : "text-rose-700 bg-rose-50 border-rose-200"
                }`}
              >
                <ShieldCheck className="h-3 w-3 text-rose-600" />
                Stop Here Before Paying
              </span>
            </div>
          </div>

          {/* Stage 4 Node */}
          <button
            type="button"
            onClick={() => handleSelectStage(4)}
            className={`flex flex-col items-center text-center z-10 w-36 transition-all group focus:outline-none ${
              activeStageId === 4 ? "scale-105" : "opacity-80 hover:opacity-100"
            }`}
          >
            <div className="relative mb-2">
              {activeStageId === 4 && (
                <span className="absolute -inset-1.5 rounded-full bg-rose-500/25 animate-ping" />
              )}
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs shadow-sm transition-all ${
                  activeStageId === 4
                    ? "border-2 border-dashed border-rose-500 bg-rose-500 text-white ring-4 ring-rose-100"
                    : "border-2 border-dashed border-rose-400 bg-rose-50 text-rose-700"
                }`}
              >
                4
              </div>
            </div>
            <span
              className={`text-xs transition-colors ${
                activeStageId === 4 ? "font-bold text-rose-800" : "font-semibold text-rose-800"
              }`}
            >
              Payment Request
            </span>
            <span className="text-[10px] text-rose-600 mt-0.5">UPI / QR / Phishing Link</span>
          </button>
        </div>

        {/* Live Stage Timer Progress Indicator */}
        {isPlaying && (
          <div className="w-full max-w-md mx-auto mt-6 h-1 bg-slate-100 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-75 rounded-full ${
                activeStageId === 3
                  ? "bg-amber-500"
                  : activeStageId === 4
                  ? "bg-rose-500"
                  : "bg-blue-600"
              }`}
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        )}
      </div>

      {/* ── 3. Dynamic Interactive Stage Showcase Box ── */}
      <div className="mt-4 rounded-xl border border-slate-200/90 bg-gradient-to-b from-slate-50/80 to-white p-5 sm:p-6 transition-all animate-fadeIn">
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-6 items-start">
          {/* Left: Psychological Manipulation & Tactics */}
          <div className="space-y-3.5">
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full border ${currentStage.badgeTone}`}
              >
                {currentStage.badge}
              </span>
              <span className="text-[11px] font-mono text-slate-500">
                Stage {currentStage.id} of 4 in Scam Attack Graph
              </span>
            </div>

            <h3 className="text-base sm:text-lg font-bold text-slate-900 leading-snug">
              {currentStage.title}: {currentStage.subtitle}
            </h3>

            <p className="text-xs text-slate-600 leading-relaxed">
              <strong className="text-slate-800">What Happens: </strong>
              {currentStage.attackerTactic}
            </p>

            <div className="rounded-lg bg-blue-50/60 border border-blue-100 p-3 text-xs text-slate-700 leading-relaxed">
              <strong className="text-blue-900">Psychological Lever: </strong>
              {currentStage.psychologicalTrigger}
            </div>

            {/* Defense Recommendation Action */}
            <div className="rounded-lg bg-emerald-50/70 border border-emerald-200/80 p-3 text-xs text-emerald-900 leading-relaxed flex items-start gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-600 flex-shrink-0 mt-0.5" />
              <div>
                <strong className="text-emerald-950">How to Stop It Here: </strong>
                {currentStage.defenseAction}
              </div>
            </div>
          </div>

          {/* Right: Live Mock Artifact Preview (SMS, Call, Threat, UPI) */}
          <div className="space-y-3">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
              Live Stimulus Artifact Example
            </span>

            <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm space-y-2.5">
              <div className="flex items-center justify-between pb-2 border-b border-slate-100">
                <span className="text-xs font-bold text-slate-800 font-mono">
                  {currentStage.exampleSnippet.sender}
                </span>
                <span className="text-[10px] font-semibold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-100">
                  Phishing Payload
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border-l-4 border-l-amber-500 text-xs text-slate-800 leading-relaxed font-sans whitespace-pre-line">
                &ldquo;{currentStage.exampleSnippet.text}&rdquo;
              </div>

              {currentStage.exampleSnippet.warning && (
                <div className="text-[11px] text-rose-700 font-medium flex items-center gap-1.5 pt-1">
                  <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
                  <span>{currentStage.exampleSnippet.warning}</span>
                </div>
              )}
            </div>

            {/* Stage Quick Switch Buttons */}
            <div className="flex items-center gap-1.5 pt-1">
              {STAGES.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => handleSelectStage(s.id)}
                  className={`flex-1 py-1.5 text-center text-[11px] font-semibold rounded-lg border transition-all ${
                    activeStageId === s.id
                      ? "bg-slate-900 text-white border-slate-900 shadow-sm"
                      : "bg-white text-slate-600 border-slate-200 hover:bg-slate-50"
                  }`}
                >
                  Stage {s.id}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── 4. Legend & Verification Assurance Footer ── */}
      <div className="mt-6 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between text-[11px] text-slate-500 gap-4">
        <div className="flex items-center gap-4 flex-wrap">
          <span className="inline-flex items-center gap-1.5 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600 shadow-sm" /> Observed Stage
          </span>
          <span className="inline-flex items-center gap-1.5 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm" /> Coercion Point
          </span>
          <span className="inline-flex items-center gap-1.5 font-medium">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm" /> Fraud Intent
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-blue-700 font-semibold">
            Scanning early stops the scam before any money leaves your account.
          </span>
          <Link
            href="/check"
            className="inline-flex items-center gap-1 text-[11px] font-bold text-blue-700 hover:text-blue-900 underline underline-offset-2 ml-1"
          >
            Check Now
            <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
