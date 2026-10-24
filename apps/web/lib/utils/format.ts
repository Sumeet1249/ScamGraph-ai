export function humanize(text: string): string {
  if (!text) return "";
  return text
    .replace(/[_-]/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function humanizeStage(stage: string): string {
  if (!stage) return "";
  const map: Record<string, string> = {
    initial_contact: "Initial Contact",
    impersonation: "Impersonation",
    pressure_coercion: "Coercive Pressure",
    fake_intent: "Malicious APK / Intent",
    mule_exfiltration: "Mule Exfiltration",
  };
  return map[stage.toLowerCase()] || humanize(stage);
}

export function formatTime(timestamp?: string | number | Date): string {
  if (!timestamp) return "Just now";
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return String(timestamp);
  return date.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit", hour12: true });
}

export function formatOffset(minutes: number): string {
  const sign = minutes >= 0 ? "+" : "-";
  const abs = Math.abs(minutes);
  const hrs = Math.floor(abs / 60);
  const mins = abs % 60;
  return `T ${sign} ${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}`;
}

export function formatDateTime(timestamp?: string | number | Date): string {
  if (!timestamp) return "Just now";
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return String(timestamp);
  return date.toLocaleString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatDate(timestamp?: string | number | Date): string {
  if (!timestamp) return "Today";
  const date = new Date(timestamp);
  if (isNaN(date.getTime())) return String(timestamp);
  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
