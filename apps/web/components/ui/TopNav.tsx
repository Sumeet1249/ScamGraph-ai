import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";
import { ChevronRight } from "lucide-react";

/** Top navigation bar — fixed header. */
export interface TopNavProps {
  children: ReactNode;
  className?: string;
}

export function TopNav({ children, className }: TopNavProps) {
  return (
    <header
      className={cn(
        "fixed top-0 right-0 left-0 md:left-56 h-14 bg-surface-1 border-b border-border",
        "flex items-center justify-between px-4 md:px-6 gap-4 z-40",
        className,
      )}
    >
      {children}
    </header>
  );
}

/** Breadcrumb navigation. */
export interface BreadcrumbProps {
  items: Array<{ label: string; href?: string }>;
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn("flex items-center gap-2", className)} aria-label="Breadcrumb">
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center gap-2">
          {idx > 0 && (
            <ChevronRight className="h-4 w-4 text-text-muted flex-shrink-0" aria-hidden />
          )}
          {item.href ? (
            <a
              href={item.href}
              className="text-body-sm text-text-secondary hover:text-text-primary transition-colors"
            >
              {item.label}
            </a>
          ) : (
            <span className="text-body-sm text-text-primary font-semibold">
              {item.label}
            </span>
          )}
        </div>
      ))}
    </nav>
  );
}

/** Top nav spacer (flex-grow). */
export function TopNavSpacer() {
  return <div className="flex-1" />;
}

/** Top nav section for actions/controls on the right. */
interface TopNavActionsProps {
  children: ReactNode;
  className?: string;
}

export function TopNavActions({ children, className }: TopNavActionsProps) {
  return (
    <div className={cn("flex items-center gap-2", className)}>
      {children}
    </div>
  );
}

/** Environment badge (dev/staging/prod indicator). */
export interface EnvBadgeProps {
  env?: "dev" | "staging" | "prod";
  className?: string;
}

export function EnvBadge({ env = "dev", className }: EnvBadgeProps) {
  const envMap = {
    dev: "bg-surface-2 text-info",
    staging: "bg-surface-2 text-warning",
    prod: "bg-surface-2 text-text-muted",
  };
  return (
    <span
      className={cn(
        "text-label px-2 py-1 rounded-md border border-border",
        envMap[env],
        className,
      )}
    >
      {env.toUpperCase()}
    </span>
  );
}
