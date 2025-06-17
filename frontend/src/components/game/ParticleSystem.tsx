'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSpring, animated, useTrail } from '@react-spring/web';
import { 
  Sparkles, 
  Heart, 
  Shield, 
  Zap, 
  Flame, 
  Snowflake,
  Droplets,
  Star,
  Plus
} from 'lucide-react';
import { DamageType, CombatAction, CombatActionResult } from '../../lib/combat/types';

interface ParticleSystemProps {
  effect: ParticleEffect | null;
  onEffectComplete?: () => void;
  className?: string;
}

interface ParticleEffect {
  id: string;
  type: ParticleEffectType;
  position: { x: number; y: number };
  action?: CombatAction;
  result?: CombatActionResult;
  intensity?: 'low' | 'medium' | 'high';
  duration?: number;
  isVisible: boolean;
}

type ParticleEffectType = 
  | 'explosion' 
  | 'healing' 
  | 'buff' 
  | 'debuff' 
  | 'critical' 
  | 'miss' 
  | 'elemental' 
  | 'death' 
  | 'levelup'
  | 'shield'
  | 'dodge';

interface Particle {
  id: number;
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  size: number;
  color: string;
  opacity: number;
  rotation: number;
  rotationSpeed: number;
}

// Generate particles based on effect type
const generateParticles = (
  type: ParticleEffectType, 
  position: { x: number; y: number },
  intensity: 'low' | 'medium' | 'high' = 'medium',
  action?: CombatAction
): Particle[] => {
  const particleCount = {
    low: { min: 8, max: 15 },
    medium: { min: 15, max: 25 },
    high: { min: 25, max: 40 }
  }[intensity];

  const count = Math.floor(Math.random() * (particleCount.max - particleCount.min) + particleCount.min);
  const particles: Particle[] = [];

  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
    const speed = getParticleSpeed(type, intensity);
    const life = getParticleLife(type);
    
    particles.push({
      id: i,
      x: position.x,
      y: position.y,
      vx: Math.cos(angle) * speed * (0.5 + Math.random() * 0.5),
      vy: Math.sin(angle) * speed * (0.5 + Math.random() * 0.5),
      life: life,
      maxLife: life,
      size: getParticleSize(type, intensity),
      color: getParticleColor(type, action),
      opacity: 1,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 10
    });
  }

  return particles;
};

const getParticleSpeed = (type: ParticleEffectType, intensity: 'low' | 'medium' | 'high'): number => {
  const baseSpeed = {
    explosion: 8,
    healing: 3,
    buff: 2,
    debuff: 2,
    critical: 12,
    miss: 4,
    elemental: 6,
    death: 1,
    levelup: 5,
    shield: 4,
    dodge: 6
  }[type];

  const multiplier = {
    low: 0.7,
    medium: 1.0,
    high: 1.5
  }[intensity];

  return baseSpeed * multiplier;
};

const getParticleLife = (type: ParticleEffectType): number => {
  return {
    explosion: 60,
    healing: 90,
    buff: 120,
    debuff: 100,
    critical: 80,
    miss: 45,
    elemental: 75,
    death: 150,
    levelup: 120,
    shield: 80,
    dodge: 60
  }[type];
};

const getParticleSize = (type: ParticleEffectType, intensity: 'low' | 'medium' | 'high'): number => {
  const baseSize = {
    explosion: 4,
    healing: 3,
    buff: 2,
    debuff: 2,
    critical: 6,
    miss: 2,
    elemental: 4,
    death: 3,
    levelup: 5,
    shield: 3,
    dodge: 2
  }[type];

  const multiplier = {
    low: 0.8,
    medium: 1.0,
    high: 1.3
  }[intensity];

  return baseSize * multiplier;
};

const getParticleColor = (type: ParticleEffectType, action?: CombatAction): string => {
  if (type === 'elemental' && action?.damage?.type) {
    switch (action.damage.type) {
      case 'fire': return '#fb923c';
      case 'cold': return '#93c5fd';
      case 'lightning': return '#c084fc';
      case 'acid': return '#84cc16';
      case 'poison': return '#a3e635';
      case 'psychic': return '#f472b6';
      case 'necrotic': return '#6b7280';
      case 'radiant': return '#fbbf24';
      case 'force': return '#818cf8';
      case 'thunder': return '#9ca3af';
      default: return '#6366f1';
    }
  }

  return {
    explosion: '#f87171',
    healing: '#34d399',
    buff: '#60a5fa',
    debuff: '#f87171',
    critical: '#fbbf24',
    miss: '#9ca3af',
    elemental: '#6366f1',
    death: '#374151',
    levelup: '#fbbf24',
    shield: '#60a5fa',
    dodge: '#34d399'
  }[type];
};

// Get effect icon based on type
const getEffectIcon = (type: ParticleEffectType, action?: CombatAction) => {
  if (type === 'elemental' && action?.damage?.type) {
    switch (action.damage.type) {
      case 'fire': return <Flame className="w-8 h-8 text-orange-400" />;
      case 'cold': return <Snowflake className="w-8 h-8 text-blue-300" />;
      case 'lightning': return <Zap className="w-8 h-8 text-purple-400" />;
      default: return <Sparkles className="w-8 h-8 text-indigo-400" />;
    }
  }

  switch (type) {
    case 'explosion': return <Zap className="w-8 h-8 text-red-400" />;
    case 'healing': return <Heart className="w-8 h-8 text-green-400" />;
    case 'buff': return <Plus className="w-8 h-8 text-blue-400" />;
    case 'debuff': return <Droplets className="w-8 h-8 text-red-400" />;
    case 'critical': return <Star className="w-8 h-8 text-yellow-400" />;
    case 'miss': return <span className="text-2xl text-gray-400">✗</span>;
    case 'shield': return <Shield className="w-8 h-8 text-blue-400" />;
    case 'dodge': return <span className="text-2xl text-green-400">◗</span>;
    case 'death': return <span className="text-2xl text-gray-600">💀</span>;
    case 'levelup': return <Star className="w-8 h-8 text-yellow-400" />;
    default: return <Sparkles className="w-8 h-8 text-gray-400" />;
  }
};

export default function ParticleSystem({
  effect,
  onEffectComplete,
  className = ''
}: ParticleSystemProps) {
  const [particles, setParticles] = useState<Particle[]>([]);
  const [showCenterIcon, setShowCenterIcon] = useState(false);

  // Initialize particles when effect becomes visible
  useEffect(() => {
    if (effect?.isVisible) {
      const newParticles = generateParticles(
        effect.type,
        effect.position,
        effect.intensity || 'medium',
        effect.action
      );
      setParticles(newParticles);
      setShowCenterIcon(true);

      // Hide center icon after initial burst
      setTimeout(() => setShowCenterIcon(false), 800);
    }
  }, [effect?.isVisible, effect?.id]);

  // Animate particles
  useEffect(() => {
    if (!effect?.isVisible || particles.length === 0) return;

    const interval = setInterval(() => {
      setParticles(prevParticles => {
        const updatedParticles = prevParticles.map(particle => ({
          ...particle,
          x: particle.x + particle.vx,
          y: particle.y + particle.vy,
          vx: particle.vx * 0.98, // Air resistance
          vy: (particle.vy + 0.2) * 0.98, // Gravity + air resistance
          life: particle.life - 1,
          opacity: particle.life / particle.maxLife,
          rotation: particle.rotation + particle.rotationSpeed,
        })).filter(particle => particle.life > 0);

        // Clean up when all particles are gone
        if (updatedParticles.length === 0) {
          setTimeout(() => {
            onEffectComplete?.();
          }, 100);
        }

        return updatedParticles;
      });
    }, 16); // ~60fps

    return () => clearInterval(interval);
  }, [effect?.isVisible, particles.length, onEffectComplete]);

  // Trail animation for particle burst
  const trail = useTrail(particles.length, {
    opacity: effect?.isVisible ? 1 : 0,
    scale: effect?.isVisible ? 1 : 0,
    config: { mass: 1, tension: 280, friction: 60 }
  });

  // Center icon spring animation
  const centerIconSpring = useSpring({
    transform: showCenterIcon ? 'scale(1) rotate(360deg)' : 'scale(0) rotate(0deg)',
    opacity: showCenterIcon ? 0.8 : 0,
    config: { mass: 1, tension: 300, friction: 25 }
  });

  if (!effect || !effect.isVisible) {
    return null;
  }

  const centerIcon = getEffectIcon(effect.type, effect.action);

  return (
    <div className={`fixed inset-0 pointer-events-none z-30 ${className}`}>
      {/* Center icon */}
      <AnimatePresence>
        {showCenterIcon && (
          <animated.div
            style={{
              position: 'absolute',
              left: effect.position.x,
              top: effect.position.y,
              transform: centerIconSpring.transform.to(t => `translate(-50%, -50%) ${t}`),
              opacity: centerIconSpring.opacity,
            }}
            className="flex items-center justify-center"
          >
            <div className="p-3 rounded-full bg-black/20 backdrop-blur-sm border border-white/20">
              {centerIcon}
            </div>
          </animated.div>
        )}
      </AnimatePresence>

      {/* Particles */}
      {particles.map((particle, index) => (
        <motion.div
          key={particle.id}
          style={{
            position: 'absolute',
            left: particle.x,
            top: particle.y,
            width: particle.size,
            height: particle.size,
            backgroundColor: particle.color,
            opacity: particle.opacity,
            transform: `translate(-50%, -50%) rotate(${particle.rotation}deg)`,
            borderRadius: effect.type === 'healing' || effect.type === 'buff' ? '50%' : 
                          effect.type === 'critical' || effect.type === 'levelup' ? '20%' : '2px',
            boxShadow: `0 0 ${particle.size * 2}px ${particle.color}`,
          }}
          animate={{
            scale: [1, 0.8, 0.6],
            opacity: [particle.opacity, particle.opacity * 0.7, 0],
          }}
          transition={{
            duration: particle.life / 60,
            ease: "easeOut"
          }}
        />
      ))}

      {/* Special effects overlay */}
      {effect.type === 'critical' && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: [0, 2, 3], opacity: [0, 0.8, 0] }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          style={{
            position: 'absolute',
            left: effect.position.x,
            top: effect.position.y,
            transform: 'translate(-50%, -50%)',
          }}
          className="w-32 h-32 rounded-full border-4 border-yellow-400"
        />
      )}

      {effect.type === 'explosion' && (
        <motion.div
          initial={{ scale: 0, opacity: 0.8 }}
          animate={{ scale: [0, 1.5, 2.5], opacity: [0.8, 0.4, 0] }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{
            position: 'absolute',
            left: effect.position.x,
            top: effect.position.y,
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(circle, #f87171 0%, #dc2626 50%, transparent 70%)',
          }}
          className="w-24 h-24 rounded-full"
        />
      )}

      {effect.type === 'healing' && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: [0, 1, 1.2], opacity: [0, 0.6, 0] }}
          transition={{ duration: 2, ease: "easeInOut" }}
          style={{
            position: 'absolute',
            left: effect.position.x,
            top: effect.position.y,
            transform: 'translate(-50%, -50%)',
            background: 'radial-gradient(circle, #34d399 0%, #10b981 40%, transparent 70%)',
          }}
          className="w-20 h-20 rounded-full"
        />
      )}

      {effect.type === 'shield' && (
        <motion.div
          initial={{ scale: 0, opacity: 0, rotate: 0 }}
          animate={{ 
            scale: [0, 1.2, 1], 
            opacity: [0, 0.8, 0.4], 
            rotate: [0, 180, 360] 
          }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{
            position: 'absolute',
            left: effect.position.x,
            top: effect.position.y,
            transform: 'translate(-50%, -50%)',
          }}
          className="w-16 h-16 border-4 border-blue-400 rounded-lg"
        />
      )}
    </div>
  );
}

// Helper function to create particle effects for common combat scenarios
export const createParticleEffect = (
  type: ParticleEffectType,
  position: { x: number; y: number },
  action?: CombatAction,
  result?: CombatActionResult,
  intensity: 'low' | 'medium' | 'high' = 'medium'
): ParticleEffect => ({
  id: `particle-${Date.now()}-${Math.random()}`,
  type,
  position,
  action,
  result,
  intensity,
  isVisible: true
}); 