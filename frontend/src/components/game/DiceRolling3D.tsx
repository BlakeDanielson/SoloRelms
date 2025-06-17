'use client';

import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Box, Text, OrbitControls } from '@react-three/drei';
import { Mesh, Vector3 } from 'three';
import { motion, AnimatePresence } from 'framer-motion';
import { Dices, RotateCcw } from 'lucide-react';

interface DiceRolling3DProps {
  diceRoll: DiceRoll | null;
  onRollComplete?: (result: number) => void;
  className?: string;
}

interface DiceRoll {
  id: string;
  type: 'd4' | 'd6' | 'd8' | 'd10' | 'd12' | 'd20' | 'd100';
  count: number;
  modifier?: number;
  advantage?: boolean;
  disadvantage?: boolean;
  result?: number;
  isRolling: boolean;
  purpose?: string; // "attack", "damage", "saving throw", "initiative", etc.
}

interface Die3DProps {
  type: DiceRoll['type'];
  position: [number, number, number];
  result?: number;
  isRolling: boolean;
  onComplete?: () => void;
  rollId: string;
}

// Individual 3D die component
function Die3D({ type, position, result, isRolling, onComplete, rollId }: Die3DProps) {
  const meshRef = useRef<Mesh>(null);
  const [currentRotation, setCurrentRotation] = useState({ x: 0, y: 0, z: 0 });
  const [rollComplete, setRollComplete] = useState(false);
  const [finalRotation, setFinalRotation] = useState({ x: 0, y: 0, z: 0 });

  // Calculate final rotation based on result
  useEffect(() => {
    if (result && !rollComplete) {
      const targetRotation = getDieFaceRotation(type, result);
      setFinalRotation(targetRotation);
    }
  }, [result, type, rollComplete]);

  // Animation loop
  useFrame((state, delta) => {
    if (!meshRef.current) return;

    if (isRolling && !rollComplete) {
      // Tumbling animation while rolling
      setCurrentRotation(prev => ({
        x: prev.x + delta * 15 + Math.sin(state.clock.elapsedTime * 10) * 0.1,
        y: prev.y + delta * 12 + Math.cos(state.clock.elapsedTime * 8) * 0.1,
        z: prev.z + delta * 18 + Math.sin(state.clock.elapsedTime * 6) * 0.1
      }));

      meshRef.current.rotation.set(currentRotation.x, currentRotation.y, currentRotation.z);

      // Simulate physics: bouncing and slowing down
      const rollDuration = 2000; // 2 seconds
      const elapsed = (Date.now() % rollDuration) / rollDuration;
      
      if (elapsed > 0.8 && result) {
        // Start settling to final position
        setRollComplete(true);
        setTimeout(() => {
          onComplete?.();
        }, 500);
      }
    } else if (rollComplete && result) {
      // Smooth transition to final rotation
      const speed = 5;
      meshRef.current.rotation.x += (finalRotation.x - meshRef.current.rotation.x) * delta * speed;
      meshRef.current.rotation.y += (finalRotation.y - meshRef.current.rotation.y) * delta * speed;
      meshRef.current.rotation.z += (finalRotation.z - meshRef.current.rotation.z) * delta * speed;
    }

    // Add subtle floating animation when idle
    if (!isRolling) {
      meshRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime * 2) * 0.05;
    } else {
      meshRef.current.position.y = position[1];
    }
  });

  // Get die geometry based on type
  const getDieGeometry = (dieType: DiceRoll['type']) => {
    switch (dieType) {
      case 'd4': return [0.8, 0.8, 0.8]; // Smaller for tetrahedron
      case 'd6': return [1, 1, 1];
      case 'd8': return [1, 1, 1]; // Will be octahedron in real implementation
      case 'd10': return [1, 1.2, 1];
      case 'd12': return [1.1, 1.1, 1.1];
      case 'd20': return [1.2, 1.2, 1.2];
      case 'd100': return [1, 1.2, 1]; // Percentile die
      default: return [1, 1, 1];
    }
  };

  // Get die color based on type
  const getDieColor = (dieType: DiceRoll['type']) => {
    switch (dieType) {
      case 'd4': return '#ff6b6b'; // Red
      case 'd6': return '#4ecdc4'; // Teal
      case 'd8': return '#45b7d1'; // Blue
      case 'd10': return '#96ceb4'; // Green
      case 'd12': return '#feca57'; // Yellow
      case 'd20': return '#ff9ff3'; // Pink
      case 'd100': return '#a55eea'; // Purple
      default: return '#ffffff';
    }
  };

  const dieSize = getDieGeometry(type);
  const dieColor = getDieColor(type);

  return (
    <group position={position}>
      <Box ref={meshRef} args={dieSize}>
        <meshPhongMaterial color={dieColor} shininess={100} />
      </Box>
      
      {/* Die faces with numbers */}
      {result && rollComplete && (
        <Text
          position={[0, 0, dieSize[2] / 2 + 0.1]}
          fontSize={0.3}
          color="white"
          anchorX="center"
          anchorY="middle"
          font="/fonts/inter-bold.woff"
        >
          {result}
        </Text>
      )}
    </group>
  );
}

// Helper function to get die face rotation for specific result
function getDieFaceRotation(type: DiceRoll['type'], result: number) {
  // Simplified rotation mapping - in a real implementation, this would be more precise
  const baseRotations = {
    1: { x: 0, y: 0, z: 0 },
    2: { x: Math.PI / 2, y: 0, z: 0 },
    3: { x: 0, y: Math.PI / 2, z: 0 },
    4: { x: 0, y: -Math.PI / 2, z: 0 },
    5: { x: -Math.PI / 2, y: 0, z: 0 },
    6: { x: Math.PI, y: 0, z: 0 },
  };

  // For dice with more faces, use modulo to map to available rotations
  const faceIndex = ((result - 1) % 6) + 1;
  return baseRotations[faceIndex as keyof typeof baseRotations] || { x: 0, y: 0, z: 0 };
}

export default function DiceRolling3D({
  diceRoll,
  onRollComplete,
  className = ''
}: DiceRolling3DProps) {
  const [diceResults, setDiceResults] = useState<number[]>([]);
  const [completedDice, setCompletedDice] = useState<boolean[]>([]);

  // Reset when new roll starts
  useEffect(() => {
    if (diceRoll?.isRolling) {
      setDiceResults([]);
      setCompletedDice(new Array(diceRoll.count).fill(false));
      
      // Simulate dice results after a delay
      setTimeout(() => {
        const results = [];
        for (let i = 0; i < diceRoll.count; i++) {
          const maxValue = parseInt(diceRoll.type.substring(1));
          results.push(Math.floor(Math.random() * maxValue) + 1);
        }
        setDiceResults(results);
      }, 100);
    }
  }, [diceRoll?.id, diceRoll?.isRolling]);

  // Handle individual die completion
  const handleDieComplete = (index: number) => {
    setCompletedDice(prev => {
      const updated = [...prev];
      updated[index] = true;
      
      // Check if all dice are complete
      if (updated.every(Boolean) && diceResults.length > 0) {
        const totalResult = diceResults.reduce((sum, result) => sum + result, 0) + (diceRoll?.modifier || 0);
        setTimeout(() => {
          onRollComplete?.(totalResult);
        }, 500);
      }
      
      return updated;
    });
  };

  // Get dice positions in 3D space
  const getDicePositions = (count: number): [number, number, number][] => {
    const positions: [number, number, number][] = [];
    const spacing = 2.5;
    const startX = -(count - 1) * spacing / 2;
    
    for (let i = 0; i < count; i++) {
      positions.push([startX + i * spacing, 0, 0]);
    }
    
    return positions;
  };

  if (!diceRoll) {
    return null;
  }

  const dicePositions = getDicePositions(diceRoll.count);
  const totalResult = diceResults.reduce((sum, result) => sum + result, 0) + (diceRoll.modifier || 0);
  const allDiceComplete = completedDice.every(Boolean) && diceResults.length > 0;

  return (
    <div className={`fixed inset-0 pointer-events-none z-40 ${className}`}>
      <AnimatePresence>
        {diceRoll.isRolling && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center"
          >
            <div className="bg-gray-900/90 backdrop-blur-sm rounded-2xl border border-white/20 p-8 max-w-4xl w-full mx-4">
              {/* Header */}
              <div className="text-center mb-6">
                <div className="flex items-center justify-center mb-2">
                  <Dices className="w-6 h-6 text-blue-400 mr-2" />
                  <h3 className="text-xl font-bold text-white">
                    Rolling {diceRoll.count}{diceRoll.type}
                    {diceRoll.modifier ? ` + ${diceRoll.modifier}` : ''}
                  </h3>
                </div>
                {diceRoll.purpose && (
                  <p className="text-gray-400 text-sm capitalize">
                    {diceRoll.purpose} roll
                  </p>
                )}
                {diceRoll.advantage && (
                  <p className="text-green-400 text-sm">With Advantage</p>
                )}
                {diceRoll.disadvantage && (
                  <p className="text-red-400 text-sm">With Disadvantage</p>
                )}
              </div>

              {/* 3D Canvas */}
              <div className="h-64 mb-6 bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl border border-gray-700 overflow-hidden">
                <Canvas
                  camera={{ position: [0, 5, 8], fov: 50 }}
                  gl={{ antialias: true }}
                >
                  <ambientLight intensity={0.6} />
                  <pointLight position={[10, 10, 10]} intensity={1} />
                  <pointLight position={[-10, -10, -10]} intensity={0.5} />
                  
                  {/* Dice */}
                  {dicePositions.map((position, index) => (
                    <Die3D
                      key={`${diceRoll.id}-${index}`}
                      type={diceRoll.type}
                      position={position}
                      result={diceResults[index]}
                      isRolling={diceRoll.isRolling && !completedDice[index]}
                      onComplete={() => handleDieComplete(index)}
                      rollId={diceRoll.id}
                    />
                  ))}
                  
                  <OrbitControls enableZoom={false} enablePan={false} />
                </Canvas>
              </div>

              {/* Results Display */}
              <div className="text-center">
                {diceResults.length > 0 && (
                  <div className="mb-4">
                    <div className="text-gray-300 text-sm mb-2">Individual Results:</div>
                    <div className="flex justify-center space-x-2 mb-4">
                      {diceResults.map((result, index) => (
                        <motion.div
                          key={index}
                          initial={{ scale: 0, opacity: 0 }}
                          animate={{ 
                            scale: completedDice[index] ? 1 : 0.8, 
                            opacity: completedDice[index] ? 1 : 0.6 
                          }}
                          className={`w-8 h-8 rounded border-2 flex items-center justify-center text-sm font-bold ${
                            completedDice[index] 
                              ? 'border-blue-400 text-blue-400 bg-blue-400/20' 
                              : 'border-gray-600 text-gray-400'
                          }`}
                        >
                          {result}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {allDiceComplete && (
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="text-center"
                  >
                    <div className="text-3xl font-bold text-white mb-2">
                      Total: {totalResult}
                    </div>
                    {diceRoll.modifier && (
                      <div className="text-sm text-gray-400">
                        ({diceResults.join(' + ')}{diceRoll.modifier > 0 ? ' + ' + diceRoll.modifier : ' - ' + Math.abs(diceRoll.modifier)})
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Loading indicator */}
                {diceRoll.isRolling && !allDiceComplete && (
                  <div className="flex items-center justify-center text-gray-400">
                    <RotateCcw className="w-4 h-4 mr-2 animate-spin" />
                    Rolling dice...
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Helper function to create dice roll objects
export const createDiceRoll = (
  type: DiceRoll['type'],
  count: number = 1,
  modifier: number = 0,
  purpose?: string,
  advantage?: boolean,
  disadvantage?: boolean
): DiceRoll => ({
  id: `roll-${Date.now()}-${Math.random()}`,
  type,
  count,
  modifier,
  advantage,
  disadvantage,
  isRolling: true,
  purpose
}); 