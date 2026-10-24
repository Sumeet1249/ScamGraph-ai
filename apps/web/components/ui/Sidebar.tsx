import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

/** Sidebar container — fixed left column. */
export interface SidebarProps {
  children: ReactNode;
  className?: string;
}

export function Sidebar({ children, className }: SidebarProps) {
  return (
    <aside
      className={cn(
        "hidden md:flex flex-col w-56 bg-surface-1 border-r border-border h-screen fixed left-0 top-0",
        "overflow-y-auto",
        className,
      )}
    >
      {children}
    </aside>
  );
}

/** Sidebar header — typically logo/branding. */
export function SidebarHeader({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "px-4 py-4 border-b border-border-subtle",
        "flex items-center gap-2",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Sidebar section — grouped nav items. */
export interface SidebarSectionProps {
  label?: string;
  children: ReactNode;
  className?: string;
}

export function SidebarSection({ label, children, className }: SidebarSectionProps) {
  return (
    <nav className={cn("flex flex-col gap-2 px-3 py-3", className)}>
      {label && (
        <div className="px-2 py-1.5 text-label text-text-muted uppercase">
          {label}
        </div>
      )}
      <div className="flex flex-col gap-1">{children}</div>
    </nav>
  );
}

/** Sidebar nav item — link with optional icon and active state. */
export interface SidebarItemProps {
  href?: string;
  label: string;
  icon?: ReactNode;
  active?: boolean;
  onClick?: () => void;
  className?: string;
}

export function SidebarItem({
  href,
  label,
  icon,
  active = false,
  onClick,
  className,
}: SidebarItemProps) {
  const Comp = href ? "a" : "button";
  return (
    <Comp
      href={href}
      onClick={onClick}
      className={cn(
        "flex items-center gap-2.5 px-3 py-2 rounded-lg text-body-sm transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-primary",
        active
          ? "bg-surface-2 text-brand-primary font-semibold"
          : "text-text-secondary hover:text-text-primary hover:bg-surface-2",
        className,
      )}
    >
      {icon && <span className="h-4 w-4 flex-shrink-0">{icon}</span>}
      <span className="truncate">{label}</span>
    </Comp>
  );
}

/** Sidebar footer — typically status/metadata. */
export function SidebarFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={cn(
        "mt-auto px-4 py-3 border-t border-border-subtle",
        "flex items-center justify-between gap-2",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Spacer — flex-grow to push footer down. */
export function SidebarSpacer() {
  return <div className="flex-1" />;
}
