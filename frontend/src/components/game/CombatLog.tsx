'use client';

import React from 'react';
import { CombatActionResult, Combatant } from '../../lib/combat/types';
import { Sword, Shield, Heart, Zap, Target, AlertTriangle, CheckCircle } from 'lucide-react';

interface CombatLogProps {
  actionResults: CombatActionResult[];
  participants: Combatant[];
  maxEntries?: number;
}

export default function CombatLog({ 
  actionResults, 
  participants, 
  maxEntries = 10 
}: CombatLogProps) {
  const getCombatantName = (id: string) => {
    return participants.find(p => p.id === id)?.name || 'Unknown';
  };

  const getActionIcon = (result: CombatActionResult) => {
    switch (result.action.category) {
      case 'attack':
        return <Sword className="w-4 h-4" />;
      case 'spell':
        return <Zap className="w-4 h-4" />;
      case 'dodge':
        return <Shield className="w-4 h-4" />;
      case 'help':
        return <Heart className="w-4 h-4" />;
      default:
        return <Target className="w-4 h-4" />;
    }
  };

  const getActionColor = (result: CombatActionResult) => {
    if (result.result.criticalHit) return 'text-yellow-400';
    if (result.result.criticalMiss) return 'text-red-400';
    if (result.result.hit) return 'text-green-400';
    if (result.result.hit === false) return 'text-gray-400';
    return 'text-blue-400';
  };

  const getResultIcon = (result: CombatActionResult) => {
    if (result.result.criticalHit) return <AlertTriangle className="w-4 h-4 text-yellow-400" />;
    if (result.result.criticalMiss) return <AlertTriangle className="w-4 h-4 text-red-400" />;
    if (result.result.hit) return <CheckCircle className="w-4 h-4 text-green-400" />;
    return <Target className="w-4 h-4 text-gray-400" />;
  };

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour12: false, timeStyle: 'medium' });
  };

  const getTargetName = (result: CombatActionResult) => {
    if (result.action.target) {
      return getCombatantName(result.action.target);
    }
    return null;
  };

  // Show most recent entries first
  const recentResults = [...actionResults]
    .reverse()
    .slice(0, maxEntries);

  return (
    <div className="bg-gray-800/50 rounded-lg p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-white flex items-center">
          <Target className="w-5 h-5 mr-2 text-blue-400" />
          Combat Log
        </h3>
        <div className="text-xs text-gray-400">
          {actionResults.length} actions total
        </div>
      </div>

      {recentResults.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <div>No actions yet</div>
          <div className="text-sm">Combat actions will appear here</div>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {recentResults.map((result, index) => {
            const actorName = getCombatantName(result.actor);
            const targetName = getTargetName(result);
            const actionColor = getActionColor(result);
            
            return (
              <div
                key={`${result.timestamp}-${index}`}
                className="bg-gray-900/50 rounded-lg p-3 border-l-4 border-l-blue-500/50"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <div className={`mr-2 ${actionColor}`}>
                      {getActionIcon(result)}
                    </div>
                    <div>
                      <div className="text-white font-medium text-sm">
                        <span className="text-blue-400">{actorName}</span>
                        {' uses '}
                        <span className="text-purple-400">{result.action.name}</span>
                        {targetName && (
                          <>
                            {' on '}
                            <span className="text-red-400">{targetName}</span>
                          </>
                        )}
                      </div>
                      <div className="text-xs text-gray-400 mt-1">
                        {result.action.description}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center text-xs text-gray-500">
                    {getResultIcon(result)}
                    <span className="ml-1">{formatTimestamp(result.timestamp)}</span>
                  </div>
                </div>

                {/* Result Details */}
                <div className="ml-6">
                  <div className={`text-sm font-medium ${actionColor}`}>
                    {result.result.effect || 'No effect'}
                  </div>
                  
                  {/* Damage/Healing */}
                  {result.result.damage !== undefined && result.result.damage !== 0 && (
                    <div className="text-sm mt-1">
                      {result.result.damage > 0 ? (
                        <span className="text-red-400">
                          💥 {result.result.damage} damage
                        </span>
                      ) : (
                        <span className="text-green-400">
                          💚 {Math.abs(result.result.damage)} healing
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Critical indicators */}
                  {result.result.criticalHit && (
                    <div className="text-yellow-400 text-sm mt-1 font-bold">
                      ⚡ Critical Hit!
                    </div>
                  )}
                  
                  {result.result.criticalMiss && (
                    <div className="text-red-400 text-sm mt-1">
                      💥 Critical Miss!
                    </div>
                  )}
                  
                  {/* Hit/Miss indicator */}
                  {result.result.hit !== undefined && (
                    <div className="text-xs text-gray-400 mt-1">
                      Result: {result.result.hit ? 'Hit' : 'Miss'}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Show more indicator */}
      {actionResults.length > maxEntries && (
        <div className="text-center text-gray-500 text-xs mt-3 pt-3 border-t border-gray-700">
          Showing {maxEntries} of {actionResults.length} actions
        </div>
      )}
    </div>
  );
} 