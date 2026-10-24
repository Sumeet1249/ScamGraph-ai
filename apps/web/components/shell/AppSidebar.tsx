"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { navGroups, activeItem } from "@/lib/nav";

export function AppSidebar() {
  const pathname = usePathname() || "/";
  const active = activeItem(pathname);
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="hidden md:block relative shrink-0 z-40 transition-[width] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
      style={{ width: isHovered ? 240 : 72 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <aside
        aria-label="Primary navigation"
        className={cn(
          "sg-rail fixed top-0 left-0 h-screen flex flex-col z-40 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] select-none",
          isHovered
            ? "w-60 shadow-2xl shadow-black/90 border-r border-border-strong bg-surface-raised backdrop-blur-xl"
            : "w-[72px] border-r border-border bg-surface-subtle",
        )}
      >
        {/* Logo */}
        <Link
          href="/"
          className={cn(
            "sg-rail__brand flex items-center h-16 border-b border-border transition-all overflow-hidden",
            isHovered ? "justify-start px-4 gap-3" : "justify-center px-0 gap-0",
          )}
          title="ScamGraph AI Dashboard"
        >
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-primary/15 border border-brand-primary/30 text-brand-primary transition-transform hover:scale-105 shadow-sm">
            <ShieldCheck className="h-5 w-5" strokeWidth={2.2} />
          </span>
          <span
            className={cn(
              "flex flex-col leading-none transition-all duration-200 whitespace-nowrap",
              isHovered
                ? "opacity-100 translate-x-0"
                : "opacity-0 -translate-x-3 pointer-events-none w-0 overflow-hidden",
            )}
          >
            <span className="text-sm font-bold tracking-tight text-text-primary">
              ScamGraph
            </span>
            <span className="text-[10px] font-semibold uppercase tracking-wider2 text-brand-primary">
              AI Platform
            </span>
          </span>
        </Link>

        {/* Nav groups */}
        <nav
          className={cn(
            "flex-1 overflow-y-auto scrollbar-thin py-3 space-y-4 overflow-x-hidden transition-all",
            isHovered ? "px-3" : "px-0",
          )}
        >
          {navGroups.map((group) => (
            <div key={group.label} className="space-y-1">
              <div
                className={cn(
                  "text-[10px] font-bold uppercase tracking-wider3 text-text-muted/80 transition-all duration-200 whitespace-nowrap overflow-hidden",
                  isHovered
                    ? "px-3 h-4 opacity-100 mb-1.5 mt-2"
                    : "px-0 h-0 opacity-0 mb-0 mt-0 pointer-events-none",
                )}
              >
                {group.label}
              </div>
              <ul className="space-y-1">
                {group.items.map((item) => {
                  const isActive = active?.href === item.href;
                  const Icon = item.icon;
                  return (
                    <li key={item.href}>
                      <Link
                        href={item.href}
                        aria-current={isActive ? "page" : undefined}
                        title={!isHovered ? item.label : item.hint}
                        className={cn(
                          "flex items-center rounded-xl h-10 transition-all duration-150 overflow-hidden group",
                          isHovered
                            ? "w-full px-3 justify-start gap-3"
                            : "w-10 mx-auto justify-center px-0 gap-0",
                          isActive
                            ? "bg-accent-soft text-accent border border-accent-line font-medium shadow-sm"
                            : "text-text-muted hover:text-text-primary hover:bg-surface-hover border border-transparent",
                        )}
                      >
                        <Icon
                          className={cn(
                            "h-5 w-5 shrink-0 transition-transform duration-150",
                            isActive ? "text-accent" : "text-text-muted group-hover:text-text-primary",
                            "group-hover:scale-110",
                          )}
                          strokeWidth={isActive ? 2.2 : 1.75}
                        />
                        <span
                          className={cn(
                            "text-body-sm font-medium whitespace-nowrap transition-all duration-200",
                            isHovered
                              ? "opacity-100 translate-x-0 ml-0"
                              : "opacity-0 -translate-x-2 pointer-events-none w-0 overflow-hidden",
                          )}
                        >
                          {item.label}
                        </span>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </nav>

        {/* Status footer */}
        <div
          className={cn(
            "border-t border-border py-3.5 transition-all overflow-hidden flex items-center",
            isHovered ? "justify-between px-4" : "justify-center px-0",
          )}
        >
          <div className="flex items-center gap-2.5 text-[11px] text-text-muted font-mono whitespace-nowrap">
            <span className="sg-dot shrink-0" data-tone="neutral" aria-hidden />
            <span
              className={cn(
                "transition-all duration-200 truncate",
                isHovered
                  ? "opacity-100 translate-x-0"
                  : "opacity-0 -translate-x-2 w-0 overflow-hidden pointer-events-none",
              )}
            >
              Engine offline
            </span>
          </div>
        </div>
      </aside>
    </div>
  );
}
