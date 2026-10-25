"use client";

import React, { useRef, useState, useEffect } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Float } from "@react-three/drei";
import * as THREE from "three";

function SentinelCore() {
  const coreRef = useRef<THREE.Mesh>(null);
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);
  const { pointer } = useThree();

  useFrame((_, delta) => {
    // Smoothly track mouse pointer with gentle damping
    if (coreRef.current) {
      coreRef.current.rotation.y += delta * 0.5;
      coreRef.current.rotation.x = THREE.MathUtils.lerp(
        coreRef.current.rotation.x,
        -pointer.y * 0.4,
        0.05
      );
      coreRef.current.rotation.z = THREE.MathUtils.lerp(
        coreRef.current.rotation.z,
        pointer.x * 0.4,
        0.05
      );
    }

    if (ring1Ref.current) {
      ring1Ref.current.rotation.z += delta * 0.6;
      ring1Ref.current.rotation.y = THREE.MathUtils.lerp(
        ring1Ref.current.rotation.y,
        pointer.x * 0.5,
        0.04
      );
    }

    if (ring2Ref.current) {
      ring2Ref.current.rotation.x += delta * 0.8;
      ring2Ref.current.rotation.z -= delta * 0.4;
    }
  });

  return (
    <Float speed={2} rotationIntensity={0.2} floatIntensity={0.3}>
      <group position={[0, 0, 0]}>
        {/* Central Sentinel Icosahedron Core */}
        <mesh ref={coreRef}>
          <icosahedronGeometry args={[1.1, 1]} />
          <meshStandardMaterial
            color="#2563eb"
            emissive="#1d4ed8"
            emissiveIntensity={1.2}
            metalness={0.9}
            roughness={0.15}
            wireframe
          />
        </mesh>

        {/* Inner Solid Nucleus */}
        <mesh>
          <octahedronGeometry args={[0.6, 0]} />
          <meshStandardMaterial
            color="#38bdf8"
            emissive="#0284c7"
            emissiveIntensity={2.0}
            metalness={0.5}
            roughness={0.2}
          />
        </mesh>

        {/* Gimbal Ring 1 */}
        <mesh ref={ring1Ref} rotation={[Math.PI / 4, 0, 0]}>
          <torusGeometry args={[1.65, 0.03, 16, 64]} />
          <meshBasicMaterial color="#60a5fa" transparent opacity={0.7} />
        </mesh>

        {/* Gimbal Ring 2 */}
        <mesh ref={ring2Ref} rotation={[-Math.PI / 4, Math.PI / 3, 0]}>
          <torusGeometry args={[1.95, 0.025, 16, 64]} />
          <meshBasicMaterial color="#38bdf8" transparent opacity={0.5} />
        </mesh>
      </group>
    </Float>
  );
}

function AmbientCyberParticles() {
  const pointsRef = useRef<THREE.Points>(null);
  const count = 36;

  const positions = React.useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2;
      const dist = 2.2 + Math.random() * 0.8;
      arr[i * 3] = Math.cos(angle) * dist;
      arr[i * 3 + 1] = (Math.random() - 0.5) * 2;
      arr[i * 3 + 2] = Math.sin(angle) * dist;
    }
    return arr;
  }, [count]);

  useFrame((_, delta) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={count}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.08} color="#93c5fd" transparent opacity={0.6} />
    </points>
  );
}

export function ThreeHeroSentinel() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-[150px] sm:h-[180px] flex items-center justify-center text-xs font-mono text-blue-600">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded-full border-2 border-blue-200 border-t-blue-600 animate-spin" />
          <span>Active Sentinel Sync...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-[150px] sm:h-[180px] relative select-none pointer-events-auto">
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 40 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[5, 10, 5]} intensity={1.5} color="#93c5fd" />
        <pointLight position={[-5, -5, 5]} intensity={0.8} color="#38bdf8" />

        <SentinelCore />
        <AmbientCyberParticles />
      </Canvas>
    </div>
  );
}
