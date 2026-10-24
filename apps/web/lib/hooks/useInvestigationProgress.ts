import { useState, useRef, useEffect } from "react";

export interface ProgressStep {
  id: string;
  label: string;
  status: "pending" | "active" | "complete" | "error";
}

export function useInvestigationProgress() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [steps, setSteps] = useState<ProgressStep[]>([
    { id: "s1", label: "Semantic analysis of message signals", status: "complete" },
    { id: "s2", label: "TinyFish web infrastructure query", status: "complete" },
    { id: "s3", label: "Payment VPA handle adjudication", status: "active" },
    { id: "s4", label: "Scam journey stage correlation", status: "pending" },
    { id: "s5", label: "Historical campaign clustering", status: "pending" },
    { id: "s6", label: "Dual-axis risk scoring & friction recommendation", status: "pending" },
  ]);

  return { steps, setSteps, containerRef };
}
