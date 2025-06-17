'use client';

import React from 'react';
import { Combatant, CombatAction } from '../../lib/combat/types';
import { getValidTargets } from '../../lib/combat/utils';
import { Heart, Shield, Crosshair, User } from 'lucide-react';

interface TargetSelectionProps {
  actor: Combatant;
  action: CombatAction;
  allCombatants: Combatant[];
  onTargetSelect: (target: Combatant) => void;
  onCancel?: () => void;
  selectedTarget?: Combatant | null;
}

export default function TargetSelection({
  actor,
  action,
  allCombatants,
  onTargetSelect,
  onCancel,
  selectedTarget
}: TargetSelectionProps) {
  const validTargets = getValidTargets(actor, action, allCombatants);

  const getTargetTypeColor = (target: Combatant) => {
    switch (target.type) {
      case 'player':
        return 'border-green-400 bg-green-900/20';
      case 'enemy':
        return 'border-red-400 bg-red-900/20';
      case 'npc':
        return 'border-blue-400 bg-blue-900/20';
      default:
        return 'border-gray-400 bg-gray-900/20';
    }
  };

  const getTargetIcon = (target: Combatant) => {
    switch (target.type) {
      case 'player':
        return <User className="w-5 h-5 text-green-400" />;
      case 'enemy':
        return <Crosshair className="w-5 h-5 text-red-400" />;
      case 'npc':
        return <Shield className="w-5 h-5 text-blue-400" />;
      default:
        return <User className="w-5 h-5 text-gray-400" />;
    }
  };

  const getHealthPercentage = (target: Combatant) => {
    return (target.health.current / target.health.max) * 100;
  };

  const getHealthColor = (percentage: number) => {
    if (percentage > 75) return 'bg-green-500';
    if (percentage > 50) return 'bg-yellow-500';
    if (percentage > 25) return 'bg-orange-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-gray-800/90 backdrop-blur-sm rounded-lg border border-white/10 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">
          Select Target for {action.name}
        </h3>
        {onCancel && (
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-white transition-colors text-sm"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Action Info */}
      <div className="bg-gray-900/50 rounded-lg p-3 mb-4">
        <div className="text-sm text-gray-300">
          <strong className="text-blue-400">{actor.name}</strong> is using{' '}
          <strong className="text-purple-400">{action.name}</strong>
        </div>
        <div className="text-xs text-gray-400 mt-1">{action.description}</div>
        {action.range && (
          <div className="text-xs text-blue-300 mt-1">
            Range: {action.range.normal}ft
            {action.range.maximum && action.range.maximum !== action.range.normal && 
              ` (max ${action.range.maximum}ft)`
            }
          </div>
        )}
      </div>

      {/* Valid Targets */}
      {validTargets.length === 0 ? (
        <div className="text-center text-gray-400 py-8">
          <Crosshair className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <div>No valid targets for this action</div>
          <div className="text-sm mt-1">
            {action.category === 'attack' && 'No enemies in range'}
            {action.category === 'help' && 'No allies to help'}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-sm text-gray-300 mb-3">
            Choose a target ({validTargets.length} available):
          </div>
          
          {validTargets.map((target) => {
            const isSelected = selectedTarget?.id === target.id;
            const healthPercentage = getHealthPercentage(target);
            
            return (
              <div
                key={target.id}
                onClick={() => onTargetSelect(target)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-400 bg-blue-900/30 shadow-lg'
                    : `${getTargetTypeColor(target)} hover:border-opacity-80 hover:bg-opacity-80`
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    {getTargetIcon(target)}
                    <div className="ml-3">
                      <div className="text-white font-medium">{target.name}</div>
                      <div className="text-xs text-gray-400 capitalize">
                        {target.type} • AC {target.armorClass}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="flex items-center text-red-400 text-sm">
                      <Heart className="w-4 h-4 mr-1" />
                      {target.health.current}/{target.health.max}
                    </div>
                    <div className="text-xs text-gray-400">
                      {Math.round(healthPercentage)}%
                    </div>
                  </div>
                </div>
                
                {/* Health Bar */}
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getHealthColor(healthPercentage)}`}
                    style={{ width: `${healthPercentage}%` }}
                  />
                </div>
                
                {/* Conditions */}
                {target.conditions.length > 0 && (
                  <div className="flex gap-1 mt-2">
                    {target.conditions.map((condition, index) => (
                      <span
                        key={index}
                        className="text-xs bg-purple-600/20 text-purple-300 px-2 py-1 rounded"
                      >
                        {condition.type}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Range Information */}
      {action.range && validTargets.length > 0 && (
        <div className="mt-4 p-3 bg-blue-900/20 rounded-lg border border-blue-500/30">
          <div className="text-sm text-blue-300">
            <strong>Range Information:</strong>
          </div>
          <div className="text-xs text-blue-200 mt-1">
            All targets shown are within range ({action.range.normal}ft)
            {action.range.maximum && action.range.maximum !== action.range.normal && (
              <>
                <br />
                Long range available up to {action.range.maximum}ft (with disadvantage)
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
} 