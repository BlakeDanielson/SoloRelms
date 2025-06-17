'use client';

import React, { useState } from 'react';
import { CombatAction, ActionType, Combatant } from '../../lib/combat/types';
import { getActionsByType, getAvailableActions } from '../../lib/combat/actions';
import { Sword, Shield, Zap, Move, RotateCcw, Eye, Search, Package } from 'lucide-react';

interface ActionSelectionProps {
  combatant: Combatant;
  onActionSelect: (action: CombatAction) => void;
  onCancel?: () => void;
  disabled?: boolean;
}

const ACTION_TYPE_ICONS = {
  action: Sword,
  bonus_action: Zap,
  movement: Move,
  reaction: Shield,
  free: Package
};

const ACTION_TYPE_COLORS = {
  action: 'bg-red-600 hover:bg-red-700',
  bonus_action: 'bg-yellow-600 hover:bg-yellow-700',
  movement: 'bg-blue-600 hover:bg-blue-700',
  reaction: 'bg-purple-600 hover:bg-purple-700',
  free: 'bg-gray-600 hover:bg-gray-700'
};

const CATEGORY_ICONS = {
  attack: Sword,
  spell: Zap,
  move: Move,
  dodge: Shield,
  dash: Move,
  help: Package,
  ready: Eye,
  hide: Eye,
  disengage: Move,
  search: Search,
  use_object: Package
};

export default function ActionSelection({ 
  combatant, 
  onActionSelect, 
  onCancel, 
  disabled = false 
}: ActionSelectionProps) {
  const [selectedActionType, setSelectedActionType] = useState<ActionType>('action');
  const [selectedAction, setSelectedAction] = useState<CombatAction | null>(null);

  const availableActions = getAvailableActions(combatant, selectedActionType);

  const handleActionSelect = (action: CombatAction) => {
    setSelectedAction(action);
  };

  const handleConfirmAction = () => {
    if (selectedAction) {
      onActionSelect(selectedAction);
      setSelectedAction(null);
    }
  };

  const handleCancel = () => {
    setSelectedAction(null);
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="bg-gray-800/90 backdrop-blur-sm rounded-lg border border-white/10 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-white">
          Select Action for {combatant.name}
        </h3>
        {onCancel && (
          <button
            onClick={handleCancel}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Action Type Tabs */}
      <div className="flex gap-2 mb-6">
        {(['action', 'bonus_action', 'movement', 'reaction', 'free'] as ActionType[]).map((actionType) => {
          const Icon = ACTION_TYPE_ICONS[actionType];
          const isSelected = selectedActionType === actionType;
          const actionCount = getActionsByType(actionType).length;
          
          return (
            <button
              key={actionType}
              onClick={() => setSelectedActionType(actionType)}
              disabled={disabled}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                isSelected
                  ? ACTION_TYPE_COLORS[actionType]
                  : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {actionType.replace('_', ' ').toUpperCase()}
              <span className="ml-2 text-xs bg-black/30 px-2 py-1 rounded">
                {actionCount}
              </span>
            </button>
          );
        })}
      </div>

      {/* Available Actions */}
      <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
        {availableActions.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No actions available for this action type
          </div>
        ) : (
          availableActions.map((action) => {
            const CategoryIcon = CATEGORY_ICONS[action.category];
            const isSelected = selectedAction?.id === action.id;
            
            return (
              <div
                key={action.id}
                onClick={() => handleActionSelect(action)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  isSelected
                    ? 'border-blue-400 bg-blue-900/20'
                    : 'border-gray-600 bg-gray-700/50 hover:border-gray-500'
                } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center">
                    <CategoryIcon className="w-5 h-5 mr-3 text-blue-400" />
                    <div>
                      <h4 className="text-white font-medium">{action.name}</h4>
                      <p className="text-sm text-gray-400">{action.description}</p>
                    </div>
                  </div>
                  
                  {/* Action Details */}
                  <div className="text-right text-sm">
                    {action.damage && (
                      <div className="text-red-400">
                        {action.damage.dice} {action.damage.type}
                      </div>
                    )}
                    {action.effects?.healing && (
                      <div className="text-green-400">
                        Heal: {action.effects.healing}
                      </div>
                    )}
                    {action.range && (
                      <div className="text-blue-400">
                        Range: {action.range.normal}ft
                      </div>
                    )}
                  </div>
                </div>

                {/* Requirements */}
                {action.requirements && (
                  <div className="flex gap-2 text-xs">
                    {action.requirements.minimumLevel && (
                      <span className="bg-purple-600/20 text-purple-300 px-2 py-1 rounded">
                        Level {action.requirements.minimumLevel}+
                      </span>
                    )}
                    {action.requirements.spellSlot !== undefined && (
                      <span className="bg-blue-600/20 text-blue-300 px-2 py-1 rounded">
                        {action.requirements.spellSlot === 0 ? 'Cantrip' : `Spell Slot ${action.requirements.spellSlot}`}
                      </span>
                    )}
                    {action.requirements.weaponType && (
                      <span className="bg-orange-600/20 text-orange-300 px-2 py-1 rounded">
                        {action.requirements.weaponType} weapon
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Action Confirmation */}
      {selectedAction && (
        <div className="bg-gray-900/50 rounded-lg p-4 border border-blue-400/30">
          <h4 className="text-white font-medium mb-2">Confirm Action</h4>
          <p className="text-gray-300 text-sm mb-4">
            Use <span className="text-blue-400 font-medium">{selectedAction.name}</span>?
          </p>
          
          <div className="flex gap-3">
            <button
              onClick={handleConfirmAction}
              disabled={disabled}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              Confirm
            </button>
            <button
              onClick={() => setSelectedAction(null)}
              disabled={disabled}
              className="flex-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 text-white px-4 py-2 rounded-md transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
} 