'use client'

import React, { useState, useEffect } from 'react'
// Using simple HTML/CSS classes instead of shadcn components for compatibility
import { Dice1, Dice2, Dice3, Dice4, Dice5, Dice6 } from 'lucide-react'

interface DiceRequirement {
  expression: string  // e.g., "1d20"
  purpose: string     // e.g., "Dexterity check"
  dc?: number        // Difficulty Class
  ability_modifier?: number
  advantage?: boolean
  disadvantage?: boolean
}

interface DiceRequirementModalProps {
  isOpen: boolean
  requirement: DiceRequirement | null
  onRollDice: (result: {
    dice_type: string
    rolls: number[]
    modifier: number
    total: number
    advantage?: boolean
    disadvantage?: boolean
  }) => Promise<void>
  onClose: () => void
  isLoading?: boolean
}

const getDiceIcon = (value: number) => {
  switch (value) {
    case 1: return <Dice1 className="w-8 h-8" />
    case 2: return <Dice2 className="w-8 h-8" />
    case 3: return <Dice3 className="w-8 h-8" />
    case 4: return <Dice4 className="w-8 h-8" />
    case 5: return <Dice5 className="w-8 h-8" />
    case 6: return <Dice6 className="w-8 h-8" />
    default: return <div className="w-8 h-8 rounded border-2 border-gray-300 flex items-center justify-center text-sm font-bold">{value}</div>
  }
}

export function DiceRequirementModal({ 
  isOpen, 
  requirement, 
  onRollDice, 
  onClose, 
  isLoading = false 
}: DiceRequirementModalProps) {
  const [rollResult, setRollResult] = useState<number | null>(null)
  const [isRolling, setIsRolling] = useState(false)
  const [hasRolled, setHasRolled] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setRollResult(null)
      setHasRolled(false)
      setIsRolling(false)
    }
  }, [isOpen, requirement])

  if (!isOpen || !requirement) return null

  // Parse dice expression (e.g., "1d20" -> { count: 1, sides: 20 })
  const parseDiceExpression = (expression: string) => {
    const match = expression.match(/(\d+)?d(\d+)/)
    if (!match) return { count: 1, sides: 20 }
    return {
      count: parseInt(match[1] || '1'),
      sides: parseInt(match[2])
    }
  }

  const { count, sides } = parseDiceExpression(requirement.expression)
  const modifier = requirement.ability_modifier || 0

  const handleRoll = async () => {
    setIsRolling(true)
    
    // Simulate dice rolling animation
    let animationCount = 0
    const animationInterval = setInterval(() => {
      setRollResult(Math.floor(Math.random() * sides) + 1)
      animationCount++
      
      if (animationCount >= 10) {
        clearInterval(animationInterval)
        
        // Generate final result
        const rolls = Array.from({ length: count }, () => Math.floor(Math.random() * sides) + 1)
        const finalRoll = rolls[0] // For single die
        const total = finalRoll + modifier
        
        setRollResult(finalRoll)
        setIsRolling(false)
        setHasRolled(true)
        
        // Prepare dice result for API
        setTimeout(async () => {
          try {
            await onRollDice({
              dice_type: `d${sides}`,
              rolls: rolls,
              modifier: modifier,
              total: total,
              advantage: requirement.advantage,
              disadvantage: requirement.disadvantage
            })
          } catch (error) {
            console.error('Failed to fulfill dice requirement:', error)
          }
        }, 1000) // Brief delay to show result
      }
    }, 100)
  }

  const getSuccessStatus = () => {
    if (!hasRolled || rollResult === null || !requirement.dc) return null
    const total = rollResult + modifier
    return total >= requirement.dc ? 'success' : 'failure'
  }

  const successStatus = getSuccessStatus()

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="w-full max-w-md bg-white/95 backdrop-blur rounded-lg border border-gray-300">
        <div className="text-center p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-amber-800 mb-2">
            🎲 Dice Roll Required
          </h2>
          <p className="text-lg text-gray-600">
            {requirement.purpose}
          </p>
        </div>
        
        <div className="p-6 space-y-6">
          {/* Dice Expression Display */}
          <div className="text-center">
            <div className="text-3xl font-bold text-amber-700 mb-2">
              {requirement.expression}
              {modifier !== 0 && (
                <span className="text-2xl ml-2">
                  {modifier > 0 ? '+' : ''}{modifier}
                </span>
              )}
            </div>
            {requirement.dc && (
              <span className="text-lg px-3 py-1 bg-gray-100 border border-gray-300 rounded-full">
                DC {requirement.dc}
              </span>
            )}
          </div>

          {/* Dice Visual */}
          <div className="flex justify-center items-center space-x-4">
            <div className={`p-4 border-2 rounded-lg ${isRolling ? 'border-amber-500 animate-pulse' : 'border-gray-300'}`}>
              {rollResult !== null ? (
                getDiceIcon(rollResult)
              ) : (
                <div className="w-8 h-8 rounded border-2 border-gray-300 flex items-center justify-center">
                  <span className="text-gray-400">?</span>
                </div>
              )}
            </div>
            
            {modifier !== 0 && rollResult !== null && (
              <>
                <span className="text-2xl font-bold">+</span>
                <div className="p-2 border rounded bg-gray-100">
                  <span className="font-bold">{modifier}</span>
                </div>
                <span className="text-2xl font-bold">=</span>
                <div className="p-2 border-2 rounded bg-amber-100 border-amber-300">
                  <span className="font-bold text-amber-800">{rollResult + modifier}</span>
                </div>
              </>
            )}
          </div>

          {/* Success/Failure Indicator */}
          {successStatus && (
            <div className="text-center">
              <span className={`text-lg px-4 py-2 rounded-full ${
                successStatus === 'success' 
                  ? 'bg-green-500 text-white' 
                  : 'bg-red-500 text-white'
              }`}>
                {successStatus === 'success' ? '✅ SUCCESS!' : '❌ FAILURE!'}
              </span>
            </div>
          )}

          {/* Special Conditions */}
          {(requirement.advantage || requirement.disadvantage) && (
            <div className="text-center">
              <span className="bg-gray-200 text-gray-800 px-3 py-1 rounded-full text-sm">
                {requirement.advantage ? '⬆️ Advantage' : '⬇️ Disadvantage'}
              </span>
            </div>
          )}

          {/* Action Button */}
          <div className="flex justify-center space-x-3">
            {!hasRolled ? (
              <button 
                onClick={handleRoll}
                disabled={isRolling || isLoading}
                className="bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white px-6 py-3 rounded-lg text-lg font-medium transition-colors"
              >
                {isRolling ? '🎲 Rolling...' : '🎲 Roll Dice'}
              </button>
            ) : (
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-2">
                  {isLoading ? 'Continuing story...' : 'Roll complete!'}
                </p>
                {isLoading && (
                  <div className="w-6 h-6 border-2 border-amber-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
} 