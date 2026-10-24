import { useEffect, useRef } from "react";

export function useJourneyAnimation() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Subtle entry stagger animation
    if (!containerRef.current) return;
    const items = containerRef.current.querySelectorAll(".sg-journey-step");
    items.forEach((item, index) => {
      (item as HTMLElement).style.opacity = "0";
      (item as HTMLElement).style.transform = "translateY(8px)";
      setTimeout(() => {
        (item as HTMLElement).style.transition = "opacity 0.4s ease, transform 0.4s ease";
        (item as HTMLElement).style.opacity = "1";
        (item as HTMLElement).style.transform = "translateY(0)";
      }, index * 80);
    });
  }, []);

  return { containerRef };
}
