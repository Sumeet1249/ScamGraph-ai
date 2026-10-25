"use client";

import React, { useState, useRef, useMemo, useEffect } from "react";
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  Minimize2,
  RefreshCw,
  ShieldAlert,
  Layers,
  ArrowRight,
  TrendingDown,
  Repeat,
  Info,
  DollarSign,
  Clock,
  Eye,
  CheckCircle,
  Box,
} from "lucide-react";
import dynamic from "next/dynamic";

const ThreeCorrelationGraph = dynamic(
  () => import("./ThreeCorrelationGraph").then((mod) => mod.ThreeCorrelationGraph),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-full flex items-center justify-center bg-[#080d1a] text-xs font-mono text-cyan-400">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-cyan-500/30 border-t-cyan-400 animate-spin" />
          <span>Initializing 3D Spatial Network...</span>
        </div>
      </div>
    ),
  }
);

export interface VisualNode {
  id: string;
  label: string;
  node_type: "ACCOUNT" | "UPI_VPA" | "PHONE" | "DEVICE" | "IP" | "REPORT" | string;
  risk_score?: number;
  tier?: string;
  bank?: string;
  x?: number;
  y?: number;
  isSeed?: boolean;
  propagatedRisk?: number;
  metadata?: Record<string, any>;
}

export interface VisualEdge {
  id: string;
  source: string;
  target: string;
  amount?: number;
  dwell_time_seconds?: number | null;
  relationship_type?: string;
  transaction_id?: string;
  is_circular?: boolean;
}

interface InteractiveCorrelationGraphProps {
  nodes: VisualNode[];
  edges: VisualEdge[];
  highlightedPath?: string[]; // Array of node IDs in currently selected path
  isCircularDetected?: boolean;
  onSelectNode?: (node: VisualNode | null) => void;
  title?: string;
  subtitle?: string;
}

export function InteractiveCorrelationGraph({
  nodes,
  edges,
  highlightedPath = [],
  isCircularDetected = false,
  onSelectNode,
  title = "Entity & Transaction Flow Graph",
  subtitle = "Interactive multi-hop topology and risk flow visualization",
}: InteractiveCorrelationGraphProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [layoutMode, setLayoutMode] = useState<"3d" | "flow" | "circular" | "grid">("3d");

  const svgRef = useRef<SVGSVGElement>(null);

  // Position nodes dynamically based on layoutMode
  const positionedNodes = useMemo(() => {
    if (!nodes || nodes.length === 0) return [];

    const width = 850;
    const height = 480;
    const padding = 70;

    if (layoutMode === "circular" || isCircularDetected) {
      // Circular Ring Layout
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(centerX, centerY) - padding - 20;

      return nodes.map((node, i) => {
        const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
        return {
          ...node,
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle),
        };
      });
    }

    if (layoutMode === "grid") {
      const cols = Math.ceil(Math.sqrt(nodes.length * 1.5));
      const colWidth = (width - padding * 2) / Math.max(1, cols - 1);
      const rows = Math.ceil(nodes.length / cols);
      const rowHeight = (height - padding * 2) / Math.max(1, rows - 1);

      return nodes.map((node, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        return {
          ...node,
          x: padding + col * colWidth,
          y: padding + row * rowHeight,
        };
      });
    }

    // Default: Multi-Hop Tiered Flow Layout (Left-to-Right progression)
    // Group into levels using edge adjacency
    const levels: Record<string, number> = {};
    const inDegree: Record<string, number> = {};

    nodes.forEach((n) => {
      inDegree[n.id] = 0;
    });
    edges.forEach((e) => {
      if (inDegree[e.target] !== undefined) {
        inDegree[e.target] = (inDegree[e.target] || 0) + 1;
      }
    });

    // Seed root nodes with level 0
    nodes.forEach((n) => {
      if (inDegree[n.id] === 0 || n.id.includes("VICTIM") || n.id.includes("SEED") || n.isSeed) {
        levels[n.id] = 0;
      }
    });

    // BFS to assign levels
    for (let pass = 0; pass < 6; pass++) {
      edges.forEach((e) => {
        const sLevel = levels[e.source];
        if (sLevel !== undefined) {
          const tLevel = levels[e.target];
          if (tLevel === undefined || tLevel <= sLevel) {
            levels[e.target] = sLevel + 1;
          }
        }
      });
    }

    // Group nodes by level
    const levelBuckets: Record<number, VisualNode[]> = {};
    nodes.forEach((n) => {
      const lvl = levels[n.id] !== undefined ? levels[n.id] : 1;
      if (!levelBuckets[lvl]) levelBuckets[lvl] = [];
      levelBuckets[lvl].push(n);
    });

    const maxLevel = Math.max(1, ...Object.keys(levelBuckets).map(Number));
    const stepX = (width - padding * 2) / Math.max(1, maxLevel);

    const result: VisualNode[] = [];
    Object.entries(levelBuckets).forEach(([lvlStr, nList]) => {
      const lvl = Number(lvlStr);
      const x = padding + lvl * stepX;
      const stepY = (height - padding * 2) / Math.max(1, nList.length + 1);

      nList.forEach((n, idx) => {
        result.push({
          ...n,
          x,
          y: padding + (idx + 1) * stepY,
        });
      });
    });

    return result;
  }, [nodes, edges, layoutMode, isCircularDetected]);

  // Lookup map for fast coordinate access
  const nodeMap = useMemo(() => {
    const map = new Map<string, VisualNode>();
    positionedNodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [positionedNodes]);

  const selectedNode = useMemo(() => {
    return positionedNodes.find((n) => n.id === selectedNodeId) || null;
  }, [positionedNodes, selectedNodeId]);

  const activeEdge = useMemo(() => {
    return edges.find((e) => e.id === hoveredEdgeId) || null;
  }, [edges, hoveredEdgeId]);

  // Handle pan & zoom drag
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPanOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleResetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  // Node color helper
  const getNodeColor = (node: VisualNode) => {
    const score = node.propagatedRisk !== undefined ? node.propagatedRisk : (node.risk_score || 0);

    if (node.isSeed || node.id.includes("FRAUD") || score >= 0.85) {
      return { fill: "#dc2626", stroke: "#f87171", text: "#fca5a5", ring: "rgba(220, 38, 38, 0.4)" };
    }
    if (score >= 0.5) {
      return { fill: "#d97706", stroke: "#fbbf24", text: "#fde68a", ring: "rgba(217, 119, 6, 0.4)" };
    }
    if (node.id.includes("VICTIM") || node.id.includes("INFLOW")) {
      return { fill: "#0284c7", stroke: "#38bdf8", text: "#bae6fd", ring: "rgba(2, 132, 199, 0.4)" };
    }
    if (node.node_type === "PHONE" || node.node_type === "DEVICE" || node.node_type === "IP") {
      return { fill: "#7c3aed", stroke: "#a78bfa", text: "#ddd6fe", ring: "rgba(124, 58, 237, 0.4)" };
    }
    return { fill: "#2563eb", stroke: "#60a5fa", text: "#bfdbfe", ring: "rgba(37, 99, 235, 0.3)" };
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative font-sans">
      {/* Header Bar */}
      <div className="px-5 py-3.5 bg-slate-900/90 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 backdrop-blur-md">
        <div className="flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-bold text-white tracking-wide">{title}</h3>
              {isCircularDetected && (
                <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-red-950/80 text-red-400 border border-red-700/60 animate-pulse">
                  <Repeat className="h-2.5 w-2.5" />
                  CIRCULAR LOOP ACTIVE
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-400">{subtitle}</p>
          </div>
        </div>

        {/* Graph Controls */}
        <div className="flex items-center gap-2">
          {/* Layout Mode Buttons */}
          <div className="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-mono">
            <button
              onClick={() => setLayoutMode("3d")}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-[11px] transition ${
                layoutMode === "3d"
                  ? "bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold shadow-md shadow-cyan-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Box className="h-3 w-3 text-cyan-300" />
              <span>3D Spatial</span>
            </button>
            <button
              onClick={() => setLayoutMode("flow")}
              className={`px-2.5 py-1 rounded text-[11px] transition ${
                layoutMode === "flow" ? "bg-cyan-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Linear Flow
            </button>
            <button
              onClick={() => setLayoutMode("circular")}
              className={`px-2.5 py-1 rounded text-[11px] transition ${
                layoutMode === "circular" ? "bg-cyan-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Wash Ring
            </button>
            <button
              onClick={() => setLayoutMode("grid")}
              className={`px-2.5 py-1 rounded text-[11px] transition ${
                layoutMode === "grid" ? "bg-cyan-600 text-white font-bold" : "text-slate-400 hover:text-white"
              }`}
            >
              Cluster Grid
            </button>
          </div>

          {/* Zoom controls */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            <button
              onClick={() => setZoomLevel((z) => Math.min(2.0, z + 0.15))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
              title="Zoom In"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.15))}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
              title="Zoom Out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={handleResetView}
              className="p-1 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition"
              title="Reset View"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Canvas Area: 3D Spatial Scene or 2D SVG Layout */}
      <div className="relative h-[520px] w-full overflow-hidden bg-[#080d1a] select-none">
        {layoutMode === "3d" ? (
          <ThreeCorrelationGraph
            nodes={nodes}
            edges={edges}
            highlightedPath={highlightedPath}
            isCircularDetected={isCircularDetected}
            selectedNodeId={selectedNodeId}
            onSelectNode={(node) => {
              setSelectedNodeId(node ? node.id : null);
              if (onSelectNode) onSelectNode(node);
            }}
          />
        ) : (
          <div
            className="relative h-full w-full overflow-hidden bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:16px_16px] cursor-grab active:cursor-grabbing select-none"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
          >
            <svg
              ref={svgRef}
              viewBox="0 0 850 480"
              className="w-full h-full"
              style={{
                transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                transformOrigin: "center center",
                transition: isDragging ? "none" : "transform 0.15s ease-out",
              }}
            >
          <defs>
            {/* Arrowheads */}
            <marker
              id="arrow-cyan"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#06b6d4" />
            </marker>
            <marker
              id="arrow-red"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
            </marker>
            <marker
              id="arrow-slate"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
            </marker>

            {/* Glowing filter */}
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background Grid Accent Lines */}
          <line x1="0" y1="240" x2="850" y2="240" stroke="#1e293b" strokeDasharray="4 4" strokeWidth="0.8" />
          <line x1="425" y1="0" x2="425" y2="480" stroke="#1e293b" strokeDasharray="4 4" strokeWidth="0.8" />

          {/* Edges */}
          {edges.map((edge) => {
            const src = nodeMap.get(edge.source);
            const tgt = nodeMap.get(edge.target);
            if (!src || !tgt || src.x === undefined || src.y === undefined || tgt.x === undefined || tgt.y === undefined) {
              return null;
            }

            const isHighlighted =
              highlightedPath.length > 0 &&
              highlightedPath.includes(edge.source) &&
              highlightedPath.includes(edge.target);

            const isHovered = hoveredEdgeId === edge.id;
            const isCircular = edge.is_circular || isCircularDetected;

            // Curve calculation
            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const midX = (src.x + tgt.x) / 2;
            const midY = (src.y + tgt.y) / 2;

            // Add offset for curve
            const curveOffset = isCircular ? 40 : Math.min(25, Math.abs(dx) * 0.1);
            const ctrlX = midX;
            const ctrlY = midY - curveOffset;

            const pathD = `M ${src.x} ${src.y} Q ${ctrlX} ${ctrlY} ${tgt.x} ${tgt.y}`;

            const strokeColor = isCircular
              ? "#ef4444"
              : isHighlighted || isHovered
              ? "#06b6d4"
              : "#475569";

            const markerUrl = isCircular
              ? "url(#arrow-red)"
              : isHighlighted || isHovered
              ? "url(#arrow-cyan)"
              : "url(#arrow-slate)";

            return (
              <g
                key={edge.id}
                className="transition-all cursor-pointer group"
                onMouseEnter={() => setHoveredEdgeId(edge.id)}
                onMouseLeave={() => setHoveredEdgeId(null)}
              >
                {/* Thick invisible stroke for easier hover hit */}
                <path d={pathD} fill="none" stroke="transparent" strokeWidth="16" />

                {/* Base Edge Path */}
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={isHighlighted || isHovered ? 2.5 : 1.5}
                  strokeDasharray={isCircular ? "6 4" : "none"}
                  markerEnd={markerUrl}
                  filter={isHighlighted || isHovered ? "url(#glow)" : undefined}
                />

                {/* Animated Flow Pulse Particles */}
                {(isHighlighted || isHovered || isCircular) && (
                  <path
                    d={pathD}
                    fill="none"
                    stroke={isCircular ? "#fca5a5" : "#67e8f9"}
                    strokeWidth="3"
                    strokeDasharray="8 32"
                    strokeLinecap="round"
                    className="animate-[dash_1.5s_linear_infinite]"
                  >
                    <animate
                      attributeName="stroke-dashoffset"
                      from="40"
                      to="0"
                      dur="1.2s"
                      repeatCount="indefinite"
                    />
                  </path>
                )}

                {/* Midpoint Amount / Dwell Badge */}
                {edge.amount && (
                  <g transform={`translate(${ctrlX}, ${ctrlY - 10})`}>
                    <rect
                      x="-38"
                      y="-10"
                      width="76"
                      height="18"
                      rx="9"
                      fill="#090d16"
                      stroke={isHighlighted || isHovered ? "#06b6d4" : "#334155"}
                      strokeWidth="1"
                    />
                    <text
                      x="0"
                      y="2"
                      textAnchor="middle"
                      fill={isHighlighted || isHovered ? "#22d3ee" : "#cbd5e1"}
                      fontSize="9"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      ₹{(edge.amount / 1000).toFixed(0)}k
                      {edge.dwell_time_seconds ? ` (${edge.dwell_time_seconds}s)` : ""}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Nodes */}
          {positionedNodes.map((node) => {
            if (node.x === undefined || node.y === undefined) return null;

            const isSelected = selectedNodeId === node.id;
            const isHovered = hoveredNodeId === node.id;
            const isPathNode = highlightedPath.includes(node.id);
            const colors = getNodeColor(node);

            const radius = isSelected ? 24 : isPathNode ? 21 : 18;

            return (
              <g
                key={node.id}
                className="cursor-pointer transition-all"
                onClick={() => {
                  const next = selectedNodeId === node.id ? null : node.id;
                  setSelectedNodeId(next);
                  if (onSelectNode) onSelectNode(next ? node : null);
                }}
                onMouseEnter={() => setHoveredNodeId(node.id)}
                onMouseLeave={() => setHoveredNodeId(null)}
              >
                {/* Glow ring on hover/selected */}
                {(isSelected || isHovered || isPathNode || node.isSeed) && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={radius + 8}
                    fill="none"
                    stroke={colors.stroke}
                    strokeWidth="1.5"
                    strokeDasharray="4 4"
                    className="animate-spin-slow opacity-80"
                  />
                )}

                {/* Outer shadow / halo */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={radius + 3}
                  fill={colors.ring}
                />

                {/* Main Node Circle */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={radius}
                  fill={colors.fill}
                  stroke={isSelected ? "#ffffff" : colors.stroke}
                  strokeWidth={isSelected ? 2.5 : 1.8}
                  filter={isSelected ? "url(#glow)" : undefined}
                />

                {/* Node Center Label Icon / Initials */}
                <text
                  x={node.x}
                  y={node.y + 4}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="10"
                  fontFamily="monospace"
                  fontWeight="bold"
                >
                  {node.node_type === "PHONE"
                    ? "📱"
                    : node.node_type === "DEVICE"
                    ? "💻"
                    : node.node_type === "IP"
                    ? "🌐"
                    : node.id.includes("VICTIM")
                    ? "VIC"
                    : node.id.includes("EXIT")
                    ? "EXIT"
                    : node.id.includes("HUB")
                    ? "HUB"
                    : "MULE"}
                </text>

                {/* Top Risk Pill */}
                {node.risk_score !== undefined && (
                  <g transform={`translate(${node.x}, ${node.y - radius - 8})`}>
                    <rect
                      x="-16"
                      y="-7"
                      width="32"
                      height="14"
                      rx="7"
                      fill="#0f172a"
                      stroke={colors.stroke}
                      strokeWidth="1"
                    />
                    <text
                      x="0"
                      y="3"
                      textAnchor="middle"
                      fill={colors.text}
                      fontSize="8"
                      fontFamily="monospace"
                      fontWeight="bold"
                    >
                      {Math.round(node.risk_score * 100)}%
                    </text>
                  </g>
                )}

                {/* Bottom Node Title */}
                <g transform={`translate(${node.x}, ${node.y + radius + 12})`}>
                  <rect
                    x="-65"
                    y="-8"
                    width="130"
                    height="18"
                    rx="4"
                    fill="#020617"
                    stroke="#1e293b"
                    strokeWidth="0.8"
                    opacity="0.9"
                  />
                  <text
                    x="0"
                    y="4"
                    textAnchor="middle"
                    fill="#f1f5f9"
                    fontSize="9.5"
                    fontFamily="monospace"
                    fontWeight={isSelected ? "bold" : "normal"}
                  >
                    {node.label && node.label.length > 20
                      ? `${node.label.slice(0, 19)}…`
                      : node.label || node.id}
                  </text>
                </g>
              </g>
            );
          })}
            </svg>
          </div>
        )}

        {/* Selected Node Inspector Flyout */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-72 bg-slate-950/95 border border-slate-700/80 rounded-xl p-4 text-xs font-mono shadow-2xl backdrop-blur-lg animate-in fade-in slide-in-from-right-4 duration-200">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-[10px] uppercase tracking-wider text-cyan-400 font-bold flex items-center gap-1.5">
                <Eye className="h-3.5 w-3.5" />
                Entity Details
              </span>
              <button
                onClick={() => setSelectedNodeId(null)}
                className="text-slate-400 hover:text-white text-xs px-1.5 py-0.5 rounded hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="mt-3 space-y-2">
              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Identifier ID</span>
                <span className="text-white font-bold text-xs select-all">{selectedNode.id}</span>
              </div>

              <div>
                <span className="text-[10px] text-slate-500 block uppercase">Entity Label / Name</span>
                <span className="text-cyan-300 font-medium text-xs">{selectedNode.label}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[9px] text-slate-500 block">TYPE</span>
                  <span className="text-white font-bold text-[11px]">{selectedNode.node_type}</span>
                </div>
                <div className="p-2 rounded bg-slate-900 border border-slate-800">
                  <span className="text-[9px] text-slate-500 block">RISK SCORE</span>
                  <span
                    className={`font-bold text-[11px] ${
                      (selectedNode.risk_score || 0) >= 0.7 ? "text-red-400" : "text-amber-400"
                    }`}
                  >
                    {Math.round((selectedNode.risk_score || 0) * 100)}%
                  </span>
                </div>
              </div>

              {selectedNode.metadata?.bank && (
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Banking Institution</span>
                  <span className="text-slate-300 text-xs">{selectedNode.metadata.bank}</span>
                </div>
              )}

              {selectedNode.metadata?.tier && (
                <div>
                  <span className="text-[10px] text-slate-500 block uppercase">Flow Hierarchy</span>
                  <span className="text-purple-300 text-xs font-semibold">{selectedNode.metadata.tier}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Hovered Edge Info Pill */}
        {activeEdge && (
          <div className="absolute bottom-4 left-4 bg-slate-950/95 border border-cyan-500/50 rounded-xl px-4 py-2.5 text-xs font-mono shadow-xl flex items-center gap-3 backdrop-blur-md">
            <DollarSign className="h-4 w-4 text-cyan-400 shrink-0" />
            <div>
              <span className="text-white font-bold">
                {activeEdge.source} → {activeEdge.target}
              </span>
              <div className="flex items-center gap-3 text-[11px] text-slate-400 mt-0.5">
                <span>
                  Amount: <strong className="text-emerald-400">₹{activeEdge.amount?.toLocaleString("en-IN")}</strong>
                </span>
                {activeEdge.dwell_time_seconds !== null && activeEdge.dwell_time_seconds !== undefined && (
                  <span>
                    Dwell: <strong className="text-amber-300">{activeEdge.dwell_time_seconds}s</strong>
                  </span>
                )}
                {activeEdge.transaction_id && <span>Txn: {activeEdge.transaction_id}</span>}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Topology Summary Bar */}
      <div className="px-5 py-3 bg-slate-950 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs font-mono text-slate-400">
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-cyan-400" />
            Nodes: <strong className="text-white">{nodes.length}</strong>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-indigo-400" />
            Transactions: <strong className="text-white">{edges.length}</strong>
          </span>
          <span className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-red-400" />
            Syndicate Risk: <strong className="text-red-400">High Confidence</strong>
          </span>
        </div>

        <div className="text-[11px] text-slate-500 flex items-center gap-2">
          <span>Click any node to inspect</span> • <span>Drag to pan & zoom</span>
        </div>
      </div>
    </div>
  );
}
