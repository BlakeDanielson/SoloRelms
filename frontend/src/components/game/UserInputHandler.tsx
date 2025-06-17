'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Keyboard, Gamepad2, Plus, X, History, BookOpen } from 'lucide-react'

interface UserInputHandlerProps {
  onSubmitAction: (content: string, type: 'action' | 'speech' | 'thought') => void
  onRollDice: (diceType: string) => void
  isProcessing?: boolean
  placeholder?: string
  className?: string
}

interface QuickAction {
  id: string
  label: string
  action: string
  icon: string
  category: 'movement' | 'interaction' | 'combat' | 'magic'
}

interface InputHistory {
  id: string
  content: string
  type: 'action' | 'speech' | 'thought'
  timestamp: Date
}

const UserInputHandler: React.FC<UserInputHandlerProps> = ({
  onSubmitAction,
  onRollDice,
  isProcessing = false,
  placeholder = "Describe your action...",
  className = ''
}) => {
  const [inputValue, setInputValue] = useState('')
  const [inputType, setInputType] = useState<'action' | 'speech' | 'thought'>('action')
  const [isListening, setIsListening] = useState(false)
  const [showQuickActions, setShowQuickActions] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [inputHistory, setInputHistory] = useState<InputHistory[]>([])
  const [showAdvancedMode, setShowAdvancedMode] = useState(false)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<any>(null)

  // Quick action templates
  const quickActions: QuickAction[] = [
    // Movement
    { id: 'move_forward', label: 'Move Forward', action: 'I move forward carefully', icon: '⬆️', category: 'movement' },
    { id: 'move_back', label: 'Step Back', action: 'I step back cautiously', icon: '⬇️', category: 'movement' },
    { id: 'hide', label: 'Hide', action: 'I try to hide behind cover', icon: '🫣', category: 'movement' },
    { id: 'sneak', label: 'Sneak', action: 'I move stealthily', icon: '🤫', category: 'movement' },
    
    // Interaction
    { id: 'investigate', label: 'Investigate', action: 'I investigate the area carefully', icon: '🔍', category: 'interaction' },
    { id: 'listen', label: 'Listen', action: 'I listen carefully for any sounds', icon: '👂', category: 'interaction' },
    { id: 'talk', label: 'Talk', action: 'I attempt to communicate', icon: '💬', category: 'interaction' },
    { id: 'wait', label: 'Wait', action: 'I wait and observe', icon: '⏸️', category: 'interaction' },
    
    // Combat
    { id: 'attack', label: 'Attack', action: 'I attack with my weapon', icon: '⚔️', category: 'combat' },
    { id: 'defend', label: 'Defend', action: 'I take a defensive stance', icon: '🛡️', category: 'combat' },
    { id: 'dodge', label: 'Dodge', action: 'I prepare to dodge', icon: '💨', category: 'combat' },
    { id: 'retreat', label: 'Retreat', action: 'I retreat from combat', icon: '🏃', category: 'combat' },
    
    // Magic
    { id: 'cast_spell', label: 'Cast Spell', action: 'I begin casting a spell', icon: '✨', category: 'magic' },
    { id: 'detect_magic', label: 'Detect Magic', action: 'I attempt to detect magical auras', icon: '🔮', category: 'magic' }
  ]

  const inputTypes = [
    { type: 'action' as const, label: 'Action', icon: '🎭', color: 'blue', description: 'Physical actions and movements' },
    { type: 'speech' as const, label: 'Speech', icon: '💬', color: 'green', description: 'Spoken words and dialogue' },
    { type: 'thought' as const, label: 'Think', icon: '💭', color: 'purple', description: 'Internal thoughts and plans' }
  ]

  const diceTypes = [
    { type: 'd4', label: 'd4', sides: 4 },
    { type: 'd6', label: 'd6', sides: 6 },
    { type: 'd8', label: 'd8', sides: 8 },
    { type: 'd10', label: 'd10', sides: 10 },
    { type: 'd12', label: 'd12', sides: 12 },
    { type: 'd20', label: 'd20', sides: 20 },
    { type: 'd100', label: 'd100', sides: 100 }
  ]

  // Initialize speech recognition
  useEffect(() => {
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setInputValue(transcript)
        setIsListening(false)
      }
      
      recognitionRef.current.onerror = () => {
        setIsListening(false)
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
  }, [])

  const handleSubmit = () => {
    if (!inputValue.trim() || isProcessing) return
    
    // Add to history
    const historyEntry: InputHistory = {
      id: Date.now().toString(),
      content: inputValue,
      type: inputType,
      timestamp: new Date()
    }
    setInputHistory(prev => [historyEntry, ...prev.slice(0, 19)]) // Keep last 20 entries
    
    onSubmitAction(inputValue, inputType)
    setInputValue('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    } else if (e.key === 'ArrowUp' && inputHistory.length > 0 && inputValue === '') {
      e.preventDefault()
      setInputValue(inputHistory[0].content)
      setInputType(inputHistory[0].type)
    }
  }

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) return
    
    if (isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }

  const handleQuickAction = (action: QuickAction) => {
    setInputValue(action.action)
    setInputType('action')
    setShowQuickActions(false)
    inputRef.current?.focus()
  }

  const handleHistorySelect = (historyItem: InputHistory) => {
    setInputValue(historyItem.content)
    setInputType(historyItem.type)
    setShowHistory(false)
    inputRef.current?.focus()
  }

  const getTypeColor = (type: string) => {
    const typeConfig = inputTypes.find(t => t.type === type)
    return typeConfig?.color || 'blue'
  }

  const groupedQuickActions = quickActions.reduce((acc, action) => {
    if (!acc[action.category]) acc[action.category] = []
    acc[action.category].push(action)
    return acc
  }, {} as Record<string, QuickAction[]>)

  return (
    <div className={`relative ${className}`}>
      {/* Quick Actions Panel */}
      {showQuickActions && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 rounded-lg p-4 z-20">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-white">Quick Actions</h3>
            <button
              onClick={() => setShowQuickActions(false)}
              className="text-gray-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {Object.entries(groupedQuickActions).map(([category, actions]) => (
              <div key={category}>
                <h4 className="text-xs font-medium text-gray-400 uppercase mb-2">{category}</h4>
                <div className="grid grid-cols-2 gap-2">
                  {actions.map((action) => (
                    <button
                      key={action.id}
                      onClick={() => handleQuickAction(action)}
                      className="flex items-center gap-2 p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded text-xs transition-colors text-left"
                    >
                      <span>{action.icon}</span>
                      <span className="flex-1">{action.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History Panel */}
      {showHistory && inputHistory.length > 0 && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-800/95 backdrop-blur-sm border border-gray-600/50 rounded-lg p-4 z-20">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-sm font-semibold text-white">Input History</h3>
            <button
              onClick={() => setShowHistory(false)}
              className="text-gray-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
          
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {inputHistory.map((item) => (
              <button
                key={item.id}
                onClick={() => handleHistorySelect(item)}
                className="w-full text-left p-2 bg-gray-700/50 hover:bg-gray-600/50 rounded text-xs transition-colors"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-1.5 py-0.5 bg-${getTypeColor(item.type)}-600/30 text-${getTypeColor(item.type)}-300 rounded text-xs`}>
                    {item.type}
                  </span>
                  <span className="text-gray-400 text-xs">
                    {item.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-gray-300 truncate">{item.content}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Advanced Mode Toggle */}
      <div className="flex gap-2 mb-2">
        <button
          onClick={() => setShowAdvancedMode(!showAdvancedMode)}
          className={`px-2 py-1 text-xs rounded transition-colors ${
            showAdvancedMode 
              ? 'bg-purple-600/30 text-purple-300 border border-purple-400/50' 
              : 'bg-gray-600/30 text-gray-400 border border-gray-500/50'
          }`}
        >
          <Gamepad2 className="w-3 h-3 inline mr-1" />
          Advanced
        </button>
        
        {/* Dice Quick Access */}
        <div className="flex gap-1">
          {diceTypes.slice(0, 3).map((dice) => (
            <button
              key={dice.type}
              onClick={() => onRollDice(dice.type)}
              className="px-2 py-1 bg-green-600/30 hover:bg-green-600/50 border border-green-400/50 rounded text-xs transition-colors"
            >
              {dice.label}
            </button>
          ))}
          
          {showAdvancedMode && diceTypes.slice(3).map((dice) => (
            <button
              key={dice.type}
              onClick={() => onRollDice(dice.type)}
              className="px-2 py-1 bg-green-600/30 hover:bg-green-600/50 border border-green-400/50 rounded text-xs transition-colors"
            >
              {dice.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Type Selector */}
      {showAdvancedMode && (
        <div className="flex gap-1 mb-2">
          {inputTypes.map((type) => (
            <button
              key={type.type}
              onClick={() => setInputType(type.type)}
              className={`px-3 py-1 text-xs rounded transition-colors flex items-center gap-1 ${
                inputType === type.type
                  ? `bg-${type.color}-600/50 text-${type.color}-300 border border-${type.color}-400/50`
                  : 'bg-gray-600/30 text-gray-400 border border-gray-500/50 hover:bg-gray-600/50'
              }`}
              title={type.description}
            >
              <span>{type.icon}</span>
              {type.label}
            </button>
          ))}
        </div>
      )}

      {/* Main Input Area */}
      <div className="flex gap-2">
        {/* Quick Actions Button */}
        <button
          onClick={() => setShowQuickActions(!showQuickActions)}
          className="p-2 bg-gray-600/30 hover:bg-gray-600/50 border border-gray-500/50 rounded transition-colors"
          title="Quick Actions"
        >
          <Plus className="w-4 h-4 text-gray-400" />
        </button>

        {/* History Button */}
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="p-2 bg-gray-600/30 hover:bg-gray-600/50 border border-gray-500/50 rounded transition-colors"
          title="Input History"
          disabled={inputHistory.length === 0}
        >
          <History className="w-4 h-4 text-gray-400" />
        </button>

        {/* Input Field */}
        <div className="flex-1 relative">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isProcessing}
            className={`w-full bg-gray-700/50 border rounded px-3 py-2 text-sm placeholder-gray-400 focus:outline-none transition-colors pr-10 ${
              inputType === 'action' 
                ? 'border-blue-400/50 focus:border-blue-400/70' 
                : inputType === 'speech'
                ? 'border-green-400/50 focus:border-green-400/70'
                : 'border-purple-400/50 focus:border-purple-400/70'
            }`}
          />
          
          {/* Type Indicator */}
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
            <span className={`text-xs ${
              inputType === 'action' ? 'text-blue-400' :
              inputType === 'speech' ? 'text-green-400' : 'text-purple-400'
            }`}>
              {inputTypes.find(t => t.type === inputType)?.icon}
            </span>
          </div>
        </div>

        {/* Voice Input Button */}
        {recognitionRef.current && (
          <button
            onClick={toggleVoiceInput}
            className={`p-2 border rounded transition-colors ${
              isListening
                ? 'bg-red-600/30 border-red-400/50 text-red-300'
                : 'bg-gray-600/30 hover:bg-gray-600/50 border border-gray-500/50 text-gray-400'
            }`}
            title={isListening ? 'Stop Listening' : 'Voice Input'}
          >
            {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
          </button>
        )}

        {/* Submit Button */}
        <button
          onClick={handleSubmit}
          disabled={!inputValue.trim() || isProcessing}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            inputType === 'action'
              ? 'bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600'
              : inputType === 'speech'
              ? 'bg-green-600 hover:bg-green-700 disabled:bg-gray-600'
              : 'bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600'
          } disabled:cursor-not-allowed text-white`}
        >
          {isProcessing ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
              Wait
            </div>
          ) : (
            <Send className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Input Hint */}
      {showAdvancedMode && (
        <div className="mt-1 text-xs text-gray-400">
          Press ↑ for history • Enter to submit • Shift+Enter for new line
        </div>
      )}
    </div>
  )
}

export default UserInputHandler 