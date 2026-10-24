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
  const [hoveredItemHref, setHoveredItemHref] = useState<string | null>(null);

  return (
    <div
      className="hidden md:block relative shrink-0 z-40 transition-[width] duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
      style={{ width: isHovered ? 240 : 72 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setHoveredItemHref(null);
      }}
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
                  const isSubActive = item.subItems?.some(
                    (s) => pathname === s.href || pathname.startsWith(s.href),
                  );
                  const isActive = active?.href === item.href || isSubActive;
                  const isItemHovered = hoveredItemHref === item.href;
                  const showSub = (isItemHovered || isSubActive) && !!item.subItems;
                  const Icon = item.icon;

                  return (
                    <li
                      key={item.href}
                      className="relative"
                      onMouseEnter={() => setHoveredItemHref(item.href)}
                      onMouseLeave={() => setHoveredItemHref(null)}
                    >
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
                            "text-body-sm font-medium whitespace-nowrap transition-all duration-200 flex-1 flex items-center justify-between",
                            isHovered
                              ? "opacity-100 translate-x-0 ml-0"
                              : "opacity-0 -translate-x-2 pointer-events-none w-0 overflow-hidden",
                          )}
                        >
                          <span>{item.label}</span>
                          {item.subItems && (
                            <span
                              className={cn(
                                "w-1.5 h-1.5 rounded-full transition-colors",
                                isSubActive ? "bg-brand-primary" : "bg-text-muted/40 group-hover:bg-brand-primary",
                              )}
                              title={`${item.subItems[0].label}`}
                            />
                          )}
                        </span>
                      </Link>

                      {/* Sub dot indicator in collapsed mode when sub-items exist */}
                      {!isHovered && item.subItems && isSubActive && (
                        <div className="w-1.5 h-1.5 rounded-full bg-brand-primary mx-auto -mt-1 mb-0.5 shadow-[0_0_6px_rgba(11,98,86,0.8)]" />
                      )}

                      {/* Expanded sub-item with small sub dot below parent */}
                      {isHovered && showSub && item.subItems && (
                        <div className="pl-6 pr-2 pt-1 pb-1 space-y-1 animate-in fade-in slide-in-from-top-1 duration-150">
                          {item.subItems.map((sub) => {
                            const isThisSubActive =
                              pathname === sub.href || pathname.startsWith(sub.href);
                            return (
                              <Link
                                key={sub.href}
                                href={sub.href}
                                className={cn(
                                  "flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-xs transition-all group/sub",
                                  isThisSubActive
                                    ? "bg-brand-primary/15 text-brand-primary font-semibold"
                                    : "text-text-muted hover:text-text-primary hover:bg-surface-hover",
                                )}
                                title={sub.hint}
                              >
                                {/* Small sub dot */}
                                <span
                                  className={cn(
                                    "w-1.5 h-1.5 rounded-full shrink-0 transition-transform group-hover/sub:scale-125",
                                    isThisSubActive
                                      ? "bg-brand-primary shadow-[0_0_6px_rgba(11,98,86,0.8)]"
                                      : "bg-text-muted/60 group-hover/sub:bg-brand-primary",
                                  )}
                                />
                                <span className="truncate">{sub.label}</span>
                              </Link>
                            );
                          })}
                        </div>
                      )}

                      {/* Collapsed flyout when hovered on 72px rail */}
                      {!isHovered && isItemHovered && item.subItems && (
                        <div className="absolute left-[70px] top-0 z-50 min-w-[175px] p-2 bg-surface-raised border border-border-strong rounded-xl shadow-2xl backdrop-blur-xl animate-in fade-in duration-150">
                          <div className="px-2 py-1 text-[10px] uppercase font-bold text-text-muted border-b border-border/50 mb-1">
                            {item.label}
                          </div>
                          {item.subItems.map((sub) => {
                            const isThisSubActive =
                              pathname === sub.href || pathname.startsWith(sub.href);
                            return (
                              <Link
                                key={sub.href}
                                href={sub.href}
                                className={cn(
                                  "flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs transition-colors",
                                  isThisSubActive
                                    ? "bg-brand-primary/15 text-brand-primary font-semibold"
                                    : "text-text-muted hover:text-text-primary hover:bg-surface-hover",
                                )}
                              >
                                <span className="w-1.5 h-1.5 rounded-full bg-brand-primary shrink-0 shadow-[0_0_6px_rgba(11,98,86,0.8)]" />
                                <span className="truncate">{sub.label}</span>
                              </Link>
                            );
                          })}
                        </div>
                      )}
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
            <span className="sg-dot shrink-0" data-tone="live" aria-hidden />
            <span
              className={cn(
                "transition-all duration-200 truncate text-[11px] font-mono",
                isHovered
                  ? "opacity-100 translate-x-0 text-text-secondary"
                  : "opacity-0 -translate-x-2 w-0 overflow-hidden pointer-events-none",
              )}
            >
              Node sync: Active
            </span>
          </div>
        </div>
      </aside>
    </div>
  );
}
