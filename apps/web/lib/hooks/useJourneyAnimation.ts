import { useRef } from "react";

export function useJourneyAnimation(steps?: any[]) {
  const ref = useRef<HTMLDivElement>(null);
  return { ref };
}
