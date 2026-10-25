"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  GitFork,
  ArrowRight,
  Sparkles,
  Share2,
  RefreshCw,
  Search,
  AlertTriangle,
  ShieldAlert,
  Info,
  Clock,
  CheckCircle2,
  Sliders,
  Layers,
  ArrowUpRight,
  TrendingDown,
  Repeat,
  Network,
  Check,
} from "lucide-react";
import {
  InteractiveCorrelationGraph,
  VisualNode,
  VisualEdge,
} from "@/components/graph/InteractiveCorrelationGraph";

// Synthetic Presets for Path Exploration
const PATH_PRESETS = [
  {
    id: "layering-chain",
    name: "3-Hop Layering Dispersal",
    desc: "Victim account drained through 2 intermediary mule hops into an exit gateway",
    sourceId: "ACC_VICTIM_001",
    targetId: "ACC_EXIT_GATEWAY",
    maxDepth: 4,
    minAmount: 10000,
  },
  {
    id: "circular-ring",
    name: "Circular Wash Cycle",
    desc: "Funds routed in a closed circle across 3 mule accounts to disguise provenance",
    sourceId: "ACC_NODE_A",
    targetId: "",
    maxDepth: 4,
    minAmount: 5000,
  },
  {
    id: "fan-out-hub",
    name: "Aggregator Fan-Out Flow",
    desc: "Central aggregator hub dispersing funds to multiple peripheral accounts",
    sourceId: "ACC_HUB_AGGREGATOR",
    targetId: "",
    maxDepth: 3,
    minAmount: 20000,
  },
];

// Synthetic Presets for Risk Propagation
const PROPAGATION_PRESETS = [
  {
    id: "confirmed-mule-seed",
    name: "Confirmed Fraud Seed (100% Risk)",
    desc: "Propagate risk from confirmed registry fraud node with λ = 0.5 distance decay",
    seedIds: "ACC_CONFIRMED_FRAUD_881",
    decayFactor: 0.5,
    maxHops: 3,
  },
  {
    id: "multi-seed-ring",
    name: "Multi-Seed Coordinated Ring",
    desc: "Two distinct suspect nodes simultaneously polluting an intermediary node",
    seedIds: "ACC_SUSPECT_401, ACC_SUSPECT_402",
    decayFactor: 0.5,
    maxHops: 2,
  },
];

export default function GraphExplorerPage() {
  const [activeTab, setActiveTab] = useState<"paths" | "clusters" | "propagation">("paths");

  // Tab 1: Path Exploration State
  const [sourceId, setSourceId] = useState(PATH_PRESETS[0].sourceId);
  const [targetId, setTargetId] = useState(PATH_PRESETS[0].targetId);
  const [maxDepth, setMaxDepth] = useState<number>(PATH_PRESETS[0].maxDepth);
  const [minAmount, setMinAmount] = useState<number>(PATH_PRESETS[0].minAmount);
  const [isTracingPaths, setIsTracingPaths] = useState(false);
  const [pathsResult, setPathsResult] = useState<any>(null);
  const [pathError, setPathError] = useState<string | null>(null);
  const [selectedPathIndex, setSelectedPathIndex] = useState<number | null>(0);

  // Tab 2: Cluster Detection State
  const [minClusterSize, setMinClusterSize] = useState<number>(2);
  const [isScanningClusters, setIsScanningClusters] = useState(false);
  const [clustersResult, setClustersResult] = useState<any>(null);
  const [clusterError, setClusterError] = useState<string | null>(null);

  // Tab 3: Risk Propagation State
  const [seedIdsInput, setSeedIdsInput] = useState(PROPAGATION_PRESETS[0].seedIds);
  const [decayFactor, setDecayFactor] = useState<number>(0.5);
  const [maxHops, setMaxHops] = useState<number>(3);
  const [isPropagating, setIsPropagating] = useState(false);
  const [propagationResult, setPropagationResult] = useState<any>(null);
  const [propError, setPropError] = useState<string | null>(null);

  // Handle Trace Paths
  const handleTracePaths = async (src?: string, tgt?: string, depth?: number, amt?: number) => {
    setIsTracingPaths(true);
    setPathError(null);
    try {
      const res = await fetch("/api/v1/graph/paths", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_id: src || sourceId,
          target_id: (tgt !== undefined ? tgt : targetId) || null,
          max_depth: depth || maxDepth,
          min_amount: amt !== undefined ? amt : minAmount,
          time_window_hours: 72,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${res.status}`);
      }

      const data = await res.json();
      setPathsResult(data);
    } catch (err: any) {
      setPathError(err.message || "Failed to trace transaction paths");
    } finally {
      setIsTracingPaths(false);
    }
  };

  // Handle Scan Clusters
  const handleScanClusters = async (size?: number) => {
    setIsScanningClusters(true);
    setClusterError(null);
    try {
      const res = await fetch("/api/v1/graph/clusters", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          min_cluster_size: size || minClusterSize,
          include_dormant: false,
          limit: 20,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${res.status}`);
      }

      const data = await res.json();
      setClustersResult(data);
    } catch (err: any) {
      setClusterError(err.message || "Failed to scan clusters");
    } finally {
      setIsScanningClusters(false);
    }
  };

  // Handle Risk Propagation
  const handleCalculatePropagation = async (seeds?: string, decay?: number, hops?: number) => {
    setIsPropagating(true);
    setPropError(null);
    try {
      const seedList = (seeds || seedIdsInput)
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      if (seedList.length === 0) {
        throw new Error("Please specify at least one valid seed entity ID.");
      }

      const res = await fetch("/api/v1/graph/risk-propagation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          seed_node_ids: seedList,
          decay_factor: decay !== undefined ? decay : decayFactor,
          max_hops: hops || maxHops,
          temporal_half_life_days: 30.0,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP error ${res.status}`);
      }

      const data = await res.json();
      setPropagationResult(data);
    } catch (err: any) {
      setPropError(err.message || "Failed to propagate risk");
    } finally {
      setIsPropagating(false);
    }
  };

  // Preset Selectors
  const selectPathPreset = (p: typeof PATH_PRESETS[0]) => {
    setSourceId(p.sourceId);
    setTargetId(p.targetId);
    setMaxDepth(p.maxDepth);
    setMinAmount(p.minAmount);
    handleTracePaths(p.sourceId, p.targetId, p.maxDepth, p.minAmount);
  };

  const selectPropPreset = (p: typeof PROPAGATION_PRESETS[0]) => {
    setSeedIdsInput(p.seedIds);
    setDecayFactor(p.decayFactor);
    setMaxHops(p.maxHops);
    handleCalculatePropagation(p.seedIds, p.decayFactor, p.maxHops);
  };

  // Load initial queries on mount
  useEffect(() => {
    handleTracePaths();
  }, []);

  // Visual Graph Data for Tab 1 (Paths)
  const pathGraphData = useMemo(() => {
    if (!pathsResult || !pathsResult.paths || pathsResult.paths.length === 0) {
      return { nodes: [], edges: [] };
    }
    const nodeMap = new Map<string, VisualNode>();
    const edgeList: VisualEdge[] = [];

    pathsResult.paths.forEach((p: any) => {
      p.nodes?.forEach((nId: string, idx: number) => {
        if (!nodeMap.has(nId)) {
          let label = nId;
          let tier = `Hop ${idx}`;

          if (nId.includes("VICTIM") || nId.includes("INFLOW")) {
            label = nId.includes("001") ? "Victim (SBI - R. Sharma)" : nId.replace(/_/g, " ");
            tier = "Origin (Victim)";
          } else if (nId === "ACC_MULE_1") {
            label = "Tier-1 Mule (ICICI - Rohit Ent.)";
            tier = "Layer 1 Dispersal";
          } else if (nId === "ACC_MULE_2") {
            label = "Tier-2 Rapid Pass (HDFC)";
            tier = "Layer 2 Rapid Turnover";
          } else if (nId === "ACC_EXIT_GATEWAY") {
            label = "Crypto P2P OTC Desk (Exit)";
            tier = "Cashout Gateway";
          } else if (nId === "ACC_NODE_A") {
            label = "Wash Ring Node A (Kavya Traders)";
            tier = "Mule Ring Hub";
          } else if (nId === "ACC_NODE_B") {
            label = "Wash Ring Node B (Zenith Global)";
            tier = "Shell Company";
          } else if (nId === "ACC_NODE_C") {
            label = "Wash Ring Node C (Sunrise Metal)";
            tier = "Wash Cycle";
          } else if (nId.includes("HUB")) {
            label = "Syndicate Aggregator Hub (Jaipur)";
            tier = "Pooling Hub";
          } else if (nId.includes("CASHOUT")) {
            label = nId.replace(/_/g, " ");
            tier = "Cashout Exit";
          }

          nodeMap.set(nId, {
            id: nId,
            label,
            node_type: "ACCOUNT",
            risk_score: idx === 0 && !nId.includes("HUB") ? 0.05 : Math.min(0.98, 0.70 + idx * 0.1),
            tier,
          });
        }
      });

      p.hops?.forEach((h: any, hIdx: number) => {
        const edgeId = `edge_${h.from_account}_${h.to_account}_${hIdx}`;
        if (!edgeList.some((e) => e.source === h.from_account && e.target === h.to_account)) {
          edgeList.push({
            id: edgeId,
            source: h.from_account,
            target: h.to_account,
            amount: h.amount,
            dwell_time_seconds: h.dwell_time_seconds,
            transaction_id: h.txn_id,
            is_circular: p.is_circular,
          });
        }
      });
    });

    return {
      nodes: Array.from(nodeMap.values()),
      edges: edgeList,
    };
  }, [pathsResult]);

  // Selected path nodes array for highlight
  const selectedPathNodes = useMemo(() => {
    if (
      !pathsResult ||
      !pathsResult.paths ||
      selectedPathIndex === null ||
      !pathsResult.paths[selectedPathIndex]
    ) {
      return [];
    }
    return pathsResult.paths[selectedPathIndex]?.nodes || [];
  }, [pathsResult, selectedPathIndex]);

  // Visual Graph Data for Tab 2 (Clusters)
  const clusterGraphData = useMemo(() => {
    if (!clustersResult || !clustersResult.clusters || clustersResult.clusters.length === 0) {
      return { nodes: [], edges: [] };
    }
    const nodeMap = new Map<string, VisualNode>();
    const edgeList: VisualEdge[] = [];

    clustersResult.clusters.forEach((c: any) => {
      c.nodes?.forEach((n: any) => {
        if (!nodeMap.has(n.id)) {
          nodeMap.set(n.id, {
            id: n.id,
            label: n.label || n.id,
            node_type: n.node_type || "ACCOUNT",
            risk_score: n.risk_score || c.suspicion_score,
            tier: c.cluster_type?.replace(/_/g, " "),
          });
        }
      });
      c.edges?.forEach((e: any, idx: number) => {
        edgeList.push({
          id: e.id || `edge_c_${idx}`,
          source: e.source_id,
          target: e.target_id,
          amount: e.amount,
          relationship_type: e.relationship_type,
          transaction_id: e.transaction_id,
        });
      });
    });

    return {
      nodes: Array.from(nodeMap.values()),
      edges: edgeList,
    };
  }, [clustersResult]);

  // Visual Graph Data for Tab 3 (Propagation)
  const propagationGraphData = useMemo(() => {
    if (!propagationResult || !propagationResult.nodes || propagationResult.nodes.length === 0) {
      return { nodes: [], edges: [] };
    }
    const nodeMap = new Map<string, VisualNode>();
    const edgeList: VisualEdge[] = [];

    const nodesList = propagationResult.nodes;
    nodesList.forEach((n: any) => {
      nodeMap.set(n.node_id, {
        id: n.node_id,
        label: n.node_id,
        node_type: n.node_type || "ACCOUNT",
        risk_score: n.total_risk,
        propagatedRisk: n.propagated_risk,
        isSeed: n.hops_from_seed === 0,
        tier: `${n.hops_from_seed} Hop(s) [λ=${propagationResult.decay_factor_used}]`,
      });
    });

    const seed = nodesList.find((n: any) => n.hops_from_seed === 0);
    const hop1 = nodesList.filter((n: any) => n.hops_from_seed === 1);
    const hop2 = nodesList.filter((n: any) => n.hops_from_seed === 2);
    const hop3 = nodesList.filter((n: any) => n.hops_from_seed === 3);

    if (seed) {
      hop1.forEach((h1: any, idx: number) => {
        edgeList.push({
          id: `prop_edge_0_${idx}`,
          source: seed.node_id,
          target: h1.node_id,
          amount: 85000,
        });
      });
    }
    hop1.forEach((h1: any) => {
      hop2.forEach((h2: any, idx: number) => {
        edgeList.push({
          id: `prop_edge_1_${idx}`,
          source: h1.node_id,
          target: h2.node_id,
          amount: 80000,
        });
      });
    });
    hop2.forEach((h2: any) => {
      hop3.forEach((h3: any, idx: number) => {
        edgeList.push({
          id: `prop_edge_2_${idx}`,
          source: h2.node_id,
          target: h3.node_id,
          amount: 75000,
        });
      });
    });

    return {
      nodes: Array.from(nodeMap.values()),
      edges: edgeList,
    };
  }, [propagationResult]);

  return (
    <div className="flex flex-col space-y-6">
      {/* Intro Header */}
      <div className="bg-gradient-to-r from-surface-1 via-indigo-950/40 to-surface-1 border border-indigo-900/40 rounded-xl p-5 text-text-secondary shadow-md flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="w-11 h-11 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.25)]">
            <GitFork className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold text-text-primary tracking-wide font-mono">
                Graph Correlation<span className="text-cyan-400">.Engine</span>
              </h1>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-semibold">
                Multi-Hop Flow & Risk Propagation
              </span>
            </div>
            <p className="text-xs text-text-muted mt-0.5 max-w-2xl">
              Deconstruct complex money flows, circular wash cycles, fan-in/fan-out structuring hubs,
              and calculate geometric risk propagation with distance decay (λ = 0.5).
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
            Depth Limit ≤ 5 Hops
          </span>
          <span className="px-3 py-1 rounded-full text-xs font-mono font-medium bg-purple-950/80 text-purple-300 border border-purple-800/60">
            Geometric Decay (λ = 0.5)
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-border pb-1">
        <button
          onClick={() => setActiveTab("paths")}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-mono font-medium transition ${
            activeTab === "paths"
              ? "bg-surface-2 text-cyan-400 border-t-2 border-t-cyan-500 border-x border-border -mb-[1px]"
              : "text-text-muted hover:text-text-primary hover:bg-surface-1"
          }`}
        >
          <Share2 className="w-4 h-4" />
          <span>Multi-Hop Flow Tracing & Cycles</span>
        </button>

        <button
          onClick={() => {
            setActiveTab("clusters");
            if (!clustersResult) handleScanClusters();
          }}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-mono font-medium transition ${
            activeTab === "clusters"
              ? "bg-surface-2 text-cyan-400 border-t-2 border-t-cyan-500 border-x border-border -mb-[1px]"
              : "text-text-muted hover:text-text-primary hover:bg-surface-1"
          }`}
        >
          <Network className="w-4 h-4" />
          <span>Suspicious Cluster Discovery</span>
        </button>

        <button
          onClick={() => {
            setActiveTab("propagation");
            if (!propagationResult) handleCalculatePropagation();
          }}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-t-lg text-xs font-mono font-medium transition ${
            activeTab === "propagation"
              ? "bg-surface-2 text-cyan-400 border-t-2 border-t-cyan-500 border-x border-border -mb-[1px]"
              : "text-text-muted hover:text-text-primary hover:bg-surface-1"
          }`}
        >
          <TrendingDown className="w-4 h-4" />
          <span>Transparent Risk Propagation (λ = 0.5)</span>
        </button>
      </div>

      {/* TAB 1: MULTI-HOP PATH TRACING */}
      {activeTab === "paths" && (
        <div className="space-y-6">
          {/* Preset Buttons */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                Select Flow Path Scenario:
              </span>
              <span className="text-[11px] font-mono text-text-muted">
                Synthetic Multi-Tier Money Trails
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {PATH_PRESETS.map((p) => {
                const isSelected = sourceId === p.sourceId;
                return (
                  <button
                    key={p.id}
                    onClick={() => selectPathPreset(p)}
                    className={`text-left p-3.5 rounded-xl border transition flex flex-col justify-between ${
                      isSelected
                        ? "bg-cyan-950/30 border-cyan-500/80 shadow-[0_0_15px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/50"
                        : "bg-surface-1 border-border hover:border-border-strong hover:bg-surface-2/60"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-text-primary">{p.name}</span>
                        {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400" />}
                      </div>
                      <p className="text-[11px] text-text-muted leading-relaxed">{p.desc}</p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-border/50 text-[10px] font-mono text-text-muted">
                      Source: <span className="text-cyan-400">{p.sourceId}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Query Bar */}
          <div className="bg-surface-1 border border-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
              <div>
                <label className="text-[10px] text-text-muted block uppercase">Source Account / VPA</label>
                <input
                  type="text"
                  value={sourceId}
                  onChange={(e) => setSourceId(e.target.value)}
                  className="bg-surface-2 border border-border rounded px-2.5 py-1 text-text-primary text-xs font-mono mt-1 w-52"
                />
              </div>

              <div>
                <label className="text-[10px] text-text-muted block uppercase">Target Account (Optional)</label>
                <input
                  type="text"
                  value={targetId}
                  onChange={(e) => setTargetId(e.target.value)}
                  placeholder="Leave empty for all paths"
                  className="bg-surface-2 border border-border rounded px-2.5 py-1 text-text-primary text-xs font-mono mt-1 w-52"
                />
              </div>

              <div>
                <label className="text-[10px] text-text-muted block uppercase">Max Depth (Hops: {maxDepth})</label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(Number(e.target.value))}
                  className="mt-2 w-28 accent-cyan-500"
                />
              </div>

              <div>
                <label className="text-[10px] text-text-muted block uppercase">Min Amount (₹)</label>
                <input
                  type="number"
                  value={minAmount}
                  onChange={(e) => setMinAmount(Number(e.target.value))}
                  className="bg-surface-2 border border-border rounded px-2.5 py-1 text-text-primary text-xs font-mono mt-1 w-24"
                />
              </div>
            </div>

            <button
              onClick={() => handleTracePaths()}
              disabled={isTracingPaths}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-mono font-bold bg-cyan-600 hover:bg-cyan-500 text-white transition disabled:opacity-50 shadow-lg shadow-cyan-900/30"
            >
              {isTracingPaths ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Exploring Graph...</span>
                </>
              ) : (
                <>
                  <Search className="w-3.5 h-3.5" />
                  <span>Trace Transaction Flow</span>
                </>
              )}
            </button>
          </div>

          {pathError && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span>{pathError}</span>
            </div>
          )}

          {/* Path Results */}
          {pathsResult && (
            <div className="space-y-4">
              {/* Circular flow warning */}
              {pathsResult.circular_flows_detected && (
                <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs font-mono flex items-center gap-3">
                  <Repeat className="w-5 h-5 text-red-400 flex-shrink-0 animate-spin" />
                  <div>
                    <span className="font-bold text-red-200 block">
                      CIRCULAR MONEY FLOW CYCLE DETECTED!
                    </span>
                    <span>
                      Funds were routed through intermediary accounts and returned to the origin entity.
                      This signature indicates high-confidence laundering or artificial turnover manipulation.
                    </span>
                  </div>
                </div>
              )}

              {/* Dynamic Interactive Visual Topology Graph */}
              {pathGraphData.nodes.length > 0 && (
                <InteractiveCorrelationGraph
                  nodes={pathGraphData.nodes}
                  edges={pathGraphData.edges}
                  highlightedPath={selectedPathNodes}
                  isCircularDetected={pathsResult.circular_flows_detected}
                  title={`Visual Flow Topology: ${pathsResult.source_id}`}
                  subtitle={`Discovered ${pathsResult.paths_found} flow path(s) • Click path cards below or nodes to inspect`}
                />
              )}

              <div className="flex items-center justify-between text-xs font-mono text-text-muted px-1">
                <span>Discovered {pathsResult.paths_found} flow path(s) originating from <strong className="text-cyan-400">{pathsResult.source_id}</strong>:</span>
                <span>Max Depth Checked: {maxDepth} hops</span>
              </div>

              {pathsResult.paths && pathsResult.paths.length > 0 ? (
                <div className="space-y-4">
                  {pathsResult.paths.map((p: any, idx: number) => (
                    <div
                      key={idx}
                      onClick={() => setSelectedPathIndex(idx)}
                      className={`bg-surface-1 border rounded-xl p-5 space-y-4 cursor-pointer transition ${
                        selectedPathIndex === idx
                          ? "border-cyan-500/80 shadow-[0_0_15px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/40"
                          : "border-border hover:border-border-strong hover:bg-surface-2/40"
                      }`}
                    >
                      {/* Path Card Header */}
                      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-border">
                        <div className="flex items-center gap-2 text-xs font-mono">
                          <span className="font-bold text-text-primary">Path #{idx + 1}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-surface-2 text-cyan-400 border border-border">
                            {p.hop_count} Hops
                          </span>
                          {p.is_circular && (
                            <span className="text-[10px] px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 font-bold uppercase">
                              Circular Wash Loop
                            </span>
                          )}
                        </div>

                        <div className="text-right text-xs font-mono">
                          <span className="text-text-muted mr-1.5">Total Path Volume:</span>
                          <span className="font-bold text-emerald-400">
                            ₹{p.total_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                          </span>
                        </div>
                      </div>

                      {/* Explanation */}
                      <p className="text-xs font-mono text-text-secondary bg-surface-2/60 p-2.5 rounded-lg border border-border/50">
                        {p.explanation}
                      </p>

                      {/* Hop Progression Breadcrumb */}
                      <div className="space-y-2">
                        <span className="text-[10px] font-mono uppercase text-text-muted block">
                          Transaction Hop Sequence:
                        </span>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
                          {p.hops?.map((hop: any, hIdx: number) => (
                            <div
                              key={hIdx}
                              className="p-3 bg-surface-2 rounded-lg border border-border text-xs font-mono space-y-1.5"
                            >
                              <div className="flex items-center justify-between text-[10px] text-text-muted">
                                <span>Hop {hIdx + 1}</span>
                                {hop.dwell_time_seconds !== null && hop.dwell_time_seconds !== undefined && (
                                  <span className={`font-bold ${
                                    hop.dwell_time_seconds < 300 ? "text-red-400" : "text-text-secondary"
                                  }`}>
                                    ⏱ Dwell: {Math.round(hop.dwell_time_seconds)}s
                                  </span>
                                )}
                              </div>

                              <div className="flex items-center gap-2 text-text-primary font-semibold truncate">
                                <span className="truncate">{hop.from_account}</span>
                                <ArrowRight className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0" />
                                <span className="truncate">{hop.to_account}</span>
                              </div>

                              <div className="flex items-center justify-between pt-1 border-t border-border/50 text-[11px]">
                                <span className="text-text-muted">{hop.txn_id || "TXN_HOP"}</span>
                                <span className="font-bold text-text-primary">
                                  ₹{hop.amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-surface-1 border border-border rounded-xl text-xs font-mono text-text-muted">
                  No downstream flow paths found matching the specified filters. Try reducing min amount or increasing max depth.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: SUSPICIOUS CLUSTER DISCOVERY */}
      {activeTab === "clusters" && (
        <div className="space-y-6">
          {/* Query Bar */}
          <div className="bg-surface-1 border border-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
              <div>
                <label className="text-[10px] text-text-muted block uppercase">Min Cluster Size</label>
                <select
                  value={minClusterSize}
                  onChange={(e) => setMinClusterSize(Number(e.target.value))}
                  className="bg-surface-2 border border-border rounded px-2.5 py-1 text-text-primary text-xs font-mono mt-1"
                >
                  <option value={2}>2+ Linked Entities</option>
                  <option value={3}>3+ Linked Entities</option>
                  <option value={4}>4+ Linked Entities</option>
                  <option value={5}>5+ Linked Entities</option>
                </select>
              </div>

              <div className="pt-4 text-xs text-text-muted">
                Detects connected components, shared-identifier mule rings, and layering dispersal hubs.
              </div>
            </div>

            <button
              onClick={() => handleScanClusters()}
              disabled={isScanningClusters}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-mono font-bold bg-cyan-600 hover:bg-cyan-500 text-white transition disabled:opacity-50 shadow-lg shadow-cyan-900/30"
            >
              {isScanningClusters ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Scanning Graph Components...</span>
                </>
              ) : (
                <>
                  <Network className="w-3.5 h-3.5" />
                  <span>Scan Suspicious Clusters</span>
                </>
              )}
            </button>
          </div>

          {clusterError && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span>{clusterError}</span>
            </div>
          )}

          {/* Cluster List */}
          {clustersResult && (
            <div className="space-y-4">
              {/* Dynamic Cluster Topology Graph */}
              {clusterGraphData.nodes.length > 0 && (
                <InteractiveCorrelationGraph
                  nodes={clusterGraphData.nodes}
                  edges={clusterGraphData.edges}
                  title={`Cluster & Mule Ring Topology: ${clustersResult.total_clusters} Communities`}
                  subtitle="Weakly connected components, shared-device links, and laundering rings"
                />
              )}

              <div className="flex items-center justify-between text-xs font-mono text-text-muted px-1">
                <span>Detected {clustersResult.total_clusters} suspicious entity cluster(s):</span>
                <span>Algorithm: NetworkX Weakly Connected Components + Shared Identity Rings</span>
              </div>

              {clustersResult.clusters && clustersResult.clusters.length > 0 ? (
                <div className="space-y-4">
                  {clustersResult.clusters.map((c: any, idx: number) => (
                    <div
                      key={idx}
                      className="bg-surface-1 border border-border rounded-xl p-5 space-y-4"
                    >
                      {/* Cluster Header */}
                      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-border">
                        <div className="flex items-center gap-2.5 text-xs font-mono">
                          <span className="font-bold text-text-primary">{c.cluster_id}</span>
                          <span className="text-[10px] px-2 py-0.5 rounded bg-surface-2 text-cyan-400 border border-border">
                            {c.cluster_type.replace(/_/g, " ")}
                          </span>
                          <span
                            className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                              c.suspicion_score >= 0.7
                                ? "bg-red-950 text-red-400 border border-red-800"
                                : "bg-amber-950 text-amber-400 border border-amber-800"
                            }`}
                          >
                            Suspicion: {Math.round(c.suspicion_score * 100)}%
                          </span>
                        </div>

                        <div className="text-xs font-mono text-text-muted">
                          <span>{c.node_count} Nodes</span> • <span>{c.edge_count} Edges</span>
                        </div>
                      </div>

                      {/* Explanation */}
                      <p className="text-xs font-mono text-text-secondary bg-surface-2/60 p-2.5 rounded-lg border border-border/50">
                        {c.reason}
                      </p>

                      {/* Nodes Pill List */}
                      <div>
                        <span className="text-[10px] font-mono uppercase text-text-muted block mb-1.5">
                          Correlated Entities in Cluster ({c.nodes?.length || 0}):
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {c.nodes?.map((node: any, nIdx: number) => (
                            <div
                              key={nIdx}
                              className="px-2.5 py-1 rounded bg-surface-2 border border-border text-xs font-mono flex items-center gap-1.5"
                            >
                              <span className="text-[10px] text-text-muted uppercase">
                                [{node.node_type}]
                              </span>
                              <span className="text-text-primary font-medium">{node.label || node.id}</span>
                              {node.risk_score > 0 && (
                                <span className="text-[10px] font-bold text-red-400">
                                  ({Math.round(node.risk_score * 100)}%)
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center bg-surface-1 border border-border rounded-xl text-xs font-mono text-text-muted">
                  No clusters found meeting the minimum size criteria.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: TRANSPARENT RISK PROPAGATION */}
      {activeTab === "propagation" && (
        <div className="space-y-6">
          {/* Preset Buttons */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-text-muted flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                Select Seed Scenario:
              </span>
              <span className="text-[11px] font-mono text-text-muted">
                Mathematical Model: Risk = Risk_seed × λ^hops
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {PROPAGATION_PRESETS.map((p) => {
                const isSelected = seedIdsInput === p.seedIds;
                return (
                  <button
                    key={p.id}
                    onClick={() => selectPropPreset(p)}
                    className={`text-left p-3.5 rounded-xl border transition flex flex-col justify-between ${
                      isSelected
                        ? "bg-cyan-950/30 border-cyan-500/80 shadow-[0_0_15px_rgba(6,182,212,0.15)] ring-1 ring-cyan-500/50"
                        : "bg-surface-1 border-border hover:border-border-strong hover:bg-surface-2/60"
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-semibold text-text-primary">{p.name}</span>
                        {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400" />}
                      </div>
                      <p className="text-[11px] text-text-muted leading-relaxed">{p.desc}</p>
                    </div>
                    <div className="mt-3 pt-2 border-t border-border/50 text-[10px] font-mono text-text-muted">
                      Seeds: <span className="text-cyan-400">{p.seedIds}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Config Bar */}
          <div className="bg-surface-1 border border-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs font-mono">
              <div>
                <label className="text-[10px] text-text-muted block uppercase">Seed Entity ID(s)</label>
                <input
                  type="text"
                  value={seedIdsInput}
                  onChange={(e) => setSeedIdsInput(e.target.value)}
                  placeholder="ACC_001, ACC_002"
                  className="bg-surface-2 border border-border rounded px-2.5 py-1 text-text-primary text-xs font-mono mt-1 w-64"
                />
              </div>

              <div>
                <label className="text-[10px] text-text-muted block uppercase">Decay Factor λ ({decayFactor})</label>
                <input
                  type="range"
                  min="0.1"
                  max="0.9"
                  step="0.05"
                  value={decayFactor}
                  onChange={(e) => setDecayFactor(Number(e.target.value))}
                  className="mt-2 w-28 accent-cyan-500"
                />
              </div>

              <div>
                <label className="text-[10px] text-text-muted block uppercase">Max Hops ({maxHops})</label>
                <input
                  type="range"
                  min="1"
                  max="4"
                  value={maxHops}
                  onChange={(e) => setMaxHops(Number(e.target.value))}
                  className="mt-2 w-24 accent-cyan-500"
                />
              </div>
            </div>

            <button
              onClick={() => handleCalculatePropagation()}
              disabled={isPropagating}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-mono font-bold bg-cyan-600 hover:bg-cyan-500 text-white transition disabled:opacity-50 shadow-lg shadow-cyan-900/30"
            >
              {isPropagating ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Calculating Decay...</span>
                </>
              ) : (
                <>
                  <TrendingDown className="w-3.5 h-3.5" />
                  <span>Calculate Propagated Risk</span>
                </>
              )}
            </button>
          </div>

          {propError && (
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-400" />
              <span>{propError}</span>
            </div>
          )}

          {/* Propagation Results */}
          {propagationResult && (
            <div className="space-y-4">
              {/* Dynamic Risk Propagation Decay Graph */}
              {propagationGraphData.nodes.length > 0 && (
                <InteractiveCorrelationGraph
                  nodes={propagationGraphData.nodes}
                  edges={propagationGraphData.edges}
                  title={`Geometric Risk Decay Topology (λ = ${propagationResult.decay_factor_used})`}
                  subtitle={`Seeds: ${propagationResult.seeds_processed} • Downstream Contaminated: ${propagationResult.affected_nodes_count}`}
                />
              )}

              {/* Summary Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-surface-1 rounded-xl border border-border">
                  <span className="text-[10px] text-text-muted uppercase font-mono">Seeds Processed</span>
                  <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
                    {propagationResult.seeds_processed}
                  </div>
                </div>

                <div className="p-4 bg-surface-1 rounded-xl border border-border">
                  <span className="text-[10px] text-text-muted uppercase font-mono">Affected Downstream Entities</span>
                  <div className="text-2xl font-bold font-mono text-amber-400 mt-1">
                    {propagationResult.affected_nodes_count}
                  </div>
                </div>

                <div className="p-4 bg-surface-1 rounded-xl border border-border">
                  <span className="text-[10px] text-text-muted uppercase font-mono">Decay Factor Used (λ)</span>
                  <div className="text-2xl font-bold font-mono text-purple-400 mt-1">
                    {propagationResult.decay_factor_used}
                  </div>
                </div>

                <div className="p-4 bg-surface-1 rounded-xl border border-border">
                  <span className="text-[10px] text-text-muted uppercase font-mono">Model Explainability</span>
                  <div className="text-xs font-mono text-emerald-400 mt-2 font-bold">
                    100% Deterministic & Auditable
                  </div>
                </div>
              </div>

              {/* Notice regarding Direct vs Propagated Segregation */}
              <div className="bg-surface-1 border border-border rounded-xl p-4 text-xs font-mono text-text-secondary flex items-start gap-3">
                <Info className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="text-text-primary font-bold block mb-1">
                    Regulatory Protection: Direct vs. Propagated Risk Segregation
                  </span>
                  <span>
                    In accordance with fair financial crime practices, propagated risk is strictly segregated from direct risk.
                    Secondary and tertiary counterparties inherit decay risk for review prioritization, but are never subjected to
                    automatic irreversible freezing without direct behavioral evidence or confirmed Smart Registry hits.
                  </span>
                </div>
              </div>

              {/* Affected Entities Table */}
              <div className="bg-surface-1 border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-4 pb-2 border-b border-border">
                  <div className="flex items-center gap-2">
                    <TrendingDown className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-bold font-mono text-text-primary">
                      Propagated Risk Breakdown
                    </h3>
                  </div>
                  <span className="text-[11px] font-mono text-text-muted">
                    Order: Risk Magnitude Descending
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="text-[10px] uppercase text-text-muted bg-surface-2 border-b border-border">
                      <tr>
                        <th className="p-2.5">Node ID</th>
                        <th className="p-2.5">Type</th>
                        <th className="p-2.5">Hops</th>
                        <th className="p-2.5">Direct Risk</th>
                        <th className="p-2.5">Propagated Risk</th>
                        <th className="p-2.5">Total Risk</th>
                        <th className="p-2.5">Path Explanation</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {propagationResult.nodes?.map((node: any, idx: number) => (
                        <tr key={idx} className="hover:bg-surface-2/50">
                          <td className="p-2.5 font-bold text-text-primary">{node.node_id}</td>
                          <td className="p-2.5 text-text-secondary">{node.node_type}</td>
                          <td className="p-2.5 text-text-muted">{node.hops_from_seed} hop(s)</td>
                          <td className="p-2.5 text-text-secondary">
                            {(node.direct_risk * 100).toFixed(1)}%
                          </td>
                          <td className="p-2.5 font-bold text-amber-400">
                            {(node.propagated_risk * 100).toFixed(1)}%
                          </td>
                          <td className="p-2.5 font-extrabold text-red-400">
                            {(node.total_risk * 100).toFixed(1)}%
                          </td>
                          <td className="p-2.5 text-text-muted text-[11px]">
                            {node.path_explanation?.join(" | ") || "Seed Origin"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
