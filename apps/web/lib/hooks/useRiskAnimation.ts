import { useState, useEffect } from "react";

export function useRiskAnimation(targetScore: number): number {
  const [val, setVal] = useState(0);

  useEffect(() => {
    let frame: number;
    const start = performance.now();
    const duration = 600;
    const initial = val;

    const animate = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(1, elapsed / duration);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setVal(Math.round(initial + (targetScore - initial) * eased));
      if (progress < 1) {
        frame = requestAnimationFrame(animate);
      }
    };

    frame = requestAnimationFrame(animate);
    return () => {
      if (frame) cancelAnimationFrame(frame);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [targetScore]);

  return val;
}
