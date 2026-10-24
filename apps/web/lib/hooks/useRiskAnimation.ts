import { useState, useEffect } from "react";

export function useRiskAnimation(targetScore: number, durationMs = 1200): number {
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    let start = 0;
    const startTime = performance.now();

    const frame = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / durationMs, 1);
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setCurrent(Math.round(eased * targetScore));

      if (progress < 1) {
        requestAnimationFrame(frame);
      }
    };

    const handle = requestAnimationFrame(frame);
    return () => cancelAnimationFrame(handle);
  }, [targetScore, durationMs]);

  return current;
}
