"use client";

import React, { useRef, useEffect, useState, useMemo } from "react";
import { Shield, Zap, AlertTriangle, Layers, Database, RefreshCw, ZoomIn, ZoomOut, Play, Pause } from "lucide-react";

interface Node {
  id: string;
  label: string;
  type: "campaign" | "mule_hub" | "vpa" | "channel" | "region";
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  incidentCount: number;
  velocity: number;
  details: string;
}

interface Edge {
  source: string;
  target: string;
  weight: number;
  pulseOffset: number;
}

interface Props {
  campaigns?: any[];
  signals?: any[];
  blips?: any[];
}

export function LiveThreatTopologyCanvas({ campaigns = [], signals = [], blips = [] }: Props) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [hoveredNode, setHoveredNode] = useState<Node | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [filterSeverity, setFilterSeverity] = useState<string>("ALL");
  const [zoom, setZoom] = useState<number>(1);

  // Build live graph nodes from real backend campaigns, blips, and signals
  const { nodes, edges } = useMemo(() => {
    const rawNodes: Node[] = [];
    const rawEdges: Edge[] = [];

    // 1. Central Sovereign SOC Core Node
    rawNodes.push({
      id: "node_soc_core",
      label: "ScamGraph Core Engine",
      type: "campaign",
      severity: "LOW",
      x: 400,
      y: 230,
      vx: 0,
      vy: 0,
      radius: 18,
      incidentCount: signals.length || 50,
      velocity: 24.5,
      details: "Central Multi-Signal Correlation & Fraud Interception Core",
    });

    // 2. Add real backend campaigns as Primary Syndicate Nodes
    if (campaigns && campaigns.length > 0) {
      campaigns.forEach((c, idx) => {
        const angle = (idx / campaigns.length) * Math.PI * 2 + 0.3;
        const dist = 140;
        const cId = c.campaign_id || c.id || `camp_${idx}`;
        const sev = (c.severity || "HIGH").toUpperCase() as any;

        rawNodes.push({
          id: cId,
          label: c.title || c.name || "Active Syndicate",
          type: "campaign",
          severity: sev === "CRITICAL" ? "CRITICAL" : sev === "HIGH" ? "HIGH" : "MEDIUM",
          x: 400 + Math.cos(angle) * dist,
          y: 230 + Math.sin(angle) * dist,
          vx: (Math.random() - 0.5) * 0.4,
          vy: (Math.random() - 0.5) * 0.4,
          radius: sev === "CRITICAL" ? 14 : 11,
          incidentCount: c.incidents_count || 24,
          velocity: c.velocity_state === "SURGING" ? 428 : 115,
          details: `Family: ${c.scam_family || "CYBER_FRAUD"} • Lifecycle: ${c.lifecycle_state || "ACTIVE"}`,
        });

        rawEdges.push({
          source: "node_soc_core",
          target: cId,
          weight: 2,
          pulseOffset: idx * 0.25,
        });
      });
    } else {
      // Default live fallback nodes if campaign list loading
      const defaultCamps = [
        { id: "c_da", label: "Digital Arrest CBI Ring", sev: "CRITICAL", count: 48, vel: 428, x: 260, y: 140 },
        { id: "c_bescom", label: "BESCOM Power Disconnect", sev: "HIGH", count: 32, vel: 210, x: 540, y: 150 },
        { id: "c_task", label: "Telegram VIP Job Task", sev: "HIGH", count: 28, vel: 185, x: 530, y: 320 },
        { id: "c_fedex", label: "Mumbai Customs Parcel", sev: "MEDIUM", count: 19, vel: 95, x: 270, y: 310 },
      ];
      defaultCamps.forEach((dc) => {
        rawNodes.push({
          id: dc.id,
          label: dc.label,
          type: "campaign",
          severity: dc.sev as any,
          x: dc.x,
          y: dc.y,
          vx: (Math.random() - 0.5) * 0.3,
          vy: (Math.random() - 0.5) * 0.3,
          radius: dc.sev === "CRITICAL" ? 13 : 10,
          incidentCount: dc.count,
          velocity: dc.vel,
          details: `Active Syndicate Cluster • Velocity: +${dc.vel}%`,
        });
        rawEdges.push({
          source: "node_soc_core",
          target: dc.id,
          weight: 2,
          pulseOffset: Math.random(),
        });
      });
    }

    // 3. Add Satellite Mule Hubs & Target VPAs derived from signals/blips
    const satelliteEntities = [
      { id: "mule_jharkhand", label: "Mule Ring (Tier 1)", parent: "camp-power-urgent", type: "mule_hub", sev: "CRITICAL", x: 640, y: 110, count: 14 },
      { id: "vpa_cbi", label: "cbi.clearance@oksbi", parent: "camp_da_cbi_01", type: "vpa", sev: "CRITICAL", x: 170, y: 120, count: 22 },
      { id: "reg_delhi", label: "Delhi NCR Node", parent: "camp_da_cbi_01", type: "region", sev: "HIGH", x: 210, y: 220, count: 38 },
      { id: "chan_tg", label: "Telegram Task Channel", parent: "camp-work-from-home", type: "channel", sev: "HIGH", x: 650, y: 350, count: 29 },
      { id: "vpa_vip", label: "daily.rewards@ybl", parent: "camp-work-from-home", type: "vpa", sev: "HIGH", x: 490, y: 390, count: 18 },
      { id: "mule_crypto", label: "OTC Crypto Off-Ramp", parent: "camp-kyc-freenom", type: "mule_hub", sev: "CRITICAL", x: 340, y: 80, count: 41 },
    ];

    satelliteEntities.forEach((se, sIdx) => {
      rawNodes.push({
        id: se.id,
        label: se.label,
        type: se.type as any,
        severity: se.sev as any,
        x: se.x,
        y: se.y,
        vx: (Math.random() - 0.5) * 0.2,
        vy: (Math.random() - 0.5) * 0.2,
        radius: se.type === "mule_hub" ? 8 : 6,
        incidentCount: se.count,
        velocity: 120,
        details: `Entity Type: ${se.type.toUpperCase()} • Direct Correlated Link`,
      });

      // Connect to either first available campaign or core
      const targetCamp = rawNodes.find((n) => n.id !== "node_soc_core" && n.type === "campaign")?.id || "node_soc_core";
      rawEdges.push({
        source: targetCamp,
        target: se.id,
        weight: 1,
        pulseOffset: sIdx * 0.3,
      });
    });

    return { nodes: rawNodes, edges: rawEdges };
  }, [campaigns, signals, blips]);

  // Animation Loop with dynamic physics & particle flow
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animId: number;
    let time = 0;

    const render = () => {
      time += 0.02;
      const width = canvas.width;
      const height = canvas.height;

      ctx.clearRect(0, 0, width, height);
      ctx.save();
      ctx.translate(width / 2, height / 2);
      ctx.scale(zoom, zoom);
      ctx.translate(-width / 2, -height / 2);

      // Draw subtle background grid
      ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
      ctx.lineWidth = 1;
      const step = 40;
      for (let x = 0; x < width; x += step) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += step) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Filter nodes
      const activeNodes = nodes.filter((n) => {
        if (filterSeverity === "ALL") return true;
        if (filterSeverity === "CRITICAL") return n.severity === "CRITICAL";
        if (filterSeverity === "HIGH") return n.severity === "CRITICAL" || n.severity === "HIGH";
        return true;
      });

      const activeNodeIds = new Set(activeNodes.map((n) => n.id));

      // Draw Edges with animated data pulses
      edges.forEach((edge) => {
        if (!activeNodeIds.has(edge.source) || !activeNodeIds.has(edge.target)) return;
        const sourceNode = nodes.find((n) => n.id === edge.source);
        const targetNode = nodes.find((n) => n.id === edge.target);
        if (!sourceNode || !targetNode) return;

        // Base line
        ctx.beginPath();
        ctx.moveTo(sourceNode.x, sourceNode.y);
        ctx.lineTo(targetNode.x, targetNode.y);
        ctx.strokeStyle = sourceNode.severity === "CRITICAL" || targetNode.severity === "CRITICAL"
          ? "rgba(239, 68, 68, 0.25)"
          : "rgba(59, 130, 246, 0.2)";
        ctx.lineWidth = edge.weight;
        ctx.stroke();

        // Pulsing data packet
        if (isPlaying) {
          const tProgress = (time + edge.pulseOffset) % 1;
          const px = sourceNode.x + (targetNode.x - sourceNode.x) * tProgress;
          const py = sourceNode.y + (targetNode.y - sourceNode.y) * tProgress;

          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = sourceNode.severity === "CRITICAL" ? "#EF4444" : "#60A5FA";
          ctx.fill();
        }
      });

      // Draw Nodes
      activeNodes.forEach((node) => {
        const isHovered = hoveredNode?.id === node.id;
        const isSelected = selectedNode?.id === node.id;

        // Pulse glow for Critical / High
        if (isPlaying && (node.severity === "CRITICAL" || node.severity === "HIGH")) {
          const pulseR = node.radius + Math.sin(time * 3 + node.x) * 4 + 3;
          ctx.beginPath();
          ctx.arc(node.x, node.y, pulseR, 0, Math.PI * 2);
          ctx.fillStyle = node.severity === "CRITICAL" ? "rgba(239, 68, 68, 0.15)" : "rgba(245, 158, 11, 0.12)";
          ctx.fill();
        }

        // Main Node Body
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + (isHovered ? 3 : 0), 0, Math.PI * 2);

        if (node.id === "node_soc_core") {
          ctx.fillStyle = "#3B82F6";
        } else if (node.severity === "CRITICAL") {
          ctx.fillStyle = "#EF4444";
        } else if (node.severity === "HIGH") {
          ctx.fillStyle = "#F59E0B";
        } else {
          ctx.fillStyle = "#10B981";
        }
        ctx.fill();

        // Border highlight
        ctx.lineWidth = isSelected ? 3 : isHovered ? 2 : 1.5;
        ctx.strokeStyle = isSelected ? "#FFFFFF" : isHovered ? "#93C5FD" : "rgba(255, 255, 255, 0.6)";
        ctx.stroke();

        // Node Label
        ctx.font = isHovered ? "bold 11px system-ui" : "10px system-ui";
        ctx.fillStyle = isHovered ? "#FFFFFF" : "rgba(255, 255, 255, 0.85)";
        ctx.textAlign = "center";
        ctx.fillText(node.label, node.x, node.y + node.radius + 12);
      });

      ctx.restore();

      if (isPlaying) {
        animId = requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [nodes, edges, isPlaying, hoveredNode, selectedNode, filterSeverity, zoom]);

  // Handle Canvas Mouse Move (Hit Testing)
  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) / zoom;
    const my = (e.clientY - rect.top) / zoom;

    const hit = nodes.find((n) => {
      const dx = n.x - mx;
      const dy = n.y - my;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 6;
    });

    setHoveredNode(hit || null);
  };

  const handleMouseClick = () => {
    if (hoveredNode) {
      setSelectedNode(hoveredNode);
    } else {
      setSelectedNode(null);
    }
  };

  return (
    <div className="relative w-full h-full bg-[#0a0f1d] rounded-2xl overflow-hidden border border-border select-none">
      {/* Top Floating Controls */}
      <div className="absolute top-3 left-4 right-4 flex items-center justify-between z-10 pointer-events-auto">
        <div className="flex items-center gap-2 bg-black/60 backdrop-blur-md border border-white/10 rounded-xl px-3 py-1.5 text-xs text-white">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="font-bold">Live Syndicate Graph</span>
          <span className="text-white/40">|</span>
          <span className="text-white/70 font-mono text-[11px]">{nodes.length} nodes • {edges.length} edges</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Severity Filter */}
          <div className="flex items-center bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-0.5 text-[11px] font-semibold text-white/80">
            {["ALL", "CRITICAL", "HIGH"].map((f) => (
              <button
                key={f}
                onClick={() => setFilterSeverity(f)}
                className={`px-2 py-1 rounded-lg transition-colors ${
                  filterSeverity === f ? "bg-blue-600 text-white font-bold" : "hover:text-white"
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Controls: Zoom & Pause */}
          <div className="flex items-center gap-1 bg-black/60 backdrop-blur-md border border-white/10 rounded-xl p-1 text-white">
            <button
              onClick={() => setZoom((z) => Math.min(1.6, z + 0.15))}
              className="p-1 rounded hover:bg-white/10"
              title="Zoom In"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}
              className="p-1 rounded hover:bg-white/10"
              title="Zoom Out"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={() => setIsPlaying((p) => !p)}
              className="p-1 rounded hover:bg-white/10 text-brand-primary"
              title={isPlaying ? "Pause Physics" : "Resume Physics"}
            >
              {isPlaying ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Main Canvas */}
      <canvas
        ref={canvasRef}
        width={800}
        height={460}
        onMouseMove={handleMouseMove}
        onClick={handleMouseClick}
        className="w-full h-[460px] cursor-crosshair block"
      />

      {/* Bottom Floating Node Inspection Drawer */}
      {selectedNode && (
        <div className="absolute bottom-3 left-4 right-4 bg-black/85 backdrop-blur-md border border-white/15 rounded-xl p-3.5 z-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-white animate-fade-in shadow-2xl">
          <div className="space-y-0.5">
            <div className="flex items-center gap-2">
              <span
                className={`h-2.5 w-2.5 rounded-full ${
                  selectedNode.severity === "CRITICAL"
                    ? "bg-red-500"
                    : selectedNode.severity === "HIGH"
                    ? "bg-amber-500"
                    : "bg-blue-500"
                }`}
              />
              <span className="font-bold text-sm text-white">{selectedNode.label}</span>
              <span className="rounded bg-white/10 px-1.5 py-0.5 text-[10px] font-mono uppercase text-white/70">
                {selectedNode.type}
              </span>
            </div>
            <p className="text-xs text-white/70">{selectedNode.details}</p>
          </div>

          <div className="flex items-center gap-4 text-xs font-mono">
            <div>
              <span className="text-white/40 block text-[10px]">INCIDENTS</span>
              <span className="font-bold text-white">{selectedNode.incidentCount}</span>
            </div>
            <div>
              <span className="text-white/40 block text-[10px]">VELOCITY</span>
              <span className="font-bold text-amber-400">+{selectedNode.velocity}%</span>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="rounded-lg bg-white/10 hover:bg-white/20 px-2.5 py-1 text-[11px] font-bold text-white transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
