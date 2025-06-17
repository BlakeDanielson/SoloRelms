'use client';

import React, { useEffect, useState } from 'react';
import { useSpring, animated, useTrail, useChain, useSpringRef } from '@react-spring/web';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, 
  Flame, 
  Snowflake, 
  Wind, 
  Sparkles, 
  Target,
  ArrowRight
} from 'lucide-react';
import { CombatAction, CombatActionResult, DamageType } from '../../lib/combat/types';

interface ProjectileEffectsProps {
  projectile: ProjectileData | null;
  onProjectileComplete?: () => void;
  className?: string;
}

interface ProjectileData {
  id: string;
  action: CombatAction;
  result?: CombatActionResult;
  startPosition: { x: number; y: number };
  endPosition: { x: number; y: number };
  isVisible: boolean;
}

interface ParticleTrailProps {
  count: number;
  damageType: DamageType;
  isActive: boolean;
}

// Particle trail component for different damage types
const ParticleTrail: React.FC<ParticleTrailProps> = ({ count, damageType, isActive }) => {
  const particles = Array.from({ length: count }, (_, i) => i);
  
  const trail = useTrail(particles.length, {
    opacity: isActive ? 1 : 0,
    scale: isActive ? 1 : 0.3,
    transform: isActive ? 'rotate(0deg)' : 'rotate(180deg)',
    config: { mass: 1, tension: 280, friction: 60 },
  });

  const getParticleColor = (type: DamageType) => {
    switch (type) {
      case 'fire': return 'bg-orange-400';
      case 'cold': return 'bg-blue-300';
      case 'lightning': return 'bg-purple-400';
      case 'acid': return 'bg-green-400';
      case 'poison': return 'bg-lime-400';
      case 'psychic': return 'bg-pink-400';
      case 'necrotic': return 'bg-gray-800';
      case 'radiant': return 'bg-yellow-200';
      case 'force': return 'bg-indigo-400';
      case 'thunder': return 'bg-gray-400';
      default: return 'bg-gray-500';
    }
  };

  const particleColor = getParticleColor(damageType);

  return (
    <>
      {trail.map((style, index) => (
        <animated.div
          key={index}
          style={{
            ...style,
            transitionDelay: `${index * 50}ms`
          }}
          className={`absolute w-2 h-2 rounded-full ${particleColor} opacity-70`}
        />
      ))}
    </>
  );
};

// Get projectile icon based on action type and damage
const getProjectileIcon = (action: CombatAction) => {
  if (action.category === 'attack') {
    return <ArrowRight className="w-6 h-6 text-gray-300" />;
  }
  
  if (action.category === 'spell' && action.damage?.type) {
    switch (action.damage.type) {
      case 'fire':
        return <Flame className="w-6 h-6 text-orange-400" />;
      case 'cold':
        return <Snowflake className="w-6 h-6 text-blue-300" />;
      case 'lightning':
        return <Zap className="w-6 h-6 text-purple-400" />;
      case 'force':
        return <Wind className="w-6 h-6 text-indigo-400" />;
      default:
        return <Sparkles className="w-6 h-6 text-indigo-400" />;
    }
  }
  
  return <Target className="w-6 h-6 text-gray-400" />;
};

// Get projectile properties based on action
const getProjectileProperties = (action: CombatAction) => {
  const baseConfig = {
    mass: 1,
    tension: 300,
    friction: 30,
    duration: 1000
  };

  switch (action.category) {
    case 'attack':
      return {
        ...baseConfig,
        tension: 400,
        friction: 20,
        duration: 800,
        trail: { enabled: false }
      };
    
    case 'spell':
      if (action.damage?.type === 'lightning') {
        return {
          ...baseConfig,
          tension: 800,
          friction: 10,
          duration: 300,
          trail: { enabled: true, count: 8 }
        };
      }
      if (action.damage?.type === 'fire') {
        return {
          ...baseConfig,
          tension: 200,
          friction: 40,
          duration: 1200,
          trail: { enabled: true, count: 12 }
        };
      }
      if (action.damage?.type === 'cold') {
        return {
          ...baseConfig,
          tension: 150,
          friction: 60,
          duration: 1500,
          trail: { enabled: true, count: 6 }
        };
      }
      return {
        ...baseConfig,
        trail: { enabled: true, count: 6 }
      };
    
    default:
      return {
        ...baseConfig,
        trail: { enabled: false }
      };
  }
};

export default function ProjectileEffects({
  projectile,
  onProjectileComplete,
  className = ''
}: ProjectileEffectsProps) {
  const [isAnimating, setIsAnimating] = useState(false);
  const [showImpact, setShowImpact] = useState(false);

  // Animation refs for chaining
  const projectileRef = useSpringRef();
  const impactRef = useSpringRef();

  useEffect(() => {
    if (projectile?.isVisible && !isAnimating) {
      setIsAnimating(true);
      setShowImpact(false);
    }
  }, [projectile?.isVisible, isAnimating]);

  const properties = projectile ? getProjectileProperties(projectile.action) : null;

  // Main projectile animation
  const projectileSpring = useSpring({
    ref: projectileRef,
    from: { 
      x: projectile?.startPosition.x || 0, 
      y: projectile?.startPosition.y || 0,
      scale: 0.5,
      opacity: 0,
      rotate: 0
    },
    to: async (next) => {
      if (!projectile || !properties) return;
      
      // Fade in
      await next({ 
        scale: 1, 
        opacity: 1,
        config: { duration: 100 }
      });
      
      // Move to target
      await next({ 
        x: projectile.endPosition.x, 
        y: projectile.endPosition.y,
        rotate: 360,
        config: properties
      });
      
      // Fade out
      await next({ 
        scale: 0.3, 
        opacity: 0,
        config: { duration: 200 }
      });
      
      setShowImpact(true);
      setTimeout(() => {
        setIsAnimating(false);
        onProjectileComplete?.();
      }, 800);
    },
    config: properties || { mass: 1, tension: 300, friction: 30 }
  });

  // Impact effect animation
  const impactSpring = useSpring({
    ref: impactRef,
    from: { scale: 0, opacity: 0 },
    to: showImpact ? [
      { scale: 1.5, opacity: 1 },
      { scale: 2.5, opacity: 0 }
    ] : { scale: 0, opacity: 0 },
    config: { mass: 1, tension: 200, friction: 25 }
  });

  // Chain animations
  useChain(showImpact ? [projectileRef, impactRef] : [projectileRef], [0, 0.8]);

  if (!projectile || !projectile.isVisible) {
    return null;
  }

  const icon = getProjectileIcon(projectile.action);
  const damageType = projectile.action.damage?.type || 'force';
  const hasTrail = properties?.trail?.enabled;

  return (
    <div className={`fixed inset-0 pointer-events-none z-40 ${className}`}>
      {/* Main projectile */}
      <animated.div
        style={{
          position: 'absolute',
          left: projectileSpring.x,
          top: projectileSpring.y,
          scale: projectileSpring.scale,
          opacity: projectileSpring.opacity,
          rotate: projectileSpring.rotate,
          transformOrigin: 'center',
        }}
        className="relative"
      >
        {/* Projectile icon */}
        <div className="relative z-10">
          {icon}
        </div>

        {/* Particle trail */}
        {hasTrail && properties?.trail && (
          <div className="absolute inset-0">
            <ParticleTrail
              count={properties.trail.count || 6}
              damageType={damageType}
              isActive={isAnimating}
            />
          </div>
        )}

        {/* Glow effect for magical projectiles */}
        {projectile.action.category === 'spell' && (
          <div className="absolute inset-0 rounded-full opacity-30 animate-pulse"
               style={{
                 background: `radial-gradient(circle, ${
                   damageType === 'fire' ? '#fb923c' :
                   damageType === 'cold' ? '#93c5fd' :
                   damageType === 'lightning' ? '#c084fc' :
                   damageType === 'force' ? '#818cf8' :
                   '#6b7280'
                 } 0%, transparent 70%)`
               }}
          />
        )}
      </animated.div>

      {/* Impact effect */}
      {showImpact && (
        <animated.div
          style={{
            position: 'absolute',
            left: projectile.endPosition.x,
            top: projectile.endPosition.y,
            scale: impactSpring.scale,
            opacity: impactSpring.opacity,
            transformOrigin: 'center',
          }}
          className="relative"
        >
          {/* Impact flash */}
          <div className={`absolute w-8 h-8 rounded-full -translate-x-1/2 -translate-y-1/2 ${
            damageType === 'fire' ? 'bg-orange-400' :
            damageType === 'cold' ? 'bg-blue-300' :
            damageType === 'lightning' ? 'bg-purple-400' :
            damageType === 'force' ? 'bg-indigo-400' :
            'bg-gray-400'
          }`} />

          {/* Impact ring */}
          <div className={`absolute w-16 h-16 rounded-full border-2 -translate-x-1/2 -translate-y-1/2 ${
            damageType === 'fire' ? 'border-orange-400' :
            damageType === 'cold' ? 'border-blue-300' :
            damageType === 'lightning' ? 'border-purple-400' :
            damageType === 'force' ? 'border-indigo-400' :
            'border-gray-400'
          }`} />

          {/* Damage number */}
          {projectile.result?.result.damage && (
            <motion.div
              initial={{ opacity: 0, y: 0, scale: 0.5 }}
              animate={{ opacity: 1, y: -30, scale: 1 }}
              exit={{ opacity: 0, y: -50, scale: 0.5 }}
              transition={{ duration: 0.8, ease: "easeOut" }}
              className="absolute -translate-x-1/2 -translate-y-1/2 text-2xl font-bold text-white"
              style={{
                textShadow: '2px 2px 4px rgba(0,0,0,0.8)',
                color: projectile.result.result.criticalHit ? '#fbbf24' : '#ffffff'
              }}
            >
              -{projectile.result.result.damage}
              {projectile.result.result.criticalHit && (
                <span className="text-yellow-300 ml-1">!</span>
              )}
            </motion.div>
          )}
        </animated.div>
      )}

      {/* Miss indicator */}
      {projectile.result && !projectile.result.result.hit && showImpact && (
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.5 }}
          transition={{ duration: 0.5 }}
          style={{
            position: 'absolute',
            left: projectile.endPosition.x,
            top: projectile.endPosition.y,
            transform: 'translate(-50%, -50%)',
          }}
          className="text-gray-400 text-xl font-bold"
        >
          MISS!
        </motion.div>
      )}
    </div>
  );
} 