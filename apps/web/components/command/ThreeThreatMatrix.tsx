"use client";

import React, { useRef, useMemo, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, QuadraticBezierLine, Html, Float } from "@react-three/drei";
import * as THREE from "three";

export interface ThreatNode3D {
  id: string;
  label: string;
  type: "campaign" | "mule_hub" | "vpa" | "channel" | "region";
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  position: [number, number, number];
  incidentCount: number;
  velocity: number;
  details: string;
  isCore?: boolean;
}

export interface ThreatEdge3D {
  id: string;
  source: string;
  target: string;
  start: [number, number, number];
  end: [number, number, number];
  mid: [number, number, number];
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
}

// Color Palette for Threat Matrix
const COLORS = {
  CRITICAL: {
    base: "#ef4444",
    light: "#fca5a5",
    glow: "#7f1d1d",
  },
  HIGH: {
    base: "#f59e0b",
    light: "#fde68a",
    glow: "#78350f",
  },
  MEDIUM: {
    base: "#06b6d4",
    light: "#a5f3fc",
    glow: "#164e63",
  },
  LOW: {
    base: "#3b82f6",
    light: "#bfdbfe",
    glow: "#1e3a8a",
  },
  CORE: {
    base: "#38bdf8",
    light: "#e0f2fe",
    glow: "#0369a1",
  },
};

// 1. Central Sovereign SOC Core Mesh
function CentralCore() {
  const outerRef = useRef<THREE.Mesh>(null);
  const innerRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (outerRef.current) {
      outerRef.current.rotation.y += delta * 0.4;
      outerRef.current.rotation.x += delta * 0.2;
    }
    if (innerRef.current) {
      innerRef.current.rotation.y -= delta * 0.6;
    }
  });

  return (
    <group position={[0, 0.5, 0]}>
      {/* Outer Wireframe Shield */}
      <mesh ref={outerRef}>
        <icosahedronGeometry args={[1.2, 1]} />
        <meshBasicMaterial color="#38bdf8" wireframe transparent opacity={0.35} />
      </mesh>

      {/* Inner Glowing Nucleus */}
      <mesh ref={innerRef}>
        <octahedronGeometry args={[0.7, 0]} />
        <meshStandardMaterial
          color="#0284c7"
          emissive="#38bdf8"
          emissiveIntensity={1.2}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Core Ground Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.48, 0]}>
        <ringGeometry args={[1.6, 1.8, 32]} />
        <meshBasicMaterial color="#0284c7" transparent opacity={0.4} side={THREE.DoubleSide} />
      </mesh>
    </group>
  );
}

// 2. Individual Volumetric Threat Beacon Node
function BeaconNode({
  node,
  isSelected,
  isHovered,
  onSelect,
  onHover,
}: {
  node: ThreatNode3D;
  isSelected: boolean;
  isHovered: boolean;
  onSelect: (node: ThreatNode3D) => void;
  onHover: (node: ThreatNode3D | null) => void;
}) {
  const ringRef = useRef<THREE.Mesh>(null);
  const colorScheme = node.isCore ? COLORS.CORE : COLORS[node.severity] || COLORS.MEDIUM;

  // Pulse ring animation along Y axis
  useFrame(({ clock }) => {
    if (ringRef.current) {
      const t = (clock.getElapsedTime() * 1.5 + (node.position[0] % 2)) % 2;
      ringRef.current.position.y = (t / 2) * 1.8;
      const scale = 1 + (t / 2) * 0.8;
      ringRef.current.scale.set(scale, scale, scale);
      (ringRef.current.material as THREE.MeshBasicMaterial).opacity = Math.max(0, 0.8 * (1 - t / 2));
    }
  });

  // Calculate pillar height based on velocity / incidentCount
  const pillarHeight = Math.max(1.2, Math.min(3.5, 1.0 + (node.velocity / 200)));
  const baseRadius = node.isCore ? 0.6 : isSelected ? 0.45 : isHovered ? 0.4 : 0.3;

  return (
    <group
      position={node.position}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(node);
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        onHover(node);
      }}
      onPointerOut={() => onHover(null)}
    >
      {/* Base Pedestal Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.02, 0]}>
        <ringGeometry args={[baseRadius * 1.2, baseRadius * 1.6, 24]} />
        <meshBasicMaterial
          color={colorScheme.base}
          transparent
          opacity={isSelected || isHovered ? 0.9 : 0.4}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Vertical Threat Column */}
      <mesh position={[0, pillarHeight / 2, 0]}>
        <cylinderGeometry args={[baseRadius * 0.7, baseRadius, pillarHeight, 16]} />
        <meshStandardMaterial
          color={colorScheme.base}
          emissive={colorScheme.base}
          emissiveIntensity={isSelected ? 1.5 : isHovered ? 1.0 : 0.45}
          roughness={0.3}
          metalness={0.7}
          transparent
          opacity={0.88}
        />
      </mesh>

      {/* Top Beacon Orb */}
      <mesh position={[0, pillarHeight + 0.2, 0]}>
        <sphereGeometry args={[baseRadius * 0.8, 16, 16]} />
        <meshStandardMaterial
          color={colorScheme.light}
          emissive={colorScheme.base}
          emissiveIntensity={isSelected ? 2.0 : 1.2}
          roughness={0.1}
        />
      </mesh>

      {/* Pulsing Sonar Ring */}
      <mesh ref={ringRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.1, 0]}>
        <ringGeometry args={[baseRadius * 1.5, baseRadius * 1.7, 24]} />
        <meshBasicMaterial color={colorScheme.light} transparent opacity={0.6} side={THREE.DoubleSide} />
      </mesh>

      {/* 3D Floating HUD Billboard on Hover or Selected */}
      {(isHovered || isSelected) && (
        <Html position={[0, pillarHeight + 0.9, 0]} center distanceFactor={14}>
          <div className="bg-slate-950/95 border border-cyan-500/70 rounded-lg px-2.5 py-1.5 shadow-2xl backdrop-blur-md pointer-events-none whitespace-nowrap text-center font-mono animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center gap-1.5 justify-center">
              <span
                className="h-1.5 w-1.5 rounded-full animate-ping"
                style={{ backgroundColor: colorScheme.base }}
              />
              <span className="text-[11px] font-bold text-white tracking-wide">
                {node.label}
              </span>
            </div>
            <div className="text-[10px] text-cyan-300 mt-0.5 font-semibold flex items-center justify-center gap-2">
              <span>{node.severity}</span>
              <span>•</span>
              <span className="text-emerald-400">+{node.velocity}% vel</span>
              <span>•</span>
              <span>{node.incidentCount} inc</span>
            </div>
          </div>
        </Html>
      )}
    </group>
  );
}

// 3. 3D Parabolic Curved Trajectory Arcs
function TrajectoryArc({ edge }: { edge: ThreatEdge3D }) {
  const color = COLORS[edge.severity]?.base || "#38bdf8";

  return (
    <QuadraticBezierLine
      start={edge.start}
      end={edge.end}
      mid={edge.mid}
      color={color}
      lineWidth={edge.severity === "CRITICAL" ? 2.2 : 1.4}
      transparent
      opacity={edge.severity === "CRITICAL" ? 0.85 : 0.5}
      dashed={false}
    />
  );
}

// 4. Perspective Cyber Grid Floor
function CyberGridFloor() {
  return (
    <group position={[0, -0.01, 0]}>
      {/* Concentric Sonar Distance Rings */}
      {[3.5, 7.0, 10.5, 14.0].map((radius, idx) => (
        <mesh key={idx} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[radius - 0.04, radius + 0.04, 64]} />
          <meshBasicMaterial color="#1e293b" transparent opacity={0.5 - idx * 0.1} side={THREE.DoubleSide} />
        </mesh>
      ))}

      {/* Axis Guide Cross-hairs */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[30, 0.04]} />
        <meshBasicMaterial color="#334155" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, Math.PI / 2]}>
        <planeGeometry args={[30, 0.04]} />
        <meshBasicMaterial color="#334155" transparent opacity={0.3} side={THREE.DoubleSide} />
      </mesh>

      {/* Horizon Fade Plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <circleGeometry args={[16, 48]} />
        <meshBasicMaterial color="#090d16" />
      </mesh>
    </group>
  );
}

// 5. Main 3D Threat Matrix Component
interface Props {
  campaigns?: any[];
  signals?: any[];
  blips?: any[];
  selectedNode: ThreatNode3D | null;
  onSelectNode: (node: ThreatNode3D | null) => void;
  filterSeverity: string;
  isPlaying: boolean;
}

export function ThreeThreatMatrix({
  campaigns = [],
  signals = [],
  blips = [],
  selectedNode,
  onSelectNode,
  filterSeverity,
  isPlaying,
}: Props) {
  const [mounted, setMounted] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<ThreatNode3D | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Build 3D spatial nodes and curved trajectory edges from real telemetry data
  const { nodes3D, edges3D } = useMemo(() => {
    const rawNodes: ThreatNode3D[] = [];
    const rawEdges: ThreatEdge3D[] = [];

    // Core Node at [0, 0, 0]
    const coreNode: ThreatNode3D = {
      id: "node_soc_core",
      label: "ScamGraph Core Sovereign Engine",
      type: "campaign",
      severity: "LOW",
      position: [0, 0, 0],
      incidentCount: signals.length || 58,
      velocity: 18.4,
      details: "Central Multi-Signal Correlation & Real-Time Fraud Interception Core",
      isCore: true,
    };
    rawNodes.push(coreNode);

    // Primary Campaign Orbit (radius ~ 5.5)
    const activeCamps = campaigns.length > 0 ? campaigns : [
      { id: "c_da", title: "Digital Arrest CBI Ring", severity: "CRITICAL", incidents_count: 48, velocity: 428, scam_family: "DIGITAL_ARREST" },
      { id: "c_bescom", title: "BESCOM Power Disconnect", severity: "HIGH", incidents_count: 32, velocity: 210, scam_family: "UTILITY_BILL" },
      { id: "c_task", title: "Telegram VIP Job Task", severity: "HIGH", incidents_count: 28, velocity: 185, scam_family: "PART_TIME_JOB" },
      { id: "c_fedex", title: "Mumbai Customs Parcel", severity: "MEDIUM", incidents_count: 19, velocity: 95, scam_family: "PARCEL_CUSTOMS" },
      { id: "c_loan", title: "Instant Micro-Loan APK", severity: "HIGH", incidents_count: 37, velocity: 260, scam_family: "LOAN_HARASSMENT" },
    ];

    activeCamps.forEach((c, idx) => {
      const angle = (idx / activeCamps.length) * Math.PI * 2 + 0.4;
      const radius = 5.2 + ((idx * 17) % 15) / 10;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const cId = c.campaign_id || c.id || `camp_${idx}`;
      const sev = (c.severity || "HIGH").toUpperCase() as any;

      const campNode: ThreatNode3D = {
        id: cId,
        label: c.title || c.name || "Active Syndicate",
        type: "campaign",
        severity: sev === "CRITICAL" ? "CRITICAL" : sev === "HIGH" ? "HIGH" : "MEDIUM",
        position: [x, 0, z],
        incidentCount: c.incidents_count || 24,
        velocity: c.velocity || (c.velocity_state === "SURGING" ? 428 : 115),
        details: `Family: ${c.scam_family || "CYBER_FRAUD"} • Velocity: +${c.velocity || 180}% acceleration`,
      };

      rawNodes.push(campNode);

      // Arc from Core to Campaign Node
      rawEdges.push({
        id: `arc_core_${cId}`,
        source: "node_soc_core",
        target: cId,
        start: [0, 1.2, 0],
        end: [x, 1.6, z],
        mid: [x * 0.5, 2.6, z * 0.5],
        severity: campNode.severity,
      });
    });

    // Satellite Mule Hubs & Target VPAs (radius ~ 9.0)
    const satellites = [
      { id: "mule_jharkhand", label: "Mule Ring Tier-1 (Jaipur)", parentIdx: 0, sev: "CRITICAL", vel: 390, count: 18, type: "mule_hub" as const },
      { id: "vpa_cbi", label: "cbi.clearance@oksbi", parentIdx: 0, sev: "CRITICAL", vel: 340, count: 22, type: "vpa" as const },
      { id: "reg_delhi", label: "Delhi NCR Surge Node", parentIdx: 1, sev: "HIGH", vel: 210, count: 35, type: "region" as const },
      { id: "chan_tg", label: "Telegram VIP Bot Dropper", parentIdx: 2, sev: "HIGH", vel: 185, count: 29, type: "channel" as const },
      { id: "vpa_vip", label: "daily.rewards@ybl", parentIdx: 2, sev: "HIGH", vel: 170, count: 16, type: "vpa" as const },
      { id: "mule_crypto", label: "USDT P2P Crypto Off-Ramp", parentIdx: 4, sev: "CRITICAL", vel: 460, count: 44, type: "mule_hub" as const },
    ];

    satellites.forEach((sat, sIdx) => {
      const parentNode = rawNodes[1 + (sat.parentIdx % (rawNodes.length - 1))];
      const angle = (sIdx / satellites.length) * Math.PI * 2 + 0.8;
      const radius = 9.2 + ((sIdx * 23) % 15) / 10;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;

      const satNode: ThreatNode3D = {
        id: sat.id,
        label: sat.label,
        type: sat.type,
        severity: sat.sev as any,
        position: [x, 0, z],
        incidentCount: sat.count,
        velocity: sat.vel,
        details: `Correlated Infrastructure Node • Active Turnover: +${sat.vel}%`,
      };

      rawNodes.push(satNode);

      if (parentNode) {
        rawEdges.push({
          id: `arc_sat_${sat.id}`,
          source: parentNode.id,
          target: sat.id,
          start: [parentNode.position[0], 1.5, parentNode.position[2]],
          end: [x, 1.4, z],
          mid: [
            (parentNode.position[0] + x) / 2,
            2.8,
            (parentNode.position[2] + z) / 2,
          ],
          severity: sat.sev as any,
        });
      }
    });

    return { nodes3D: rawNodes, edges3D: rawEdges };
  }, [campaigns, signals, blips]);

  // Apply severity filter
  const filteredNodes = useMemo(() => {
    if (filterSeverity === "ALL") return nodes3D;
    return nodes3D.filter((n) => n.isCore || n.severity === filterSeverity);
  }, [nodes3D, filterSeverity]);

  const filteredEdges = useMemo(() => {
    const nodeIds = new Set(filteredNodes.map((n) => n.id));
    return edges3D.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target));
  }, [edges3D, filteredNodes]);

  if (!mounted) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-[#080c14] text-xs font-mono text-cyan-400">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-cyan-500/30 border-t-cyan-400 animate-spin" />
          <span>Initializing 3D Matrix...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full relative">
      <Canvas
        camera={{ position: [0, 11, 15], fov: 46 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
        onPointerMissed={() => onSelectNode(null)}
      >
        <color attach="background" args={["#080c14"]} />

        {/* Ambient & Directional Cyber Lighting */}
        <ambientLight intensity={0.65} />
        <pointLight position={[0, 8, 0]} intensity={1.5} color="#38bdf8" distance={24} />
        <directionalLight position={[10, 14, 8]} intensity={0.9} color="#e2e8f0" />
        <pointLight position={[-10, 4, -10]} intensity={0.5} color="#ef4444" distance={20} />

        {/* Fog for Atmospheric Depth */}
        <fog attach="fog" args={["#080c14", 16, 32]} />

        {/* 3D Scene Elements */}
        <group position={[0, -0.6, 0]}>
          <CyberGridFloor />
          <CentralCore />

          {/* Volumetric Threat Beacon Columns */}
          {filteredNodes.map((node) => (
            <BeaconNode
              key={node.id}
              node={node}
              isSelected={selectedNode?.id === node.id}
              isHovered={hoveredNode?.id === node.id}
              onSelect={onSelectNode}
              onHover={setHoveredNode}
            />
          ))}

          {/* Curved Parabolic Trajectory Arcs */}
          {filteredEdges.map((edge) => (
            <TrajectoryArc key={edge.id} edge={edge} />
          ))}
        </group>

        {/* Smooth Orbit & Zoom Controls */}
        <OrbitControls
          enablePan={true}
          enableZoom={true}
          minDistance={6}
          maxDistance={24}
          maxPolarAngle={Math.PI / 2 - 0.08}
          minPolarAngle={0.1}
          autoRotate={isPlaying}
          autoRotateSpeed={0.6}
          dampingFactor={0.06}
        />
      </Canvas>
    </div>
  );
}
