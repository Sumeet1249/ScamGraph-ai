"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  MuleNode,
  NODE_TYPE_INFO,
  RISK_COLORS,
} from "@/types/mulehunter";
import {
  ShieldAlert,
  Landmark,
  UserCheck,
  AlertOctagon,
  CreditCard,
  Coins,
  Building,
  Box,
  Trash2,
  Copy,
  Link as LinkIcon,
  Check,
} from "lucide-react";

interface BoxNodeProps {
  node: MuleNode;
  isSelected: boolean;
  isConnectSource: boolean;
  isConnectingMode: boolean;
  onSelect: (nodeId: string, event: React.MouseEvent) => void;
  onStartDrag: (nodeId: string, event: React.MouseEvent) => void;
  onStartConnect: (nodeId: string, portPosition?: "top" | "right" | "bottom" | "left") => void;
  onCompleteConnect: (targetNodeId: string) => void;
  onUpdateText: (nodeId: string, title: string, subtitle: string) => void;
  onDuplicate: (nodeId: string) => void;
  onDelete: (nodeId: string) => void;
}

export const BoxNode: React.FC<BoxNodeProps> = ({
  node,
  isSelected,
  isConnectSource,
  isConnectingMode,
  onSelect,
  onStartDrag,
  onStartConnect,
  onCompleteConnect,
  onUpdateText,
  onDuplicate,
  onDelete,
}) => {
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingSubtitle, setIsEditingSubtitle] = useState(false);
  const [tempTitle, setTempTitle] = useState(node.title);
  const [tempSubtitle, setTempSubtitle] = useState(node.subtitle);

  const titleInputRef = useRef<HTMLInputElement>(null);
  const subtitleInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setTempTitle(node.title);
  }, [node.title]);

  useEffect(() => {
    setTempSubtitle(node.subtitle);
  }, [node.subtitle]);

  useEffect(() => {
    if (isEditingTitle) {
      titleInputRef.current?.focus();
      titleInputRef.current?.select();
    }
  }, [isEditingTitle]);

  useEffect(() => {
    if (isEditingSubtitle) {
      subtitleInputRef.current?.focus();
      subtitleInputRef.current?.select();
    }
  }, [isEditingSubtitle]);

  const handleTitleSubmit = () => {
    setIsEditingTitle(false);
    if (tempTitle.trim() && tempTitle !== node.title) {
      onUpdateText(node.id, tempTitle.trim(), node.subtitle);
    } else {
      setTempTitle(node.title);
    }
  };

  const handleSubtitleSubmit = () => {
    setIsEditingSubtitle(false);
    if (tempSubtitle !== node.subtitle) {
      onUpdateText(node.id, node.title, tempSubtitle.trim());
    } else {
      setTempSubtitle(node.subtitle);
    }
  };

  // Node type icon selector
  const getNodeIcon = () => {
    switch (node.type) {
      case "origin":
        return <UserCheck className="w-3.5 h-3.5 text-cyan-400" />;
      case "mule_l1":
        return <AlertOctagon className="w-3.5 h-3.5 text-red-400" />;
      case "mule_l2":
        return <ShieldAlert className="w-3.5 h-3.5 text-orange-400" />;
      case "mule_l3":
        return <ShieldAlert className="w-3.5 h-3.5 text-purple-400" />;
      case "cashout":
        return <CreditCard className="w-3.5 h-3.5 text-red-400" />;
      case "crypto":
        return <Coins className="w-3.5 h-3.5 text-purple-400" />;
      case "shell":
        return <Building className="w-3.5 h-3.5 text-pink-400" />;
      case "destination":
        return <Landmark className="w-3.5 h-3.5 text-indigo-400" />;
      default:
        return <Box className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  const typeMeta = NODE_TYPE_INFO[node.type] || NODE_TYPE_INFO.custom;
  const riskMeta = RISK_COLORS[node.risk] || RISK_COLORS.medium;

  // Border style class
  const borderStyleClass =
    node.strokeStyle === "dashed"
      ? "border-dashed"
      : node.strokeStyle === "dotted"
      ? "border-dotted"
      : "border-solid";

  return (
    <div
      id={`mule-node-${node.id}`}
      style={{
        transform: `translate3d(${node.x}px, ${node.y}px, 0)`,
        width: node.width || 260,
        minHeight: node.height || 140,
        backgroundColor: node.fillColor || "#0F172A",
        borderColor: node.strokeColor || "#38BDF8",
        borderWidth: `${node.strokeWidth || 2}px`,
      }}
      className={`absolute select-none rounded-xl ${borderStyleClass} transition-shadow duration-150 cursor-grab active:cursor-grabbing group ${
        isSelected
          ? "ring-2 ring-cyan-400 ring-offset-2 ring-offset-[#080C14] shadow-[0_0_24px_rgba(6,182,212,0.4)] z-20"
          : isConnectSource
          ? "ring-2 ring-emerald-400 ring-offset-2 ring-offset-[#080C14] shadow-[0_0_20px_rgba(16,185,129,0.5)] z-20"
          : node.glow
          ? `shadow-[0_0_18px_${node.strokeColor}44]`
          : "shadow-lg shadow-black/40"
      }`}
      onClick={(e) => {
        if (isConnectingMode) {
          e.stopPropagation();
          onCompleteConnect(node.id);
        } else {
          onSelect(node.id, e);
        }
      }}
      onMouseDown={(e) => {
        // Only initiate drag if not clicking an input or button
        if (
          !(e.target as HTMLElement).closest("button") &&
          !(e.target as HTMLElement).closest("input") &&
          !(e.target as HTMLElement).closest(".connection-port")
        ) {
          onStartDrag(node.id, e);
        }
      }}
    >
      {/* Selection Action Toolbar on top when selected */}
      {isSelected && (
        <div className="absolute -top-10 left-1/2 -translate-x-1/2 flex items-center gap-1 bg-cyber-900/95 border border-cyan-500/40 rounded-lg p-1 shadow-xl backdrop-blur-md z-30">
          <button
            title="Connect to another node"
            onClick={(e) => {
              e.stopPropagation();
              onStartConnect(node.id);
            }}
            className="flex items-center gap-1 px-2 py-1 text-[11px] font-mono text-cyan-300 hover:bg-cyan-950/80 rounded transition"
          >
            <LinkIcon className="w-3 h-3" />
            <span>Connect</span>
          </button>
          <div className="w-px h-4 bg-slate-700 mx-0.5" />
          <button
            title="Duplicate node"
            onClick={(e) => {
              e.stopPropagation();
              onDuplicate(node.id);
            }}
            className="p-1 text-slate-300 hover:text-white hover:bg-slate-800 rounded transition"
          >
            <Copy className="w-3 h-3" />
          </button>
          <button
            title="Delete node"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(node.id);
            }}
            className="p-1 text-red-400 hover:text-red-300 hover:bg-red-950/80 rounded transition"
          >
            <Trash2 className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* ================= CARD HEADER ================= */}
      <div className="flex items-center justify-between px-3.5 py-2.5 border-b border-white/10 bg-black/25 rounded-t-[10px]">
        {/* Type Badge & Icon */}
        <div className="flex items-center gap-1.5 min-w-0">
          <div className="p-1 rounded bg-white/10 flex-shrink-0">
            {getNodeIcon()}
          </div>
          <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-slate-300 truncate">
            {typeMeta.badge}
          </span>
        </div>

        {/* Risk Badge */}
        <div
          className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono font-semibold border ${riskMeta.bg} ${riskMeta.text} ${riskMeta.border}`}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
          <span className="uppercase">{node.risk}</span>
        </div>
      </div>

      {/* ================= CARD BODY ================= */}
      <div className="p-3.5 space-y-2">
        {/* Title / Bank Name (Editable) */}
        <div>
          {isEditingTitle ? (
            <div className="flex items-center gap-1">
              <input
                ref={titleInputRef}
                type="text"
                value={tempTitle}
                onChange={(e) => setTempTitle(e.target.value)}
                onBlur={handleTitleSubmit}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleTitleSubmit();
                  if (e.key === "Escape") {
                    setTempTitle(node.title);
                    setIsEditingTitle(false);
                  }
                }}
                className="w-full text-xs font-semibold text-white bg-black/60 border border-cyan-500 rounded px-1.5 py-0.5 outline-none font-mono"
              />
              <button
                onClick={handleTitleSubmit}
                className="p-1 bg-cyan-600 text-white rounded hover:bg-cyan-500"
              >
                <Check className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <div
              onDoubleClick={(e) => {
                e.stopPropagation();
                setIsEditingTitle(true);
              }}
              title="Double-click to edit title"
              className="text-xs font-bold text-slate-100 hover:text-cyan-300 font-mono tracking-tight leading-snug cursor-text truncate transition"
            >
              {node.title || "Untitled Box"}
            </div>
          )}
        </div>

        {/* Subtitle / Account details (Editable) */}
        <div>
          {isEditingSubtitle ? (
            <div className="flex items-center gap-1">
              <input
                ref={subtitleInputRef}
                type="text"
                value={tempSubtitle}
                onChange={(e) => setTempSubtitle(e.target.value)}
                onBlur={handleSubtitleSubmit}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSubtitleSubmit();
                  if (e.key === "Escape") {
                    setTempSubtitle(node.subtitle);
                    setIsEditingSubtitle(false);
                  }
                }}
                className="w-full text-[11px] text-slate-200 bg-black/60 border border-cyan-500 rounded px-1.5 py-0.5 outline-none font-mono"
              />
              <button
                onClick={handleSubtitleSubmit}
                className="p-1 bg-cyan-600 text-white rounded hover:bg-cyan-500"
              >
                <Check className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <div
              onDoubleClick={(e) => {
                e.stopPropagation();
                setIsEditingSubtitle(true);
              }}
              title="Double-click to edit subtitle / account"
              className="text-[11px] text-slate-400 hover:text-slate-200 font-mono leading-tight cursor-text line-clamp-2 transition"
            >
              {node.subtitle || "Double-click to add details..."}
            </div>
          )}
        </div>

        {/* Account Number & IFSC / UPI Pill if present */}
        {(node.accountNumber || node.upiId) && (
          <div className="pt-1 flex flex-wrap gap-1">
            {node.accountNumber && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-slate-300 border border-white/5">
                A/C: {node.accountNumber}
              </span>
            )}
            {node.upiId && (
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/40 text-cyan-300 border border-cyan-500/20">
                UPI: {node.upiId}
              </span>
            )}
          </div>
        )}

        {/* Flow Volume / Balance Tag */}
        {node.amount && (
          <div className="pt-1 flex items-center justify-between text-[11px] font-mono border-t border-white/10">
            <span className="text-slate-400 text-[10px]">Churn Volume:</span>
            <span className="font-bold text-amber-300 bg-amber-950/40 px-1.5 py-0.2 rounded border border-amber-500/30">
              {node.amount}
            </span>
          </div>
        )}
      </div>

      {/* ================= 4 CONNECTION PORTS (NORTH, SOUTH, EAST, WEST) ================= */}
      {/* Top Port */}
      <div
        className="connection-port absolute -top-2 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-400 hover:scale-125 hover:bg-cyan-400 cursor-crosshair transition shadow-md z-30"
        title="Connect from Top"
        onClick={(e) => {
          e.stopPropagation();
          if (isConnectingMode) {
            onCompleteConnect(node.id);
          } else {
            onStartConnect(node.id, "top");
          }
        }}
      />
      {/* Right Port */}
      <div
        className="connection-port absolute top-1/2 -right-2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-400 hover:scale-125 hover:bg-cyan-400 cursor-crosshair transition shadow-md z-30"
        title="Connect from Right"
        onClick={(e) => {
          e.stopPropagation();
          if (isConnectingMode) {
            onCompleteConnect(node.id);
          } else {
            onStartConnect(node.id, "right");
          }
        }}
      />
      {/* Bottom Port */}
      <div
        className="connection-port absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-400 hover:scale-125 hover:bg-cyan-400 cursor-crosshair transition shadow-md z-30"
        title="Connect from Bottom"
        onClick={(e) => {
          e.stopPropagation();
          if (isConnectingMode) {
            onCompleteConnect(node.id);
          } else {
            onStartConnect(node.id, "bottom");
          }
        }}
      />
      {/* Left Port */}
      <div
        className="connection-port absolute top-1/2 -left-2 -translate-y-1/2 w-4 h-4 rounded-full bg-slate-900 border-2 border-cyan-400 hover:scale-125 hover:bg-cyan-400 cursor-crosshair transition shadow-md z-30"
        title="Connect from Left"
        onClick={(e) => {
          e.stopPropagation();
          if (isConnectingMode) {
            onCompleteConnect(node.id);
          } else {
            onStartConnect(node.id, "left");
          }
        }}
      />
    </div>
  );
};
