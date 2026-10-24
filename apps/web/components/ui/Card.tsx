import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils/cn";

/** Base card — surface-1 with subtle border and shadow. */
export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  /** Padding size: sm, md, lg, or none. Defaults to md. */
  pad?: "sm" | "md" | "lg" | "none";
}

const padMap = {
  sm: "p-2",
  md: "p-4",
  lg: "p-6",
  none: "p-0",
};

export function Card({ className, pad = "md", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-card border border-border bg-surface-1 shadow-card",
        padMap[pad],
        className,
      )}
      {...props}
    />
  );
}

/** Elevated card — surface-2 with stronger shadow and border. */
export function CardElevated({ className, pad = "md", ...props }: CardProps) {
  return (
    <div
      className={cn(
        "rounded-card border border-border-strong bg-surface-2 shadow-elevated",
        padMap[pad],
        className,
      )}
      {...props}
    />
  );
}

/** Metric card — displays a single KPI with label and value. */
export interface MetricCardProps extends HTMLAttributes<HTMLDivElement> {
  label: string;
  value: ReactNode;
  /** Optional secondary detail or icon. */
  detail?: ReactNode;
  /** Tone for bottom accent border. */
  tone?: "neutral" | "success" | "caution" | "danger";
}

const toneBorder: Record<string, string> = {
  neutral: "border-b-border-strong",
  success: "border-b-success",
  caution: "border-b-warning",
  danger: "border-b-danger",
};

export function MetricCard({
  label,
  value,
  detail,
  tone = "neutral",
  className,
  ...props
}: MetricCardProps) {
  return (
    <div
      className={cn(
        "rounded-card border border-border bg-surface-1 p-5",
        "border-b-2 flex flex-col justify-between gap-3",
        toneBorder[tone],
        className,
      )}
      {...props}
    >
      <div>
        <div className="eyebrow">{label}</div>
        <div className="mt-2 font-mono text-3xl font-bold text-text-primary tabular-nums tracking-tight">
          {value}
        </div>
      </div>
      {detail && <div className="text-xs text-text-secondary leading-snug">{detail}</div>}
    </div>
  );
}

/** Assessment card — displays risk assessment state with badge and detail. */
export interface AssessmentCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string;
  badge?: ReactNode;
  children: ReactNode;
}

export function AssessmentCard({
  title,
  badge,
  children,
  className,
  ...props
}: AssessmentCardProps) {
  return (
    <Card className={cn("flex flex-col gap-3", className)} {...props}>
      <div className="flex items-center justify-between">
        <h4 className="text-body font-semibold text-text-primary">{title}</h4>
        {badge && <div>{badge}</div>}
      </div>
      <div className="text-body-sm text-text-secondary">{children}</div>
    </Card>
  );
}
