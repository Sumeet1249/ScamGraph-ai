"use client";

import React, { useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Float, OrbitControls } from "@react-three/drei";
import * as THREE from "three";

interface Props {
  actionId: string;
}

// 1. 3D Interceptor Shield Geometry
function GuardShieldMesh({ actionId }: { actionId: string }) {
  const shieldRef = useRef<THREE.Group>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  // Dynamic colors based on risk posture of the chosen action
  const isHighRisk = actionId === "share_credential" || actionId === "share_screen" || actionId === "install_app";
  const isTargetRisk = actionId === "approve_collect";

  const primaryColor = isHighRisk ? "#ef4444" : isTargetRisk ? "#f59e0b" : "#3b82f6";
  const glowColor = isHighRisk ? "#7f1d1d" : isTargetRisk ? "#78350f" : "#1e3a8a";

  useFrame((_, delta) => {
    if (shieldRef.current) {
      shieldRef.current.rotation.y += delta * 0.4;
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.8;
      ringRef.current.rotation.x += delta * 0.2;
    }
    if (coreRef.current) {
      coreRef.current.rotation.y -= delta * 0.9;
    }
  });

  return (
    <Float speed={2.5} rotationIntensity={0.25} floatIntensity={0.35}>
      <group ref={shieldRef}>
        {/* Shield Faceted Front Polyhedron */}
        <mesh position={[0, 0, 0]}>
          <octahedronGeometry args={[1.2, 0]} />
          <meshStandardMaterial
            color={primaryColor}
            emissive={glowColor}
            emissiveIntensity={1.4}
            metalness={0.85}
            roughness={0.2}
          />
        </mesh>

        {/* Inner Diamond Core */}
        <mesh ref={coreRef} position={[0, 0, 0]}>
          <dodecahedronGeometry args={[0.55, 0]} />
          <meshStandardMaterial
            color="#ffffff"
            emissive={primaryColor}
            emissiveIntensity={2.0}
            wireframe
          />
        </mesh>

        {/* Outer Scanner Radar Ring */}
        <mesh ref={ringRef} rotation={[Math.PI / 3, 0, 0]}>
          <torusGeometry args={[1.8, 0.03, 16, 64]} />
          <meshBasicMaterial
            color={primaryColor}
            transparent
            opacity={0.85}
          />
        </mesh>
      </group>
    </Float>
  );
}

export function ThreeGuardShield({ actionId }: Props) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[180px] flex items-center justify-center rounded-xl bg-[#080e1b] border border-border-divider text-xs font-mono text-cyan-400">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-cyan-500/30 border-t-cyan-400 animate-spin" />
          <span>Initializing Interceptor HUD...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[180px] relative rounded-xl overflow-hidden bg-gradient-to-b from-[#0c1322] to-[#070b14] border border-border-divider shadow-inner select-none cursor-grab active:cursor-grabbing">
      {/* Top HUD Label */}
      <div className="absolute top-2.5 left-3 z-10 flex items-center gap-2 pointer-events-none">
        <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse" />
        <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-cyan-300">
          ScamGraph Autonomous Interceptor HUD
        </span>
      </div>

      <div className="absolute bottom-2 right-3 z-10 text-[9px] font-mono text-white/40 pointer-events-none">
        Drag to inspect defense shield
      </div>

      <Canvas
        camera={{ position: [0, 0.5, 4.4], fov: 42 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={["#080e1b"]} />

        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 10, 5]} intensity={1.4} color="#93c5fd" />
        <pointLight position={[-4, -4, 4]} intensity={0.8} color="#06b6d4" />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          rotateSpeed={0.8}
          autoRotate
          autoRotateSpeed={1.2}
          maxPolarAngle={Math.PI / 2 + 0.3}
          minPolarAngle={Math.PI / 2 - 0.3}
        />

        <GuardShieldMesh actionId={actionId} />
      </Canvas>
    </div>
  );
}
