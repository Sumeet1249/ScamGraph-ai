"use client";

import React, { useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Float, Torus, Sphere } from "@react-three/drei";
import * as THREE from "three";

interface Props {
  isSafer: boolean;
  riskScore: number;
  riskLevel: string;
}

// 1. Central Holographic Security Core
function HologramCore({ isSafer, riskScore }: { isSafer: boolean; riskScore: number }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const outerRingRef = useRef<THREE.Mesh>(null);
  const innerRingRef = useRef<THREE.Mesh>(null);

  const primaryColor = isSafer ? "#10b981" : "#f43f5e";
  const glowColor = isSafer ? "#059669" : "#be123c";

  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * (isSafer ? 0.7 : 1.4);
      meshRef.current.rotation.x += delta * 0.4;
    }
    if (outerRingRef.current) {
      outerRingRef.current.rotation.z += delta * (isSafer ? 0.9 : -1.5);
      outerRingRef.current.rotation.x += delta * 0.3;
    }
    if (innerRingRef.current) {
      innerRingRef.current.rotation.y -= delta * 1.1;
      innerRingRef.current.rotation.z += delta * 0.5;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.3} floatIntensity={0.4}>
      {/* Central Geometry: Shield Octahedron if Safe, Spiky Icosahedron if Breached */}
      <mesh ref={meshRef} position={[0, 0, 0]}>
        {isSafer ? (
          <octahedronGeometry args={[1.3, 0]} />
        ) : (
          <icosahedronGeometry args={[1.3, 1]} />
        )}
        <meshStandardMaterial
          color={primaryColor}
          emissive={glowColor}
          emissiveIntensity={1.8}
          wireframe={!isSafer}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>

      {/* Orbiting Defense Field Ring 1 */}
      <mesh ref={outerRingRef}>
        <torusGeometry args={[2.0, 0.04, 16, 64]} />
        <meshBasicMaterial
          color={isSafer ? "#34d399" : "#fb7185"}
          transparent
          opacity={0.8}
        />
      </mesh>

      {/* Orbiting Defense Field Ring 2 */}
      <mesh ref={innerRingRef} rotation={[Math.PI / 4, 0, 0]}>
        <torusGeometry args={[2.4, 0.03, 16, 64]} />
        <meshBasicMaterial
          color={isSafer ? "#06b6d4" : "#e11d48"}
          transparent
          opacity={0.6}
        />
      </mesh>
    </Float>
  );
}

// 2. Simulated Threat Pulse Particles
function ThreatPulseParticles({ isSafer }: { isSafer: boolean }) {
  const pointsRef = useRef<THREE.Points>(null);

  const particleCount = 48;
  const positions = React.useMemo(() => {
    const coords = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const angle = (i / particleCount) * Math.PI * 2;
      const r = 2.8 + Math.random() * 0.8;
      coords[i * 3] = Math.cos(angle) * r;
      coords[i * 3 + 1] = (Math.random() - 0.5) * 1.6;
      coords[i * 3 + 2] = Math.sin(angle) * r;
    }
    return coords;
  }, [particleCount]);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * (isSafer ? 0.3 : 1.2);
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.12}
        color={isSafer ? "#6ee7b7" : "#fda4af"}
        transparent
        opacity={0.75}
      />
    </points>
  );
}

export function ThreeAttackVectorChamber({ isSafer, riskScore, riskLevel }: Props) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[220px] flex items-center justify-center rounded-xl bg-[#070c18] border border-border/80 text-xs font-mono text-emerald-400">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-emerald-500/30 border-t-emerald-400 animate-spin" />
          <span>Loading 3D Vector Chamber...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[220px] relative rounded-xl overflow-hidden bg-[#070c18] border border-border/80 select-none cursor-grab active:cursor-grabbing">
      {/* Overlay Status Badge */}
      <div className="absolute top-2.5 left-3 z-10 flex items-center gap-2 pointer-events-none">
        <span
          className={`h-2 w-2 rounded-full ${
            isSafer ? "bg-emerald-400 animate-pulse" : "bg-rose-500 animate-ping"
          }`}
        />
        <span className="text-[10px] font-mono font-bold tracking-wider uppercase text-white/90">
          3D Vector Chamber • {isSafer ? "THREAT INTERCEPTED" : "BREACH SIMULATION"}
        </span>
      </div>

      <div className="absolute bottom-2.5 right-3 z-10 text-[10px] font-mono text-white/50 pointer-events-none">
        Rotate 360° to inspect vector
      </div>

      <Canvas
        camera={{ position: [0, 1.2, 5.2], fov: 42 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
      >
        <color attach="background" args={["#070c18"]} />

        <ambientLight intensity={0.4} />
        <pointLight
          position={[5, 5, 5]}
          intensity={1.5}
          color={isSafer ? "#10b981" : "#f43f5e"}
        />
        <pointLight position={[-5, -5, -5]} intensity={0.5} color="#38bdf8" />

        <OrbitControls
          enableZoom={false}
          enablePan={false}
          rotateSpeed={0.7}
          autoRotate
          autoRotateSpeed={isSafer ? 1.0 : 2.5}
          maxPolarAngle={Math.PI / 2 + 0.2}
          minPolarAngle={Math.PI / 2 - 0.5}
        />

        {/* Central Core */}
        <HologramCore isSafer={isSafer} riskScore={riskScore} />

        {/* Particle Cloud */}
        <ThreatPulseParticles isSafer={isSafer} />
      </Canvas>
    </div>
  );
}
