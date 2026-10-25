"use client";

import React, { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, QuadraticBezierLine, Html, Float } from "@react-three/drei";
import * as THREE from "three";
import { VisualNode, VisualEdge } from "./InteractiveCorrelationGraph";

interface ThreeCorrelationGraphProps {
  nodes: VisualNode[];
  edges: VisualEdge[];
  highlightedPath?: string[];
  isCircularDetected?: boolean;
  selectedNodeId: string | null;
  onSelectNode?: (node: VisualNode | null) => void;
}

interface Node3DWithPos extends VisualNode {
  position: [number, number, number];
  color: string;
  glowColor: string;
}

interface Edge3DWithCurves {
  id: string;
  source: string;
  target: string;
  start: [number, number, number];
  end: [number, number, number];
  mid: [number, number, number];
  amount?: number;
  dwellTime?: number | null;
  isCircular?: boolean;
  isHighlighted?: boolean;
}

// 1. Cybernetic Floor Grid with Radial Concentric Rings
function CyberFloor() {
  return (
    <group position={[0, -2.5, 0]}>
      {/* Ground Grid */}
      <gridHelper args={[36, 36, "#1e293b", "#0f172a"]} position={[0, 0, 0]} />

      {/* Target Concentric Radar Rings */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[4.8, 5.0, 64]} />
        <meshBasicMaterial color="#06b6d4" transparent opacity={0.25} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[9.8, 10.0, 64]} />
        <meshBasicMaterial color="#3b82f6" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

// 2. Circular Loop Indicator Torus (renders when circular flow detected)
function CircularWashLoopField({ radius = 7 }: { radius?: number }) {
  const torusRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (torusRef.current) {
      torusRef.current.rotation.z += delta * 0.4;
      torusRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <group position={[0, 0, 0]}>
      {/* Rotating Cyber Torus Ring */}
      <mesh ref={torusRef} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[radius, 0.08, 16, 64]} />
        <meshStandardMaterial
          color="#ef4444"
          emissive="#b91c1c"
          emissiveIntensity={1.5}
          wireframe
        />
      </mesh>
    </group>
  );
}

// 3. 3D Spatial Entity Node
function EntityNode3D({
  node,
  isSelected,
  isHighlighted,
  onHover,
  onClick,
}: {
  node: Node3DWithPos;
  isSelected: boolean;
  isHighlighted: boolean;
  onHover: (node: Node3DWithPos | null) => void;
  onClick: () => void;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * (isSelected ? 1.8 : 0.6);
      meshRef.current.rotation.x += delta * 0.3;
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 1.2;
    }
  });

  const nodeRadius = isSelected ? 0.65 : isHighlighted ? 0.55 : 0.42;

  return (
    <group position={node.position}>
      {/* Vertical Foundation Riser Light to Floor */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={2}
            array={new Float32Array([0, 0, 0, 0, -2.5 - node.position[1], 0])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial
          color={node.color}
          transparent
          opacity={isSelected || hovered ? 0.7 : 0.22}
          linewidth={1}
        />
      </line>

      {/* Orbiting Orbital Ring for Seed or Selected Nodes */}
      {(isSelected || node.isSeed) && (
        <mesh ref={ringRef} rotation={[Math.PI / 3, 0, 0]}>
          <ringGeometry args={[nodeRadius * 1.5, nodeRadius * 1.65, 32]} />
          <meshBasicMaterial
            color={node.color}
            side={THREE.DoubleSide}
            transparent
            opacity={0.8}
          />
        </mesh>
      )}

      {/* Core Node Polyhedron */}
      <Float speed={1.5} rotationIntensity={0.2} floatIntensity={0.2}>
        <mesh
          ref={meshRef}
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHovered(true);
            onHover(node);
          }}
          onPointerOut={() => {
            setHovered(false);
            onHover(null);
          }}
          cursor="pointer"
        >
          {node.node_type === "ACCOUNT" ? (
            <dodecahedronGeometry args={[nodeRadius, 0]} />
          ) : node.node_type === "UPI_VPA" ? (
            <octahedronGeometry args={[nodeRadius, 0]} />
          ) : (
            <sphereGeometry args={[nodeRadius, 24, 24]} />
          )}
          <meshStandardMaterial
            color={node.color}
            emissive={node.glowColor}
            emissiveIntensity={isSelected ? 1.6 : hovered ? 1.2 : 0.5}
            roughness={0.25}
            metalness={0.8}
            wireframe={node.isSeed}
          />
        </mesh>
      </Float>

      {/* Floating 3D Billboard Label on Hover / Selected */}
      {(hovered || isSelected) && (
        <Html position={[0, nodeRadius + 0.5, 0]} center distanceFactor={14}>
          <div className="bg-slate-950/90 backdrop-blur-md border border-cyan-500/40 rounded-lg p-2.5 shadow-2xl text-white pointer-events-none whitespace-nowrap min-w-[160px] text-xs">
            <div className="flex items-center gap-1.5 font-bold font-mono">
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: node.color }}
              />
              <span className="text-white text-[12px]">{node.label}</span>
            </div>
            <div className="flex items-center justify-between text-[10px] text-slate-300 font-mono mt-1 border-t border-white/10 pt-1">
              <span>TYPE: {node.node_type}</span>
              <span className="text-amber-400 font-bold">
                RISK: {((node.propagatedRisk ?? node.risk_score ?? 0) * 100).toFixed(0)}%
              </span>
            </div>
            {node.bank && (
              <div className="text-[10px] text-slate-400 mt-0.5 font-mono">
                BANK: {node.bank}
              </div>
            )}
          </div>
        </Html>
      )}
    </group>
  );
}

// 4. Parabolic 3D Bezier Edge Arcs with Flow Pulses
function FlowEdgeArc3D({
  edge,
  isHighlighted,
}: {
  edge: Edge3DWithCurves;
  isHighlighted: boolean;
}) {
  const arcColor = edge.isCircular
    ? "#ef4444"
    : isHighlighted
    ? "#06b6d4"
    : "#475569";

  return (
    <group>
      <QuadraticBezierLine
        start={edge.start}
        end={edge.end}
        mid={edge.mid}
        color={arcColor}
        lineWidth={isHighlighted || edge.isCircular ? 2.5 : 1.2}
        transparent
        opacity={isHighlighted || edge.isCircular ? 0.9 : 0.4}
      />

      {/* Edge Midpoint Holographic Amount Tag */}
      {edge.amount && (isHighlighted || edge.isCircular) && (
        <Html position={edge.mid} center distanceFactor={16}>
          <div className="bg-slate-950/85 backdrop-blur-sm border border-cyan-500/30 rounded px-1.5 py-0.5 text-[9px] font-mono text-cyan-300 shadow pointer-events-none">
            ₹{(edge.amount / 1000).toFixed(0)}k
            {edge.dwellTime ? ` (${edge.dwellTime}s)` : ""}
          </div>
        </Html>
      )}
    </group>
  );
}

export function ThreeCorrelationGraph({
  nodes,
  edges,
  highlightedPath = [],
  isCircularDetected = false,
  selectedNodeId,
  onSelectNode,
}: ThreeCorrelationGraphProps) {
  const [mounted, setMounted] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<Node3DWithPos | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Compute 3D Spatial coordinates
  const { nodes3D, edges3D } = useMemo(() => {
    if (!nodes || nodes.length === 0) {
      return { nodes3D: [], edges3D: [] };
    }

    // Build levels / tiers for multi-hop depth
    const levels: Record<string, number> = {};
    const adj: Record<string, string[]> = {};
    const inDegree: Record<string, number> = {};

    nodes.forEach((n) => {
      adj[n.id] = [];
      inDegree[n.id] = 0;
    });

    edges.forEach((e) => {
      if (adj[e.source]) adj[e.source].push(e.target);
      if (inDegree[e.target] !== undefined) inDegree[e.target]++;
    });

    // Seeds or in-degree 0 at level 0
    nodes.forEach((n) => {
      if (n.isSeed || inDegree[n.id] === 0) {
        levels[n.id] = 0;
      }
    });

    // BFS forward
    const queue = Object.keys(levels);
    const visited = new Set(queue);

    while (queue.length > 0) {
      const curr = queue.shift()!;
      const currLevel = levels[curr] || 0;
      (adj[curr] || []).forEach((nxt) => {
        if (!visited.has(nxt)) {
          visited.add(nxt);
          levels[nxt] = currLevel + 1;
          queue.push(nxt);
        }
      });
    }

    nodes.forEach((n) => {
      if (levels[n.id] === undefined) {
        levels[n.id] = 1;
      }
    });

    // Arrange nodes in 3D space
    const nodesByLevel: Record<number, VisualNode[]> = {};
    nodes.forEach((n) => {
      const lvl = levels[n.id] || 0;
      if (!nodesByLevel[lvl]) nodesByLevel[lvl] = [];
      nodesByLevel[lvl].push(n);
    });

    const maxLevel = Math.max(...Object.keys(nodesByLevel).map(Number), 0);
    const posMap: Record<string, [number, number, number]> = {};

    const computedNodes3D: Node3DWithPos[] = nodes.map((node, idx) => {
      let x = 0;
      let y = 0;
      let z = 0;

      if (isCircularDetected) {
        // Arrange in 3D circle
        const angle = (idx / nodes.length) * Math.PI * 2;
        const radius = 6.2;
        x = Math.cos(angle) * radius;
        z = Math.sin(angle) * radius;
        y = Math.sin(angle * 2) * 0.8;
      } else {
        // Multi-tier Flow Layout along X (left to right) and Y (stratum elevation)
        const lvl = levels[node.id] || 0;
        const group = nodesByLevel[lvl] || [node];
        const indexInGroup = group.findIndex((gn) => gn.id === node.id);
        const groupCount = group.length;

        // X spans from -8.5 to +8.5
        x = maxLevel > 0 ? (lvl / maxLevel) * 16 - 8 : (idx - nodes.length / 2) * 2;
        // Y elevation staggered by stratum
        y = (lvl * 0.8) - 0.5;
        // Z spread within level
        z = (indexInGroup - (groupCount - 1) / 2) * 3.2;
      }

      posMap[node.id] = [x, y, z];

      // Color mapping
      const score = node.propagatedRisk !== undefined ? node.propagatedRisk : (node.risk_score || 0);
      let color = "#3b82f6";
      let glowColor = "#1e3a8a";

      if (node.isSeed || node.id.includes("FRAUD") || score >= 0.85) {
        color = "#ef4444";
        glowColor = "#7f1d1d";
      } else if (score >= 0.5) {
        color = "#f59e0b";
        glowColor = "#78350f";
      } else if (node.id.includes("VICTIM") || node.id.includes("INFLOW")) {
        color = "#06b6d4";
        glowColor = "#164e63";
      } else if (node.node_type === "PHONE" || node.node_type === "DEVICE") {
        color = "#a855f7";
        glowColor = "#581c87";
      }

      return {
        ...node,
        position: [x, y, z],
        color,
        glowColor,
      };
    });

    // Build 3D Bezier edge curves
    const computedEdges3D: Edge3DWithCurves[] = edges
      .filter((e) => posMap[e.source] && posMap[e.target])
      .map((e) => {
        const start = posMap[e.source];
        const end = posMap[e.target];

        // Midpoint with upward parabolic lift
        const mid: [number, number, number] = [
          (start[0] + end[0]) / 2,
          Math.max(start[1], end[1]) + 1.2 + Math.random() * 0.4,
          (start[2] + end[2]) / 2,
        ];

        return {
          id: e.id,
          source: e.source,
          target: e.target,
          start,
          end,
          mid,
          amount: e.amount,
          dwellTime: e.dwell_time_seconds,
          isCircular: e.is_circular || isCircularDetected,
          isHighlighted:
            highlightedPath.includes(e.source) && highlightedPath.includes(e.target),
        };
      });

    return { nodes3D: computedNodes3D, edges3D: computedEdges3D };
  }, [nodes, edges, highlightedPath, isCircularDetected]);

  if (!mounted) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#080d1a] text-xs font-mono text-cyan-400">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-cyan-500/30 border-t-cyan-400 animate-spin" />
          <span>Initializing 3D Spatial Network...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full relative cursor-grab active:cursor-grabbing">
      <Canvas
        camera={{ position: [0, 8, 14], fov: 48 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={["#080d1a"]} />
        <fog attach="fog" args={["#080d1a", 16, 36]} />

        {/* Ambient & Directional Lighting */}
        <ambientLight intensity={0.4} />
        <directionalLight position={[10, 20, 10]} intensity={1.2} color="#93c5fd" />
        <pointLight position={[-10, -5, -10]} intensity={0.6} color="#06b6d4" />

        <OrbitControls
          enableDamping
          dampingFactor={0.06}
          rotateSpeed={0.8}
          zoomSpeed={1.0}
          panSpeed={0.8}
          minDistance={4}
          maxDistance={32}
          maxPolarAngle={Math.PI / 2 + 0.1}
        />

        {/* Ground Radar & Grid */}
        <CyberFloor />

        {/* Circular Torus Ring if Circular Wash Loop detected */}
        {isCircularDetected && <CircularWashLoopField radius={6.2} />}

        {/* 3D Curved Flow Edges */}
        {edges3D.map((edge) => (
          <FlowEdgeArc3D
            key={edge.id}
            edge={edge}
            isHighlighted={edge.isHighlighted || false}
          />
        ))}

        {/* 3D Entity Nodes */}
        {nodes3D.map((node) => (
          <EntityNode3D
            key={node.id}
            node={node}
            isSelected={selectedNodeId === node.id}
            isHighlighted={highlightedPath.includes(node.id)}
            onHover={setHoveredNode}
            onClick={() => {
              if (onSelectNode) {
                onSelectNode(selectedNodeId === node.id ? null : node);
              }
            }}
          />
        ))}
      </Canvas>
    </div>
  );
}
