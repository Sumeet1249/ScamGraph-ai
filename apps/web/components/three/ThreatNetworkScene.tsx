"use client";

import { Suspense, useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Line as DreiLine } from "@react-three/drei";
import * as THREE from "three";
import { useReducedMotion } from "@/lib/hooks/useReducedMotion";

/**
 * Three.js compatibility proof-of-concept: Threat Intelligence Network.
 *
 * Abstract threat nodes orbiting a central core — NOT fake geography.
 * Nodes represent incidents / campaigns / infrastructure clusters.
 *
 * Phase 1 scope: prove R3F v8 + React 18 + drei render cleanly, lazy-load,
 * and degrade gracefully under reduced motion / WebGL failure.
 * Phase 6 will expand this into the full Command Center visualization.
 *
 * Performance: ~14 nodes only. No post-processing. Pause rotation under
 * reduced motion.
 */

type Node = { id: number; radius: number; angle: number; speed: number; y: number; size: number };

function NetworkNodes({ reduced }: { reduced: boolean }) {
  const group = useRef<THREE.Group>(null);

  // Deterministic node layout (no random per-render churn)
  const nodes = useMemo<Node[]>(() => {
    const count = 14;
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      radius: 2.2 + ((i * 37) % 90) / 100,
      angle: (i / count) * Math.PI * 2,
      speed: 0.05 + ((i * 13) % 30) / 1000,
      y: (((i * 53) % 100) - 50) / 60,
      size: 0.06 + ((i * 29) % 5) / 100,
    }));
  }, []);

  useFrame((_, delta) => {
    if (!group.current || reduced) return;
    group.current.rotation.y += delta * 0.06;
  });

  return (
    <group ref={group}>
      {nodes.map((n) => {
        const x = Math.cos(n.angle) * n.radius;
        const z = Math.sin(n.angle) * n.radius;
        const isHub = n.id % 5 === 0;
        return (
          <group key={n.id} position={[x, n.y, z]}>
            <mesh>
              <sphereGeometry args={[n.size, 16, 16]} />
              <meshBasicMaterial color={isHub ? "#A8836B" : "#C4B5E8"} />
            </mesh>
          </group>
        );
      })}

      {/* Connection lines from core to each node */}
      {nodes.map((n) => {
        const x = Math.cos(n.angle) * n.radius;
        const z = Math.sin(n.angle) * n.radius;
        return (
          <DreiLine
            key={`l-${n.id}`}
            points={[[0, 0, 0], [x, n.y, z]]}
            color="#E5E4E2"
            lineWidth={1}
            transparent
            opacity={0.22}
          />
        );
      })}

      {/* Central core */}
      <mesh>
        <icosahedronGeometry args={[0.28, 0]} />
        <meshBasicMaterial color="#E5E4E2" wireframe />
      </mesh>
    </group>
  );
}

function Scene({ reduced }: { reduced: boolean }) {
  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[4, 4, 4]} intensity={0.5} />
      <NetworkNodes reduced={reduced} />
    </>
  );
}

/**
 * Static 2D fallback used when WebGL is unavailable. R3F Canvas also accepts a
 * `fallback` prop, but we render this when the parent detects reduced motion
 * preference at the page level OR Canvas itself fails.
 */
export function ThreatNetworkFallback() {
  return (
    <div
      className="flex h-full w-full items-center justify-center"
      role="img"
      aria-label="Threat intelligence network (static view)"
    >
      <svg viewBox="0 0 200 200" className="h-full w-full opacity-70" aria-hidden>
        <circle cx="100" cy="100" r="8" fill="none" stroke="#E5E4E2" strokeWidth="1" />
        {Array.from({ length: 12 }).map((_, i) => {
          const a = (i / 12) * Math.PI * 2;
          const r = 60;
          const x = 100 + Math.cos(a) * r;
          const y = 100 + Math.sin(a) * r;
          return (
            <g key={i}>
              <line x1="100" y1="100" x2={x} y2={y} stroke="#E5E4E2" strokeOpacity="0.22" strokeWidth="1" />
              <circle cx={x} cy={y} r={i % 5 === 0 ? 3.5 : 2.5} fill={i % 5 === 0 ? "#A8836B" : "#C4B5E8"} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function ThreatNetworkScene() {
  const reduced = useReducedMotion();

  return (
    <div className="relative h-full w-full">
      <Canvas
        dpr={[1, 1.5]}
        camera={{ position: [0, 0, 6], fov: 50 }}
        gl={{ antialias: true, powerPreference: "default" }}
        fallback={<ThreatNetworkFallback />}
      >
        <Suspense fallback={null}>
          <Scene reduced={reduced} />
        </Suspense>
      </Canvas>
      <span className="pointer-events-none absolute bottom-3 left-3 text-[10px] font-mono text-ink-dim">
        Threat Intelligence Network
      </span>
    </div>
  );
}
