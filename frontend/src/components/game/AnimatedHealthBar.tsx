'use client';

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Shield, Plus } from 'lucide-react';

interface AnimatedHealthBarProps {
  current: number;
  max: number;
  temporary?: number;
  name: string;
  isDead?: boolean;
  recentDamage?: number;
  recentHealing?: number;
  className?: string;
  showNumbers?: boolean;
  size?: 'sm' | 'md' | 'lg';
  armorClass?: number;
}

export default function AnimatedHealthBar({
  current,
  max,
  temporary = 0,
  name,
  isDead = false,
  recentDamage,
  recentHealing,
  className = '',
  showNumbers = true,
  size = 'md',
  armorClass
}: AnimatedHealthBarProps) {
  const [previousHealth, setPreviousHealth] = useState(current);
  const [damageIndicator, setDamageIndicator] = useState<number | null>(null);
  const [healingIndicator, setHealingIndicator] = useState<number | null>(null);
  const [isShaking, setIsShaking] = useState(false);

  // Track health changes for animations
  useEffect(() => {
    if (current < previousHealth) {
      const damage = previousHealth - current;
      setDamageIndicator(damage);
      setIsShaking(true);
      
      setTimeout(() => {
        setDamageIndicator(null);
        setIsShaking(false);
      }, 2000);
    } else if (current > previousHealth) {
      const healing = current - previousHealth;
      setHealingIndicator(healing);
      
      setTimeout(() => {
        setHealingIndicator(null);
      }, 2000);
    }
    
    setPreviousHealth(current);
  }, [current, previousHealth]);

  // Calculate percentages
  const healthPercentage = Math.max(0, Math.min(100, (current / max) * 100));
  const tempPercentage = Math.max(0, Math.min(100, (temporary / max) * 100));
  const totalPercentage = Math.min(100, healthPercentage + tempPercentage);

  // Size configurations
  const sizeConfig = {
    sm: {
      height: 'h-2',
      padding: 'p-2',
      text: 'text-xs',
      icon: 'w-3 h-3'
    },
    md: {
      height: 'h-3',
      padding: 'p-3',
      text: 'text-sm',
      icon: 'w-4 h-4'
    },
    lg: {
      height: 'h-4',
      padding: 'p-4',
      text: 'text-base',
      icon: 'w-5 h-5'
    }
  };

  const config = sizeConfig[size];

  // Health bar color based on percentage
  const getHealthColor = (percentage: number) => {
    if (percentage > 75) return 'bg-green-500';
    if (percentage > 50) return 'bg-yellow-500';
    if (percentage > 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const healthColor = getHealthColor(healthPercentage);

  return (
    <div className={`relative ${config.padding} ${className}`}>
      {/* Header with name and AC */}
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-1">
          <Heart className={`${config.icon} text-red-400`} />
          <span className={`${config.text} font-medium text-white`}>{name}</span>
        </div>
        
        {armorClass && (
          <div className="flex items-center gap-1">
            <Shield className={`${config.icon} text-blue-400`} />
            <span className={`${config.text} text-blue-300`}>{armorClass}</span>
          </div>
        )}
      </div>

      {/* Health bar container */}
      <motion.div
        className={`relative w-full ${config.height} bg-gray-700 rounded-full overflow-hidden border border-gray-600`}
        animate={isShaking ? {
          x: [-2, 2, -2, 2, 0],
          transition: { duration: 0.4, ease: "easeInOut" }
        } : {}}
      >
        {/* Background gradient for visual depth */}
        <div className="absolute inset-0 bg-gradient-to-r from-gray-800 to-gray-700" />
        
        {/* Main health bar */}
        <motion.div
          className={`absolute left-0 top-0 h-full ${healthColor} relative overflow-hidden`}
          initial={{ width: `${healthPercentage}%` }}
          animate={{ width: `${healthPercentage}%` }}
          transition={{
            duration: 0.8,
            ease: "easeOut"
          }}
        >
          {/* Health bar shine effect */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20"
            animate={{
              x: ['-100%', '100%'],
              transition: {
                duration: 2,
                repeat: Infinity,
                ease: "linear",
                repeatDelay: 3
              }
            }}
          />
        </motion.div>

        {/* Temporary health bar */}
        {temporary > 0 && (
          <motion.div
            className="absolute left-0 top-0 h-full bg-blue-400 opacity-70"
            initial={{ width: `${tempPercentage}%` }}
            animate={{ width: `${tempPercentage}%` }}
            style={{ left: `${healthPercentage}%` }}
            transition={{
              duration: 0.6,
              ease: "easeOut"
            }}
          />
        )}

        {/* Death overlay */}
        {isDead && (
          <motion.div
            className="absolute inset-0 bg-black opacity-50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            transition={{ duration: 0.5 }}
          />
        )}
      </motion.div>

      {/* Health numbers */}
      {showNumbers && (
        <div className="flex items-center justify-between mt-1">
          <motion.span
            className={`${config.text} font-medium ${isDead ? 'text-red-400' : 'text-white'}`}
            animate={isDead ? { 
              color: ['#ffffff', '#ef4444', '#ffffff'],
              transition: { duration: 1, repeat: Infinity }
            } : {}}
          >
            {current}{temporary > 0 && ` (+${temporary})`} / {max}
          </motion.span>
          
          <span className={`${config.text} text-gray-400`}>
            {Math.round(totalPercentage)}%
          </span>
        </div>
      )}

      {/* Floating damage/healing indicators */}
      <AnimatePresence>
        {damageIndicator && (
          <motion.div
            className="absolute right-0 top-0 pointer-events-none"
            initial={{ opacity: 0, y: 0, scale: 0.8 }}
            animate={{ opacity: 1, y: -20, scale: 1 }}
            exit={{ opacity: 0, y: -40, scale: 0.6 }}
            transition={{ duration: 2, ease: "easeOut" }}
          >
            <div className="bg-red-500 text-white px-2 py-1 rounded text-sm font-bold shadow-lg">
              -{damageIndicator}
            </div>
          </motion.div>
        )}

        {healingIndicator && (
          <motion.div
            className="absolute right-0 top-0 pointer-events-none"
            initial={{ opacity: 0, y: 0, scale: 0.8 }}
            animate={{ opacity: 1, y: -20, scale: 1 }}
            exit={{ opacity: 0, y: -40, scale: 0.6 }}
            transition={{ duration: 2, ease: "easeOut" }}
          >
            <div className="bg-green-500 text-white px-2 py-1 rounded text-sm font-bold shadow-lg flex items-center gap-1">
              <Plus className="w-3 h-3" />
              {healingIndicator}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Critical health warning */}
      {healthPercentage <= 25 && !isDead && (
        <motion.div
          className="absolute inset-0 border-2 border-red-500 rounded pointer-events-none"
          animate={{
            opacity: [0.3, 0.8, 0.3],
            scale: [1, 1.02, 1],
            transition: {
              duration: 1.5,
              repeat: Infinity,
              ease: "easeInOut"
            }
          }}
        />
      )}

      {/* Dead indicator */}
      {isDead && (
        <motion.div
          className="absolute inset-0 flex items-center justify-center pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div className="bg-black/70 text-red-400 px-2 py-1 rounded text-sm font-bold border border-red-600">
            DEAD
          </div>
        </motion.div>
      )}
    </div>
  );
} 