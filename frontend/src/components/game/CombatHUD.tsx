import React, { useState, useEffect } from 'react'
import { Sword, Shield, Heart, Zap, Clock, Target, Skull, Plus, Minus, RotateCcw } from 'lucide-react'
import type { Character, StatusEffect, CombatEntity, CombatAction } from '@/types/game'

interface CombatHUDProps {
  playerCharacter: Character
  combatEntities: CombatEntity[]
  currentTurn: string
  isInCombat: boolean
  availableActions: CombatAction[]
  onActionSelect: (action: CombatAction) => void
  onEndTurn: () => void
  onRollInitiative: () => void
  className?: string
}

const CombatHUD: React.FC<CombatHUDProps> = ({
  playerCharacter,
  combatEntities,
  currentTurn,
  isInCombat,
  availableActions,
  onActionSelect,
  onEndTurn,
  onRollInitiative,
  className = ''
}) => {
  const [selectedAction, setSelectedAction] = useState<CombatAction | null>(null)
  const [hoveredEntity, setHoveredEntity] = useState<string | null>(null)

  // Calculate health percentage for visual indicators
  const getHealthPercentage = (current: number, max: number) => (current / max) * 100

  // Get health bar color based on percentage
  const getHealthColor = (percentage: number) => {
    if (percentage > 75) return 'bg-green-500'
    if (percentage > 50) return 'bg-yellow-500'
    if (percentage > 25) return 'bg-orange-500'
    return 'bg-red-500'
  }

  // Get status effect icon
  const getStatusIcon = (effect: StatusEffect) => {
    const iconMap: Record<string, string> = {
      'blessed': '✨',
      'poisoned': '☠️',
      'burning': '🔥',
      'frozen': '❄️',
      'stunned': '💫',
      'inspired': '🎵',
      'rage': '😡',
      'invisible': '👻',
      'hasted': '⚡',
      'slowed': '🐌'
    }
    return iconMap[effect.icon] || '🔮'
  }

  // Sort entities by initiative (highest first)
  const sortedEntities = [...combatEntities].sort((a, b) => b.initiative - a.initiative)
  const isPlayerTurn = currentTurn === playerCharacter.id.toString()

  if (!isInCombat) {
    return (
      <div className={`bg-gray-800/50 rounded-lg border border-gray-600/50 p-4 ${className}`}>
        <div className="text-center text-gray-400">
          <Target className="w-8 h-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No active combat</p>
          <button
            onClick={onRollInitiative}
            className="mt-2 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm transition-colors"
          >
            Roll Initiative
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`bg-gradient-to-br from-gray-900 to-gray-800 rounded-lg border border-red-500/30 shadow-lg ${className}`}>
      {/* Combat Header */}
      <div className="bg-red-900/50 p-3 rounded-t-lg border-b border-red-500/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sword className="w-5 h-5 text-red-400" />
            <span className="font-semibold text-red-200">Combat Active</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-red-300">
            <Clock className="w-4 h-4" />
            <span>Turn: {currentTurn}</span>
          </div>
        </div>
      </div>

      {/* Initiative Tracker */}
      <div className="p-3 border-b border-gray-600/50">
        <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-1">
          <Target className="w-4 h-4" />
          Initiative Order
        </h3>
        <div className="space-y-1">
          {sortedEntities.map((entity) => (
            <div
              key={entity.id}
              className={`flex items-center gap-2 p-2 rounded transition-all ${
                entity.isActive
                  ? 'bg-blue-600/30 border border-blue-400/50 shadow-md'
                  : 'bg-gray-700/30 hover:bg-gray-600/30'
              }`}
              onMouseEnter={() => setHoveredEntity(entity.id)}
              onMouseLeave={() => setHoveredEntity(null)}
            >
              {/* Avatar */}
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                entity.type === 'player' ? 'bg-blue-500' :
                entity.type === 'ally' ? 'bg-green-500' : 'bg-red-500'
              }`}>
                {entity.name[0]}
              </div>

              {/* Name and Initiative */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-sm font-medium truncate ${
                    entity.isActive ? 'text-blue-200' : 'text-gray-300'
                  }`}>
                    {entity.name}
                  </span>
                  <span className="text-xs text-gray-400">({entity.initiative})</span>
                </div>
              </div>

              {/* Health Bar */}
              <div className="w-16 h-2 bg-gray-600 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${getHealthColor(getHealthPercentage(entity.currentHp, entity.maxHp))}`}
                  style={{ width: `${getHealthPercentage(entity.currentHp, entity.maxHp)}%` }}
                />
              </div>

              {/* HP Text */}
              <span className="text-xs text-gray-400 w-8 text-right">
                {entity.currentHp}
              </span>

              {/* Status Effects */}
              {entity.statusEffects.length > 0 && (
                <div className="flex gap-1">
                  {entity.statusEffects.slice(0, 3).map((effect) => (
                    <div
                      key={effect.id}
                      className={`w-4 h-4 rounded-full flex items-center justify-center text-xs ${
                        effect.type === 'buff' ? 'bg-green-500/30 text-green-400' :
                        effect.type === 'debuff' ? 'bg-red-500/30 text-red-400' :
                        'bg-blue-500/30 text-blue-400'
                      }`}
                      title={`${effect.name} (${effect.duration} turns): ${effect.description}`}
                    >
                      {getStatusIcon(effect)}
                    </div>
                  ))}
                  {entity.statusEffects.length > 3 && (
                    <div className="w-4 h-4 rounded-full bg-gray-500/30 flex items-center justify-center text-xs text-gray-400">
                      +{entity.statusEffects.length - 3}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Player Combat Stats */}
      <div className="p-3 border-b border-gray-600/50">
        <h3 className="text-sm font-medium text-gray-300 mb-2">Your Stats</h3>
        <div className="grid grid-cols-2 gap-3">
          {/* Health */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-red-300 flex items-center gap-1">
                <Heart className="w-3 h-3" />
                Health
              </span>
              <span className="text-red-200">{playerCharacter.current_hp}/{playerCharacter.max_hp}</span>
            </div>
            <div className="w-full h-2 bg-gray-600 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${getHealthColor(getHealthPercentage(playerCharacter.current_hp, playerCharacter.max_hp))}`}
                style={{ width: `${getHealthPercentage(playerCharacter.current_hp, playerCharacter.max_hp)}%` }}
              />
            </div>
          </div>

          {/* Armor Class */}
          <div className="space-y-1">
            <div className="flex items-center justify-between text-xs">
              <span className="text-blue-300 flex items-center gap-1">
                <Shield className="w-3 h-3" />
                AC
              </span>
              <span className="text-blue-200">{playerCharacter.armor_class}</span>
            </div>
            <div className="w-full h-2 bg-gray-600 rounded-full overflow-hidden">
              <div className="h-full bg-blue-500 transition-all duration-300" style={{ width: `${Math.min(100, (playerCharacter.armor_class / 25) * 100)}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {isPlayerTurn && (
        <div className="p-3">
          <h3 className="text-sm font-medium text-gray-300 mb-2">Available Actions</h3>
          <div className="grid grid-cols-2 gap-2 mb-3">
            {availableActions.map((action) => {
              const IconComponent = action.icon
              return (
                <button
                  key={action.id}
                  onClick={() => {
                    setSelectedAction(action)
                    onActionSelect(action)
                  }}
                  disabled={action.disabled}
                  className={`p-2 rounded transition-all group ${
                    selectedAction?.id === action.id
                      ? 'bg-blue-600 border border-blue-400'
                      : action.disabled
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                      : 'bg-gray-700 hover:bg-gray-600 border border-transparent hover:border-gray-500'
                  }`}
                  title={action.description}
                >
                  <div className="flex items-center gap-2">
                    <IconComponent className="w-4 h-4" />
                    <span className="text-sm font-medium">{action.name}</span>
                  </div>
                  {action.cooldown && (
                    <div className="text-xs text-gray-400 mt-1">
                      Cooldown: {action.cooldown}
                    </div>
                  )}
                </button>
              )
            })}
          </div>

          {/* End Turn Button */}
          <button
            onClick={onEndTurn}
            className="w-full py-2 bg-yellow-600 hover:bg-yellow-700 rounded font-medium transition-colors flex items-center justify-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            End Turn
          </button>
        </div>
      )}

      {/* Not Player Turn */}
      {!isPlayerTurn && (
        <div className="p-3">
          <div className="text-center text-gray-400">
            <Clock className="w-6 h-6 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Waiting for {currentTurn}'s turn...</p>
          </div>
        </div>
      )}
    </div>
  )
}

export default CombatHUD 