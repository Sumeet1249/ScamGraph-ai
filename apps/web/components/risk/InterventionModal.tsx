"use client";

import React, { useState, useEffect } from "react";
import { ShieldAlert, AlertTriangle, Clock, ArrowRight, X } from "lucide-react";

interface InterventionModalProps {
  isOpen: boolean;
  onClose: () => void;
  bannerTitle?: string;
  bannerMessage?: string;
  frictionDelaySeconds?: number;
  reasonCodes?: string[];
}

export function InterventionModal({
  isOpen,
  onClose,
  bannerTitle = "High Risk Pre-Payment Interlock",
  bannerMessage = "Multi-source verified threat detected directly before payment intent.",
  frictionDelaySeconds = 10,
  reasonCodes = [],
}: InterventionModalProps) {
  const [secondsRemaining, setSecondsRemaining] = useState<number>(frictionDelaySeconds);

  useEffect(() => {
    if (!isOpen) {
      setSecondsRemaining(frictionDelaySeconds);
      return;
    }

    setSecondsRemaining(frictionDelaySeconds);
    const interval = setInterval(() => {
      setSecondsRemaining((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isOpen, frictionDelaySeconds]);

  if (!isOpen) return null;

  const progressPercent = ((frictionDelaySeconds - secondsRemaining) / frictionDelaySeconds) * 100;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-xl rounded-2xl bg-surface-raised border border-danger/30 p-6 sm:p-8 shadow-2xl text-text-primary space-y-6">
        {/* Header Alert */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start space-x-3.5">
            <div className="w-12 h-12 rounded-xl bg-danger/15 border border-danger/30 flex items-center justify-center text-danger shrink-0">
              <ShieldAlert className="w-6 h-6 animate-pulse" />
            </div>
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="px-2.5 py-0.5 rounded-full bg-danger/15 text-danger text-[10px] font-bold uppercase tracking-wider font-mono border border-danger/30">
                  Adaptive Friction Interlock
                </span>
                <span className="px-2 py-0.5 rounded-full bg-warning/15 text-warning text-[10px] font-bold uppercase tracking-wider font-mono border border-warning/30">
                  Simulation Only
                </span>
              </div>
              <h2 className="text-xl font-bold text-text-primary tracking-tight">
                {bannerTitle}
              </h2>
              <p className="text-[11px] text-warning/90 font-mono">
                Simulation warning only — ScamGraph never blocks real payments automatically.
              </p>
            </div>
          </div>

          {/* Circular Countdown Gauge */}
          <div className="flex flex-col items-center justify-center shrink-0">
            <div className="relative w-12 h-12 flex items-center justify-center">
              <svg className="w-12 h-12 -rotate-90">
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="#3E322C"
                  strokeWidth="3"
                  fill="transparent"
                />
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="#EC6B65"
                  strokeWidth="3"
                  fill="transparent"
                  strokeDasharray="125.6"
                  strokeDashoffset={125.6 - (125.6 * progressPercent) / 100}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-linear"
                />
              </svg>
              <span className="absolute font-mono font-bold text-xs text-text-primary">
                {secondsRemaining}s
              </span>
            </div>
          </div>
        </div>

        <p className="text-xs sm:text-sm text-text-primary leading-relaxed bg-danger/10 border border-danger/25 p-3.5 rounded-xl">
          {bannerMessage}
        </p>

        {/* Reason Codes Provenance List */}
        {reasonCodes.length > 0 && (
          <div className="space-y-2">
            <div className="text-[11px] font-bold uppercase tracking-wider text-text-muted flex items-center space-x-1.5">
              <AlertTriangle className="w-3.5 h-3.5 text-warning" />
              <span>Corroborated Multi-Source Findings:</span>
            </div>
            <div className="rounded-xl bg-surface-inset border border-border-input p-3.5 space-y-2 max-h-44 overflow-y-auto font-mono text-xs text-text-secondary">
              {reasonCodes.map((rc, idx) => (
                <div key={idx} className="flex items-start space-x-2">
                  <span className="text-danger font-bold shrink-0">[{idx + 1}]</span>
                  <span className="break-all text-[11px] leading-relaxed">{rc}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-2">
          <button
            disabled={secondsRemaining > 0}
            onClick={onClose}
            className={`w-full py-3.5 px-6 rounded-xl text-xs font-bold uppercase tracking-wider transition-all flex items-center justify-center space-x-2 ${
              secondsRemaining > 0
                ? "bg-surface text-text-muted border border-border-input cursor-not-allowed shadow-none"
                : "bg-danger text-on-brand hover:brightness-110 active:scale-[0.98] shadow-none"
            }`}
          >
            {secondsRemaining > 0 ? (
              <>
                <Clock className="w-4 h-4 animate-spin text-text-muted" />
                <span>Interlocked ({secondsRemaining}s remaining to review)</span>
              </>
            ) : (
              <>
                <span>I Understand the Risk — Consciously Proceed</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
