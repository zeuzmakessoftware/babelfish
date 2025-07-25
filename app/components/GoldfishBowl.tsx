'use client';

import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { 
  OrbitControls, 
  Environment, 
  Float, 
  Text3D, 
  Sphere, 
  Box, 
  Cylinder,
  Sparkles
} from '@react-three/drei';
import { useRef, useState, useEffect } from 'react';
import * as THREE from 'three';

// Enhanced Goldfish component with more impressive visuals
function Goldfish({ 
  position = [0, 0, 0], 
  isSpeaking = false, 
  isListening = false 
}: { 
  position?: [number, number, number];
  isSpeaking?: boolean;
  isListening?: boolean;
}) {
  const fishRef = useRef<THREE.Group>(null);
  const tailRef = useRef<THREE.Mesh>(null);
  const eyeRef1 = useRef<THREE.Mesh>(null);
  const eyeRef2 = useRef<THREE.Mesh>(null);
  
  useFrame(({ clock }) => {
    if (fishRef.current) {
      // Reduced movement range and kept fish more centered
      fishRef.current.position.x = position[0] + Math.sin(clock.elapsedTime * 0.5) * 0.3;
      fishRef.current.position.y = position[1] + Math.sin(clock.elapsedTime * 0.3) * 0.1;
      fishRef.current.position.z = position[2] + Math.cos(clock.elapsedTime * 0.4) * 0.15;
      
      // Smoother rotation
      fishRef.current.rotation.y = Math.sin(clock.elapsedTime * 0.5) * 0.2;
      fishRef.current.rotation.z = Math.sin(clock.elapsedTime * 0.8) * 0.05;
      
      // More stable scaling
      const baseScale = 1.0;
      const speakingScale = isSpeaking ? 1.1 : 1.0;
      const listeningScale = isListening ? 1.05 : 1.0;
      const breathingScale = Math.sin(clock.elapsedTime * 2) * 0.01;
      fishRef.current.scale.setScalar(baseScale * speakingScale * listeningScale + breathingScale);
    }
    
    if (tailRef.current) {
      // More dynamic tail movement
      tailRef.current.rotation.y = Math.sin(clock.elapsedTime * 6) * 0.4;
      tailRef.current.rotation.z = Math.cos(clock.elapsedTime * 4) * 0.2;
    }

    // Animated eyes
    if (eyeRef1.current && eyeRef2.current) {
      const eyeScale = 1 + Math.sin(clock.elapsedTime * 8) * 0.1;
      eyeRef1.current.scale.setScalar(eyeScale);
      eyeRef2.current.scale.setScalar(eyeScale);
    }
  });

  return (
    <group ref={fishRef} position={position}>
      {/* Enhanced main body with more stable material */}
      <mesh castShadow receiveShadow>
        <sphereGeometry args={[0.15, 32, 32]} />
        <meshStandardMaterial 
          color={isSpeaking ? "#ffaa00" : isListening ? "#ff6b6b" : "#ff8c42"} 
          roughness={0.4}
          metalness={0.3}
        />
      </mesh>
      
      {/* Enhanced tail with better geometry */}
      <mesh ref={tailRef} position={[-0.2, 0, 0]} castShadow>
        <coneGeometry args={[0.1, 0.18, 12]} />
        <meshPhysicalMaterial 
          color="#ff6b42" 
          roughness={0.3}
          metalness={0.1}
          clearcoat={0.8}
        />
      </mesh>
      
      {/* Enhanced eyes with animation */}
      <mesh ref={eyeRef1} position={[0.1, 0.06, 0.08]} castShadow>
        <sphereGeometry args={[0.025, 12, 12]} />
        <meshPhysicalMaterial color="black" roughness={0} metalness={0.8} />
      </mesh>
      <mesh ref={eyeRef2} position={[0.1, 0.06, -0.08]} castShadow>
        <sphereGeometry args={[0.025, 12, 12]} />
        <meshPhysicalMaterial color="black" roughness={0} metalness={0.8} />
      </mesh>
      
      {/* Enhanced fins with better materials */}
      <mesh position={[0, -0.08, 0.12]} rotation={[0, 0, 0.5]} castShadow>
        <boxGeometry args={[0.04, 0.1, 0.015]} />
        <meshPhysicalMaterial color="#ff9933" roughness={0.4} metalness={0.1} />
      </mesh>
      <mesh position={[0, -0.08, -0.12]} rotation={[0, 0, -0.5]} castShadow>
        <boxGeometry args={[0.04, 0.1, 0.015]} />
        <meshPhysicalMaterial color="#ff9933" roughness={0.4} metalness={0.1} />
      </mesh>
      
      {/* Top fin */}
      <mesh position={[0, 0.12, 0]} rotation={[0, 0, 0]} castShadow>
        <boxGeometry args={[0.06, 0.08, 0.01]} />
        <meshPhysicalMaterial color="#ff7722" roughness={0.4} metalness={0.1} />
      </mesh>
      
      {/* Enhanced speech bubbles */}
      {isSpeaking && (
        <Float speed={3} floatIntensity={0.8}>
          <mesh position={[0.35, 0.25, 0]}>
            <sphereGeometry args={[0.06, 12, 12]} />
            <meshPhysicalMaterial 
              color="white" 
              transparent 
              opacity={0.9} 
              roughness={0}
              metalness={0}
              transmission={0.8}
            />
          </mesh>
          <mesh position={[0.45, 0.35, 0.1]}>
            <sphereGeometry args={[0.04, 8, 8]} />
            <meshPhysicalMaterial 
              color="white" 
              transparent 
              opacity={0.7} 
              roughness={0}
              transmission={0.6}
            />
          </mesh>
        </Float>
      )}
      
      {/* Enhanced listening indicator with particles */}
      {isListening && (
        <>
          <mesh position={[0, 0.3, 0]}>
            <ringGeometry args={[0.18, 0.22, 16]} />
            <meshBasicMaterial color="#00ff88" transparent opacity={0.8} />
          </mesh>
          <mesh position={[0, 0.3, 0]}>
            <ringGeometry args={[0.25, 0.28, 16]} />
            <meshBasicMaterial color="#00ffaa" transparent opacity={0.4} />
          </mesh>
          <Sparkles 
            count={20} 
            scale={[0.8, 0.8, 0.8]} 
            size={3} 
            speed={0.8} 
            color="#00ff88"
            position={[0, 0.3, 0]}
          />
        </>
      )}
    </group>
  );
}

// Enhanced water with better visual effects
function Water() {
  const waterRef = useRef<THREE.Mesh>(null);
  
  useFrame(({ clock }) => {
    if (waterRef.current) {
      waterRef.current.rotation.y = clock.elapsedTime * 0.05;
      waterRef.current.position.y = -0.5 + Math.sin(clock.elapsedTime * 0.5) * 0.02;
    }
  });

  return (
    <mesh ref={waterRef} position={[0, -0.5, 0]} receiveShadow>
      <sphereGeometry args={[1.85, 64, 64, 0, Math.PI * 2, 0, Math.PI * 0.6]} />
      <meshPhysicalMaterial 
        color="#2196F3" 
        transparent 
        opacity={0.3}
        roughness={0}
        metalness={0.1}
        transmission={0.6}
        thickness={1}
        clearcoat={1}
        clearcoatRoughness={0}
      />
    </mesh>
  );
}

// Enhanced decorations with more variety
function Decorations() {
  return (
    <group>
      {/* More realistic gravel with variety */}
      {Array.from({ length: 25 }).map((_, i) => (
        <mesh 
          key={i} 
          position={[
            (Math.random() - 0.5) * 1.5,
            -1.9 + Math.random() * 0.1,
            (Math.random() - 0.5) * 1.5
          ]}
          castShadow
          receiveShadow
        >
          <sphereGeometry args={[0.03 + Math.random() * 0.06, 8, 8]} />
          <meshPhysicalMaterial 
            color={`hsl(${25 + Math.random() * 80}, ${40 + Math.random() * 30}%, ${25 + Math.random() * 35}%)`}
            roughness={0.8}
            metalness={0.1}
          />
        </mesh>
      ))}
      
      {/* Enhanced seaweed with swaying animation */}
      <group position={[-1.2, -1, 0.8]}>
        <Float speed={1} floatIntensity={0.5}>
          <Cylinder args={[0.025, 0.025, 1.8]} position={[0, 0.9, 0]} castShadow>
            <meshPhysicalMaterial color="#2d5a27" roughness={0.6} />
          </Cylinder>
        </Float>
        <Float speed={1.2} floatIntensity={0.4}>
          <Cylinder args={[0.02, 0.02, 1.4]} position={[0.15, 0.7, 0]} castShadow>
            <meshPhysicalMaterial color="#3d6a37" roughness={0.6} />
          </Cylinder>
        </Float>
        <Float speed={0.8} floatIntensity={0.6}>
          <Cylinder args={[0.03, 0.03, 1.6]} position={[-0.1, 0.8, 0.1]} castShadow>
            <meshPhysicalMaterial color="#1d4a17" roughness={0.6} />
          </Cylinder>
        </Float>
      </group>
      
      {/* Enhanced castle with more details */}
      <group position={[1, -1.5, -0.5]}>
        <Box args={[0.35, 0.6, 0.35]} castShadow receiveShadow>
          <meshPhysicalMaterial color="#8B4513" roughness={0.8} metalness={0.1} />
        </Box>
        <Cylinder args={[0.1, 0.1, 0.4]} position={[-0.15, 0.5, -0.15]} castShadow>
          <meshPhysicalMaterial color="#A0522D" roughness={0.8} />
        </Cylinder>
        <Cylinder args={[0.1, 0.1, 0.4]} position={[0.15, 0.5, -0.15]} castShadow>
          <meshPhysicalMaterial color="#A0522D" roughness={0.8} />
        </Cylinder>
        <Cylinder args={[0.1, 0.1, 0.4]} position={[-0.15, 0.5, 0.15]} castShadow>
          <meshPhysicalMaterial color="#A0522D" roughness={0.8} />
        </Cylinder>
        <Cylinder args={[0.1, 0.1, 0.4]} position={[0.15, 0.5, 0.15]} castShadow>
          <meshPhysicalMaterial color="#A0522D" roughness={0.8} />
        </Cylinder>
        
        {/* Castle flags */}
        <mesh position={[-0.15, 0.8, -0.15]}>
          <boxGeometry args={[0.08, 0.05, 0.01]} />
          <meshPhysicalMaterial color="#ff0000" />
        </mesh>
        <mesh position={[0.15, 0.8, 0.15]}>
          <boxGeometry args={[0.08, 0.05, 0.01]} />
          <meshPhysicalMaterial color="#0000ff" />
        </mesh>
      </group>

      {/* Coral decoration */}
      <group position={[-0.8, -1.6, -1.1]}>
        <Sphere args={[0.08, 8, 8]} castShadow>
          <meshPhysicalMaterial color="#ff6b9d" roughness={0.6} />
        </Sphere>
        <Cylinder args={[0.03, 0.08, 0.3]} position={[0, 0.15, 0]} castShadow>
          <meshPhysicalMaterial color="#ff8fab" roughness={0.6} />
        </Cylinder>
        <Sphere args={[0.04, 6, 6]} position={[0.15, 0.1, 0]} castShadow>
          <meshPhysicalMaterial color="#ffadc6" roughness={0.6} />
        </Sphere>
      </group>
    </group>
  );
}

// Enhanced glass bowl with better materials and more stylized look
function GlassBowl() {
  const bowlRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (bowlRef.current) {
      bowlRef.current.rotation.y = clock.elapsedTime * 0.02;
    }
  });

  return (
    <group ref={bowlRef}>
      {/* Main bowl body */}
      <mesh receiveShadow>
        <sphereGeometry 
          args={[2.1, 64, 64, 0, Math.PI * 2, 0, Math.PI * 0.75]} 
        />
        <meshPhysicalMaterial 
          color="#ffffff"
          metalness={0}
          roughness={0}
          transmission={0.92}
          transparent={true}
          opacity={0.2}
          thickness={0.5}
          clearcoat={1}
          clearcoatRoughness={0}
          ior={1.45}
          envMapIntensity={1.5}
        />
      </mesh>

      {/* Bowl base */}
      <mesh position={[0, -2.1, 0]} rotation={[Math.PI, 0, 0]}>
        <cylinderGeometry args={[0.8, 1.2, 0.3, 32]} />
        <meshPhysicalMaterial 
          color="#ffffff"
          metalness={0.1}
          roughness={0.1}
          transmission={0.8}
          transparent={true}
          opacity={0.4}
          thickness={1}
          clearcoat={1}
          clearcoatRoughness={0}
          ior={1.45}
        />
      </mesh>
    </group>
  );
}

// Enhanced bubble system with more variety
function Bubbles() {
  const bubblesRef = useRef<THREE.Group>(null);
  
  useFrame(({ clock }) => {
    if (bubblesRef.current) {
      bubblesRef.current.children.forEach((bubble, i) => {
        const speed = 0.008 + (i % 3) * 0.003;
        bubble.position.y += speed;
        bubble.position.x += Math.sin(clock.elapsedTime + i) * 0.001;
        
        if (bubble.position.y > 2.2) {
          bubble.position.y = -2;
          bubble.position.x = (Math.random() - 0.5) * 3.5;
          bubble.position.z = (Math.random() - 0.5) * 3.5;
        }
        
        // Rotate bubbles for more realism
        bubble.rotation.x = clock.elapsedTime * (0.5 + i * 0.1);
        bubble.rotation.y = clock.elapsedTime * (0.3 + i * 0.08);
      });
    }
  });

  return (
    <group ref={bubblesRef}>
      {Array.from({ length: 35 }).map((_, i) => (
        <mesh 
          key={i}
          position={[
            (Math.random() - 0.5) * 3.5,
            -2 + Math.random() * 4.2,
            (Math.random() - 0.5) * 3.5
          ]}
        >
          <sphereGeometry args={[0.015 + Math.random() * 0.025, 8, 8]} />
          <meshPhysicalMaterial 
            color="white" 
            transparent 
            opacity={0.6} 
            roughness={0}
            metalness={0}
            transmission={0.9}
            thickness={0.1}
          />
        </mesh>
      ))}
    </group>
  );
}

// Main enhanced scene component
export default function GoldfishBowlScene({ 
  isSpeaking, 
  isListening 
}: { 
  isSpeaking: boolean; 
  isListening: boolean; 
}) {
  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <Canvas
        camera={{ 
          position: [5, 3, 6], 
          fov: 40,
          near: 0.1,
          far: 100
        }}
        shadows
        gl={{ antialias: true, alpha: true }}
      >
        {/* Enhanced lighting setup */}
        <ambientLight intensity={0.4} color="#4a90e2" />
        
        {/* Main directional light */}
        <directionalLight 
          position={[8, 8, 5]} 
          intensity={1.4}
          color="#ffffff"
          castShadow
          shadow-mapSize-width={4096}
          shadow-mapSize-height={4096}
          shadow-camera-far={50}
          shadow-camera-near={1}
          shadow-camera-top={10}
          shadow-camera-bottom={-10}
          shadow-camera-left={-10}
          shadow-camera-right={10}
        />
        
        {/* Accent lights for atmosphere */}
        <pointLight position={[3, 2, 4]} intensity={0.9} color="#88ccff" castShadow />
        <pointLight position={[-3, 2, -2]} intensity={0.7} color="#ffaa88" />
        <pointLight position={[0, 4, 0]} intensity={0.5} color="#ffffff" />
        
        {/* Underwater effect light */}
        <spotLight
          position={[0, 6, 0]}
          angle={Math.PI / 3}
          penumbra={0.5}
          intensity={0.6}
          color="#4a90e2"
          castShadow
        />
        
        {/* Environment for reflections */}
        <Environment preset="apartment" />
        
        {/* Scene components */}
        <GlassBowl />
        <Water />
        <Goldfish 
          position={[0, 0, 0]} 
          isSpeaking={isSpeaking} 
          isListening={isListening} 
        />
        <Decorations />
        <Bubbles />
        
        {/* Atmospheric particles */}
        <Sparkles 
          count={50} 
          scale={[8, 8, 8]} 
          size={1} 
          speed={0.2} 
          color="#ffffff"
          opacity={0.3}
        />
        
                 {/* Enhanced controls */}
         <OrbitControls 
           enablePan={false}
           enableZoom={true}
           maxDistance={10}
           minDistance={4}
           maxPolarAngle={Math.PI / 1.6}
           minPolarAngle={Math.PI / 8}
           autoRotate={false}
           autoRotateSpeed={0.5}
           target={[0, 0, 0]}
         />
      </Canvas>
    </div>
  );
} 