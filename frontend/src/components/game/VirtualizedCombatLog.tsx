'use client';

import React, { useEffect, useRef, useMemo, useState } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sword, 
  Shield, 
  Heart, 
  Zap, 
  Target,
  Flame,
  Snowflake,
  Wind,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Settings
} from 'lucide-react';
import { CombatActionResult, Combatant } from '../../lib/combat/types';

interface VirtualizedCombatLogProps {
  actionResults: CombatActionResult[];
  participants: Combatant[];
  maxHeight?: number;
  showTimestamps?: boolean;
  showDamageNumbers?: boolean;
  autoScroll?: boolean;
  className?: string;
}

interface LogEntry {
  id: string;
  timestamp: number;
  type: 'action' | 'status' | 'round' | 'combat';
  data: CombatActionResult | any;
  actor?: Combatant;
  target?: Combatant;
}

export default function VirtualizedCombatLog({
  actionResults,
  participants,
  maxHeight = 400,
  showTimestamps = true,
  showDamageNumbers = true,
  autoScroll = true,
  className = ''
}: VirtualizedCombatLogProps) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    showCriticals: true,
    showMisses: true,
    showHealing: true,
    showDamageDetails: true,
    animateNewEntries: true
  });

  // Convert action results to enhanced log entries
  const logEntries = useMemo(() => {
    const entries: LogEntry[] = [];
    
    actionResults.forEach((result, index) => {
      const actor = participants.find(p => p.id === result.actor);
      const target = participants.find(p => p.id === result.action.target);
      
      // Filter based on settings
      if (!settings.showCriticals && result.result.criticalHit) return;
      if (!settings.showMisses && !result.result.hit) return;
      if (!settings.showHealing && result.action.name.toLowerCase().includes('heal')) return;
      
      entries.push({
        id: `${result.timestamp}-${index}`,
        timestamp: result.timestamp,
        type: 'action',
        data: result,
        actor,
        target
      });
    });
    
    return entries.reverse(); // Most recent first
  }, [actionResults, participants, settings]);

  // Virtualization setup
  const virtualizer = useVirtualizer({
    count: logEntries.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80, // Estimated height per item
    overscan: 5,
  });

  // Auto-scroll to bottom when new entries are added
  useEffect(() => {
    if (autoScroll && logEntries.length > 0 && parentRef.current) {
      const scrollElement = parentRef.current;
      scrollElement.scrollTop = scrollElement.scrollHeight;
    }
  }, [logEntries.length, autoScroll]);

  // Get action icon based on action type and damage
  const getActionIcon = (result: CombatActionResult) => {
    const { action } = result;
    
    if (action.category === 'attack') {
      return <Sword className="w-4 h-4 text-red-400" />;
    }
    
    if (action.category === 'spell') {
      if (action.name.toLowerCase().includes('heal')) {
        return <Heart className="w-4 h-4 text-green-400" />;
      }
      if (action.damage?.type === 'fire') {
        return <Flame className="w-4 h-4 text-orange-400" />;
      }
      if (action.damage?.type === 'cold') {
        return <Snowflake className="w-4 h-4 text-blue-300" />;
      }
      if (action.damage?.type === 'lightning') {
        return <Zap className="w-4 h-4 text-purple-400" />;
      }
      if (action.damage?.type === 'force') {
        return <Wind className="w-4 h-4 text-indigo-400" />;
      }
      return <Sparkles className="w-4 h-4 text-indigo-400" />;
    }
    
    return <Target className="w-4 h-4 text-gray-400" />;
  };

  // Get result color based on outcome
  const getResultColor = (result: CombatActionResult) => {
    if (result.result.criticalHit) return 'text-yellow-400';
    if (result.result.criticalMiss) return 'text-red-600';
    if (!result.result.hit) return 'text-gray-500';
    if (result.action.name.toLowerCase().includes('heal')) return 'text-green-400';
    return 'text-white';
  };

  // Format log entry text
  const formatLogEntry = (entry: LogEntry) => {
    const result = entry.data as CombatActionResult;
    const actorName = entry.actor?.name || 'Unknown';
    const targetName = entry.target?.name || 'Unknown';
    
    let message = `${actorName} used ${result.action.name}`;
    
    if (entry.target) {
      message += ` on ${targetName}`;
    }
    
    if (result.result.criticalHit) {
      message += ' (Critical Hit!)';
    } else if (result.result.criticalMiss) {
      message += ' (Critical Miss!)';
    } else if (!result.result.hit) {
      message += ' (Miss)';
    }
    
    return message;
  };

  // Get damage/healing details
  const getDamageDetails = (result: CombatActionResult) => {
    if (!settings.showDamageDetails) return null;
    
    if (result.result.hit && result.result.damage) {
      const isHealing = result.action.name.toLowerCase().includes('heal');
      return (
        <span className={`text-sm font-medium ${isHealing ? 'text-green-300' : 'text-red-300'}`}>
          {isHealing ? '+' : '-'}{result.result.damage}
          {result.action.damage?.type && ` (${result.action.damage.type})`}
        </span>
      );
    }
    
    return null;
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 1
    });
  };

  return (
    <div className={`bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center">
          <h3 className="text-xl font-bold text-white mr-4">Combat Log</h3>
          <div className="text-sm text-gray-400">
            {logEntries.length} entries
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-b border-white/10 bg-gray-900/50"
          >
            <div className="p-4 space-y-3">
              <h4 className="text-sm font-medium text-white mb-2">Display Options</h4>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <label className="flex items-center space-x-2 text-gray-300">
                  <input
                    type="checkbox"
                    checked={settings.showCriticals}
                    onChange={(e) => setSettings(prev => ({ ...prev, showCriticals: e.target.checked }))}
                    className="rounded"
                  />
                  <span>Show Criticals</span>
                </label>
                
                <label className="flex items-center space-x-2 text-gray-300">
                  <input
                    type="checkbox"
                    checked={settings.showMisses}
                    onChange={(e) => setSettings(prev => ({ ...prev, showMisses: e.target.checked }))}
                    className="rounded"
                  />
                  <span>Show Misses</span>
                </label>
                
                <label className="flex items-center space-x-2 text-gray-300">
                  <input
                    type="checkbox"
                    checked={settings.showHealing}
                    onChange={(e) => setSettings(prev => ({ ...prev, showHealing: e.target.checked }))}
                    className="rounded"
                  />
                  <span>Show Healing</span>
                </label>
                
                <label className="flex items-center space-x-2 text-gray-300">
                  <input
                    type="checkbox"
                    checked={settings.showDamageDetails}
                    onChange={(e) => setSettings(prev => ({ ...prev, showDamageDetails: e.target.checked }))}
                    className="rounded"
                  />
                  <span>Damage Details</span>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Virtualized Log Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: maxHeight }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div
              ref={parentRef}
              className="overflow-auto"
              style={{ height: maxHeight }}
            >
              <div
                style={{
                  height: virtualizer.getTotalSize(),
                  width: '100%',
                  position: 'relative',
                }}
              >
                {virtualizer.getVirtualItems().map((virtualItem) => {
                  const entry = logEntries[virtualItem.index];
                  const result = entry.data as CombatActionResult;
                  const resultColor = getResultColor(result);
                  const damageDetails = getDamageDetails(result);
                  
                  return (
                    <motion.div
                      key={entry.id}
                      initial={settings.animateNewEntries ? { opacity: 0, x: -20 } : {}}
                      animate={{ opacity: 1, x: 0 }}
                      style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: virtualItem.size,
                        transform: `translateY(${virtualItem.start}px)`,
                      }}
                      className="flex items-center p-3 border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      {/* Action Icon */}
                      <div className="flex-shrink-0 mr-3">
                        {getActionIcon(result)}
                      </div>
                      
                      {/* Main Content */}
                      <div className="flex-1 min-w-0">
                        <div className={`text-sm font-medium ${resultColor}`}>
                          {formatLogEntry(entry)}
                        </div>
                        
                        {/* Damage/Healing Details */}
                        {damageDetails && (
                          <div className="mt-1">
                            {damageDetails}
                          </div>
                        )}
                        
                        {/* Timestamp */}
                        {showTimestamps && (
                          <div className="text-xs text-gray-500 mt-1">
                            {formatTimestamp(entry.timestamp)}
                          </div>
                        )}
                      </div>
                      
                      {/* Critical Hit Indicator */}
                      {result.result.criticalHit && (
                        <div className="flex-shrink-0 ml-2">
                          <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {logEntries.length === 0 && isExpanded && (
        <div className="p-8 text-center text-gray-500">
          <Zap className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No combat actions yet</p>
          <p className="text-sm">Start combat to see the action log</p>
        </div>
      )}
    </div>
  );
} 