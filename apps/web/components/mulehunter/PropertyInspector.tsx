"use client";

import React from "react";
import {
  MuleNode,
  MuleEdge,
  MuleNodeType,
  RiskLevel,
  BorderStyle,
  LineStyle,
  COLOR_PALETTE,
  NODE_TYPE_INFO,
} from "@/types/mulehunter";
import {
  Sliders,
  Palette,
  ShieldAlert,
  ArrowRightLeft,
  Trash2,
  Copy,
  Info,
  Layers,
  Sparkles,
  DollarSign,
  Maximize2,
  FileSpreadsheet,
} from "lucide-react";

interface PropertyInspectorProps {
  selectedNode: MuleNode | null;
  selectedEdge: MuleEdge | null;
  graphName: string;
  graphDesc: string;
  nodesCount: number;
  edgesCount: number;
  mulesCount: number;
  totalVolume: string;
  onUpdateGraphMeta: (name: string, desc: string) => void;
  onUpdateNode: (updatedNode: MuleNode) => void;
  onUpdateEdge: (updatedEdge: MuleEdge) => void;
  onDuplicateNode: (nodeId: string) => void;
  onDeleteNode: (nodeId: string) => void;
  onDeleteEdge: (edgeId: string) => void;
  onReverseEdge: (edgeId: string) => void;
  onAutoLayout: () => void;
}

export const PropertyInspector: React.FC<PropertyInspectorProps> = ({
  selectedNode,
  selectedEdge,
  graphName,
  graphDesc,
  nodesCount,
  edgesCount,
  mulesCount,
  totalVolume,
  onUpdateGraphMeta,
  onUpdateNode,
  onUpdateEdge,
  onDuplicateNode,
  onDeleteNode,
  onDeleteEdge,
  onReverseEdge,
  onAutoLayout,
}) => {
  // ================= 1. NODE INSPECTOR =================
  if (selectedNode) {
    return (
      <aside className="w-80 bg-cyber-900 border-l border-cyber-700/80 p-4 overflow-y-auto space-y-5 text-slate-200 select-none">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-cyber-700">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              Node Properties
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onDuplicateNode(selectedNode.id)}
              title="Duplicate Node (Ctrl+D)"
              className="p-1.5 text-slate-400 hover:text-white hover:bg-cyber-800 rounded transition"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onDeleteNode(selectedNode.id)}
              title="Delete Node (Del)"
              className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-950/80 rounded transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Basic Entity Info */}
        <div className="space-y-3">
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Title / Bank Name
            </label>
            <input
              type="text"
              value={selectedNode.title}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, title: e.target.value })
              }
              className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
              placeholder="e.g. HDFC Bank - Mule 1"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Subtitle / Description
            </label>
            <input
              type="text"
              value={selectedNode.subtitle}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, subtitle: e.target.value })
              }
              className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
              placeholder="e.g. High Velocity Churn Account"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">
                Account Number
              </label>
              <input
                type="text"
                value={selectedNode.accountNumber || ""}
                onChange={(e) =>
                  onUpdateNode({
                    ...selectedNode,
                    accountNumber: e.target.value,
                  })
                }
                className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2 py-1 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
                placeholder="501004..."
              />
            </div>
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">
                UPI ID / VPA
              </label>
              <input
                type="text"
                value={selectedNode.upiId || ""}
                onChange={(e) =>
                  onUpdateNode({ ...selectedNode, upiId: e.target.value })
                }
                className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2 py-1 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
                placeholder="user@okhdfc"
              />
            </div>
          </div>

          {/* Node Role & Risk Level */}
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">
                Entity Type
              </label>
              <select
                value={selectedNode.type}
                onChange={(e) => {
                  const newType = e.target.value as MuleNodeType;
                  const meta = NODE_TYPE_INFO[newType];
                  onUpdateNode({
                    ...selectedNode,
                    type: newType,
                    fillColor: meta.defaultFill,
                    strokeColor: meta.defaultStroke,
                    risk: meta.defaultRisk,
                  });
                }}
                className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="origin">Victim / Origin</option>
                <option value="mule_l1">Layer 1 Mule</option>
                <option value="mule_l2">Layer 2 Mule</option>
                <option value="mule_l3">Layer 3 Mule</option>
                <option value="destination">Destination</option>
                <option value="cashout">Cash-out ATM</option>
                <option value="crypto">Crypto On-Ramp</option>
                <option value="shell">Shell Co / POS</option>
                <option value="custom">Custom Node</option>
              </select>
            </div>

            <div>
              <label className="text-[11px] font-mono text-slate-400 block mb-1">
                Risk Classification
              </label>
              <select
                value={selectedNode.risk}
                onChange={(e) =>
                  onUpdateNode({
                    ...selectedNode,
                    risk: e.target.value as RiskLevel,
                  })
                }
                className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2 py-1 text-xs font-mono text-white focus:outline-none focus:border-cyan-500"
              >
                <option value="critical">Critical (Mule)</option>
                <option value="high">High Risk</option>
                <option value="medium">Medium</option>
                <option value="low">Low Risk</option>
                <option value="verified">Verified / Clean</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Churn Amount / Balance
            </label>
            <input
              type="text"
              value={selectedNode.amount || ""}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, amount: e.target.value })
              }
              className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-amber-300 focus:outline-none focus:border-amber-500"
              placeholder="e.g. ₹14,00,000 IN"
            />
          </div>
        </div>

        {/* Visual Styling: Fill Color */}
        <div className="space-y-2 pt-3 border-t border-cyber-800">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-mono text-slate-300 font-semibold flex items-center gap-1.5">
              <Palette className="w-3.5 h-3.5 text-cyan-400" />
              Inside Color (Fill)
            </label>
            <input
              type="color"
              value={selectedNode.fillColor}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, fillColor: e.target.value })
              }
              className="w-6 h-6 rounded cursor-pointer border border-cyber-700 bg-transparent"
              title="Custom Fill Color"
            />
          </div>
          <div className="grid grid-cols-4 gap-1.5">
            {COLOR_PALETTE.fills.map((f) => (
              <button
                key={f.name}
                type="button"
                onClick={() =>
                  onUpdateNode({ ...selectedNode, fillColor: f.value })
                }
                style={{ backgroundColor: f.value }}
                title={f.name}
                className={`h-7 rounded border transition ${
                  selectedNode.fillColor.toLowerCase() === f.value.toLowerCase()
                    ? "border-cyan-400 scale-105 shadow-md shadow-cyan-500/20"
                    : "border-cyber-700 hover:border-slate-500"
                }`}
              />
            ))}
          </div>
        </div>

        {/* Visual Styling: Outline Stroke */}
        <div className="space-y-2 pt-3 border-t border-cyber-800">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-mono text-slate-300 font-semibold flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              Outline (Border)
            </label>
            <input
              type="color"
              value={selectedNode.strokeColor}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, strokeColor: e.target.value })
              }
              className="w-6 h-6 rounded cursor-pointer border border-cyber-700 bg-transparent"
              title="Custom Stroke Color"
            />
          </div>
          <div className="grid grid-cols-4 gap-1.5">
            {COLOR_PALETTE.strokes.map((s) => (
              <button
                key={s.name}
                type="button"
                onClick={() =>
                  onUpdateNode({ ...selectedNode, strokeColor: s.value })
                }
                style={{ backgroundColor: s.value }}
                title={s.name}
                className={`h-7 rounded border transition ${
                  selectedNode.strokeColor.toLowerCase() ===
                  s.value.toLowerCase()
                    ? "border-white scale-105 shadow-md shadow-white/30"
                    : "border-cyber-700 hover:border-slate-500"
                }`}
              />
            ))}
          </div>

          {/* Stroke Width & Style */}
          <div className="grid grid-cols-2 gap-2 pt-1">
            <div>
              <span className="text-[10px] font-mono text-slate-400 block mb-1">
                Width: {selectedNode.strokeWidth}px
              </span>
              <input
                type="range"
                min={1}
                max={5}
                step={1}
                value={selectedNode.strokeWidth}
                onChange={(e) =>
                  onUpdateNode({
                    ...selectedNode,
                    strokeWidth: Number(e.target.value),
                  })
                }
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>
            <div>
              <span className="text-[10px] font-mono text-slate-400 block mb-1">
                Border Pattern
              </span>
              <div className="flex rounded border border-cyber-700 overflow-hidden text-xs">
                {(["solid", "dashed", "dotted"] as BorderStyle[]).map(
                  (style) => (
                    <button
                      key={style}
                      type="button"
                      onClick={() =>
                        onUpdateNode({ ...selectedNode, strokeStyle: style })
                      }
                      className={`flex-1 py-1 text-[10px] font-mono capitalize transition ${
                        selectedNode.strokeStyle === style
                          ? "bg-cyan-900/60 text-cyan-300 font-bold"
                          : "text-slate-400 hover:bg-cyber-800"
                      }`}
                    >
                      {style}
                    </button>
                  )
                )}
              </div>
            </div>
          </div>

          {/* Glow Effect Toggle */}
          <div className="flex items-center justify-between pt-1">
            <span className="text-[11px] font-mono text-slate-300">
              Cyber Glow Halo
            </span>
            <input
              type="checkbox"
              checked={!!selectedNode.glow}
              onChange={(e) =>
                onUpdateNode({ ...selectedNode, glow: e.target.checked })
              }
              className="accent-cyan-400 cursor-pointer w-4 h-4 rounded"
            />
          </div>
        </div>

        {/* Intelligence Notes */}
        <div className="space-y-1.5 pt-3 border-t border-cyber-800">
          <label className="text-[11px] font-mono text-slate-400 block">
            Investigation Intelligence & Evidence Notes
          </label>
          <textarea
            rows={3}
            value={selectedNode.notes || ""}
            onChange={(e) =>
              onUpdateNode({ ...selectedNode, notes: e.target.value })
            }
            className="w-full bg-cyber-950 border border-cyber-700 rounded-md p-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500 resize-none"
            placeholder="Document KYC anomalies, IP matches, RBI circular references..."
          />
        </div>
      </aside>
    );
  }

  // ================= 2. EDGE / CONNECTION INSPECTOR =================
  if (selectedEdge) {
    return (
      <aside className="w-80 bg-cyber-900 border-l border-cyber-700/80 p-4 overflow-y-auto space-y-5 text-slate-200 select-none">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-cyber-700">
          <div className="flex items-center gap-2">
            <ArrowRightLeft className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-white">
              Connection Properties
            </span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onReverseEdge(selectedEdge.id)}
              title="Reverse flow direction"
              className="p-1.5 text-slate-400 hover:text-white hover:bg-cyber-800 rounded transition"
            >
              <ArrowRightLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onDeleteEdge(selectedEdge.id)}
              title="Delete Connection"
              className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-950/80 rounded transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Label & Amount */}
        <div className="space-y-3">
          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Transaction Label / Mode
            </label>
            <input
              type="text"
              value={selectedEdge.label}
              onChange={(e) =>
                onUpdateEdge({ ...selectedEdge, label: e.target.value })
              }
              className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-indigo-500"
              placeholder="e.g. ₹5,00,000 (IMPS) or P2P Transfer"
            />
          </div>

          <div>
            <label className="text-[11px] font-mono text-slate-400 block mb-1">
              Amount (Numeric / Currency)
            </label>
            <input
              type="text"
              value={selectedEdge.amount || ""}
              onChange={(e) =>
                onUpdateEdge({ ...selectedEdge, amount: e.target.value })
              }
              className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-emerald-300 focus:outline-none focus:border-emerald-500"
              placeholder="₹5,00,000"
            />
          </div>

          {/* Color Presets */}
          <div className="space-y-2 pt-2 border-t border-cyber-800">
            <div className="flex items-center justify-between">
              <label className="text-[11px] font-mono text-slate-300 font-semibold">
                Flow Color
              </label>
              <input
                type="color"
                value={selectedEdge.color}
                onChange={(e) =>
                  onUpdateEdge({ ...selectedEdge, color: e.target.value })
                }
                className="w-6 h-6 rounded cursor-pointer border border-cyber-700 bg-transparent"
              />
            </div>
            <div className="grid grid-cols-4 gap-1.5">
              {COLOR_PALETTE.strokes.map((c) => (
                <button
                  key={c.name}
                  type="button"
                  onClick={() =>
                    onUpdateEdge({ ...selectedEdge, color: c.value })
                  }
                  style={{ backgroundColor: c.value }}
                  title={c.name}
                  className={`h-7 rounded border transition ${
                    selectedEdge.color.toLowerCase() === c.value.toLowerCase()
                      ? "border-white scale-105 shadow-md shadow-white/30"
                      : "border-cyber-700 hover:border-slate-500"
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Line Style (Solid, Dashed, Animated Flow) */}
          <div className="space-y-1.5 pt-2 border-t border-cyber-800">
            <span className="text-[11px] font-mono text-slate-300 font-semibold block">
              Flow Animation & Style
            </span>
            <div className="grid grid-cols-3 gap-1 rounded border border-cyber-700 p-1 bg-cyber-950">
              {(["solid", "dashed", "animated"] as LineStyle[]).map(
                (style) => (
                  <button
                    key={style}
                    type="button"
                    onClick={() =>
                      onUpdateEdge({ ...selectedEdge, style })
                    }
                    className={`py-1.5 text-[10px] font-mono capitalize rounded transition ${
                      selectedEdge.style === style
                        ? "bg-indigo-600 text-white font-bold shadow"
                        : "text-slate-400 hover:bg-cyber-800 hover:text-white"
                    }`}
                  >
                    {style === "animated" ? "Flowing" : style}
                  </button>
                )
              )}
            </div>
          </div>

          {/* Stroke Width */}
          <div className="space-y-1 pt-2">
            <div className="flex justify-between text-[10px] font-mono text-slate-400">
              <span>Line Thickness</span>
              <span>{selectedEdge.width}px</span>
            </div>
            <input
              type="range"
              min={1}
              max={6}
              step={1}
              value={selectedEdge.width}
              onChange={(e) =>
                onUpdateEdge({
                  ...selectedEdge,
                  width: Number(e.target.value),
                })
              }
              className="w-full accent-indigo-400 cursor-pointer"
            />
          </div>

          {/* Directed Arrowhead */}
          <div className="flex items-center justify-between pt-2">
            <span className="text-[11px] font-mono text-slate-300">
              Directed Arrowhead
            </span>
            <input
              type="checkbox"
              checked={selectedEdge.arrow}
              onChange={(e) =>
                onUpdateEdge({ ...selectedEdge, arrow: e.target.checked })
              }
              className="accent-indigo-400 cursor-pointer w-4 h-4 rounded"
            />
          </div>
        </div>
      </aside>
    );
  }

  // ================= 3. GRAPH OVERVIEW & SUMMARY (WHEN NOTHING IS SELECTED) =================
  return (
    <aside className="w-80 bg-cyber-900 border-l border-cyber-700/80 p-4 overflow-y-auto space-y-5 text-slate-200 select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-cyber-700">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-white">
            MuleHunter Intelligence
          </span>
        </div>
        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/30 text-cyan-300">
          RBIH SOC
        </span>
      </div>

      {/* Investigation Details */}
      <div className="space-y-3">
        <div>
          <label className="text-[11px] font-mono text-slate-400 block mb-1">
            Investigation Name
          </label>
          <input
            type="text"
            value={graphName}
            onChange={(e) => onUpdateGraphMeta(e.target.value, graphDesc)}
            className="w-full bg-cyber-950 border border-cyber-700 rounded-md px-2.5 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-cyan-500 font-semibold"
          />
        </div>
        <div>
          <label className="text-[11px] font-mono text-slate-400 block mb-1">
            Case Summary & Modus Operandi
          </label>
          <textarea
            rows={3}
            value={graphDesc}
            onChange={(e) => onUpdateGraphMeta(graphName, e.target.value)}
            className="w-full bg-cyber-950 border border-cyber-700 rounded-md p-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500 resize-none"
          />
        </div>
      </div>

      {/* Metrics Stats Grid */}
      <div className="space-y-2 pt-2 border-t border-cyber-800">
        <span className="text-[11px] font-mono text-slate-300 font-semibold block">
          Network Metrics
        </span>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-2.5 rounded-lg bg-cyber-950 border border-cyber-800">
            <span className="text-[10px] font-mono text-slate-400 block">
              Total Accounts
            </span>
            <span className="text-lg font-bold font-mono text-white">
              {nodesCount}
            </span>
          </div>
          <div className="p-2.5 rounded-lg bg-cyber-950 border border-cyber-800">
            <span className="text-[10px] font-mono text-slate-400 block">
              Connections
            </span>
            <span className="text-lg font-bold font-mono text-cyan-300">
              {edgesCount}
            </span>
          </div>
          <div className="p-2.5 rounded-lg bg-red-950/40 border border-red-500/30">
            <span className="text-[10px] font-mono text-red-300 block">
              Flagged Mules
            </span>
            <span className="text-lg font-bold font-mono text-red-400">
              {mulesCount}
            </span>
          </div>
          <div className="p-2.5 rounded-lg bg-amber-950/40 border border-amber-500/30">
            <span className="text-[10px] font-mono text-amber-300 block">
              Total Volume
            </span>
            <span className="text-xs font-bold font-mono text-amber-300 truncate block mt-1">
              {totalVolume}
            </span>
          </div>
        </div>
      </div>

      {/* Auto-Organize Action */}
      <div className="pt-2 border-t border-cyber-800">
        <button
          onClick={onAutoLayout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-cyber-800 hover:bg-cyber-700 border border-cyber-600 text-xs font-mono text-cyan-300 hover:text-white transition shadow"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Auto-Arrange Flow (DAG Layout)</span>
        </button>
      </div>

      {/* RBIH Information Card */}
      <div className="p-3 rounded-lg bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/30 text-xs font-mono space-y-1.5">
        <div className="flex items-center gap-1.5 text-indigo-300 font-bold">
          <Info className="w-3.5 h-3.5" />
          <span>MuleHunter.AI Intelligence</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Inspired by the Reserve Bank Innovation Hub (RBIH) MuleHunter project.
          Designed for financial intelligence units, banks, and cybersecurity
          investigators to trace multi-hop digital money laundering chains.
        </p>
      </div>

      {/* Quick Tips */}
      <div className="text-[11px] font-mono text-slate-400 space-y-1 pt-2 border-t border-cyber-800">
        <div className="font-semibold text-slate-300 mb-1">Canvas Controls:</div>
        <div>• <span className="text-cyan-400">Double click box</span> to edit text inline</div>
        <div>• <span className="text-cyan-400">Click & drag</span> to position boxes</div>
        <div>• <span className="text-cyan-400">Click ports / Connect mode</span> to draw arrows</div>
        <div>• <span className="text-cyan-400">Click arrow</span> to edit amount/style</div>
        <div>• <span className="text-cyan-400">Delete key</span> to remove selected item</div>
        <div>• <span className="text-cyan-400">Scroll wheel</span> to zoom in/out</div>
      </div>
    </aside>
  );
};
