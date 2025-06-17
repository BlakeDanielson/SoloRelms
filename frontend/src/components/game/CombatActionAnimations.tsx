'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sword, 
  Shield, 
  Zap, 
  Heart, 
  Sparkles, 
  Target,
  ArrowUp,
  Flame,
  Snowflake,
  Wind
} from 'lucide-react';
import { CombatAction, CombatActionResult } from '../../lib/combat/types';

interface CombatActionAnimationsProps {
  action: CombatAction | null;
  result?: CombatActionResult | null;
  isVisible: boolean;
  onAnimationComplete?: () => void;
  className?: string;
}

// Animation variants for different action types
const actionVariants = {
  // Attack animations
  attack: {
    initial: { scale: 0.8, rotate: -45, opacity: 0 },
    animate: { 
      scale: [0.8, 1.2, 1], 
      rotate: [-45, 15, 0], 
      opacity: [0, 1, 1],
      transition: { 
        duration: 0.6, 
        times: [0, 0.4, 1],
        ease: "easeOut" 
      }
    },
    exit: { 
      scale: 0.5, 
      opacity: 0, 
      transition: { duration: 0.3 } 
    }
  },

  // Spell animations
  spell: {
    initial: { scale: 0, rotate: 0, opacity: 0 },
    animate: { 
      scale: [0, 1.3, 1], 
      rotate: [0, 360, 720], 
      opacity: [0, 1, 1],
      transition: { 
        duration: 0.8,
        times: [0, 0.5, 1],
        ease: "easeInOut" 
      }
    },
    exit: { 
      scale: 0, 
      rotate: 1080, 
      opacity: 0, 
      transition: { duration: 0.4 } 
    }
  },

  // Movement/defensive animations
  move: {
    initial: { scale: 0.5, x: -20, opacity: 0 },
    animate: { 
      scale: [0.5, 1.1, 1], 
      x: [-20, 10, 0], 
      opacity: [0, 1, 1],
      transition: { 
        duration: 0.5, 
        ease: "easeOut" 
      }
    },
    exit: { 
      scale: 0.5, 
      x: 20, 
      opacity: 0, 
      transition: { duration: 0.3 } 
    }
  },

  // Utility animations (dodge, dash, help, etc.)
  default: {
    initial: { scale: 0.6, y: 20, opacity: 0 },
    animate: { 
      scale: [0.6, 1.2, 1], 
      y: [20, -10, 0], 
      opacity: [0, 1, 1],
      transition: { 
        duration: 0.7,
        ease: "easeOut" 
      }
    },
    exit: { 
      scale: 0.6, 
      y: -20, 
      opacity: 0, 
      transition: { duration: 0.4 } 
    }
  }
};

// Result effect animations
const resultVariants = {
  hit: {
    initial: { scale: 0, opacity: 0 },
    animate: {
      scale: [0, 1.5, 1],
      opacity: [0, 1, 0.8],
      transition: { duration: 0.5, ease: "easeOut" }
    },
    exit: { scale: 2, opacity: 0, transition: { duration: 0.3 } }
  },

  miss: {
    initial: { x: 0, opacity: 0 },
    animate: {
      x: [0, -10, 10, -5, 5, 0],
      opacity: [0, 1, 1, 1, 1, 0.5],
      transition: { duration: 0.6, ease: "easeInOut" }
    },
    exit: { opacity: 0, transition: { duration: 0.2 } }
  },

  critical: {
    initial: { scale: 0, rotate: 0, opacity: 0 },
    animate: {
      scale: [0, 1.8, 1.2],
      rotate: [0, 360, 720],
      opacity: [0, 1, 1],
      transition: { duration: 0.8, ease: "easeOut" }
    },
    exit: { 
      scale: 2.5, 
      opacity: 0, 
      transition: { duration: 0.4 } 
    }
  }
};

// Get icon based on action category and damage type
const getActionIcon = (action: CombatAction) => {
  switch (action.category) {
    case 'attack':
      return <Sword className="w-8 h-8" />;
    case 'dodge':
      return <Shield className="w-8 h-8" />;
    case 'spell':
      if (action.damage?.type === 'fire') return <Flame className="w-8 h-8" />;
      if (action.damage?.type === 'cold') return <Snowflake className="w-8 h-8" />;
      if (action.damage?.type === 'lightning') return <Zap className="w-8 h-8" />;
      if (action.damage?.type === 'force') return <Wind className="w-8 h-8" />;
      return <Sparkles className="w-8 h-8" />;
    case 'help':
      return <Heart className="w-8 h-8" />;
    case 'move':
    case 'dash':
      return <ArrowUp className="w-8 h-8" />;
    default:
      return <Target className="w-8 h-8" />;
  }
};

// Get color scheme based on action and result
const getColorScheme = (action: CombatAction, result?: CombatActionResult | null) => {
  if (result?.result.criticalHit) {
    return {
      primary: 'text-yellow-300',
      secondary: 'text-yellow-100',
      bg: 'bg-yellow-500/20',
      border: 'border-yellow-400',
      glow: 'shadow-yellow-400/50'
    };
  }

  if (result?.result.criticalMiss || (result && !result.result.hit)) {
    return {
      primary: 'text-gray-400',
      secondary: 'text-gray-300',
      bg: 'bg-gray-500/20',
      border: 'border-gray-400',
      glow: 'shadow-gray-400/30'
    };
  }

  switch (action.category) {
    case 'attack':
      return {
        primary: 'text-red-400',
        secondary: 'text-red-200',
        bg: 'bg-red-500/20',
        border: 'border-red-400',
        glow: 'shadow-red-400/50'
      };
    case 'spell':
      if (action.damage?.type === 'fire') {
        return {
          primary: 'text-orange-400',
          secondary: 'text-orange-200',
          bg: 'bg-orange-500/20',
          border: 'border-orange-400',
          glow: 'shadow-orange-400/50'
        };
      }
      if (action.damage?.type === 'cold') {
        return {
          primary: 'text-blue-400',
          secondary: 'text-blue-200',
          bg: 'bg-blue-500/20',
          border: 'border-blue-400',
          glow: 'shadow-blue-400/50'
        };
      }
      if (action.damage?.type === 'lightning') {
        return {
          primary: 'text-purple-400',
          secondary: 'text-purple-200',
          bg: 'bg-purple-500/20',
          border: 'border-purple-400',
          glow: 'shadow-purple-400/50'
        };
      }
      return {
        primary: 'text-indigo-400',
        secondary: 'text-indigo-200',
        bg: 'bg-indigo-500/20',
        border: 'border-indigo-400',
        glow: 'shadow-indigo-400/50'
      };
    case 'dodge':
    case 'move':
      return {
        primary: 'text-blue-400',
        secondary: 'text-blue-200',
        bg: 'bg-blue-500/20',
        border: 'border-blue-400',
        glow: 'shadow-blue-400/50'
      };
    case 'help':
    case 'dash':
      return {
        primary: 'text-green-400',
        secondary: 'text-green-200',
        bg: 'bg-green-500/20',
        border: 'border-green-400',
        glow: 'shadow-green-400/50'
      };
    default:
      return {
        primary: 'text-gray-400',
        secondary: 'text-gray-200',
        bg: 'bg-gray-500/20',
        border: 'border-gray-400',
        glow: 'shadow-gray-400/30'
      };
  }
};

export default function CombatActionAnimations({
  action,
  result,
  isVisible,
  onAnimationComplete,
  className = ''
}: CombatActionAnimationsProps) {
  if (!action || !isVisible) return null;

  const colorScheme = getColorScheme(action, result);
  const icon = getActionIcon(action);
  
  // Get appropriate animation variant
  const getAnimationVariant = (category: CombatAction['category']) => {
    if (category === 'attack' || category === 'spell' || category === 'move') {
      return actionVariants[category];
    }
    return actionVariants.default;
  };
  
  const variant = getAnimationVariant(action.category);

  return (
    <div className={`fixed inset-0 pointer-events-none flex items-center justify-center z-50 ${className}`}>
      <AnimatePresence onExitComplete={onAnimationComplete}>
        {isVisible && (
          <motion.div
            className="relative"
            variants={variant}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {/* Main action icon */}
            <motion.div
              className={`
                relative p-6 rounded-full border-2 backdrop-blur-sm
                ${colorScheme.bg} ${colorScheme.border} ${colorScheme.primary}
                shadow-lg ${colorScheme.glow}
              `}
              whileHover={{ scale: 1.05 }}
            >
              {icon}
              
              {/* Pulsing ring effect */}
              <motion.div
                className={`absolute inset-0 rounded-full border-2 ${colorScheme.border}`}
                animate={{
                  scale: [1, 1.5, 2],
                  opacity: [0.8, 0.3, 0],
                }}
                transition={{
                  duration: 1.2,
                  repeat: Infinity,
                  ease: "easeOut"
                }}
              />
            </motion.div>

            {/* Action name */}
            <motion.div
              className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 text-center"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ delay: 0.2, duration: 0.4 }}
            >
              <div className={`text-lg font-bold ${colorScheme.primary}`}>
                {action.name}
              </div>
              
              {/* Damage display */}
              {result && result.result.hit && result.result.damage && (
                <motion.div
                  className={`text-2xl font-bold ${colorScheme.primary} mt-1`}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.4, duration: 0.3 }}
                >
                  -{result.result.damage}
                </motion.div>
              )}
            </motion.div>

            {/* Result overlay animations */}
            <AnimatePresence>
              {result?.result.criticalHit && (
                <motion.div
                  className="absolute inset-0 flex items-center justify-center"
                  variants={resultVariants.critical}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                >
                  <div className="text-yellow-300 text-3xl font-bold">
                    CRITICAL!
                  </div>
                </motion.div>
              )}

              {result?.result.criticalMiss && (
                <motion.div
                  className="absolute inset-0 flex items-center justify-center"
                  variants={resultVariants.miss}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                >
                  <div className="text-gray-400 text-xl font-bold">
                    FUMBLE!
                  </div>
                </motion.div>
              )}

              {result && !result.result.hit && !result.result.criticalMiss && (
                <motion.div
                  className="absolute inset-0 flex items-center justify-center"
                  variants={resultVariants.miss}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                >
                  <div className="text-gray-400 text-xl font-bold">
                    MISS!
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Particle effects for critical hits */}
            {result?.result.criticalHit && (
              <>
                {[...Array(8)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-2 h-2 bg-yellow-400 rounded-full"
                    style={{
                      left: '50%',
                      top: '50%',
                    }}
                    animate={{
                      x: [0, (Math.cos(i * 45 * Math.PI / 180) * 60)],
                      y: [0, (Math.sin(i * 45 * Math.PI / 180) * 60)],
                      opacity: [1, 0],
                      scale: [1, 0.5],
                    }}
                    transition={{
                      duration: 0.8,
                      delay: 0.2,
                      ease: "easeOut"
                    }}
                  />
                ))}
              </>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
} 