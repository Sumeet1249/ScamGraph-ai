"use client";
import { useState, useEffect } from "react";
import { 
  Activity, 
  TrendingUp, 
  Clock, 
  AlertCircle, 
  ArrowUpRight, 
  CheckCircle2, 
  Filter, 
  Download,
  Calendar,
  Layers,
  Sparkles
} from "lucide-react";

export default function ApiUsagePage() {
  const [timeRange, setTimeRange] = useState<"24h" | "7d" | "30d">("24h");
  const [hoveredHour, setHoveredHour] = useState<number | null>(14);
  const [telemetry, setTelemetry] = useState<any>(null);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const res = await fetch(`/api/v1/developers/usage?timeRange=${timeRange}`);
        if (res.ok) {
          const data = await res.json();
          setTelemetry(data);
        }
      } catch (err) {
        console.error("Failed to load telemetry", err);
      }
    };
    fetchUsage();
  }, [timeRange]);

  const endpointStats = [
    {
      endpoint: "/v1/check/universal",
      method: "POST",
      calls: "32,840",
      share: "68.1%",
      p95: "118ms",
      successRate: "99.9%",
      errors: 12
    },
    {
      endpoint: "/v1/guard/intent/eval",
      method: "POST",
      calls: "9,412",
      share: "19.5%",
      p95: "74ms",
      successRate: "99.9%",
      errors: 2
    },
    {
      endpoint: "/v1/check/{id}",
      method: "GET",
      calls: "3,120",
      share: "6.5%",
      p95: "42ms",
      successRate: "100.0%",
      errors: 0
    },
    {
      endpoint: "/v1/radar/snapshot",
      method: "GET",
      calls: "1,940",
      share: "4.0%",
      p95: "164ms",
      successRate: "99.4%",
      errors: 2
    },
    {
      endpoint: "/v1/artifacts/ingest",
      method: "POST",
      calls: "902",
      share: "1.9%",
      p95: "240ms",
      successRate: "98.8%",
      errors: 0
    }
  ];

  // Hourly volume distribution (24 intervals)
  const hourlyData = [
    { h: 0, v: 40, err: 0 },
    { h: 1, v: 28, err: 0 },
    { h: 2, v: 20, err: 0 },
    { h: 3, v: 15, err: 0 },
    { h: 4, v: 22, err: 0 },
    { h: 5, v: 35, err: 0 },
    { h: 6, v: 60, err: 0 },
    { h: 7, v: 85, err: 0 },
    { h: 8, v: 115, err: 1 },
    { h: 9, v: 130, err: 1 },
    { h: 10, v: 145, err: 2 },
    { h: 11, v: 155, err: 1 },
    { h: 12, v: 162, err: 2 },
    { h: 13, v: 170, err: 3 },
    { h: 14, v: 178, err: 12 }, // Peak hour
    { h: 15, v: 165, err: 2 },
    { h: 16, v: 150, err: 1 },
    { h: 17, v: 140, err: 1 },
    { h: 18, v: 120, err: 0 },
    { h: 19, v: 100, err: 1 },
    { h: 20, v: 80, err: 0 },
    { h: 21, v: 65, err: 0 },
    { h: 22, v: 50, err: 0 },
    { h: 23, v: 38, err: 0 }
  ];

  const totalRequests = telemetry?.total_requests?.toLocaleString() ?? "48,214";
  const successRate = telemetry?.success_rate ? `${telemetry.success_rate.toFixed(2)}%` : "99.88%";
  const p50 = telemetry?.p50_latency_ms ? `${telemetry.p50_latency_ms}ms` : "64ms";
  const p95 = telemetry?.p95_latency_ms ? `${telemetry.p95_latency_ms}ms` : "142ms";
  const p99 = telemetry?.p99_latency_ms ? `${telemetry.p99_latency_ms}ms` : "280ms";
  const errorRate = telemetry?.error_rate ? `${telemetry.error_rate.toFixed(2)}%` : "0.12%";
  const totalErrors = telemetry?.total_errors ?? 58;
  const quotaLimit = telemetry?.quota_limit ?? 50000;
  const quotaUsed = telemetry?.quota_used ?? 48214;
  const quotaPct = Math.min(Math.round((quotaUsed / quotaLimit) * 100), 100);
  const activeEndpointStats = telemetry?.endpoints && telemetry.endpoints.length > 0 ? telemetry.endpoints : endpointStats;

  const peakPoint = hourlyData.find(d => d.h === (hoveredHour ?? 14)) || hourlyData[14];
  const peakCalls = peakPoint.v * 21.5;

  return (
    <div className="w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col gap-8">
      {/* 1. Header & Timeframe Selector */}
      <section className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-viz-text tracking-tight">API Usage &amp; Telemetry</h1>
          <p className="text-sm text-on-surface-variant">Real-time throughput, percentile response latency, and rate-limit quota consumption.</p>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto">
          <div className="flex items-center bg-surface p-1 rounded-lg border border-border-divider shadow-sm text-xs">
            <button
              onClick={() => setTimeRange("24h")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                timeRange === "24h" ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              24 Hours
            </button>
            <button
              onClick={() => setTimeRange("7d")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                timeRange === "7d" ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange("30d")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-colors ${
                timeRange === "30d" ? "bg-primary text-on-primary shadow-sm" : "text-on-surface-variant hover:text-on-surface"
              }`}
            >
              30 Days
            </button>
          </div>

          <button className="h-9 px-3 bg-surface hover:bg-surface-subtle border border-border-divider rounded-lg text-xs font-medium inline-flex items-center gap-1.5 transition-colors shadow-sm">
            <Download className="h-3.5 w-3.5 text-viz-neutral" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
        </div>
      </section>

      {/* 2. Top KPI Metric Cards */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-surface rounded-xl p-5 border border-border-divider/70 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-viz-neutral font-medium">
            <span>Total Requests ({timeRange})</span>
            <span className="p-1 rounded bg-surface-subtle text-primary">
              <Activity className="h-4 w-4" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-bold text-viz-text font-mono">{totalRequests}</div>
            <div className="flex items-center gap-1 text-[11px] text-viz-primary font-semibold mt-1">
              <ArrowUpRight className="h-3.5 w-3.5" />
              <span>+18.4% vs previous window</span>
            </div>
          </div>
          <div className="pt-2 border-t border-border-divider/50 flex items-center justify-between text-[11px] text-viz-neutral font-mono">
            <span>{quotaLimit.toLocaleString()} monthly quota</span>
            <span className="text-primary font-bold">{quotaPct}% used</span>
          </div>
        </div>

        {/* Metric 2 */}
        <div className="bg-surface rounded-xl p-5 border border-border-divider/70 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-viz-neutral font-medium">
            <span>Success Rate (2xx)</span>
            <span className="p-1 rounded bg-surface-subtle text-viz-primary">
              <CheckCircle2 className="h-4 w-4" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-bold text-viz-text font-mono">{successRate}</div>
            <div className="flex items-center gap-1 text-[11px] text-viz-neutral mt-1">
              <span>{Math.round(quotaUsed * 0.9988).toLocaleString()} successful verifications</span>
            </div>
          </div>
          <div className="pt-2 border-t border-border-divider/50 flex items-center justify-between text-[11px] text-viz-neutral font-mono">
            <span>Target SLA: &gt;99.5%</span>
            <span className="text-viz-primary font-bold">Exceeding</span>
          </div>
        </div>

        {/* Metric 3 */}
        <div className="bg-surface rounded-xl p-5 border border-border-divider/70 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-viz-neutral font-medium">
            <span>Response Latency (p95)</span>
            <span className="p-1 rounded bg-surface-subtle text-primary">
              <Clock className="h-4 w-4" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-bold text-viz-text font-mono">{p95}</div>
            <div className="grid grid-cols-2 gap-2 mt-1 font-mono text-[11px] text-viz-neutral">
              <span>p50: <strong className="text-viz-text">{p50}</strong></span>
              <span>p99: <strong className="text-viz-text">{p99}</strong></span>
            </div>
          </div>
          <div className="pt-2 border-t border-border-divider/50 flex items-center justify-between text-[11px] text-viz-neutral font-mono">
            <span>p95 SLA ceiling: 300ms</span>
            <span className="text-viz-primary font-bold">Optimal</span>
          </div>
        </div>

        {/* Metric 4 */}
        <div className="bg-surface rounded-xl p-5 border border-border-divider/70 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between text-xs text-viz-neutral font-medium">
            <span>Error Rate (Window)</span>
            <span className="p-1 rounded bg-tone-warning-bg text-viz-warning">
              <AlertCircle className="h-4 w-4" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-bold text-viz-text font-mono">{errorRate}</div>
            <div className="flex items-center gap-1 text-[11px] text-viz-neutral mt-1">
              <span>{totalErrors} total errors recorded</span>
            </div>
          </div>
          <div className="pt-2 border-t border-border-divider/50 flex items-center justify-between text-[11px] text-viz-neutral font-mono">
            <span>Client errors &lt; 0.5%</span>
            <span className="text-viz-primary font-bold">Compliant</span>
          </div>
        </div>
      </section>

      {/* 3. Volume & Latency Visualizations */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Multi-series Volume Chart (8 Cols) */}
        <div className="lg:col-span-8 bg-surface rounded-xl p-6 border border-border-divider/70 shadow-sm flex flex-col">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 border-b border-border-divider">
            <div>
              <h2 className="text-base font-bold text-viz-text">Hourly Ingestion Volume &amp; Status Composition</h2>
              <p className="text-xs text-on-surface-variant mt-0.5">24-hour request distribution sampled at 60-minute intervals</p>
            </div>
            <div className="flex flex-wrap items-center gap-4 text-xs text-on-surface-variant font-medium">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-primary" />
                <span>2xx Success</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-viz-warning" />
                <span>4xx Client Error</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-sm bg-tone-danger-text" />
                <span>5xx Server Error</span>
              </span>
            </div>
          </div>

          {/* SVG Volume Chart */}
          <div className="relative w-full h-64 mt-4 flex flex-col justify-end">
            <svg className="w-full h-full" preserveAspectRatio="none" viewBox="0 0 800 240">
              {/* Grid Lines */}
              <line stroke="#E1E4E8" strokeDasharray="3 3" x1="40" x2="780" y1="20" y2="20" />
              <line stroke="#E1E4E8" strokeDasharray="3 3" x1="40" x2="780" y1="75" y2="75" />
              <line stroke="#E1E4E8" strokeDasharray="3 3" x1="40" x2="780" y1="130" y2="130" />
              <line stroke="#E1E4E8" strokeDasharray="3 3" x1="40" x2="780" y1="185" y2="185" />
              <line stroke="#80858C" x1="40" x2="780" y1="210" y2="210" />

              {/* Y Axis Labels */}
              <text fill="#80858C" fontSize="10" textAnchor="end" x="32" y="24">4k</text>
              <text fill="#80858C" fontSize="10" textAnchor="end" x="32" y="79">3k</text>
              <text fill="#80858C" fontSize="10" textAnchor="end" x="32" y="134">2k</text>
              <text fill="#80858C" fontSize="10" textAnchor="end" x="32" y="189">1k</text>

              {/* Bars */}
              {hourlyData.map((d, idx) => {
                const x = 50 + idx * 30;
                const height = d.v;
                const y = 210 - height;
                const isPeak = d.h === (hoveredHour ?? 14);

                return (
                  <g key={d.h} className="cursor-pointer" onMouseEnter={() => setHoveredHour(d.h)}>
                    <rect
                      x={x}
                      y={y}
                      width="18"
                      height={height}
                      rx="2"
                      fill={isPeak ? "#00483f" : "#0B6256"}
                      className="transition-colors hover:fill-primary"
                    />
                    {d.err > 0 && (
                      <rect
                        x={x}
                        y={y - 3}
                        width="18"
                        height="3"
                        rx="1"
                        fill="#B86200"
                      />
                    )}
                  </g>
                );
              })}
            </svg>

            {/* Pinned Tooltip */}
            <div className="absolute top-2 left-1/2 -translate-x-12 bg-surface rounded-xl p-3 shadow-lg border border-border-control flex flex-col gap-1 z-10 pointer-events-none text-xs">
              <div className="flex items-center justify-between gap-4 border-b border-border-divider pb-1">
                <span className="font-bold text-on-surface">{peakPoint.h}:00 – {peakPoint.h + 1}:00 UTC</span>
                <span className="text-primary font-bold font-mono">{Math.round(peakCalls)} calls</span>
              </div>
              <div className="flex flex-col gap-1 font-mono text-[11px] pt-1">
                <div className="flex items-center justify-between gap-4">
                  <span className="flex items-center gap-1 text-on-surface-variant">
                    <span className="w-2 h-2 rounded-full bg-primary" />
                    200 OK
                  </span>
                  <span className="text-on-surface font-semibold">{Math.round(peakCalls - peakPoint.err)}</span>
                </div>
                <div className="flex items-center justify-between gap-4">
                  <span className="flex items-center gap-1 text-on-surface-variant">
                    <span className="w-2 h-2 rounded-full bg-viz-warning" />
                    4xx Client Error
                  </span>
                  <span className="text-tone-warning-strong-text font-semibold">{peakPoint.err}</span>
                </div>
              </div>
            </div>
          </div>

          {/* X Axis labels */}
          <div className="flex justify-between pl-10 pr-4 mt-2 text-viz-neutral font-mono text-[10px] border-t border-border-divider pt-2">
            <span>00:00</span>
            <span>04:00</span>
            <span>08:00</span>
            <span className="text-primary font-bold">12:00</span>
            <span className="text-primary font-bold">16:00</span>
            <span>20:00</span>
            <span>24:00</span>
          </div>
        </div>

        {/* Latency Percentile Distribution Card (4 Cols) */}
        <div className="lg:col-span-4 bg-surface rounded-xl p-6 border border-border-divider/70 shadow-sm flex flex-col justify-between">
          <div className="pb-3 border-b border-border-divider">
            <h2 className="text-base font-bold text-viz-text">Latency Distribution &amp; SLA</h2>
            <p className="text-xs text-on-surface-variant mt-0.5">Response durations against latency compliance targets</p>
          </div>

          {/* Percentiles Grid */}
          <div className="grid grid-cols-2 gap-3 my-4 text-xs">
            <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider">
              <span className="text-viz-neutral block text-[11px]">Median (p50)</span>
              <span className="text-2xl font-bold text-viz-text font-mono">64<span className="text-xs font-normal text-viz-neutral">ms</span></span>
            </div>
            <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider">
              <span className="text-viz-neutral block text-[11px]">p90 Percentile</span>
              <span className="text-2xl font-bold text-viz-text font-mono">112<span className="text-xs font-normal text-viz-neutral">ms</span></span>
            </div>
            <div className="p-3 rounded-xl bg-tone-info-bg border border-tone-info-text/20">
              <span className="text-tone-info-text block text-[11px] font-semibold">p95 Benchmark</span>
              <span className="text-2xl font-bold text-tone-info-text font-mono">142<span className="text-xs font-normal text-tone-info-text/80">ms</span></span>
            </div>
            <div className="p-3 rounded-xl bg-surface-subtle border border-border-divider">
              <span className="text-viz-neutral block text-[11px]">Tail Latency (p99)</span>
              <span className="text-2xl font-bold text-viz-text font-mono">280<span className="text-xs font-normal text-viz-neutral">ms</span></span>
            </div>
          </div>

          {/* SLA Response Time Histogram Breakdown */}
          <div className="flex flex-col gap-2 pt-2 border-t border-border-divider/60">
            <span className="font-mono text-[10px] text-viz-neutral font-bold uppercase tracking-wider">
              SLA Latency Tiers
            </span>
            <div className="flex flex-col gap-2 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-viz-text w-24">&lt; 100ms</span>
                <div className="flex-1 mx-2 bg-surface-subtle rounded-full h-2 overflow-hidden border border-border-divider/40">
                  <div className="bg-primary h-full rounded-full" style={{ width: "78%" }} />
                </div>
                <span className="font-mono font-bold w-12 text-right">78.0%</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-viz-text w-24">100 - 200ms</span>
                <div className="flex-1 mx-2 bg-surface-subtle rounded-full h-2 overflow-hidden border border-border-divider/40">
                  <div className="bg-viz-primary h-full rounded-full" style={{ width: "18%" }} />
                </div>
                <span className="font-mono font-bold w-12 text-right">18.0%</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-viz-text w-24">200 - 500ms</span>
                <div className="flex-1 mx-2 bg-surface-subtle rounded-full h-2 overflow-hidden border border-border-divider/40">
                  <div className="bg-viz-warning h-full rounded-full" style={{ width: "3.8%" }} />
                </div>
                <span className="font-mono font-bold w-12 text-right">3.8%</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-viz-text w-24">&gt; 500ms</span>
                <div className="flex-1 mx-2 bg-surface-subtle rounded-full h-2 overflow-hidden border border-border-divider/40">
                  <div className="bg-tone-danger-text h-full rounded-full" style={{ width: "0.2%" }} />
                </div>
                <span className="font-mono font-bold w-12 text-right">0.2%</span>
              </div>
            </div>
          </div>
        </div>

      </section>

      {/* 4. Endpoint Consumption Breakdown Table */}
      <section className="bg-surface rounded-xl shadow-sm border border-border-divider/70 overflow-hidden flex flex-col">
        <div className="p-5 border-b border-border-divider/60 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-viz-text">Endpoint Consumption Breakdown</h2>
            <p className="text-xs text-on-surface-variant">Throughput and latency breakdown per subscribed ScamGraph API route.</p>
          </div>
          <span className="font-mono text-xs text-viz-neutral">5 Active Routes</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-subtle font-mono text-[11px] uppercase tracking-wider text-on-surface-variant border-b border-border-divider">
              <tr>
                <th className="py-3 px-4 font-bold">API Route</th>
                <th className="py-3 px-3 font-bold">Total Invocations</th>
                <th className="py-3 px-3 font-bold">Volume Share</th>
                <th className="py-3 px-3 font-bold">Latency (p95)</th>
                <th className="py-3 px-3 font-bold">2xx Success</th>
                <th className="py-3 px-4 text-right font-bold">429 / Throttled</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-divider text-on-surface">
              {activeEndpointStats.map((ep: any) => (
                <tr key={ep.endpoint} className="hover:bg-surface-subtle transition-colors">
                  <td className="py-3.5 px-4 font-mono">
                    <span className="px-1.5 py-0.5 rounded bg-surface-subtle border border-border-divider text-primary font-bold mr-2 text-[10px]">
                      {ep.method}
                    </span>
                    <span className="font-semibold text-viz-text">{ep.endpoint}</span>
                  </td>
                  <td className="py-3.5 px-3 font-mono font-bold text-viz-text">{ep.calls}</td>
                  <td className="py-3.5 px-3 font-mono text-viz-neutral">{ep.share}</td>
                  <td className="py-3.5 px-3 font-mono text-viz-text">{ep.p95}</td>
                  <td className="py-3.5 px-3">
                    <span className="font-mono font-bold text-viz-primary flex items-center gap-1">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      {ep.successRate}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right font-mono">
                    {ep.errors > 0 ? (
                      <span className="text-viz-warning font-bold">{ep.errors}</span>
                    ) : (
                      <span className="text-viz-neutral">0</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 5. Rate Limit Quotas & Thresholds Strip */}
      <div className="p-4 rounded-xl bg-surface-subtle text-on-surface-variant flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs border border-border-divider/60">
        <div className="flex items-center gap-3">
          <span className="font-bold text-viz-text">Sandbox Rate Limits:</span>
          <span>Burst: <strong className="font-mono text-viz-text">60 req/min</strong></span>
          <span>·</span>
          <span>Daily quota: <strong className="font-mono text-viz-text">1,000 req/key</strong></span>
          <span>·</span>
          <span>Audit retention: <strong className="font-mono text-viz-text">30 days</strong> (DPDP Section 8)</span>
        </div>
        <span className="font-mono text-primary font-semibold hover:underline cursor-pointer">
          Request Limit Increase →
        </span>
      </div>
    </div>
  );
}
