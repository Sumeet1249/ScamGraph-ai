"use client";

import React, { useMemo } from "react";
import { MuleEdge, MuleNode } from "@/types/mulehunter";

interface ConnectionLineProps {
  edge: MuleEdge;
  sourceNode: MuleNode;
  targetNode: MuleNode;
  isSelected: boolean;
  onSelect: (edgeId: string, event: React.MouseEvent) => void;
  onDelete?: (edgeId: string) => void;
}

export const ConnectionLine: React.FC<ConnectionLineProps> = ({
  edge,
  sourceNode,
  targetNode,
  isSelected,
  onSelect,
}) => {
  // Compute anchor points on box boundaries
  const { pathData, midPoint, arrowAngle, p2 } = useMemo(() => {
    const sCenter = {
      x: sourceNode.x + sourceNode.width / 2,
      y: sourceNode.y + sourceNode.height / 2,
    };
    const tCenter = {
      x: targetNode.x + targetNode.width / 2,
      y: targetNode.y + targetNode.height / 2,
    };

    const dx = tCenter.x - sCenter.x;
    const dy = tCenter.y - sCenter.y;

    let p1 = { x: sCenter.x, y: sCenter.y };
    let p2 = { x: tCenter.x, y: tCenter.y };

    // Choose exit side of source node and entry side of target node
    if (Math.abs(dx) >= Math.abs(dy)) {
      if (dx > 0) {
        // Target is to the right
        p1 = { x: sourceNode.x + sourceNode.width, y: sCenter.y };
        p2 = { x: targetNode.x, y: tCenter.y };
      } else {
        // Target is to the left
        p1 = { x: sourceNode.x, y: sCenter.y };
        p2 = { x: targetNode.x + targetNode.width, y: tCenter.y };
      }
    } else {
      if (dy > 0) {
        // Target is below
        p1 = { x: sCenter.x, y: sourceNode.y + sourceNode.height };
        p2 = { x: tCenter.x, y: targetNode.y };
      } else {
        // Target is above
        p1 = { x: sCenter.x, y: sourceNode.y };
        p2 = { x: tCenter.x, y: targetNode.y + targetNode.height };
      }
    }

    // Bezier control points
    const curvature = 0.45;
    let cp1x = p1.x;
    let cp1y = p1.y;
    let cp2x = p2.x;
    let cp2y = p2.y;

    if (Math.abs(dx) >= Math.abs(dy)) {
      const offsetX = Math.abs(p2.x - p1.x) * curvature;
      cp1x = dx > 0 ? p1.x + offsetX : p1.x - offsetX;
      cp2x = dx > 0 ? p2.x - offsetX : p2.x + offsetX;
    } else {
      const offsetY = Math.abs(p2.y - p1.y) * curvature;
      cp1y = dy > 0 ? p1.y + offsetY : p1.y - offsetY;
      cp2y = dy > 0 ? p2.y - offsetY : p2.y + offsetY;
    }

    const pathData = `M ${p1.x} ${p1.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;

    // Approximate mid point on cubic bezier for label placement
    const t = 0.5;
    const midX =
      Math.pow(1 - t, 3) * p1.x +
      3 * Math.pow(1 - t, 2) * t * cp1x +
      3 * (1 - t) * Math.pow(t, 2) * cp2x +
      Math.pow(t, 3) * p2.x;
    const midY =
      Math.pow(1 - t, 3) * p1.y +
      3 * Math.pow(1 - t, 2) * t * cp1y +
      3 * (1 - t) * Math.pow(t, 2) * cp2y +
      Math.pow(t, 3) * p2.y;

    // Angle at end point for arrowhead
    const arrowAngle = Math.atan2(p2.y - cp2y, p2.x - cp2x) * (180 / Math.PI);

    return {
      pathData,
      midPoint: { x: midX, y: midY },
      arrowAngle,
      p2,
    };
  }, [sourceNode, targetNode]);

  const strokeColor = edge.color || "#6366F1";
  const strokeWidth = edge.width || 2;
  const isAnimated = edge.style === "animated";
  const isDashed = edge.style === "dashed";

  return (
    <g
      className={`group transition-opacity ${
        isSelected ? "opacity-100" : "opacity-90 hover:opacity-100"
      }`}
    >
      {/* Invisible wider hit-testing path for easy clicking */}
      <path
        d={pathData}
        fill="none"
        stroke="transparent"
        strokeWidth={Math.max(strokeWidth + 16, 24)}
        className="cursor-pointer"
        onClick={(e) => onSelect(edge.id, e)}
      />

      {/* Selected glow halo */}
      {isSelected && (
        <path
          d={pathData}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth + 6}
          strokeOpacity={0.4}
          strokeLinecap="round"
          filter="blur(3px)"
        />
      )}

      {/* Base line */}
      <path
        d={pathData}
        fill="none"
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeOpacity={isAnimated ? 0.6 : 0.9}
        strokeDasharray={isDashed ? "6 6" : undefined}
        strokeLinecap="round"
        className="transition-all"
        onClick={(e) => onSelect(edge.id, e)}
      />

      {/* Animated flow dashes when animated */}
      {isAnimated && (
        <path
          d={pathData}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth + 1}
          strokeDasharray="8 12"
          strokeLinecap="round"
          className="pointer-events-none animate-flow-dash"
          style={{
            filter: `drop-shadow(0 0 4px ${strokeColor})`,
          }}
        />
      )}

      {/* Directed Arrowhead */}
      {edge.arrow && (
        <g
          transform={`translate(${p2.x}, ${p2.y}) rotate(${arrowAngle})`}
          className="pointer-events-none"
        >
          <polygon
            points="-12,-5 0,0 -12,5 -8,0"
            fill={strokeColor}
            stroke={strokeColor}
            strokeWidth={1}
            style={{
              filter: `drop-shadow(0 0 3px ${strokeColor})`,
            }}
          />
        </g>
      )}

      {/* Label Badge at midpoint */}
      {edge.label && (
        <g
          transform={`translate(${midPoint.x}, ${midPoint.y})`}
          className="cursor-pointer select-none"
          onClick={(e) => onSelect(edge.id, e)}
        >
          {/* Badge Background */}
          <rect
            x={-Math.max(edge.label.length * 4.2 + 14, 36)}
            y={-12}
            width={Math.max(edge.label.length * 8.4 + 28, 72)}
            height={24}
            rx={12}
            fill="#090E17"
            stroke={isSelected ? strokeColor : `${strokeColor}88`}
            strokeWidth={isSelected ? 1.5 : 1}
            className="transition-all"
            style={{
              filter: isSelected
                ? `drop-shadow(0 0 8px ${strokeColor}99)`
                : "drop-shadow(0 2px 4px rgba(0,0,0,0.7))",
            }}
          />

          {/* Small dot indicator */}
          <circle
            cx={-Math.max(edge.label.length * 4.2 + 14, 36) + 10}
            cy={0}
            r={3}
            fill={strokeColor}
          />

          {/* Label Text */}
          <text
            x={6}
            y={4}
            textAnchor="middle"
            fill={isSelected ? "#FFFFFF" : "#E2E8F0"}
            fontSize={11}
            fontWeight={600}
            fontFamily="ui-monospace, monospace"
            className="pointer-events-none tracking-tight"
          >
            {edge.label}
          </text>
        </g>
      )}
    </g>
  );
};
