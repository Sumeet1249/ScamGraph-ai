"use client";

import React, { useState, useRef, useEffect, useCallback, useMemo } from "react";
import {
  MuleNode,
  MuleEdge,
  MuleNodeType,
  MuleGraphData,
  NODE_TYPE_INFO,
  DEFAULT_MULE_SCENARIO,
  FAST_UPI_SCENARIO,
  BLANK_SCENARIO,
} from "@/types/mulehunter";
import { BoxNode } from "./BoxNode";
import { ConnectionLine } from "./ConnectionLine";
import { PropertyInspector } from "./PropertyInspector";
import { Toolbar } from "./Toolbar";
import { CheckCircle2, AlertTriangle, Info, X } from "lucide-react";

const STORAGE_KEY = "scamgraph_mulehunter_graph_v1";

export const MuleHunterCanvas: React.FC = () => {
  // Graph Data State
  const [nodes, setNodes] = useState<MuleNode[]>(DEFAULT_MULE_SCENARIO.nodes);
  const [edges, setEdges] = useState<MuleEdge[]>(DEFAULT_MULE_SCENARIO.edges);
  const [graphName, setGraphName] = useState<string>(DEFAULT_MULE_SCENARIO.name);
  const [graphDesc, setGraphDesc] = useState<string>(DEFAULT_MULE_SCENARIO.description);

  // Canvas Viewport Pan & Zoom
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 30, y: 20 });
  const [zoom, setZoom] = useState<number>(0.92);

  // Selection
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  // Connecting State
  const [isConnectingMode, setIsConnectingMode] = useState<boolean>(false);
  const [connectSourceNodeId, setConnectSourceNodeId] = useState<string | null>(null);
  const [connectDraftPos, setConnectDraftPos] = useState<{ x: number; y: number } | null>(null);

  // Canvas Viewport Options
  const [gridType, setGridType] = useState<"dots" | "blueprint" | "none">("blueprint");
  const [isSimulating, setIsSimulating] = useState<boolean>(true);

  // Toast Notification
  const [toast, setToast] = useState<{ message: string; type: "success" | "info" | "warning" } | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingCanvasRef = useRef<boolean>(false);
  const lastMousePosRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // Dragging Node State
  const draggingNodeRef = useRef<{
    nodeId: string;
    startNodeX: number;
    startNodeY: number;
    startMouseX: number;
    startMouseY: number;
  } | null>(null);

  // Auto-hide toast after 4s
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 4000);
    return () => clearTimeout(timer);
  }, [toast]);

  // Load from localStorage on initial mount if available
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed: MuleGraphData = JSON.parse(saved);
        if (parsed && Array.isArray(parsed.nodes) && Array.isArray(parsed.edges)) {
          setNodes(parsed.nodes);
          setEdges(parsed.edges);
          if (parsed.name) setGraphName(parsed.name);
          if (parsed.description) setGraphDesc(parsed.description);
          if (parsed.pan) setPan(parsed.pan);
          if (parsed.zoom) setZoom(parsed.zoom);
        }
      }
    } catch (e) {
      console.error("Failed to load initial MuleHunter graph:", e);
    }
  }, []);

  // Save to localStorage helper
  const handleSaveLocalStorage = useCallback(() => {
    try {
      const data: MuleGraphData = {
        id: "mulehunter-" + Date.now(),
        name: graphName,
        description: graphDesc,
        updatedAt: new Date().toISOString(),
        nodes,
        edges,
        pan,
        zoom,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      setToast({ message: "Investigation saved to browser storage!", type: "success" });
    } catch (e) {
      setToast({ message: "Failed to save to local storage", type: "warning" });
    }
  }, [graphName, graphDesc, nodes, edges, pan, zoom]);

  // Load from localStorage helper
  const handleLoadLocalStorage = useCallback(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (!saved) {
        setToast({ message: "No saved investigation found in browser", type: "warning" });
        return;
      }
      const parsed: MuleGraphData = JSON.parse(saved);
      if (parsed && Array.isArray(parsed.nodes)) {
        setNodes(parsed.nodes);
        setEdges(parsed.edges || []);
        setGraphName(parsed.name || "MuleHunter Investigation");
        setGraphDesc(parsed.description || "");
        if (parsed.pan) setPan(parsed.pan);
        if (parsed.zoom) setZoom(parsed.zoom);
        setToast({ message: "Investigation loaded from browser storage!", type: "info" });
      }
    } catch (e) {
      setToast({ message: "Error reading saved investigation", type: "warning" });
    }
  }, []);

  // Export JSON file
  const handleExportJSON = useCallback(() => {
    const data: MuleGraphData = {
      id: "mulehunter-" + Date.now(),
      name: graphName,
      description: graphDesc,
      updatedAt: new Date().toISOString(),
      nodes,
      edges,
      pan,
      zoom,
    };
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mulehunter-graph-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setToast({ message: "Investigation exported as JSON", type: "success" });
  }, [graphName, graphDesc, nodes, edges, pan, zoom]);

  // Import JSON file
  const handleImportJSON = useCallback((file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const parsed = JSON.parse(content);
        if (parsed && Array.isArray(parsed.nodes) && Array.isArray(parsed.edges)) {
          setNodes(parsed.nodes);
          setEdges(parsed.edges);
          if (parsed.name) setGraphName(parsed.name);
          if (parsed.description) setGraphDesc(parsed.description);
          if (parsed.pan) setPan(parsed.pan);
          if (parsed.zoom) setZoom(parsed.zoom);
          setToast({ message: `Imported "${parsed.name || "Investigation"}" successfully!`, type: "success" });
        } else {
          setToast({ message: "Invalid MuleHunter JSON format", type: "warning" });
        }
      } catch (err) {
        setToast({ message: "Failed to parse JSON file", type: "warning" });
      }
    };
    reader.readAsText(file);
  }, []);

  // Export SVG directly
  const handleExportSVG = useCallback(() => {
    if (nodes.length === 0) {
      setToast({ message: "Canvas is empty. Add nodes to export.", type: "warning" });
      return;
    }

    // Compute bounding box of all nodes
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    nodes.forEach((n) => {
      minX = Math.min(minX, n.x);
      minY = Math.min(minY, n.y);
      maxX = Math.max(maxX, n.x + (n.width || 260));
      maxY = Math.max(maxY, n.y + (n.height || 140));
    });

    const padding = 80;
    const width = maxX - minX + padding * 2;
    const height = maxY - minY + padding * 2;
    const offsetX = -minX + padding;
    const offsetY = -minY + padding;

    // Build SVG Content
    let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="background:#090E17; font-family: ui-monospace, monospace;">\n`;

    // Background Grid
    svgContent += `  <defs>
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1E293B" stroke-width="0.7"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="#090E17" />
  <rect width="100%" height="100%" fill="url(#grid)" opacity="0.6"/>\n`;

    // Render Edges in SVG
    edges.forEach((edge) => {
      const sNode = nodes.find((n) => n.id === edge.sourceId);
      const tNode = nodes.find((n) => n.id === edge.targetId);
      if (!sNode || !tNode) return;

      const p1 = { x: sNode.x + sNode.width / 2 + offsetX, y: sNode.y + sNode.height / 2 + offsetY };
      const p2 = { x: tNode.x + tNode.width / 2 + offsetX, y: tNode.y + tNode.height / 2 + offsetY };
      const dx = p2.x - p1.x;
      const cp1x = p1.x + dx * 0.4;
      const cp2x = p2.x - dx * 0.4;

      const pathData = `M ${p1.x} ${p1.y} C ${cp1x} ${p1.y}, ${cp2x} ${p2.y}, ${p2.x} ${p2.y}`;
      svgContent += `  <path d="${pathData}" fill="none" stroke="${edge.color || "#6366F1"}" stroke-width="${edge.width || 2}" stroke-linecap="round"/>\n`;
      if (edge.label) {
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        svgContent += `  <rect x="${midX - 50}" y="${midY - 12}" width="100" height="24" rx="12" fill="#0F172A" stroke="${edge.color || "#6366F1"}" stroke-width="1"/>
  <text x="${midX}" y="${midY + 4}" fill="#F8FAFC" font-size="11" text-anchor="middle" font-weight="bold">${edge.label}</text>\n`;
      }
    });

    // Render Nodes in SVG
    nodes.forEach((n) => {
      const nx = n.x + offsetX;
      const ny = n.y + offsetY;
      const nw = n.width || 260;
      const nh = n.height || 140;

      svgContent += `  <g transform="translate(${nx}, ${ny})">
    <rect width="${nw}" height="${nh}" rx="12" fill="${n.fillColor || "#0F172A"}" stroke="${n.strokeColor || "#38BDF8"}" stroke-width="${n.strokeWidth || 2}" />
    <rect width="${nw}" height="32" rx="12" fill="#000000" fill-opacity="0.25"/>
    <text x="14" y="21" fill="#E2E8F0" font-size="10" font-weight="bold">${(n.type || "NODE").toUpperCase()}</text>
    <text x="${nw - 14}" y="21" fill="${n.risk === "critical" ? "#EF4444" : "#F59E0B"}" font-size="10" font-weight="bold" text-anchor="end">${n.risk.toUpperCase()}</text>
    <text x="14" y="58" fill="#F8FAFC" font-size="13" font-weight="bold">${n.title || ""}</text>
    <text x="14" y="80" fill="#94A3B8" font-size="11">${n.subtitle || ""}</text>
    ${n.accountNumber ? `<text x="14" y="104" fill="#38BDF8" font-size="10">A/C: ${n.accountNumber}</text>` : ""}
    ${n.amount ? `<text x="${nw - 14}" y="125" fill="#F59E0B" font-size="11" font-weight="bold" text-anchor="end">${n.amount}</text>` : ""}
  </g>\n`;
    });

    svgContent += `</svg>`;

    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `mulehunter-diagram-${new Date().toISOString().slice(0, 10)}.svg`;
    a.click();
    URL.revokeObjectURL(url);
    setToast({ message: "Vector SVG diagram exported!", type: "success" });
  }, [nodes, edges]);

  // Export PNG by drawing SVG into Canvas
  const handleExportPNG = useCallback(() => {
    if (nodes.length === 0) {
      setToast({ message: "Canvas is empty. Add nodes to export.", type: "warning" });
      return;
    }

    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;

    nodes.forEach((n) => {
      minX = Math.min(minX, n.x);
      minY = Math.min(minY, n.y);
      maxX = Math.max(maxX, n.x + (n.width || 260));
      maxY = Math.max(maxY, n.y + (n.height || 140));
    });

    const padding = 80;
    const width = Math.max(maxX - minX + padding * 2, 800);
    const height = Math.max(maxY - minY + padding * 2, 600);
    const offsetX = -minX + padding;
    const offsetY = -minY + padding;

    const canvas = document.createElement("canvas");
    canvas.width = width * 2; // high res 2x scale
    canvas.height = height * 2;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.scale(2, 2);

    // Dark Background
    ctx.fillStyle = "#080C14";
    ctx.fillRect(0, 0, width, height);

    // Subtle Grid dots
    ctx.fillStyle = "#1E293B";
    for (let x = 0; x < width; x += 30) {
      for (let y = 0; y < height; y += 30) {
        ctx.fillRect(x, y, 1.5, 1.5);
      }
    }

    // Draw Edges
    edges.forEach((edge) => {
      const sNode = nodes.find((n) => n.id === edge.sourceId);
      const tNode = nodes.find((n) => n.id === edge.targetId);
      if (!sNode || !tNode) return;

      const p1 = { x: sNode.x + sNode.width / 2 + offsetX, y: sNode.y + sNode.height / 2 + offsetY };
      const p2 = { x: tNode.x + tNode.width / 2 + offsetX, y: tNode.y + tNode.height / 2 + offsetY };
      const dx = p2.x - p1.x;
      const cp1x = p1.x + dx * 0.4;
      const cp2x = p2.x - dx * 0.4;

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y);
      ctx.bezierCurveTo(cp1x, p1.y, cp2x, p2.y, p2.x, p2.y);
      ctx.strokeStyle = edge.color || "#6366F1";
      ctx.lineWidth = edge.width || 2;
      ctx.stroke();

      if (edge.label) {
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        ctx.fillStyle = "#0F172A";
        ctx.strokeStyle = edge.color || "#6366F1";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(midX - 55, midY - 12, 110, 24, 12);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = "#F8FAFC";
        ctx.font = "bold 11px monospace";
        ctx.textAlign = "center";
        ctx.fillText(edge.label, midX, midY + 4);
      }
      ctx.restore();
    });

    // Draw Nodes
    nodes.forEach((n) => {
      const nx = n.x + offsetX;
      const ny = n.y + offsetY;
      const nw = n.width || 260;
      const nh = n.height || 140;

      ctx.save();
      ctx.fillStyle = n.fillColor || "#0F172A";
      ctx.strokeStyle = n.strokeColor || "#38BDF8";
      ctx.lineWidth = n.strokeWidth || 2;

      ctx.beginPath();
      ctx.roundRect(nx, ny, nw, nh, 12);
      ctx.fill();
      ctx.stroke();

      // Header strip
      ctx.fillStyle = "rgba(0,0,0,0.3)";
      ctx.beginPath();
      ctx.roundRect(nx, ny, nw, 32, [12, 12, 0, 0]);
      ctx.fill();

      // Header Text
      ctx.fillStyle = "#94A3B8";
      ctx.font = "bold 10px monospace";
      ctx.textAlign = "left";
      ctx.fillText((n.type || "NODE").toUpperCase(), nx + 12, ny + 20);

      ctx.fillStyle = n.risk === "critical" ? "#EF4444" : "#F59E0B";
      ctx.textAlign = "right";
      ctx.fillText(n.risk.toUpperCase(), nx + nw - 12, ny + 20);

      // Body text
      ctx.fillStyle = "#FFFFFF";
      ctx.font = "bold 13px monospace";
      ctx.textAlign = "left";
      ctx.fillText(n.title || "Untitled", nx + 12, ny + 56);

      ctx.fillStyle = "#94A3B8";
      ctx.font = "11px monospace";
      ctx.fillText((n.subtitle || "").slice(0, 32), nx + 12, ny + 76);

      if (n.accountNumber) {
        ctx.fillStyle = "#38BDF8";
        ctx.font = "10px monospace";
        ctx.fillText(`A/C: ${n.accountNumber}`, nx + 12, ny + 98);
      }

      if (n.amount) {
        ctx.fillStyle = "#F59E0B";
        ctx.font = "bold 11px monospace";
        ctx.textAlign = "right";
        ctx.fillText(n.amount, nx + nw - 12, ny + 124);
      }
      ctx.restore();
    });

    const dataUrl = canvas.toDataURL("image/png");
    const a = document.createElement("a");
    a.href = dataUrl;
    a.download = `mulehunter-diagram-${new Date().toISOString().slice(0, 10)}.png`;
    a.click();
    setToast({ message: "High-resolution PNG diagram downloaded!", type: "success" });
  }, [nodes, edges]);

  // Load Preset
  const handleLoadPreset = (presetKey: "default" | "upi" | "blank") => {
    if (presetKey === "default") {
      setNodes(DEFAULT_MULE_SCENARIO.nodes);
      setEdges(DEFAULT_MULE_SCENARIO.edges);
      setGraphName(DEFAULT_MULE_SCENARIO.name);
      setGraphDesc(DEFAULT_MULE_SCENARIO.description);
      setPan({ x: 30, y: 20 });
      setZoom(0.92);
      setToast({ message: "Loaded RBIH Flagship 3-Hop Ring template", type: "info" });
    } else if (presetKey === "upi") {
      setNodes(FAST_UPI_SCENARIO.nodes);
      setEdges(FAST_UPI_SCENARIO.edges);
      setGraphName(FAST_UPI_SCENARIO.name);
      setGraphDesc(FAST_UPI_SCENARIO.description);
      setPan({ x: 50, y: 50 });
      setZoom(1);
      setToast({ message: "Loaded Fast UPI Churn Syndicate template", type: "info" });
    } else {
      setNodes([]);
      setEdges([]);
      setGraphName(BLANK_SCENARIO.name);
      setGraphDesc(BLANK_SCENARIO.description);
      setSelectedNodeId(null);
      setSelectedEdgeId(null);
      setToast({ message: "Blank investigation canvas ready", type: "info" });
    }
  };

  // Clear Canvas
  const handleClearCanvas = () => {
    if (confirm("Clear all nodes and connections from the canvas?")) {
      setNodes([]);
      setEdges([]);
      setSelectedNodeId(null);
      setSelectedEdgeId(null);
      setToast({ message: "Canvas cleared", type: "info" });
    }
  };

  // Add Node
  const handleAddNode = (type: MuleNodeType) => {
    const meta = NODE_TYPE_INFO[type] || NODE_TYPE_INFO.custom;
    const id = `node-${Date.now().toString(36)}`;
    // Center in current view
    const canvasCenterX = (-pan.x + (containerRef.current?.clientWidth || 800) / 2) / zoom - 130;
    const canvasCenterY = (-pan.y + (containerRef.current?.clientHeight || 600) / 2) / zoom - 70;

    const newNode: MuleNode = {
      id,
      x: Math.round(canvasCenterX + (Math.random() * 40 - 20)),
      y: Math.round(canvasCenterY + (Math.random() * 40 - 20)),
      width: 260,
      height: 140,
      title: type === "origin" ? "Victim Account" : type === "cashout" ? "ATM Cash-Out Point" : `${meta.label}`,
      subtitle: "Click to configure account details",
      type,
      risk: meta.defaultRisk,
      fillColor: meta.defaultFill,
      strokeColor: meta.defaultStroke,
      strokeWidth: 2,
      strokeStyle: "solid",
      glow: type === "mule_l1" || type === "cashout",
      amount: "₹0",
    };

    setNodes((prev) => [...prev, newNode]);
    setSelectedNodeId(id);
    setSelectedEdgeId(null);
    setToast({ message: `Created new ${meta.label} box`, type: "success" });
  };

  // Duplicate Node
  const handleDuplicateNode = useCallback((nodeId: string) => {
    const sourceNode = nodes.find((n) => n.id === nodeId);
    if (!sourceNode) return;
    const newId = `node-${Date.now().toString(36)}`;
    const duplicatedNode: MuleNode = {
      ...sourceNode,
      id: newId,
      x: sourceNode.x + 40,
      y: sourceNode.y + 40,
      title: `${sourceNode.title} (Copy)`,
    };
    setNodes((prev) => [...prev, duplicatedNode]);
    setSelectedNodeId(newId);
    setSelectedEdgeId(null);
    setToast({ message: "Node duplicated", type: "info" });
  }, [nodes]);

  // Delete Node
  const handleDeleteNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
    setEdges((prev) => prev.filter((e) => e.sourceId !== nodeId && e.targetId !== nodeId));
    setSelectedNodeId((current) => (current === nodeId ? null : current));
  }, []);

  // Delete Edge
  const handleDeleteEdge = useCallback((edgeId: string) => {
    setEdges((prev) => prev.filter((e) => e.id !== edgeId));
    setSelectedEdgeId((current) => (current === edgeId ? null : current));
  }, []);

  // Reverse Edge
  const handleReverseEdge = (edgeId: string) => {
    setEdges((prev) =>
      prev.map((e) => {
        if (e.id === edgeId) {
          return { ...e, sourceId: e.targetId, targetId: e.sourceId };
        }
        return e;
      })
    );
  };

  // Start connect mode or draft connection from port
  const handleStartConnect = (sourceId: string) => {
    setIsConnectingMode(true);
    setConnectSourceNodeId(sourceId);
    setToast({ message: "Click target box to complete link (or Esc to cancel)", type: "info" });
  };

  // Complete connect
  const handleCompleteConnect = (targetId: string) => {
    if (!connectSourceNodeId) {
      setConnectSourceNodeId(targetId);
      return;
    }
    if (connectSourceNodeId === targetId) {
      setToast({ message: "Cannot connect a box to itself", type: "warning" });
      return;
    }

    // Check if edge already exists
    const exists = edges.some(
      (e) => e.sourceId === connectSourceNodeId && e.targetId === targetId
    );
    if (exists) {
      setToast({ message: "Connection already exists between these boxes", type: "warning" });
      setIsConnectingMode(false);
      setConnectSourceNodeId(null);
      return;
    }

    const sourceNode = nodes.find((n) => n.id === connectSourceNodeId);
    const newEdgeId = `edge-${Date.now().toString(36)}`;
    const newEdge: MuleEdge = {
      id: newEdgeId,
      sourceId: connectSourceNodeId,
      targetId,
      label: "Transfer",
      amount: "₹1,00,000",
      color: sourceNode?.strokeColor || "#6366F1",
      width: 2,
      style: "animated",
      arrow: true,
    };

    setEdges((prev) => [...prev, newEdge]);
    setSelectedEdgeId(newEdgeId);
    setSelectedNodeId(null);
    setIsConnectingMode(false);
    setConnectSourceNodeId(null);
    setToast({ message: "Boxes connected successfully!", type: "success" });
  };

  // Keyboard Shortcuts (Delete, Duplicate, Escape)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input or textarea
      if (
        document.activeElement?.tagName === "INPUT" ||
        document.activeElement?.tagName === "TEXTAREA"
      ) {
        return;
      }

      if (e.key === "Delete" || e.key === "Backspace") {
        if (selectedNodeId) {
          handleDeleteNode(selectedNodeId);
        } else if (selectedEdgeId) {
          handleDeleteEdge(selectedEdgeId);
        }
      }

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "d") {
        e.preventDefault();
        if (selectedNodeId) {
          handleDuplicateNode(selectedNodeId);
        }
      }

      if (e.key === "Escape") {
        setIsConnectingMode(false);
        setConnectSourceNodeId(null);
        setSelectedNodeId(null);
        setSelectedEdgeId(null);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedNodeId, selectedEdgeId, handleDeleteNode, handleDeleteEdge, handleDuplicateNode]);

  // Mouse drag handling for Canvas Pan & Node Drag
  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    // If clicking background canvas
    if (e.target === containerRef.current || (e.target as HTMLElement).tagName === "svg") {
      setSelectedNodeId(null);
      setSelectedEdgeId(null);
      if (isConnectingMode) {
        setIsConnectingMode(false);
        setConnectSourceNodeId(null);
      }
      isDraggingCanvasRef.current = true;
      lastMousePosRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleStartNodeDrag = (nodeId: string, e: React.MouseEvent) => {
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;
    setSelectedNodeId(nodeId);
    setSelectedEdgeId(null);
    draggingNodeRef.current = {
      nodeId,
      startNodeX: node.x,
      startNodeY: node.y,
      startMouseX: e.clientX,
      startMouseY: e.clientY,
    };
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    // 1. If dragging a node
    if (draggingNodeRef.current) {
      const { nodeId, startNodeX, startNodeY, startMouseX, startMouseY } =
        draggingNodeRef.current;
      const dx = (e.clientX - startMouseX) / zoom;
      const dy = (e.clientY - startMouseY) / zoom;

      setNodes((prev) =>
        prev.map((n) => {
          if (n.id === nodeId) {
            return {
              ...n,
              x: Math.round(startNodeX + dx),
              y: Math.round(startNodeY + dy),
            };
          }
          return n;
        })
      );
      return;
    }

    // 2. If panning canvas
    if (isDraggingCanvasRef.current) {
      const dx = e.clientX - lastMousePosRef.current.x;
      const dy = e.clientY - lastMousePosRef.current.y;
      lastMousePosRef.current = { x: e.clientX, y: e.clientY };
      setPan((prev) => ({ x: prev.x + dx, y: prev.y + dy }));
    }
  };

  const handleMouseUp = () => {
    draggingNodeRef.current = null;
    isDraggingCanvasRef.current = false;
  };

  // Zoom with Wheel
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    const newZoom = Math.min(Math.max(zoom * zoomFactor, 0.3), 2.5);
    setZoom(newZoom);
  };

  // Auto-arrange hierarchical DAG layout
  const handleAutoLayout = () => {
    if (nodes.length === 0) return;

    // Calculate in-degree for each node
    const inDegrees: Record<string, number> = {};
    const adj: Record<string, string[]> = {};
    nodes.forEach((n) => {
      inDegrees[n.id] = 0;
      adj[n.id] = [];
    });
    edges.forEach((e) => {
      if (inDegrees[e.targetId] !== undefined) {
        inDegrees[e.targetId] = (inDegrees[e.targetId] || 0) + 1;
      }
      if (adj[e.sourceId]) {
        adj[e.sourceId].push(e.targetId);
      }
    });

    // Assign rank layers using BFS
    const ranks: Record<string, number> = {};
    const queue: string[] = [];

    nodes.forEach((n) => {
      if (inDegrees[n.id] === 0) {
        ranks[n.id] = 0;
        queue.push(n.id);
      }
    });

    // If cycle or no source, start with first node
    if (queue.length === 0 && nodes.length > 0) {
      ranks[nodes[0].id] = 0;
      queue.push(nodes[0].id);
    }

    while (queue.length > 0) {
      const curr = queue.shift()!;
      const currRank = ranks[curr] || 0;
      const neighbors = adj[curr] || [];
      neighbors.forEach((nbr) => {
        if (ranks[nbr] === undefined || ranks[nbr] < currRank + 1) {
          ranks[nbr] = currRank + 1;
          queue.push(nbr);
        }
      });
    }

    // Default any disconnected nodes to rank 0
    nodes.forEach((n) => {
      if (ranks[n.id] === undefined) ranks[n.id] = 0;
    });

    // Group nodes by layer
    const layers: Record<number, string[]> = {};
    Object.entries(ranks).forEach(([nodeId, r]) => {
      if (!layers[r]) layers[r] = [];
      layers[r].push(nodeId);
    });

    const colWidth = 350;
    const rowHeight = 180;
    const startX = 60;
    const startY = 60;

    setNodes((prev) =>
      prev.map((n) => {
        const layerIdx = ranks[n.id] || 0;
        const layerNodes = layers[layerIdx] || [n.id];
        const rowIdx = layerNodes.indexOf(n.id);

        return {
          ...n,
          x: startX + layerIdx * colWidth,
          y: startY + rowIdx * rowHeight,
        };
      })
    );

    setToast({ message: "Auto-arranged graph into hierarchical flow", type: "success" });
  };

  // Selected item getters
  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  );
  const selectedEdge = useMemo(
    () => edges.find((e) => e.id === selectedEdgeId) || null,
    [edges, selectedEdgeId]
  );

  // Stats
  const mulesCount = useMemo(
    () =>
      nodes.filter(
        (n) =>
          n.type === "mule_l1" ||
          n.type === "mule_l2" ||
          n.type === "mule_l3" ||
          n.risk === "critical"
      ).length,
    [nodes]
  );

  const totalVolume = useMemo(() => {
    let sum = 0;
    edges.forEach((e) => {
      const numeric = parseInt((e.amount || e.label || "").replace(/[^0-9]/g, ""), 10);
      if (!isNaN(numeric)) sum += numeric;
    });
    if (sum === 0) return "₹24,50,000";
    return `₹${sum.toLocaleString("en-IN")}`;
  }, [edges]);

  return (
    <div className="flex flex-col h-full w-full min-h-[680px] bg-[#080C14] overflow-hidden select-none relative font-sans">
      {/* Toast Notification Banner */}
      {toast && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-lg bg-cyber-900/95 border border-cyan-500/50 text-cyan-300 shadow-2xl backdrop-blur-md animate-in fade-in slide-in-from-top duration-200">
          {toast.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          ) : toast.type === "warning" ? (
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          ) : (
            <Info className="w-4 h-4 text-cyan-400" />
          )}
          <span className="text-xs font-mono font-semibold">{toast.message}</span>
          <button
            onClick={() => setToast(null)}
            className="ml-2 text-slate-400 hover:text-white"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Floating Mode Prompt Bar when in Connecting Mode */}
      {isConnectingMode && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 z-40 flex items-center gap-3 px-5 py-2.5 rounded-full bg-emerald-950/90 border border-emerald-500/60 text-emerald-200 shadow-xl backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-mono font-bold">
            {connectSourceNodeId
              ? "Click destination box to complete transaction arrow"
              : "Click the origin box to start connection"}
          </span>
          <button
            onClick={() => {
              setIsConnectingMode(false);
              setConnectSourceNodeId(null);
            }}
            className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-900 hover:bg-emerald-800 text-white transition ml-2"
          >
            Cancel (Esc)
          </button>
        </div>
      )}

      {/* Main Top Toolbar */}
      <Toolbar
        isConnectingMode={isConnectingMode}
        onToggleConnectMode={() => {
          setIsConnectingMode(!isConnectingMode);
          setConnectSourceNodeId(null);
        }}
        onAddNode={handleAddNode}
        hasSelection={!!selectedNodeId || !!selectedEdgeId}
        onDeleteSelected={() => {
          if (selectedNodeId) handleDeleteNode(selectedNodeId);
          if (selectedEdgeId) handleDeleteEdge(selectedEdgeId);
        }}
        onDuplicateSelected={() => {
          if (selectedNodeId) handleDuplicateNode(selectedNodeId);
        }}
        zoom={zoom}
        onZoomIn={() => setZoom((z) => Math.min(z * 1.1, 2.5))}
        onZoomOut={() => setZoom((z) => Math.max(z * 0.9, 0.3))}
        onResetZoom={() => setZoom(1)}
        onFitView={() => {
          setPan({ x: 30, y: 20 });
          setZoom(0.9);
        }}
        isSimulating={isSimulating}
        onToggleSimulation={() => setIsSimulating(!isSimulating)}
        gridType={gridType}
        onCycleGrid={() =>
          setGridType((g) => (g === "blueprint" ? "dots" : g === "dots" ? "none" : "blueprint"))
        }
        onSaveLocalStorage={handleSaveLocalStorage}
        onLoadLocalStorage={handleLoadLocalStorage}
        onExportJSON={handleExportJSON}
        onImportJSON={handleImportJSON}
        onExportPNG={handleExportPNG}
        onExportSVG={handleExportSVG}
        onLoadPreset={handleLoadPreset}
        onClearCanvas={handleClearCanvas}
      />

      {/* Main Content Area: Canvas + Property Inspector */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Interactive Canvas Viewport */}
        <div
          ref={containerRef}
          onMouseDown={handleCanvasMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onWheel={handleWheel}
          className="flex-1 h-full relative overflow-hidden cursor-default bg-[#080C14]"
        >
          {/* Zoom & Pan Container */}
          <div
            style={{
              transform: `translate3d(${pan.x}px, ${pan.y}px, 0) scale(${zoom})`,
              transformOrigin: "0 0",
            }}
            className="absolute inset-0 w-full h-full pointer-events-none"
          >
            {/* Background SVG Grid & Vector Connection Lines */}
            <svg
              className="absolute overflow-visible pointer-events-auto"
              style={{
                width: "5000px",
                height: "5000px",
                transform: "translate(-2000px, -2000px)",
              }}
            >
              <defs>
                <style>{`
                  @keyframes flowDashAnim {
                    to {
                      stroke-dashoffset: -20;
                    }
                  }
                  .animate-flow-dash {
                    animation: flowDashAnim 0.8s linear infinite;
                  }
                `}</style>

                {/* Dot Grid Pattern */}
                <pattern
                  id="canvas-dots-grid"
                  width="24"
                  height="24"
                  patternUnits="userSpaceOnUse"
                >
                  <circle cx="2" cy="2" r="1" fill="#1E293B" />
                </pattern>

                {/* Blueprint Grid Pattern */}
                <pattern
                  id="canvas-blueprint-grid"
                  width="40"
                  height="40"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 40 0 L 0 0 0 40"
                    fill="none"
                    stroke="#111B2E"
                    strokeWidth="1"
                  />
                  <path
                    d="M 200 0 L 0 0 0 200"
                    fill="none"
                    stroke="#1D2A42"
                    strokeWidth="1.5"
                  />
                </pattern>
              </defs>

              {/* Grid Background */}
              {gridType !== "none" && (
                <rect
                  x="0"
                  y="0"
                  width="100%"
                  height="100%"
                  fill={gridType === "blueprint" ? "url(#canvas-blueprint-grid)" : "url(#canvas-dots-grid)"}
                />
              )}

              {/* Shift SVG group to match 0,0 of HTML canvas container */}
              <g transform="translate(2000, 2000)">
                {/* Render Directed Edges */}
                {edges.map((edge) => {
                  const sourceNode = nodes.find((n) => n.id === edge.sourceId);
                  const targetNode = nodes.find((n) => n.id === edge.targetId);
                  if (!sourceNode || !targetNode) return null;

                  return (
                    <ConnectionLine
                      key={edge.id}
                      edge={{
                        ...edge,
                        style: isSimulating ? edge.style : edge.style === "animated" ? "dashed" : edge.style,
                      }}
                      sourceNode={sourceNode}
                      targetNode={targetNode}
                      isSelected={selectedEdgeId === edge.id}
                      onSelect={(edgeId, e) => {
                        e.stopPropagation();
                        setSelectedEdgeId(edgeId);
                        setSelectedNodeId(null);
                      }}
                    />
                  );
                })}
              </g>
            </svg>

            {/* Render Box Nodes (Interactive HTML layer) */}
            <div className="absolute inset-0 pointer-events-auto">
              {nodes.map((node) => (
                <BoxNode
                  key={node.id}
                  node={node}
                  isSelected={selectedNodeId === node.id}
                  isConnectSource={connectSourceNodeId === node.id}
                  isConnectingMode={isConnectingMode}
                  onSelect={(id, e) => {
                    e.stopPropagation();
                    setSelectedNodeId(id);
                    setSelectedEdgeId(null);
                  }}
                  onStartDrag={handleStartNodeDrag}
                  onStartConnect={handleStartConnect}
                  onCompleteConnect={handleCompleteConnect}
                  onUpdateText={(id, title, subtitle) => {
                    setNodes((prev) =>
                      prev.map((n) => (n.id === id ? { ...n, title, subtitle } : n))
                    );
                  }}
                  onDuplicate={handleDuplicateNode}
                  onDelete={handleDeleteNode}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Right-Side Property Inspector Panel */}
        <PropertyInspector
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          graphName={graphName}
          graphDesc={graphDesc}
          nodesCount={nodes.length}
          edgesCount={edges.length}
          mulesCount={mulesCount}
          totalVolume={totalVolume}
          onUpdateGraphMeta={(name, desc) => {
            setGraphName(name);
            setGraphDesc(desc);
          }}
          onUpdateNode={(updated) => {
            setNodes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)));
          }}
          onUpdateEdge={(updated) => {
            setEdges((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));
          }}
          onDuplicateNode={handleDuplicateNode}
          onDeleteNode={handleDeleteNode}
          onDeleteEdge={handleDeleteEdge}
          onReverseEdge={handleReverseEdge}
          onAutoLayout={handleAutoLayout}
        />
      </div>
    </div>
  );
};
