'use client'

import React, { useState, useEffect } from 'react'
import { Dice1, Dice2, Dice3, Dice4, Dice5, Dice6, Plus, Minus, RotateCcw } from 'lucide-react'

interface DiceRoll {
  id: string
  diceType: string
  rolls: number[]
  modifier: number
  total: number
  timestamp: Date
  label?: string
}

interface DiceRollerProps {
  onRollComplete: (roll: DiceRoll) => void
  className?: string
}

interface CustomRoll {
  diceType: string
  count: number
  modifier: number
  label: string
}

const DiceRoller: React.FC<DiceRollerProps> = ({
  onRollComplete,
  className = ''
}) => {
  const [isRolling, setIsRolling] = useState(false)
  const [lastRoll, setLastRoll] = useState<DiceRoll | null>(null)
  const [rollHistory, setRollHistory] = useState<DiceRoll[]>([])
  const [showCustomRoll, setShowCustomRoll] = useState(false)
  const [customRoll, setCustomRoll] = useState<CustomRoll>({
    diceType: 'd20',
    count: 1,
    modifier: 0,
    label: ''
  })

  const standardDice = [
    { type: 'd4', sides: 4, color: 'emerald' },
    { type: 'd6', sides: 6, color: 'blue' },
    { type: 'd8', sides: 8, color: 'purple' },
    { type: 'd10', sides: 10, color: 'pink' },
    { type: 'd12', sides: 12, color: 'orange' },
    { type: 'd20', sides: 20, color: 'red' },
    { type: 'd100', sides: 100, color: 'yellow' }
  ]

  const quickRolls = [
    { label: 'Attack', dice: 'd20', modifier: 5, description: 'Standard attack roll' },
    { label: 'Damage', dice: 'd8', modifier: 3, description: 'Weapon damage' },
    { label: 'Save', dice: 'd20', modifier: 2, description: 'Saving throw' },
    { label: 'Skill', dice: 'd20', modifier: 3, description: 'Skill check' },
    { label: 'Initiative', dice: 'd20', modifier: 1, description: 'Initiative roll' },
    { label: 'Perception', dice: 'd20', modifier: 4, description: 'Perception check' }
  ]

  const rollDice = async (
    diceType: string, 
    count: number = 1, 
    modifier: number = 0, 
    label?: string
  ) => {
    setIsRolling(true)
    
    // Simulate rolling animation delay
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const sides = parseInt(diceType.substring(1))
    const rolls: number[] = []
    
    for (let i = 0; i < count; i++) {
      rolls.push(Math.floor(Math.random() * sides) + 1)
    }
    
    const baseTotal = rolls.reduce((sum, roll) => sum + roll, 0)
    const total = baseTotal + modifier
    
    const newRoll: DiceRoll = {
      id: Date.now().toString(),
      diceType: count > 1 ? `${count}${diceType}` : diceType,
      rolls,
      modifier,
      total,
      timestamp: new Date(),
      label
    }
    
    setLastRoll(newRoll)
    setRollHistory(prev => [newRoll, ...prev.slice(0, 9)]) // Keep last 10 rolls
    onRollComplete(newRoll)
    setIsRolling(false)
  }

  const handleQuickRoll = (quickRoll: typeof quickRolls[0]) => {
    rollDice(quickRoll.dice, 1, quickRoll.modifier, quickRoll.label)
  }

  const handleCustomRoll = () => {
    rollDice(
      customRoll.diceType,
      customRoll.count,
      customRoll.modifier,
      customRoll.label || undefined
    )
    setShowCustomRoll(false)
  }

  const getDiceIcon = (result: number) => {
    const icons = {
      1: Dice1,
      2: Dice2,
      3: Dice3,
      4: Dice4,
      5: Dice5,
      6: Dice6
    }
    const Icon = icons[result as keyof typeof icons] || Dice6
    return <Icon className="w-4 h-4" />
  }

  const getResultColor = (roll: DiceRoll) => {
    if (roll.diceType.includes('d20')) {
      const naturalRoll = roll.rolls[0]
      if (naturalRoll === 20) return 'text-green-400' // Natural 20
      if (naturalRoll === 1) return 'text-red-400' // Natural 1
    }
    return 'text-white'
  }

  const formatRollResult = (roll: DiceRoll) => {
    const baseSum = roll.rolls.reduce((sum, r) => sum + r, 0)
    let result = roll.rolls.join(' + ')
    
    if (roll.modifier !== 0) {
      result += ` ${roll.modifier >= 0 ? '+' : ''}${roll.modifier}`
    }
    
    return `${result} = ${roll.total}`
  }

  return (
    <div className={`bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-600/50 p-4 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-white">Dice Roller</h3>
        <button
          onClick={() => setShowCustomRoll(!showCustomRoll)}
          className="px-3 py-1 bg-purple-600/30 hover:bg-purple-600/50 border border-purple-400/50 rounded text-xs transition-colors"
        >
          Custom Roll
        </button>
      </div>

      {/* Custom Roll Panel */}
      {showCustomRoll && (
        <div className="mb-4 p-3 bg-gray-700/50 rounded border border-gray-600/50">
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Dice Type</label>
              <select
                value={customRoll.diceType}
                onChange={(e) => setCustomRoll(prev => ({ ...prev, diceType: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
              >
                {standardDice.map(dice => (
                  <option key={dice.type} value={dice.type}>{dice.type}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-xs text-gray-400 mb-1">Count</label>
              <input
                type="number"
                min="1"
                max="20"
                value={customRoll.count}
                onChange={(e) => setCustomRoll(prev => ({ ...prev, count: parseInt(e.target.value) || 1 }))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-2 mb-3">
            <div>
              <label className="block text-xs text-gray-400 mb-1">Modifier</label>
              <input
                type="number"
                value={customRoll.modifier}
                onChange={(e) => setCustomRoll(prev => ({ ...prev, modifier: parseInt(e.target.value) || 0 }))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
              />
            </div>
            
            <div>
              <label className="block text-xs text-gray-400 mb-1">Label (optional)</label>
              <input
                type="text"
                placeholder="e.g., Fireball damage"
                value={customRoll.label}
                onChange={(e) => setCustomRoll(prev => ({ ...prev, label: e.target.value }))}
                className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm"
              />
            </div>
          </div>
          
          <button
            onClick={handleCustomRoll}
            disabled={isRolling}
            className="w-full px-3 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded text-sm font-medium transition-colors"
          >
            Roll {customRoll.count}{customRoll.diceType}
            {customRoll.modifier !== 0 && ` ${customRoll.modifier >= 0 ? '+' : ''}${customRoll.modifier}`}
          </button>
        </div>
      )}

      {/* Quick Rolls */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Quick Rolls</h4>
        <div className="grid grid-cols-2 gap-2">
          {quickRolls.map((quick) => (
            <button
              key={quick.label}
              onClick={() => handleQuickRoll(quick)}
              disabled={isRolling}
              className="p-2 bg-gray-700/50 hover:bg-gray-600/50 disabled:bg-gray-700/30 border border-gray-600/50 rounded text-xs transition-colors text-left"
              title={quick.description}
            >
              <div className="font-medium text-blue-300">{quick.label}</div>
              <div className="text-gray-400">{quick.dice}{quick.modifier >= 0 ? '+' : ''}{quick.modifier}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Standard Dice */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-300 mb-2">Standard Dice</h4>
        <div className="grid grid-cols-4 gap-2">
          {standardDice.map((dice) => (
            <button
              key={dice.type}
              onClick={() => rollDice(dice.type)}
              disabled={isRolling}
              className={`p-2 bg-${dice.color}-600/20 hover:bg-${dice.color}-600/40 disabled:bg-gray-700/30 border border-${dice.color}-400/50 rounded text-xs font-medium transition-colors`}
            >
              {dice.type}
            </button>
          ))}
        </div>
      </div>

      {/* Last Roll Result */}
      {lastRoll && (
        <div className="mb-4 p-3 bg-gray-700/50 rounded border border-gray-600/50">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h4 className="text-sm font-medium text-white">
                {lastRoll.label || 'Roll Result'}
              </h4>
              <div className="text-xs text-gray-400">
                {lastRoll.diceType}
                {lastRoll.modifier !== 0 && ` ${lastRoll.modifier >= 0 ? '+' : ''}${lastRoll.modifier}`}
              </div>
            </div>
            <div className={`text-xl font-bold ${getResultColor(lastRoll)}`}>
              {lastRoll.total}
            </div>
          </div>
          
          <div className="flex items-center gap-2 mb-2">
            {lastRoll.rolls.map((roll, index) => (
              <div key={index} className="flex items-center gap-1">
                {lastRoll.diceType.includes('d6') && getDiceIcon(roll)}
                <span className="text-sm">{roll}</span>
                {index < lastRoll.rolls.length - 1 && <span className="text-gray-400">+</span>}
              </div>
            ))}
            {lastRoll.modifier !== 0 && (
              <>
                <span className="text-gray-400">{lastRoll.modifier >= 0 ? '+' : ''}</span>
                <span className="text-sm">{Math.abs(lastRoll.modifier)}</span>
              </>
            )}
          </div>
          
          <div className="text-xs text-gray-400">
            {formatRollResult(lastRoll)}
          </div>
          
          {/* Special result indicators */}
          {lastRoll.diceType.includes('d20') && (
            <div className="mt-2">
              {lastRoll.rolls[0] === 20 && (
                <div className="text-xs text-green-400 font-medium">🎉 Natural 20! Critical Success!</div>
              )}
              {lastRoll.rolls[0] === 1 && (
                <div className="text-xs text-red-400 font-medium">💥 Natural 1! Critical Failure!</div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Rolling Animation */}
      {isRolling && (
        <div className="flex items-center justify-center py-4">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-3 h-3 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
          <span className="ml-3 text-sm text-gray-400">Rolling...</span>
        </div>
      )}

      {/* Roll History */}
      {rollHistory.length > 0 && (
        <div>
          <div className="flex justify-between items-center mb-2">
            <h4 className="text-sm font-medium text-gray-300">Recent Rolls</h4>
            <button
              onClick={() => setRollHistory([])}
              className="text-xs text-gray-400 hover:text-white transition-colors"
              title="Clear History"
            >
              <RotateCcw className="w-3 h-3" />
            </button>
          </div>
          
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {rollHistory.slice(0, 5).map((roll) => (
              <div key={roll.id} className="flex justify-between items-center p-2 bg-gray-700/30 rounded text-xs">
                <div className="flex-1">
                  <span className="text-gray-300">
                    {roll.label && `${roll.label}: `}
                    {roll.diceType}
                    {roll.modifier !== 0 && ` ${roll.modifier >= 0 ? '+' : ''}${roll.modifier}`}
                  </span>
                </div>
                <div className={`font-medium ${getResultColor(roll)}`}>
                  {roll.total}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DiceRoller 