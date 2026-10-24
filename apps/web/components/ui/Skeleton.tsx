import { cn } from "@/lib/utils/cn";

/** Loading placeholder block. Subtle pulse, not a flashing spinner. */
export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse-soft rounded-md bg-surface-2/70", className)}
      aria-hidden
    />
  );
}

/** A stacked text skeleton: title line + body line(s). */
export function TextSkeleton({
  lines = 2,
  className,
}: {
  lines?: number;
  className?: string;
}) {
  return (
    <div className={cn("space-y-2", className)} aria-hidden>
      <Skeleton className="h-4 w-2/3" />
      {Array.from({ length: lines - 1 }).map((_, i) => (
        <Skeleton key={i} className="h-3 w-full" />
      ))}
    </div>
  );
}
