"use client";

import React, { useState, useRef } from "react";
import { MuleNodeType } from "@/types/mulehunter";
import {
  Plus,
  Link as LinkIcon,
  Trash2,
  Copy,
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Save,
  Download,
  Upload,
  Play,
  Pause,
  Grid,
  FileCode,
  Image as ImageIcon,
  Sparkles,
  Layers,
  ChevronDown,
  Building,
  AlertOctagon,
  CreditCard,
  UserCheck,
  FileText,
  RefreshCw,
  FolderOpen,
} from "lucide-react";

interface ToolbarProps {
  isConnectingMode: boolean;
  onToggleConnectMode: () => void;
  onAddNode: (type: MuleNodeType) => void;
  hasSelection: boolean;
  onDeleteSelected: () => void;
  onDuplicateSelected: () => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
  onFitView: () => void;
  isSimulating: boolean;
  onToggleSimulation: () => void;
  gridType: "dots" | "blueprint" | "none";
  onCycleGrid: () => void;
  onSaveLocalStorage: () => void;
  onLoadLocalStorage: () => void;
  onExportJSON: () => void;
  onImportJSON: (file: File) => void;
  onExportPNG: () => void;
  onExportSVG: () => void;
  onLoadPreset: (presetKey: "default" | "upi" | "blank") => void;
  onClearCanvas: () => void;
}

export const Toolbar: React.FC<ToolbarProps> = ({
  isConnectingMode,
  onToggleConnectMode,
  onAddNode,
  hasSelection,
  onDeleteSelected,
  onDuplicateSelected,
  zoom,
  onZoomIn,
  onZoomOut,
  onResetZoom,
  onFitView,
  isSimulating,
  onToggleSimulation,
  gridType,
  onCycleGrid,
  onSaveLocalStorage,
  onLoadLocalStorage,
  onExportJSON,
  onImportJSON,
  onExportPNG,
  onExportSVG,
  onLoadPreset,
  onClearCanvas,
}) => {
  const [addMenuOpen, setAddMenuOpen] = useState(false);
  const [exportMenuOpen, setExportMenuOpen] = useState(false);
  const [presetMenuOpen, setPresetMenuOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImportJSON(file);
      e.target.value = "";
    }
  };

  return (
    <header className="h-14 bg-cyber-950/95 border-b border-cyber-700/80 px-4 flex items-center justify-between backdrop-blur-md z-40 select-none">
      {/* Hidden File Input for JSON Import */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* ================= LEFT CONTROLS: ADD NODES & MODES ================= */}
      <div className="flex items-center gap-2">
        {/* Add Node Dropdown / Quick Button */}
        <div className="relative">
          <div className="flex rounded-lg overflow-hidden border border-cyan-500/40 bg-cyan-950/40 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.15)]">
            <button
              onClick={() => onAddNode("mule_l1")}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono font-bold hover:bg-cyan-900/60 hover:text-white transition"
              title="Add a Layer-1 Mule Account"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>+ Add Mule</span>
            </button>
            <button
              onClick={() => setAddMenuOpen(!addMenuOpen)}
              className="px-2 border-l border-cyan-500/30 hover:bg-cyan-900/60 transition"
              title="More Box Types"
            >
              <ChevronDown className="w-3 h-3" />
            </button>
          </div>

          {/* Add Menu Dropdown */}
          {addMenuOpen && (
            <div
              className="absolute left-0 mt-2 w-56 rounded-lg bg-cyber-900 border border-cyber-700 shadow-2xl p-1.5 space-y-1 z-50 animate-in fade-in zoom-in-95 duration-100"
              onMouseLeave={() => setAddMenuOpen(false)}
            >
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-slate-400 font-bold tracking-wider">
                Create Canvas Box
              </div>
              <button
                onClick={() => {
                  onAddNode("mule_l1");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-red-300 hover:bg-red-950/60 hover:text-white transition"
              >
                <AlertOctagon className="w-4 h-4 text-red-400" />
                <span>+ Layer 1 Mule (Hub)</span>
              </button>
              <button
                onClick={() => {
                  onAddNode("mule_l2");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-orange-300 hover:bg-orange-950/60 hover:text-white transition"
              >
                <AlertOctagon className="w-4 h-4 text-orange-400" />
                <span>+ Layer 2 Mule (Splitter)</span>
              </button>
              <button
                onClick={() => {
                  onAddNode("origin");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-cyan-300 hover:bg-cyan-950/60 hover:text-white transition"
              >
                <UserCheck className="w-4 h-4 text-cyan-400" />
                <span>+ Victim / Originator</span>
              </button>
              <button
                onClick={() => {
                  onAddNode("cashout");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-red-300 hover:bg-red-950/60 hover:text-white transition"
              >
                <CreditCard className="w-4 h-4 text-red-400" />
                <span>+ ATM / Cash Withdrawal</span>
              </button>
              <button
                onClick={() => {
                  onAddNode("destination");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-indigo-300 hover:bg-indigo-950/60 hover:text-white transition"
              >
                <Building className="w-4 h-4 text-indigo-400" />
                <span>+ Bank / Destination Box</span>
              </button>
              <button
                onClick={() => {
                  onAddNode("custom");
                  setAddMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-white transition"
              >
                <FileText className="w-4 h-4 text-slate-400" />
                <span>+ Custom Blank Box</span>
              </button>
            </div>
          )}
        </div>

        {/* Connect Mode Toggle */}
        <button
          onClick={onToggleConnectMode}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono font-bold border transition ${
            isConnectingMode
              ? "bg-emerald-950/80 border-emerald-500 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.3)] animate-pulse"
              : "bg-cyber-900 border-cyber-700 text-slate-300 hover:border-slate-500 hover:text-white"
          }`}
          title="Click to toggle link/connection mode (or click port handles on boxes)"
        >
          <LinkIcon className="w-3.5 h-3.5" />
          <span>{isConnectingMode ? "Connecting Mode (ON)" : "Connect"}</span>
        </button>

        {/* Selection Actions */}
        {hasSelection && (
          <div className="flex items-center gap-1 pl-2 border-l border-cyber-700">
            <button
              onClick={onDuplicateSelected}
              className="p-1.5 text-xs font-mono text-slate-300 hover:text-white bg-cyber-900 hover:bg-cyber-800 border border-cyber-700 rounded-md transition"
              title="Duplicate (Ctrl+D)"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={onDeleteSelected}
              className="p-1.5 text-xs font-mono text-red-400 hover:text-red-300 bg-red-950/40 hover:bg-red-950/80 border border-red-500/30 rounded-md transition"
              title="Delete Selected (Del)"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* ================= CENTER CONTROLS: SIMULATION & VIEW ================= */}
      <div className="flex items-center gap-2">
        {/* Flow Simulation Toggle */}
        <button
          onClick={onToggleSimulation}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-mono border transition ${
            isSimulating
              ? "bg-indigo-950/60 border-indigo-500/60 text-indigo-300 shadow-[0_0_10px_rgba(99,102,241,0.2)]"
              : "bg-cyber-900 border-cyber-700 text-slate-400 hover:text-slate-200"
          }`}
          title="Toggle animated fund flow along connection lines"
        >
          {isSimulating ? (
            <Pause className="w-3 h-3 text-indigo-400" />
          ) : (
            <Play className="w-3 h-3 text-slate-400" />
          )}
          <span>Flow Sim</span>
        </button>

        {/* Grid Style Toggle */}
        <button
          onClick={onCycleGrid}
          className="p-1.5 text-slate-400 hover:text-cyan-300 bg-cyber-900 hover:bg-cyber-800 border border-cyber-700 rounded-md transition"
          title={`Canvas Grid: ${gridType.toUpperCase()}`}
        >
          <Grid className="w-3.5 h-3.5" />
        </button>

        {/* Zoom Controls */}
        <div className="flex items-center rounded-lg border border-cyber-700 bg-cyber-900 overflow-hidden text-xs font-mono text-slate-300">
          <button
            onClick={onZoomOut}
            className="p-1.5 hover:bg-cyber-800 hover:text-white transition"
            title="Zoom Out (-)"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onResetZoom}
            className="px-2 py-1 hover:bg-cyber-800 hover:text-cyan-300 transition text-[11px]"
            title="Reset Zoom to 100%"
          >
            {Math.round(zoom * 100)}%
          </button>
          <button
            onClick={onZoomIn}
            className="p-1.5 hover:bg-cyber-800 hover:text-white transition"
            title="Zoom In (+)"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onFitView}
            className="p-1.5 hover:bg-cyber-800 hover:text-cyan-300 border-l border-cyber-700 transition"
            title="Fit to Canvas"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* ================= RIGHT CONTROLS: PRESETS, SAVE & EXPORT ================= */}
      <div className="flex items-center gap-2">
        {/* Scenarios Preset Dropdown */}
        <div className="relative">
          <button
            onClick={() => setPresetMenuOpen(!presetMenuOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-cyber-900 border border-cyber-700 text-slate-300 hover:border-slate-500 hover:text-white transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Templates</span>
            <ChevronDown className="w-3 h-3" />
          </button>

          {presetMenuOpen && (
            <div
              className="absolute right-0 mt-2 w-64 rounded-lg bg-cyber-900 border border-cyber-700 shadow-2xl p-1.5 space-y-1 z-50 animate-in fade-in zoom-in-95 duration-100"
              onMouseLeave={() => setPresetMenuOpen(false)}
            >
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-slate-400 font-bold tracking-wider">
                MuleHunter Scenarios
              </div>
              <button
                onClick={() => {
                  onLoadPreset("default");
                  setPresetMenuOpen(false);
                }}
                className="w-full px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-cyan-300 hover:bg-cyan-950/60 hover:text-white transition"
              >
                <div className="font-bold">RBIH Flagship 3-Hop Ring</div>
                <div className="text-[10px] text-slate-400 truncate">
                  Victim → L1 Axis/Kotak → 4 L2 Mules → ATM/Crypto
                </div>
              </button>
              <button
                onClick={() => {
                  onLoadPreset("upi");
                  setPresetMenuOpen(false);
                }}
                className="w-full px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-amber-300 hover:bg-amber-950/60 hover:text-white transition"
              >
                <div className="font-bold">Fast UPI Churn Syndicate</div>
                <div className="text-[10px] text-slate-400 truncate">
                  3 Victims → 1 Collector VPA → QR Cashout
                </div>
              </button>
              <div className="w-full h-px bg-cyber-800 my-1" />
              <button
                onClick={() => {
                  onLoadPreset("blank");
                  setPresetMenuOpen(false);
                }}
                className="w-full px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-white transition"
              >
                <div className="font-bold">Blank Canvas</div>
                <div className="text-[10px] text-slate-400">
                  Start fresh investigation
                </div>
              </button>
            </div>
          )}
        </div>

        {/* Local Storage Save / Load */}
        <div className="flex items-center rounded-lg border border-cyber-700 bg-cyber-900 overflow-hidden text-xs font-mono">
          <button
            onClick={onSaveLocalStorage}
            className="flex items-center gap-1 px-2.5 py-1.5 text-slate-300 hover:text-white hover:bg-cyber-800 transition"
            title="Save Investigation to Browser"
          >
            <Save className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Save</span>
          </button>
          <button
            onClick={onLoadLocalStorage}
            className="flex items-center gap-1 px-2.5 py-1.5 border-l border-cyber-700 text-slate-300 hover:text-white hover:bg-cyber-800 transition"
            title="Load last saved state"
          >
            <FolderOpen className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">Load</span>
          </button>
        </div>

        {/* Export / Download Menu */}
        <div className="relative">
          <button
            onClick={() => setExportMenuOpen(!exportMenuOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono bg-gradient-to-r from-cyan-950 to-blue-950 border border-cyan-500/40 text-cyan-300 hover:text-white hover:border-cyan-400 transition shadow-[0_0_12px_rgba(6,182,212,0.15)]"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export</span>
            <ChevronDown className="w-3 h-3" />
          </button>

          {exportMenuOpen && (
            <div
              className="absolute right-0 mt-2 w-52 rounded-lg bg-cyber-900 border border-cyber-700 shadow-2xl p-1.5 space-y-1 z-50 animate-in fade-in zoom-in-95 duration-100"
              onMouseLeave={() => setExportMenuOpen(false)}
            >
              <div className="px-2 py-1 text-[10px] font-mono uppercase text-slate-400 font-bold tracking-wider">
                Export Options
              </div>
              <button
                onClick={() => {
                  onExportJSON();
                  setExportMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-cyan-300 transition"
              >
                <FileCode className="w-4 h-4 text-cyan-400" />
                <span>Download JSON</span>
              </button>
              <button
                onClick={() => {
                  fileInputRef.current?.click();
                  setExportMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-cyan-300 transition"
              >
                <Upload className="w-4 h-4 text-emerald-400" />
                <span>Import JSON</span>
              </button>
              <div className="w-full h-px bg-cyber-800 my-1" />
              <button
                onClick={() => {
                  onExportPNG();
                  setExportMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-indigo-300 transition"
              >
                <ImageIcon className="w-4 h-4 text-indigo-400" />
                <span>Export as PNG</span>
              </button>
              <button
                onClick={() => {
                  onExportSVG();
                  setExportMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-slate-300 hover:bg-cyber-800 hover:text-indigo-300 transition"
              >
                <FileCode className="w-4 h-4 text-indigo-400" />
                <span>Export as SVG</span>
              </button>
              <div className="w-full h-px bg-cyber-800 my-1" />
              <button
                onClick={() => {
                  onClearCanvas();
                  setExportMenuOpen(false);
                }}
                className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-mono text-left text-red-400 hover:bg-red-950/80 transition"
              >
                <Trash2 className="w-4 h-4 text-red-400" />
                <span>Clear Canvas</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
