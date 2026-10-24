import { cn } from "@/lib/utils/cn";
import type React from "react";

/** Base skeleton — animated shimmer. */
export interface SkeletonProps {
  className?: string;
  style?: React.CSSProperties;
}

export function Skeleton({ className, style }: SkeletonProps) {
  return (
    <div
      className={cn(
        "rounded-lg bg-gradient-to-r from-surface-2 via-surface-3 to-surface-2 bg-200% animate-shimmer",
        className,
      )}
      role="status"
      aria-busy
      aria-label="Loading"
      style={style}
    />
  );
}

/** Incident detail skeleton. */
export function IncidentSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex gap-4">
        <Skeleton className="h-12 w-12 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-6 w-1/2" />
          <Skeleton className="h-4 w-1/3" />
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-8 w-24" />
        ))}
      </div>

      {/* Content cards */}
      <div className="space-y-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-20 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Evidence graph skeleton. */
export function EvidenceGraphSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      {/* Graph container */}
      <Skeleton className="h-96 w-full rounded-card" />

      {/* Legend */}
      <div className="flex gap-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-3 w-3 rounded-full" />
            <Skeleton className="h-4 w-20" />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Assessment card skeleton. */
export function AssessmentSkeleton() {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Skeleton className="h-5 w-1/3" />
        <Skeleton className="h-6 w-16" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
      </div>
    </div>
  );
}

/** Metric card skeleton. */
export function MetricSkeleton() {
  return (
    <div className="space-y-3">
      <Skeleton className="h-3 w-1/2" />
      <Skeleton className="h-10 w-2/3" />
      <Skeleton className="h-4 w-1/3" />
    </div>
  );
}

/** Campaign list skeleton. */
export function CampaignListSkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="flex items-center justify-between">
            <Skeleton className="h-5 w-1/3" />
            <Skeleton className="h-6 w-16" />
          </div>
          <Skeleton className="h-4 w-full" />
        </div>
      ))}
    </div>
  );
}

/** Command/Lab query results skeleton. */
export function QueryResultsSkeleton() {
  return (
    <div className="space-y-3">
      {/* Query bar */}
      <Skeleton className="h-10 w-full rounded-lg" />

      {/* Result rows */}
      <div className="space-y-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-1/4" />
            <Skeleton className="h-8 w-1/3" />
            <Skeleton className="h-8 w-1/4" />
          </div>
        ))}
      </div>
    </div>
  );
}

/** Investigation (Shield) skeleton — multi-section. */
export function InvestigationSkeleton() {
  return (
    <div className="space-y-6">
      {/* Overview section */}
      <div className="space-y-3">
        <Skeleton className="h-5 w-1/4" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-24" />
          ))}
        </div>
      </div>

      {/* Analysis section */}
      <div className="space-y-3">
        <Skeleton className="h-5 w-1/4" />
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16" />
          ))}
        </div>
      </div>

      {/* Timeline section */}
      <div className="space-y-3">
        <Skeleton className="h-5 w-1/4" />
        <Skeleton className="h-64" />
      </div>
    </div>
  );
}

/** Data table rows skeleton. */
export interface TableSkeletonProps {
  rows?: number;
  cols?: number;
}

export function TableSkeleton({ rows = 6, cols = 4 }: TableSkeletonProps) {
  return (
    <div className="space-y-2">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-3">
          {Array.from({ length: cols }).map((_, j) => (
            <Skeleton key={j} className="h-8 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

/** Timeline skeleton. */
export function TimelineSkeleton() {
  return (
    <div className="space-y-6">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex gap-4">
          {/* Timeline dot */}
          <Skeleton className="h-3 w-3 rounded-full flex-shrink-0 mt-2" />

          {/* Content */}
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-1/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        </div>
      ))}
    </div>
  );
}

/** Chart/graph skeleton. */
export function ChartSkeleton() {
  return (
    <div className="flex flex-col gap-4 h-80">
      {/* Legend */}
      <div className="flex gap-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-2">
            <Skeleton className="h-2 w-4" />
            <Skeleton className="h-4 w-16" />
          </div>
        ))}
      </div>

      {/* Chart area */}
      <div className="flex-1 flex items-end gap-2">
        {Array.from({ length: 12 }).map((_, i) => (
          <Skeleton
            key={i}
            className="flex-1 rounded-t-lg"
            style={{ height: `${Math.random() * 100}%` }}
          />
        ))}
      </div>
    </div>
  );
}
