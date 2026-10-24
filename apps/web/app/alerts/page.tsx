"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  BellRing,
  AlertTriangle,
  ArrowUpRight,
  CheckCircle,
  Eye,
  Filter,
  RefreshCw,
  TrendingUp,
  ShieldAlert,
} from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { Button } from "@/components/ui";

interface AlertItem {
  alert_id: str;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  campaign_id?: string;
  campaign_name?: string;
  metrics: Record<string, any>;
  status: "NEW" | "ACKNOWLEDGED" | "INVESTIGATING" | "RESOLVED" | "DISMISSED";
  created_at: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/v1/console/alerts");
      if (res.ok) {
        const data = await res.json();
        setAlerts(data);
      }
    } catch (e) {
      console.error("Failed to load alerts:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, []);

  const handleUpdateStatus = async (alertId: string, newStatus: string) => {
    try {
      const res = await fetch(`/api/v1/console/alerts/${alertId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (res.ok) {
        setAlerts((prev) =>
          prev.map((a) => (a.alert_id === alertId ? { ...a, status: newStatus as any } : a))
        );
      }
    } catch (e) {
      console.error("Failed to update alert status:", e);
    }
  };

  const filtered = alerts.filter((a) => {
    if (statusFilter !== "ALL" && a.status !== statusFilter) return false;
    if (severityFilter !== "ALL" && a.severity !== severityFilter) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <PageHeader
          title="Operational Alert Center"
          description="High-priority threat signals, regional outbreak alerts, and velocity spikes requiring investigator triage."
        />
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchAlerts} disabled={loading}>
            <RefreshCw className={`h-3.5 w-3.5 mr-1.5 ${loading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-wrap items-center gap-3 p-3 rounded-xl border border-line bg-surface">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-ink-muted">
          <Filter className="h-3.5 w-3.5" />
          <span>Status:</span>
        </div>
        {["ALL", "NEW", "ACKNOWLEDGED", "INVESTIGATING", "RESOLVED"].map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              statusFilter === s
                ? "bg-accent text-white shadow-sm"
                : "bg-surface-elevated text-ink-muted hover:text-ink hover:bg-elevated"
            }`}
          >
            {s}
          </button>
        ))}

        <div className="h-4 w-[1px] bg-line mx-2" />

        <div className="flex items-center gap-1.5 text-xs font-semibold text-ink-muted">
          <span>Severity:</span>
        </div>
        {["ALL", "CRITICAL", "HIGH", "MEDIUM"].map((sev) => (
          <button
            key={sev}
            onClick={() => setSeverityFilter(sev)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              severityFilter === sev
                ? "bg-purple-600 text-white shadow-sm"
                : "bg-surface-elevated text-ink-muted hover:text-ink hover:bg-elevated"
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Alerts Stream */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="p-8 text-center rounded-xl border border-line bg-surface text-ink-dim text-sm">
            No active operational alerts match the selected criteria.
          </div>
        ) : (
          filtered.map((alert) => (
            <div
              key={alert.alert_id}
              className="p-5 rounded-xl border border-line bg-surface hover:border-accent/40 transition-all space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-0.5 rounded text-[11px] font-bold uppercase tracking-wider font-mono ${
                      alert.severity === "CRITICAL"
                        ? "bg-red-500/15 text-red-400 border border-red-500/30"
                        : alert.severity === "HIGH"
                        ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        : "bg-blue-500/15 text-blue-400 border border-blue-500/30"
                    }`}
                  >
                    {alert.severity}
                  </span>
                  <span className="text-xs font-mono font-semibold text-ink-muted">
                    {alert.alert_type}
                  </span>
                  <span className="text-xs text-ink-dim">
                    • {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs px-2 py-0.5 rounded font-medium ${
                      alert.status === "NEW"
                        ? "bg-blue-500/10 text-blue-400"
                        : alert.status === "INVESTIGATING"
                        ? "bg-purple-500/10 text-purple-400"
                        : "bg-emerald-500/10 text-emerald-400"
                    }`}
                  >
                    {alert.status}
                  </span>
                  {alert.status === "NEW" && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleUpdateStatus(alert.alert_id, "ACKNOWLEDGED")}
                    >
                      Acknowledge
                    </Button>
                  )}
                  {alert.status === "ACKNOWLEDGED" && (
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => handleUpdateStatus(alert.alert_id, "INVESTIGATING")}
                    >
                      Investigate
                    </Button>
                  )}
                  {alert.status === "INVESTIGATING" && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleUpdateStatus(alert.alert_id, "RESOLVED")}
                    >
                      Mark Resolved
                    </Button>
                  )}
                </div>
              </div>

              <div>
                <h4 className="text-base font-semibold text-ink">{alert.title}</h4>
                <p className="text-xs text-ink-muted leading-relaxed mt-1">
                  {alert.description}
                </p>
              </div>

              {/* Metrics & Context */}
              <div className="flex flex-wrap items-center gap-4 pt-2 text-xs font-mono text-ink-muted border-t border-line">
                {alert.campaign_name && (
                  <div>
                    <span className="text-ink-dim">Campaign: </span>
                    <Link
                      href={`/campaigns/${alert.campaign_id}`}
                      className="text-accent hover:underline inline-flex items-center"
                    >
                      {alert.campaign_name}
                      <ArrowUpRight className="h-3 w-3 ml-0.5" />
                    </Link>
                  </div>
                )}
                {alert.metrics.velocity_spike_pct && (
                  <div>
                    <span className="text-ink-dim">Velocity Spike: </span>
                    <span className="text-amber-400 font-bold">
                      +{alert.metrics.velocity_spike_pct}%
                    </span>
                  </div>
                )}
                {alert.metrics.unique_entities && (
                  <div>
                    <span className="text-ink-dim">Entities: </span>
                    <span className="text-ink font-semibold">{alert.metrics.unique_entities}</span>
                  </div>
                )}
                {alert.metrics.primary_channels && (
                  <div>
                    <span className="text-ink-dim">Channels: </span>
                    <span className="text-ink">{alert.metrics.primary_channels.join(", ")}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
