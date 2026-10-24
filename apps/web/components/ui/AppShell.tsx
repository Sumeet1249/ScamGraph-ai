import type { ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

/** AppShell layout — manages fixed header/sidebar + scrollable content. */
export interface AppShellProps {
  /** Main content area. */
  children: ReactNode;
  /** Optional sidebar component. */
  sidebar?: ReactNode;
  /** Optional top navigation. */
  topNav?: ReactNode;
  /** Additional className for main content. */
  className?: string;
}

export function AppShell({ children, sidebar, topNav, className }: AppShellProps) {
  return (
    <div className="bg-background text-text-primary min-h-screen flex flex-col">
      {/* Fixed top nav */}
      {topNav && <div>{topNav}</div>}

      <div className="flex flex-1 gap-0">
        {/* Fixed sidebar */}
        {sidebar && <div>{sidebar}</div>}

        {/* Main scrollable content */}
        <main
          className={cn(
            "flex-1 overflow-auto",
            "pt-14 md:pt-14", // Offset for top nav height
            "md:ml-0 ml-0", // Sidebar handled by position: fixed
            className,
          )}
        >
          {children}
        </main>
      </div>
    </div>
  );
}

/** Content container — responsive padding and max-width. */
export interface ContentProps {
  children: ReactNode;
  className?: string;
}

export function Content({ children, className }: ContentProps) {
  return (
    <div
      className={cn(
        "px-4 md:px-6 py-6 mx-auto max-w-7xl w-full",
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Page section — grouped content with optional title and description. */
export interface PageSectionProps {
  title?: string;
  description?: string;
  children: ReactNode;
  className?: string;
  action?: ReactNode;
}

export function PageSection({
  title,
  description,
  children,
  className,
  action,
}: PageSectionProps) {
  return (
    <section className={cn("flex flex-col gap-4", className)}>
      {(title || description || action) && (
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-col gap-1">
            {title && <h2 className="text-h2 font-bold text-text-primary">{title}</h2>}
            {description && <p className="text-body text-text-secondary">{description}</p>}
          </div>
          {action && <div className="flex-shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

/** Grid layout for cards/metrics. */
export interface GridProps {
  children: ReactNode;
  columns?: "1" | "2" | "3" | "4";
  gap?: "sm" | "md" | "lg";
  className?: string;
}

const colsMap = {
  "1": "grid-cols-1",
  "2": "grid-cols-1 md:grid-cols-2",
  "3": "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
  "4": "grid-cols-2 md:grid-cols-3 lg:grid-cols-4",
};

const gapMap = {
  sm: "gap-3",
  md: "gap-4",
  lg: "gap-6",
};

export function Grid({
  children,
  columns = "3",
  gap = "md",
  className,
}: GridProps) {
  return (
    <div
      className={cn(
        "grid",
        colsMap[columns],
        gapMap[gap],
        className,
      )}
    >
      {children}
    </div>
  );
}

/** Two-column layout — sidebar + main. */
export interface TwoColumnProps {
  sidebar: ReactNode;
  children: ReactNode;
  className?: string;
}

export function TwoColumn({ sidebar, children, className }: TwoColumnProps) {
  return (
    <div className={cn("flex gap-6", className)}>
      <div className="w-80 flex-shrink-0">{sidebar}</div>
      <div className="flex-1">{children}</div>
    </div>
  );
}
