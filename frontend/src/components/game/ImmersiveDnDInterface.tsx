'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { useAuth, useUser } from '@clerk/nextjs'
import { Sword, Shield, Heart, Plus, Minus, Users, MapPin, Target, Clock, MessageCircle, Dice6, Package, Scroll, Book, Settings, History } from 'lucide-react'
import SceneDisplay from './SceneDisplay'
import CharacterAvatar from './CharacterAvatar'
import GameImage from './GameImage'
import UserInputHandler from './UserInputHandler'
import DiceRoller from './DiceRoller'
import CombatHUD from './CombatHUD'
import InventoryPanel from './InventoryPanel'
import EnhancedInventoryPanel from './EnhancedInventoryPanel'
import CharacterProgressionPanel from './CharacterProgressionPanel'
import ConnectionStatusIndicator, { CompactConnectionStatus } from './ConnectionStatus'
import { TTSButton } from './TTSButton'
import TTSSettings, { TTSSettings as TTSSettingsType } from './TTSSettings'
import StoryProgressTracker from './StoryProgressTracker'
import QuestManager from './QuestManager'
import JournalSystem from './JournalSystem'
import SettingsPanel from './SettingsPanel'
import NarrativeContextDisplay from './NarrativeContextDisplay'
import { DiceRequirementModal } from './DiceRequirementModal'
import { useGameCommunication } from '@/hooks/useGameCommunication'
import { useMockNarrativeContext } from '@/hooks/useNarrativeContext'
import { useTTS } from '@/hooks/useTTS'
import type { Character, GameState, ChatMessage, StatusEffect, CombatEntity, CombatAction } from '@/types/game'

interface ImmersiveDnDInterfaceProps {
  characterId?: string | null
  storyId?: string | null
}

const ImmersiveDnDInterface: React.FC<ImmersiveDnDInterfaceProps> = ({ characterId, storyId }) => {
  // Auth hook
  const { getToken } = useAuth()
  const { user } = useUser()
  
  // State for loading and auth
  const [token, setToken] = useState<string | null>(null)
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])
  const [chatContainerRef, setChatContainerRef] = useState<HTMLDivElement | null>(null)
  
  // Dice requirement modal state
  const [showDiceRequirement, setShowDiceRequirement] = useState(false)
  const [diceRequirement, setDiceRequirement] = useState<{
    expression: string
    purpose: string
    dc?: number
    ability_modifier?: number
    advantage?: boolean
    disadvantage?: boolean
  } | null>(null)
  const [isDiceFulfillmentLoading, setIsDiceFulfillmentLoading] = useState(false)
  
  // TTS state
  const [ttsSettings, setTtsSettings] = useState({
    enabled: true,
    autoPlay: false,
    voice: 'alloy' as const,
    model: 'tts-1' as const
  })
  
  // Character state (initialize with mock data)
  const [character, setCharacter] = useState<Character>({
    id: 1,
    name: "Adventurer",
    class: "Fighter",
    race: "Human",
    level: 1,
    current_hp: 10,
    max_hp: 10,
    armor_class: 14,
    location: "Starting Village",
    status_effects: [],
    inventory: []
  })
  
  // Game state
  const [gameState, setGameState] = useState<GameState>({
    current_scene: "The Adventure Begins",
    current_location: "Starting Village",
    scene_type: "exploration",
    objectives: [],
    recent_events: [],
    party_members: [],
    world_state: {
      time_of_day: "morning",
      weather: "clear",
      season: "spring",
      important_npcs: [],
      active_quests: [],
      world_events: []
    }
  })
  
  // Story progress
  const [storyProgress, setStoryProgress] = useState({
    currentStage: "Introduction",
    stagesCompleted: [],
    storyCompleted: false
  })

  // Game communication hook
  const gameCommunication = useGameCommunication({
    gameId: storyId || 'demo-story',
    characterId: Number(characterId) || 1,
    authToken: token,
    tokenRefreshCallback: (newToken: string) => {
      setToken(newToken)
    },
    onNewMessage: (message) => {
      console.log('📨 New message received from game communication:', message)
      setChatMessages(prev => [...prev, message])
    },
    onGameStateUpdate: (updates) => {
      console.log('🎮 Game state update received:', updates)
      setGameState(prev => ({ ...prev, ...updates }))
    },
    onCharacterUpdate: (updates) => {
      console.log('👤 Character update received:', updates)
      setCharacter(prev => ({ ...prev, ...updates }))
    },
    onConnectionChange: (status) => {
      console.log('🔗 Connection status changed:', status)
    }
  })

  // Additional UI state for game panels and interactions
  const [isTyping, setIsTyping] = useState(false)
  const [showDiceRoller, setShowDiceRoller] = useState(false)
  const [showCombatHUD, setShowCombatHUD] = useState(false)
  const [showInventoryPanel, setShowInventoryPanel] = useState(false)
  const [showEnhancedInventory, setShowEnhancedInventory] = useState(false)
  const [showCharacterProgression, setShowCharacterProgression] = useState(false)
  const [showStoryProgress, setShowStoryProgress] = useState(true)
  const [showQuestManager, setShowQuestManager] = useState(false)
  const [showJournalSystem, setShowJournalSystem] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [showNarrativeContext, setShowNarrativeContext] = useState(false)
  const [showTTSSettings, setShowTTSSettings] = useState(false)
  const [isInCombat, setIsInCombat] = useState(false)
  const [currentTurn, setCurrentTurn] = useState<string>('1')

  // TTS Hook for auto-play functionality
  const { speak } = useTTS()

  // Narrative context data
  const narrativeData = useMockNarrativeContext()

  // Mock combat data - will be replaced with real data
  const [combatEntities, setCombatEntities] = useState<CombatEntity[]>([
    {
      id: '1',
      name: 'Elara Brightblade',
      type: 'player',
      initiative: 16,
      currentHp: 42,
      maxHp: 55,
      armorClass: 18,
      statusEffects: [
        { id: '1', name: 'Blessed', icon: 'blessed', duration: 3, type: 'buff', description: '+1d4 to attack rolls and saving throws' }
      ],
      isActive: true
    },
    {
      id: '2',
      name: 'Goblin Warrior',
      type: 'enemy',
      initiative: 12,
      currentHp: 8,
      maxHp: 15,
      armorClass: 15,
      statusEffects: [],
      isActive: false
    },
    {
      id: '3',
      name: 'Thorin Ironbeard',
      type: 'ally',
      initiative: 14,
      currentHp: 35,
      maxHp: 40,
      armorClass: 16,
      statusEffects: [
        { id: '2', name: 'Rage', icon: 'rage', duration: 2, type: 'buff', description: 'Advantage on Strength checks and saves, +2 damage to melee attacks' }
      ],
      isActive: false
    }
  ])

  const [availableActions, setAvailableActions] = useState<CombatAction[]>([
    { id: 'attack', name: 'Attack', icon: Sword, description: 'Make a weapon attack', actionType: 'attack' },
    { id: 'defend', name: 'Defend', icon: Shield, description: 'Take the Dodge action', actionType: 'defend' },
    { id: 'cast', name: 'Cast Spell', icon: Target, description: 'Cast a spell', actionType: 'spell' },
    { id: 'item', name: 'Use Item', icon: Package, description: 'Use an item from inventory', actionType: 'item' }
  ])

  // Calculate HP percentage for health bar
  const hpPercentage = (character.current_hp / character.max_hp) * 100

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef) {
      chatContainerRef.scrollTop = chatContainerRef.scrollHeight
    }
  }, [chatMessages, chatContainerRef])

  // Fetch real story and character data
  useEffect(() => {
    const fetchGameData = async () => {
      if (!characterId || !storyId) {
        console.log('Missing characterId or storyId, using mock data')
        setIsLoading(false)
        return
      }

      try {
        setIsLoading(true)
        const token = await getToken()

        // Fetch character data
        const characterResponse = await fetch(`http://localhost:8000/api/characters/${characterId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        // Fetch story data
        const storyResponse = await fetch(`http://localhost:8000/api/stories/${storyId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (characterResponse.ok && storyResponse.ok) {
          const characterData = await characterResponse.json()
          const storyData = await storyResponse.json()

          // Update character state with real data
          setCharacter({
            id: characterData.id,
            name: characterData.name,
            class: characterData.character_class,
            race: characterData.race,
            level: characterData.level,
            current_hp: characterData.hit_points,
            max_hp: characterData.max_hit_points,
            armor_class: characterData.armor_class || 10,
            location: storyData.current_stage || "Unknown Location",
            status_effects: [],
            inventory: characterData.inventory || []
          })

          // Update story progress with real data
          setStoryProgress({
            currentStage: storyData.current_stage,
            stagesCompleted: storyData.stages_completed || [],
            storyCompleted: storyData.story_completed
          })

          // Update game state
          setGameState(prev => ({
            ...prev,
            current_scene: storyData.title || "Adventure in Progress",
            current_location: `${characterData.name}'s Adventure`,
            objectives: [],
            recent_events: []
          }))

          // Fetch and add opening narrative
          try {
            console.log('🎭 Fetching opening narrative for story:', storyId)
            const openingResponse = await fetch(`http://localhost:8000/api/stories/${storyId}/opening`, {
              headers: {
                'Authorization': `Bearer ${token}`
              }
            })
            
            if (openingResponse.ok) {
              const openingData = await openingResponse.json()
              console.log('✅ Opening narrative received:', openingData)
              
              const narrativeContent = openingData.opening_narrative || 
                `Welcome to your adventure, ${characterData.name}! Your story begins here. What would you like to do?`
              
              const openingMessage: ChatMessage = {
                id: 'opening-narrative',
                type: 'dm_narration',
                content: narrativeContent,
                timestamp: new Date()
              }
              setChatMessages([openingMessage])
              console.log('✅ Opening narrative displayed successfully')
            } else {
              console.warn('⚠️ Failed to fetch opening narrative, using fallback')
              // Fallback welcome message
              const welcomeMessage: ChatMessage = {
                id: 'welcome',
                type: 'dm_narration',
                content: `Welcome to your adventure, ${characterData.name}! Your story begins here. What would you like to do?`,
                timestamp: new Date()
              }
              setChatMessages([welcomeMessage])
            }
          } catch (openingError) {
            console.error('❌ Failed to fetch opening narrative:', openingError)
            // Fallback welcome message
            const welcomeMessage: ChatMessage = {
              id: 'welcome',
              type: 'dm_narration',
              content: `Welcome to your adventure, ${characterData.name}! Your story begins here. What would you like to do?`,
              timestamp: new Date()
            }
            setChatMessages([welcomeMessage])
          }

          console.log('✅ Successfully loaded character and story data')
        } else {
          console.error('Failed to fetch game data:', {
            character: characterResponse.status,
            story: storyResponse.status
          })
          setError('Failed to load game data')
        }
      } catch (err) {
        console.error('Error fetching game data:', err)
        setError('Failed to load game data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchGameData()
  }, [characterId, storyId, getToken])

  // Initialize orchestration session when game loads
  useEffect(() => {
    const initializeOrchestrationSession = async () => {
      if (!characterId || !user?.id) {
        console.log('⚠️ Cannot initialize orchestration session: missing characterId or user ID')
        return
      }

      try {
        console.log('🚀 Initializing orchestration session for user:', user.id)
        const sessionId = await gameCommunication.startOrchestrationSession(user.id)
        
        if (sessionId) {
          console.log('✅ Orchestration session initialized successfully:', sessionId)
        } else {
          console.warn('⚠️ Failed to initialize orchestration session')
        }
      } catch (error) {
        console.error('❌ Error initializing orchestration session:', error)
      }
    }

    // Only initialize session after character data is loaded
    if (character.id && user?.id && !gameCommunication.sessionId) {
      initializeOrchestrationSession()
    }
  }, [character.id, user?.id, gameCommunication, characterId])

  // Handle dice rolling using real communication
  const rollDice = async (diceType: string) => {
    try {
      const diceRoll = await gameCommunication.rollDice({
        dice_type: diceType,
        count: 1,
        modifier: 0,
        label: `${diceType} roll`
      })

      if (diceRoll) {
        const newMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'dice_roll',
          content: `${diceRoll.label}: Rolled ${diceRoll.diceType}: ${diceRoll.total}`,
          timestamp: new Date(),
          metadata: diceRoll
        }
        setChatMessages(prev => [...prev, newMessage])
      }
    } catch (error) {
      console.error('Failed to roll dice:', error)
      // Fallback to client-side roll
      const result = Math.floor(Math.random() * parseInt(diceType.substring(1))) + 1
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'dice_roll',
        content: `Rolled ${diceType}: ${result}`,
        timestamp: new Date(),
        metadata: { dice: diceType, result }
      }
      setChatMessages(prev => [...prev, newMessage])
    }
  }

  // Handle player action submission using real communication
  const handlePlayerInput = async (content: string, type: 'action' | 'speech' | 'thought') => {
    if (!content.trim()) return
    
    // NEW: Check for pending dice requirement first
    try {
      const gameStatus = await gameCommunication.getGameStatus()
      if (gameStatus?.world_state?.waiting_for_dice) {
        // There's a pending dice requirement - show modal instead of sending action
        const requirement = gameStatus.world_state.pending_dice_requirement
        if (requirement) {
          setDiceRequirement({
            expression: requirement.dice_expression || requirement.expression,
            purpose: requirement.purpose || 'Dice Roll Required',
            dc: requirement.dc,
            ability_modifier: requirement.ability_modifier || requirement.modifier || 0,
            advantage: requirement.advantage || false,
            disadvantage: requirement.disadvantage || false
          })
          setShowDiceRequirement(true)
          
          // Add a message explaining why the action can't proceed
          const blockMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: `🎲 You must complete the pending dice roll (${requirement.purpose}) before taking another action!`,
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, blockMessage])
          return
        }
      }
    } catch (error) {
      console.warn('Could not check dice requirement status:', error)
      // Continue with normal action if status check fails
    }
    
    setIsTyping(true)
    
    try {
      // Send action through the communication system
      const playerMessage = await gameCommunication.sendPlayerAction(type, content)
      
      if (playerMessage) {
        console.log('✅ Action sent successfully:', playerMessage)
        
        // Messages will be added via the onNewMessage callback
        // The AI response will follow automatically with a small delay
        setIsTyping(false)
      } else {
        console.error('❌ Failed to send action')
        setIsTyping(false)
      }
    } catch (error) {
      // Check if this is a dice requirement error
      if (error instanceof Error && error.message.includes('waiting for dice roll')) {
        console.log('🎲 Dice roll required, showing modal')
        // Try to extract dice requirement from error headers or response
        // For now, show a generic dice requirement
        setDiceRequirement({
          expression: "1d20",
          purpose: "Continue Action",
          dc: 15,
          ability_modifier: 0
        })
        setShowDiceRequirement(true)
        setIsTyping(false)
      } else {
        console.error('❌ Error sending action:', error)
        setIsTyping(false)
      }
    }
  }

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'dm_narration': return <MessageCircle className="w-4 h-4 text-purple-400" />
      case 'player_action': return <Users className="w-4 h-4 text-blue-400" />
      case 'player_speech': return <MessageCircle className="w-4 h-4 text-green-400" />
      case 'player_thought': return <Clock className="w-4 h-4 text-purple-400" />
      case 'dice_roll': return <Dice6 className="w-4 h-4 text-green-400" />
      default: return <Clock className="w-4 h-4 text-gray-400" />
    }
  }

  // Handle combat actions
  const handleCombatAction = (action: CombatAction) => {
    console.log('Combat action selected:', action)
    // Integration with backend API will happen here
    // For now, just show a message
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: `Selected action: ${action.name} - ${action.description}`,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleEndTurn = () => {
    console.log('Ending turn')
    // Backend integration for turn management
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: 'Turn ended. Waiting for next player...',
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleRollInitiative = () => {
    setIsInCombat(true)
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: 'Combat has begun! Rolling initiative...',
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  // Handle inventory actions
  const handleUseItem = (item: any) => {
    console.log('Using item:', item)
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: `Used ${item.name}: ${item.description}`,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleEquipItem = (item: any, slot: string) => {
    console.log('Equipping item:', item, 'to slot:', slot)
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: `Equipped ${item.name} to ${slot} slot`,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleUnequipItem = (slot: string) => {
    console.log('Unequipping from slot:', slot)
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: `Unequipped item from ${slot} slot`,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleDiscardItem = (item: any) => {
    console.log('Discarding item:', item)
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'system',
      content: `Discarded ${item.name}`,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
  }

  const handleMoveItem = (fromIndex: number, toIndex: number) => {
    console.log('Moving item from', fromIndex, 'to', toIndex)
  }

  // NEW: Handle dice requirement fulfillment
  const handleDiceRequirementFulfillment = async (result: {
    dice_type: string
    rolls: number[]
    modifier: number
    total: number
    advantage?: boolean
    disadvantage?: boolean
  }) => {
    setIsDiceFulfillmentLoading(true)
    
    try {
      console.log('🎲 Fulfilling dice requirement with result:', result)
      
      // Call the fulfillment API
      const aiMessage = await gameCommunication.fulfillDiceRequirement(result)
      
      console.log('✅ Dice requirement fulfilled, AI response:', aiMessage)
      
      // Close the dice requirement modal
      setShowDiceRequirement(false)
      setDiceRequirement(null)
      
      // Add a confirmation message
      const confirmMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'dice_roll',
        content: `🎲 Rolled ${result.dice_type}: ${result.rolls.join(', ')} ${result.modifier ? `+ ${result.modifier}` : ''} = ${result.total}`,
        timestamp: new Date(),
        metadata: { dice: result.dice_type, result: result.total, rolls: result.rolls, modifier: result.modifier }
      }
      setChatMessages(prev => [...prev, confirmMessage])
      
      // The AI continuation response will be added via the onNewMessage callback
      
    } catch (error) {
      console.error('❌ Failed to fulfill dice requirement:', error)
      // Keep the modal open on error
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'system',
        content: `❌ Failed to process dice roll: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      }
      setChatMessages(prev => [...prev, errorMessage])
    } finally {
      setIsDiceFulfillmentLoading(false)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-red-900/50 backdrop-blur-sm border border-red-500/50 rounded-lg p-6 max-w-md text-center">
          <div className="text-red-400 text-xl font-semibold mb-4">⚠️ Authentication Error</div>
          <div className="text-white mb-4">{error}</div>
          <div className="space-x-4">
            <button
              onClick={() => window.location.reload()}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Refresh Page
            </button>
            <button
              onClick={() => setError(null)}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-800 text-white">
      <div className="grid grid-cols-12 gap-4 p-4 h-screen">
        
        {/* Character Panel - Left */}
        <div className="col-span-3 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-purple-500/30 p-4 overflow-y-auto">
          <div className="text-center mb-6">
            <div className="mx-auto mb-3 flex justify-center">
              <CharacterAvatar 
                character={character}
                size="xl"
                showLevel={true}
                showClass={true}
              />
            </div>
            <h2 className="text-xl font-bold text-purple-300">{character.name}</h2>
            <p className="text-sm text-gray-300">{character.race} {character.class}</p>
            <p className="text-xs text-gray-400">Level {character.level}</p>
          </div>

          {/* Health Bar */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm flex items-center gap-2">
                <Heart className="w-4 h-4 text-red-400" />
                Health
              </span>
              <span className="text-sm">{character.current_hp}/{character.max_hp}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all duration-300 ${
                  hpPercentage > 50 ? 'bg-green-500' : hpPercentage > 25 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${hpPercentage}%` }}
              />
            </div>
          </div>

          {/* Armor Class */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <Shield className="w-4 h-4 text-blue-400" />
              <span className="text-sm">Armor Class</span>
            </div>
            <div className="text-2xl font-bold text-blue-300">{character.armor_class}</div>
          </div>

          {/* Status Effects */}
          {character.status_effects.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-semibold mb-2 text-purple-300">Status Effects</h3>
              <div className="flex flex-wrap gap-1">
                {character.status_effects.map((effect, index) => (
                  <span key={index} className="px-2 py-1 bg-purple-600/30 text-xs rounded-full border border-purple-400/50">
                    {effect}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Inventory */}
          <div>
            <h3 className="text-sm font-semibold mb-3 text-purple-300">Inventory</h3>
            <div className="space-y-2">
              {character.inventory.map((item) => (
                <div key={item.id} className="bg-gray-700/50 rounded p-2 border border-gray-600/50">
                  <div className="flex justify-between items-start">
                    <span className="text-sm font-medium text-blue-300">{item.name}</span>
                    {item.quantity > 1 && (
                      <span className="text-xs text-gray-400">x{item.quantity}</span>
                    )}
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{item.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Main Game View - Center */}
        <div className="col-span-6 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-purple-500/30 flex flex-col">
          
          {/* Scene Display */}
          <SceneDisplay
            sceneName={gameState.current_scene}
            sceneImageUrl={gameState.scene_image_url}
            location={gameState.current_location}
            sceneType={gameState.scene_type}
            onImageLoad={() => console.log('Scene image loaded')}
            onImageError={() => console.log('Scene image failed to load')}
          />

          {/* Chat Messages */}
          <div 
            ref={setChatContainerRef}
            className="h-96 p-4 overflow-y-auto space-y-3"
          >
            {chatMessages.map((message) => {
              const isPlayerMessage = ['player_action', 'player_speech', 'player_thought'].includes(message.type)
              
              return (
                <div key={message.id} className={`flex gap-3 ${
                  isPlayerMessage ? 'justify-end' : 'justify-start'
                }`}>
                  {/* Avatar for non-player messages */}
                  {!isPlayerMessage && (
                    <div className="flex-shrink-0">
                      {message.type === 'dm_narration' ? (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center text-white text-sm font-bold">
                          DM
                        </div>
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
                          {getMessageIcon(message.type)}
                        </div>
                      )}
                    </div>
                  )}

                  <div className={`max-w-xs lg:max-w-md xl:max-w-lg ${
                    message.type === 'player_action' 
                      ? 'bg-blue-600/30 border-blue-400/50' 
                      : message.type === 'player_speech'
                      ? 'bg-green-600/30 border-green-400/50'
                      : message.type === 'player_thought'
                      ? 'bg-purple-600/30 border-purple-400/50'
                      : message.type === 'dice_roll'
                      ? 'bg-yellow-600/30 border-yellow-400/50'
                      : message.type === 'dm_narration' && message.metadata?.combat_detected
                      ? 'bg-red-600/30 border-red-400/50'
                      : 'bg-purple-600/30 border-purple-400/50'
                  } rounded-lg p-3 border`}>
                    <div className="flex items-center gap-2 mb-1">
                      {isPlayerMessage && getMessageIcon(message.type)}
                      <span className="text-xs text-gray-400">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {isPlayerMessage && (
                        <span className={`text-xs font-medium ${
                          message.type === 'player_action' ? 'text-blue-300' :
                          message.type === 'player_speech' ? 'text-green-300' :
                          'text-purple-300'
                        }`}>
                          {message.type === 'player_action' ? 'Action' :
                           message.type === 'player_speech' ? 'Speech' : 'Thought'}
                        </span>
                      )}
                      {/* Combat Detection Indicator for DM messages */}
                      {message.type === 'dm_narration' && message.metadata?.combat_detected && (
                        <span className="text-xs font-medium bg-red-500/20 border border-red-400/50 rounded px-2 py-1 text-red-300 flex items-center gap-1">
                          ⚔️ Combat Initiated
                        </span>
                      )}
                    </div>
                    <div className="flex items-start gap-2">
                      <p className={`text-sm leading-relaxed flex-1 ${
                        message.type === 'player_thought' ? 'italic' : ''
                      }`}>
                        {message.type === 'player_speech' && '"'}{message.content}{message.type === 'player_speech' && '"'}
                      </p>
                      
                      {/* TTS Button for DM narration */}
                      {message.type === 'dm_narration' && (
                        <TTSButton 
                          text={message.content}
                          size="sm"
                          showText={false}
                          voice={ttsSettings.voice}
                          model={ttsSettings.model}
                          className="flex-shrink-0"
                        />
                      )}
                    </div>
                    
                    {/* Enhanced dice roll display */}
                    {message.type === 'dice_roll' && message.metadata && (
                      <div className="mt-2 text-xs">
                        {message.metadata.rolls && (
                          <div className="flex items-center gap-1 text-gray-400">
                            <span>Rolls: {message.metadata.rolls.join(', ')}</span>
                            {message.metadata.total === 20 && message.metadata.diceType?.includes('d20') && (
                              <span className="text-green-400 font-medium">🎉 Crit!</span>
                            )}
                            {message.metadata.total === 1 && message.metadata.diceType?.includes('d20') && (
                              <span className="text-red-400 font-medium">💥 Fail!</span>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {/* Combat Detection Metadata for DM messages */}
                    {message.type === 'dm_narration' && message.metadata && (
                      <div className="mt-2 text-xs space-y-1">
                        {message.metadata.combat_detected && (
                          <div className="bg-red-900/30 border border-red-500/30 rounded p-2">
                            <div className="flex items-center gap-2 text-red-300 font-medium mb-1">
                              ⚔️ Combat Status
                            </div>
                            <div className="text-gray-300 space-y-1">
                              <div>• Combat events: {message.metadata.combat_events_count || 0}</div>
                              {message.metadata.parsing_confidence && (
                                <div>• Detection confidence: {(message.metadata.parsing_confidence * 100).toFixed(0)}%</div>
                              )}
                              {message.metadata.dice_required && message.metadata.dice_required.length > 0 && (
                                <div>• Dice required: {message.metadata.dice_required.map((d: any) => d.expression).join(', ')}</div>
                              )}
                            </div>
                          </div>
                        )}
                        {message.metadata.model_used && (
                          <div className="text-gray-500">
                            AI Model: {message.metadata.model_used}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Avatar for player messages */}
                  {isPlayerMessage && (
                    <div className="flex-shrink-0">
                      <CharacterAvatar 
                        character={character}
                        size="sm"
                      />
                    </div>
                  )}
                </div>
              )
            })}
            {isTyping && (
              <div className="flex gap-3 justify-start">
                <div className="bg-purple-600/30 border-purple-400/50 rounded-lg p-3 border">
                  <div className="flex items-center gap-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                    <span className="text-xs text-gray-400">AI DM is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Input */}
          <div className="p-4 border-t border-gray-600/50">
            {/* Connection Status */}
            <div className="flex justify-between items-center mb-3">
              <CompactConnectionStatus
                status={gameCommunication.connectionStatus}
                isLoading={gameCommunication.isLoading}
                error={gameCommunication.error}
                onReconnect={gameCommunication.connect}
              />
              {gameCommunication.isLoading && (
                <span className="text-xs text-blue-400">Processing...</span>
              )}
            </div>
            
            {/* Scene Type Quick Change (for testing) */}
            <div className="flex gap-1 mb-2">
              {[
                { type: 'exploration', label: '🗺️ Explore', color: 'green' },
                { type: 'combat', label: '⚔️ Combat', color: 'red' },
                { type: 'dialogue', label: '💬 Talk', color: 'purple' },
                { type: 'story_narration', label: '📜 Story', color: 'gray' }
              ].map(({ type, label, color }) => (
                <button
                  key={type}
                  onClick={() => setGameState(prev => ({ ...prev, scene_type: type as any }))}
                  className={`px-2 py-1 bg-${color}-600/30 hover:bg-${color}-600/50 border border-${color}-400/50 rounded text-xs transition-colors ${
                    gameState.scene_type === type ? `bg-${color}-600/50` : ''
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
            
            {/* Enhanced User Input Handler */}
            <UserInputHandler
              onSubmitAction={handlePlayerInput}
              onRollDice={rollDice}
              isProcessing={gameCommunication.isLoading || isTyping}
              placeholder="Describe your action, speech, or thoughts..."
            />
          </div>
        </div>

        {/* Location/Map Panel - Right */}
        <div className="col-span-3 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-purple-500/30 p-4 overflow-y-auto">
          
          {/* Story Progress Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowStoryProgress(!showStoryProgress)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showStoryProgress 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              📖 {showStoryProgress ? 'Hide' : 'Show'} Story Progress
            </button>
          </div>

          {/* Dice Roller Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowDiceRoller(!showDiceRoller)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showDiceRoller 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              🎲 {showDiceRoller ? 'Hide' : 'Show'} Dice Roller
            </button>
          </div>

          {/* Combat HUD Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowCombatHUD(!showCombatHUD)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showCombatHUD 
                  ? 'bg-red-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              ⚔️ {showCombatHUD ? 'Hide' : 'Show'} Combat HUD
            </button>
          </div>

          {/* Inventory Panel Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowEnhancedInventory(!showEnhancedInventory)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showEnhancedInventory 
                  ? 'bg-orange-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              🎒 {showEnhancedInventory ? 'Hide' : 'Show'} Inventory
            </button>
          </div>

          {/* Character Progression Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowCharacterProgression(!showCharacterProgression)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showCharacterProgression 
                  ? 'bg-yellow-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              ⭐ {showCharacterProgression ? 'Hide' : 'Show'} Progression
            </button>
          </div>

          {/* Quest Manager Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowQuestManager(!showQuestManager)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showQuestManager 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              <Scroll className="w-4 h-4 inline mr-2" />
              {showQuestManager ? 'Hide' : 'Show'} Quests
            </button>
          </div>

          {/* Journal System Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowJournalSystem(!showJournalSystem)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showJournalSystem 
                  ? 'bg-indigo-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              <Book className="w-4 h-4 inline mr-2" />
              {showJournalSystem ? 'Hide' : 'Show'} Journal
            </button>
          </div>

          {/* Narrative Context Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowNarrativeContext(!showNarrativeContext)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showNarrativeContext 
                  ? 'bg-purple-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              <History className="w-4 h-4 inline mr-2" />
              {showNarrativeContext ? 'Hide' : 'Show'} Story Context
            </button>
          </div>

          {/* Settings Toggle */}
          <div className="mb-4">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`w-full px-3 py-2 rounded text-sm font-medium transition-colors ${
                showSettings 
                  ? 'bg-gray-600 text-white' 
                  : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
              }`}
            >
              <Settings className="w-4 h-4 inline mr-2" />
              {showSettings ? 'Hide' : 'Show'} Settings
            </button>
          </div>

          {/* TTS Controls */}
          <div className="mb-4 space-y-2">
            {/* Quick TTS Toggle */}
            <div className="bg-gray-800/30 rounded-lg p-3 border border-purple-500/20">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-purple-300 font-medium text-sm">🎤 Auto-play TTS</span>
                  {ttsSettings.autoPlay && (
                    <span className="text-xs bg-green-600/30 text-green-300 px-2 py-0.5 rounded">ON</span>
                  )}
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={ttsSettings.autoPlay}
                    onChange={(e) => {
                      const newSettings = { ...ttsSettings, autoPlay: e.target.checked };
                      setTtsSettings(newSettings);
                      localStorage.setItem('tts-settings', JSON.stringify(newSettings));
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-gray-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
              <p className="text-xs text-gray-400">
                Voice: {ttsSettings.voice} • Model: {ttsSettings.model === 'gpt-4o-mini-tts' ? 'GPT-4o Mini' : ttsSettings.model.toUpperCase()}
              </p>
            </div>

            {/* Full Settings Button */}
            <button
              onClick={() => setShowTTSSettings(true)}
              className="w-full px-3 py-2 rounded text-sm font-medium transition-colors bg-gray-700/50 text-gray-300 hover:bg-gray-600/50 border border-gray-600/30"
            >
              ⚙️ Advanced TTS Settings
            </button>
          </div>

          {/* Story Progress Panel */}
          {showStoryProgress && (
            <div className="mb-6">
              <StoryProgressTracker
                currentStage={storyProgress.currentStage}
                stagesCompleted={storyProgress.stagesCompleted}
                storyCompleted={storyProgress.storyCompleted}
                compact={true}
              />
            </div>
          )}

          {/* Dice Roller Panel */}
          {showDiceRoller && (
            <div className="mb-6">
              <DiceRoller
                onRollComplete={(roll) => {
                  const newMessage: ChatMessage = {
                    id: Date.now().toString(),
                    type: 'dice_roll',
                    content: `${roll.label || 'Rolled'} ${roll.diceType}${roll.modifier !== 0 ? ` ${roll.modifier >= 0 ? '+' : ''}${roll.modifier}` : ''}: ${roll.total}`,
                    timestamp: new Date(),
                    metadata: roll
                  }
                  setChatMessages(prev => [...prev, newMessage])
                }}
              />
            </div>
          )}
          
          {/* Current Location */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <MapPin className="w-5 h-5 text-yellow-400" />
              <h3 className="font-semibold text-yellow-300">Current Location</h3>
            </div>
            <div className="bg-gray-700/50 rounded p-3 border border-gray-600/50">
              <p className="text-sm font-medium text-blue-300">{gameState.current_location}</p>
            </div>
          </div>

          {/* Mini Map Placeholder */}
          <div className="mb-6">
            <h3 className="font-semibold mb-3 text-yellow-300">Region Map</h3>
            <div className="bg-gray-700/50 rounded p-3 border border-gray-600/50 h-32 flex items-center justify-center">
              <p className="text-xs text-gray-400 text-center">Interactive map<br/>coming soon</p>
            </div>
          </div>

          {/* Objectives */}
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <Target className="w-5 h-5 text-green-400" />
              <h3 className="font-semibold text-green-300">Objectives</h3>
            </div>
            <div className="space-y-2">
              {gameState.objectives.map((objective, index) => (
                <div key={index} className="bg-gray-700/50 rounded p-2 border border-gray-600/50">
                  <div className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full mt-1.5 flex-shrink-0"></div>
                    <p className="text-sm text-gray-300">{objective}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Events */}
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Clock className="w-5 h-5 text-blue-400" />
              <h3 className="font-semibold text-blue-300">Recent Events</h3>
            </div>
            <div className="space-y-2">
              {gameState.recent_events.map((event, index) => (
                <div key={index} className="bg-gray-700/50 rounded p-2 border border-gray-600/50">
                  <p className="text-sm text-gray-300">{event}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Combat HUD Overlay */}
      {showCombatHUD && (
        <div className="fixed top-4 left-4 z-40 w-80">
          <CombatHUD
            playerCharacter={character}
            combatEntities={combatEntities}
            currentTurn={currentTurn}
            isInCombat={isInCombat}
            availableActions={availableActions}
            onActionSelect={handleCombatAction}
            onEndTurn={handleEndTurn}
            onRollInitiative={handleRollInitiative}
          />
        </div>
      )}

      {/* Enhanced Inventory Panel Modal */}
      <EnhancedInventoryPanel
        character={{
          id: character.id,
          name: character.name,
          race: character.race,
          character_class: character.class,
          level: character.level,
          current_hp: character.current_hp,
          max_hp: character.max_hp,
          armor_class: character.armor_class,
          inventory: (character.inventory || []).map(item => ({
            ...item,
            rarity: item.rarity || 'common' as const
          }))
        }}
        inventory={(character.inventory || []).map(item => ({
          ...item,
          rarity: item.rarity || 'common' as const
        }))}
        isOpen={showEnhancedInventory}
        onClose={() => setShowEnhancedInventory(false)}
        onUseItem={handleUseItem}
        onEquipItem={handleEquipItem}
        onUnequipItem={handleUnequipItem}
        onDiscardItem={handleDiscardItem}
        onMoveItem={handleMoveItem}
      />

      {/* Quest Manager Modal */}
      <QuestManager
        isOpen={showQuestManager}
        onClose={() => setShowQuestManager(false)}
        character={{
          id: character.id,
          name: character.name,
          level: character.level
        }}
      />

      {/* Journal System Modal */}
      <JournalSystem
        isOpen={showJournalSystem}
        onClose={() => setShowJournalSystem(false)}
        character={{
          id: character.id,
          name: character.name,
          level: character.level
        }}
      />

      {/* Settings Panel Modal */}
      <SettingsPanel
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onSettingsChange={(settings) => {
          console.log('Settings updated:', settings)
          // Handle settings changes - could update game behavior
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: '⚙️ Settings updated successfully!',
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, newMessage])
        }}
      />

      {/* Character Progression Panel Modal */}
      <CharacterProgressionPanel
        character={{
          id: character.id,
          name: character.name,
          race: character.race,
          character_class: character.class,
          level: character.level,
          xp_current: 4200, // Mock XP data
          xp_to_next_level: 2300,
          hit_points: character.current_hp,
          max_hit_points: character.max_hp,
          armor_class: character.armor_class,
          proficiency_bonus: Math.max(2, Math.floor((character.level - 1) / 4) + 2),
          abilities: {
            strength: 16,
            dexterity: 14,
            constitution: 15,
            intelligence: 12,
            wisdom: 13,
            charisma: 18 // Mock ability scores
          }
        }}
        isOpen={showCharacterProgression}
        onClose={() => setShowCharacterProgression(false)}
        onLevelUp={() => {
          console.log('Level up triggered!');
          // Integration with backend API will happen here
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: `🎉 ${character.name} leveled up! New abilities and features unlocked.`,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, newMessage]);
        }}
        onSkillUpgrade={(skillId) => {
          console.log('Skill upgrade:', skillId);
          // Integration with backend API will happen here
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: `📈 Skill upgraded: ${skillId}. New bonuses applied!`,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, newMessage]);
        }}
        onAllocateAttributePoint={(attribute) => {
          console.log('Attribute upgrade:', attribute);
          // Integration with backend API will happen here
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: `💪 ${attribute} increased! Character stats improved.`,
            timestamp: new Date()
          };
          setChatMessages(prev => [...prev, newMessage]);
        }}
      />

      {/* Narrative Context Display */}
      <NarrativeContextDisplay
        isOpen={showNarrativeContext}
        onToggle={() => setShowNarrativeContext(!showNarrativeContext)}
        majorDecisions={narrativeData.majorDecisions}
        npcStatuses={narrativeData.npcStatuses}
        worldState={narrativeData.worldState}
      />

      {/* TTS Settings Modal */}
      <TTSSettings
        isOpen={showTTSSettings}
        onClose={() => setShowTTSSettings(false)}
        onSettingsChange={(newSettings) => {
          setTtsSettings(newSettings);
          // Save to localStorage
          if (typeof window !== 'undefined') {
            localStorage.setItem('tts-settings', JSON.stringify(newSettings));
          }
          const newMessage: ChatMessage = {
            id: Date.now().toString(),
            type: 'system',
            content: `🎤 TTS Settings updated! Voice: ${newSettings.voice}, Model: ${newSettings.model}${newSettings.autoPlay ? ', Auto-play enabled' : ''}`,
            timestamp: new Date()
          }
          setChatMessages(prev => [...prev, newMessage]);
        }}
        currentSettings={ttsSettings}
      />

      {/* NEW: Dice Requirement Modal */}
      <DiceRequirementModal
        isOpen={showDiceRequirement}
        requirement={diceRequirement}
        onRollDice={handleDiceRequirementFulfillment}
        onClose={() => {
          setShowDiceRequirement(false)
          setDiceRequirement(null)
        }}
        isLoading={isDiceFulfillmentLoading}
      />
    </div>
  )
}

export default ImmersiveDnDInterface 