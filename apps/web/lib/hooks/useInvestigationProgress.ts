import { useState, useRef } from "react";

export interface ProgressStep {
  id: string;
  label: string;
  status: "pending" | "active" | "complete" | "error";
}

export function useInvestigationProgress() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [steps, setSteps] = useState<ProgressStep[]>([
    { id: "1", label: "Extracting lexical and punycode URL signals", status: "complete" },
    { id: "2", label: "Evaluating SMS linguistic urgency & dialect", status: "complete" },
    { id: "3", label: "Cross-modal vishing & OTP correlation", status: "complete" },
    { id: "4", label: "Inspecting UPI QR & Reverse-Collect fraud", status: "active" },
    { id: "5", label: "Reconstructing forensic digital twin", status: "pending" },
  ]);

  return { steps, containerRef, setSteps };
}
