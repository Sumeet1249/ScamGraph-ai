import { cn } from "@/lib/utils/cn";
import { pct, similarityBucket, humanize } from "@/lib/utils/format";
import type { FingerprintSimilarityResult } from "@/lib/api/types";

const DIMENSIONS: { key: keyof FingerprintSimilarityResult; label: string }[] = [
  { key: "semantic_similarity", label: "Semantic" },
  { key: "journey_similarity", label: "Journey" },
  { key: "pattern_similarity", label: "Pattern" },
  { key: "infrastructure_similarity", label: "Infrastructure" },
  { key: "payment_similarity", label: "Payment" },
  { key: "identifier_overlap", label: "Identifier" },
];

const bucketTone: Record<string, string> = {
  HIGH: "text-safe",
  MEDIUM: "text-caution",
  LOW: "text-risk-high",
  NONE: "text-ink-dim",
};

/**
 * Multi-dimensional fingerprint similarity breakdown.
 * Always shows numeric values alongside any 3D representation — never force
 * judges to interpret the 3D graphic alone (product principle).
 */
export function SimilarityBreakdown({
  similarity,
}: {
  similarity: FingerprintSimilarityResult;
}) {
  return (
    <div className="panel p-5">
      <div className="eyebrow mb-4">Fingerprint Similarity</div>
      <div className="space-y-2.5">
        {DIMENSIONS.map(({ key, label }) => {
          const value = similarity[key] as number;
          const bucket = similarityBucket(value);
          return (
            <div key={key} className="flex items-center gap-3">
              <span className="w-28 shrink-0 text-sm text-ink-muted">{label}</span>
              <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-2">
                <div
                  className={cn("h-full rounded-full", bucketTone[bucket].replace("text-", "bg-"))}
                  style={{ width: `${Math.round((value ?? 0) * 100)}%` }}
                />
              </div>
              <span className="w-16 shrink-0 text-right font-mono text-xs text-ink-muted">
                {pct(value)}%
              </span>
              <span className={cn("w-16 shrink-0 text-right text-xs font-semibold", bucketTone[bucket])}>
                {humanize(bucket)}
              </span>
            </div>
          );
        })}
      </div>
      {similarity.explanation && (
        <p className="mt-4 text-xs text-ink-dim">{similarity.explanation}</p>
      )}
    </div>
  );
}
