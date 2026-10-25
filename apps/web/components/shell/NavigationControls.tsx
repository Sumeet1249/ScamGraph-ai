"use client";

import { useEffect, useState } from "react";
import { ArrowLeft, ArrowRight, Home } from "lucide-react";
import Link from "next/link";

/**
 * Floating Navigation Controls (Back & Forward buttons)
 * Positioned in the corner of the page with smooth startup-grade styling.
 */
export function NavigationControls() {
  const [canGoBack, setCanGoBack] = useState(false);

  useEffect(() => {
    // Check if browser has navigation history
    if (typeof window !== "undefined") {
      setCanGoBack(window.history.length > 1);
    }
  }, []);

  const handleBack = () => {
    if (typeof window !== "undefined") {
      window.history.back();
    }
  };

  const handleForward = () => {
    if (typeof window !== "undefined") {
      window.history.forward();
    }
  };

  return (
    <aside
      aria-label="Page Navigation Controls"
      className="fixed bottom-6 right-6 z-50 flex items-center gap-1.5 p-1.5 rounded-full bg-white/95 backdrop-blur-md border border-blue-200/90 shadow-lg shadow-blue-500/10 transition-all hover:shadow-xl hover:border-blue-400 group"
    >
      {/* Back Button */}
      <button
        type="button"
        onClick={handleBack}
        title="Go Back to Previous Page"
        aria-label="Back"
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-slate-700 hover:text-blue-700 hover:bg-blue-50 active:scale-95 transition-all"
      >
        <ArrowLeft className="w-3.5 h-3.5 text-blue-600 group-hover:-translate-x-0.5 transition-transform" />
        <span className="hidden sm:inline">Back</span>
      </button>

      {/* Divider */}
      <span className="w-px h-4 bg-blue-200/80" />

      {/* Home shortcut */}
      <Link
        href="/"
        title="Go to Home"
        aria-label="Home"
        className="p-1.5 rounded-full text-slate-600 hover:text-blue-700 hover:bg-blue-50 active:scale-95 transition-all"
      >
        <Home className="w-3.5 h-3.5" />
      </Link>

      {/* Divider */}
      <span className="w-px h-4 bg-blue-200/80" />

      {/* Forward Button */}
      <button
        type="button"
        onClick={handleForward}
        title="Go Forward to Next Page"
        aria-label="Forward"
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold text-slate-700 hover:text-blue-700 hover:bg-blue-50 active:scale-95 transition-all"
      >
        <span className="hidden sm:inline">Forward</span>
        <ArrowRight className="w-3.5 h-3.5 text-blue-600 group-hover:translate-x-0.5 transition-transform" />
      </button>
    </aside>
  );
}
