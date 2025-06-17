import { useState, useEffect, useCallback, useRef } from 'react'
import { apiClient } from '@/lib/api'
import type {
  Character,
  GameState,
  ChatMessage,
  DiceRoll,
  PlayerAction,
  ConnectionStatus,
  ApiResponse
} from '@/types/game'

interface UseGameCommunicationProps {
  gameId?: string
  characterId?: number
  authToken?: string | null
  tokenRefreshCallback?: () => Promise<string | null>
  onNewMessage?: (message: ChatMessage) => void
  onGameStateUpdate?: (gameState: Partial<GameState>) => void
  onCharacterUpdate?: (character: Partial<Character>) => void
  onConnectionChange?: (status: ConnectionStatus) => void
}

interface GameCommunicationState {
  isConnected: boolean
  connectionStatus: ConnectionStatus
  isLoading: boolean
  error: string | null
  lastPing: Date | null
  sessionId: string | null
}

export function useGameCommunication(props: UseGameCommunicationProps = {}) {
  const {
    gameId = 'default',
    characterId = 1,
    authToken,
    tokenRefreshCallback,
    onNewMessage,
    onGameStateUpdate,
    onCharacterUpdate,
    onConnectionChange
  } = props

  // State management
  const [state, setState] = useState<GameCommunicationState>({
    isConnected: false,
    connectionStatus: 'disconnected',
    isLoading: false,
    error: null,
    lastPing: null,
    sessionId: null
  })

  // Refs for cleanup
  const connectionCheckInterval = useRef<NodeJS.Timeout | null>(null)
  const pingInterval = useRef<NodeJS.Timeout | null>(null)

  // Set auth token and refresh callback on apiClient when they change
  useEffect(() => {
    if (authToken !== undefined) {
      apiClient.setAuthToken(authToken)
    }
    if (tokenRefreshCallback) {
      apiClient.setTokenRefreshCallback(tokenRefreshCallback)
    }
  }, [authToken, tokenRefreshCallback])

  // Update connection status
  const updateConnectionStatus = useCallback((status: ConnectionStatus, error?: string) => {
    setState(prev => ({
      ...prev,
      connectionStatus: status,
      isConnected: status === 'connected',
      error: error || null
    }))
    onConnectionChange?.(status)
  }, [onConnectionChange])

  // Setup WebSocket event listeners
  useEffect(() => {
    // Connection status events
    const handleConnection = (data: { status: string; error?: any; reason?: string }) => {
      console.log('🔗 Connection status changed:', data)
      
      // Handle cases where data might be undefined or malformed
      if (!data || typeof data !== 'object') {
        console.warn('⚠️ Received invalid connection data:', data)
        return
      }
      
      switch (data.status) {
        case 'connected':
          updateConnectionStatus('connected')
          break
        case 'disconnected':
          updateConnectionStatus('disconnected', data.reason)
          break
        case 'error':
          updateConnectionStatus('error', data.error?.message || 'Connection error')
          break
        case 'failed':
          updateConnectionStatus('error', 'Failed to connect after multiple attempts')
          break
        default:
          console.warn('⚠️ Unknown connection status:', data.status)
          updateConnectionStatus('disconnected')
      }
    }

    // Chat message events
    const handleChatMessage = (data: ChatMessage) => {
      console.log('💬 New chat message:', data)
      onNewMessage?.(data)
    }

    // Game state update events
    const handleGameStateUpdate = (data: Partial<GameState>) => {
      console.log('🎮 Game state updated:', data)
      onGameStateUpdate?.(data)
    }

    // Character update events
    const handleCharacterUpdate = (data: Partial<Character>) => {
      console.log('👤 Character updated:', data)
      onCharacterUpdate?.(data)
    }

    // Scene change events
    const handleSceneChange = (data: any) => {
      console.log('🎭 Scene changed:', data)
      if (data.game_state_updates) {
        onGameStateUpdate?.(data.game_state_updates)
      }
    }

    // System notifications
    const handleSystemNotification = (data: any) => {
      console.log('🔔 System notification:', data)
      // Handle system notifications (errors, warnings, etc.)
    }

    // Register WebSocket event listeners
    apiClient.on('connection', handleConnection)
    apiClient.on('chat_message', handleChatMessage)
    apiClient.on('game_state_update', handleGameStateUpdate)
    apiClient.on('character_update', handleCharacterUpdate)
    apiClient.on('scene_change', handleSceneChange)
    apiClient.on('system_notification', handleSystemNotification)

    // Cleanup function
    return () => {
      apiClient.off('connection', handleConnection)
      apiClient.off('chat_message', handleChatMessage)
      apiClient.off('game_state_update', handleGameStateUpdate)
      apiClient.off('character_update', handleCharacterUpdate)
      apiClient.off('scene_change', handleSceneChange)
      apiClient.off('system_notification', handleSystemNotification)
    }
  }, [onNewMessage, onGameStateUpdate, onCharacterUpdate, updateConnectionStatus])

  // Connection monitoring
  useEffect(() => {
    // Check connection status periodically
    connectionCheckInterval.current = setInterval(() => {
      const currentStatus = apiClient.connectionState as ConnectionStatus
      if (currentStatus !== state.connectionStatus) {
        updateConnectionStatus(currentStatus)
      }
    }, 1000)

    // Send periodic pings to maintain connection
    pingInterval.current = setInterval(() => {
      if (apiClient.isConnected) {
        const pingTime = new Date()
        apiClient.send('ping', { timestamp: pingTime.toISOString() })
        setState(prev => ({ ...prev, lastPing: pingTime }))
      }
    }, 30000) // Ping every 30 seconds

    return () => {
      if (connectionCheckInterval.current) {
        clearInterval(connectionCheckInterval.current)
      }
      if (pingInterval.current) {
        clearInterval(pingInterval.current)
      }
    }
  }, [state.connectionStatus, updateConnectionStatus])

  // API Methods
  const sendPlayerAction = useCallback(async (
    type: 'action' | 'speech' | 'thought',
    content: string
  ): Promise<ChatMessage | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      console.log('🚀 Sending player action:', { type, content, characterId, gameId })
      
      const response = await apiClient.sendPlayerAction(gameId, {
        type,
        content,
        character_id: characterId
      })

      console.log('📡 Raw API response:', response)
      console.log('📦 Response data:', response.data)

      if (response.success && response.data) {
        console.log('✅ API call successful, processing response...')
        
        // Log the structure of the response data
        console.log('🔍 Response structure check:')
        console.log('  - player_message exists:', !!response.data.player_message)
        console.log('  - ai_response exists:', !!response.data.ai_response)
        console.log('  - game_state_updates exists:', !!response.data.game_state_updates)
        
        if (response.data.player_message) {
          console.log('👤 Player message data:', response.data.player_message)
        }
        
        if (response.data.ai_response) {
          console.log('🤖 AI response data:', response.data.ai_response)
        } else {
          console.warn('⚠️ No AI response in backend response! This might be the issue.')
          console.log('🔍 Full response.data keys:', Object.keys(response.data))
        }

        // Create player message from the response
        const playerMessage: ChatMessage = {
          id: response.data.player_message.id,
          type: response.data.player_message.type as any,
          content: response.data.player_message.content,
          timestamp: new Date(response.data.player_message.timestamp),
          character_id: characterId
        }

        console.log('👤 Created player message:', playerMessage)

        // Create AI response message if present
        let aiMessage: ChatMessage | null = null
        if (response.data.ai_response) {
          aiMessage = {
            id: response.data.ai_response.id,
            type: response.data.ai_response.type as any,
            content: response.data.ai_response.content,
            timestamp: new Date(response.data.ai_response.timestamp)
          }
          console.log('🤖 Created AI message:', aiMessage)
          console.log('🤖 AI message content length:', aiMessage.content?.length || 0)
          console.log('🤖 AI message content preview:', aiMessage.content?.substring(0, 100) + '...')
        } else {
          console.warn('⚠️ No AI response to process - AI message will be null')
        }

        // Trigger callbacks for the messages
        console.log('📤 Calling onNewMessage for player message...')
        onNewMessage?.(playerMessage)
        
        if (aiMessage) {
          console.log('📤 Scheduling AI message callback in 500ms...')
          // Add a small delay to make the AI response feel more natural
          setTimeout(() => {
            console.log('📤 Calling onNewMessage for AI message...')
            onNewMessage?.(aiMessage)
          }, 500)
        } else {
          console.warn('❌ No AI message to schedule - user will not see AI response')
        }

        // Also send via WebSocket for real-time updates
        console.log('📡 Sending WebSocket update...')
        apiClient.send('player_action', {
          game_id: gameId,
          player_message: playerMessage,
          ai_response: aiMessage,
          game_state_updates: response.data.game_state_updates
        })

        setState(prev => ({ ...prev, isLoading: false }))
        
        // Return the player message (AI response will be handled via callback)
        return playerMessage
      } else {
        const errorMsg = response.error || 'Failed to send action'
        console.error('❌ API call failed:', errorMsg)
        console.error('❌ Full response:', response)
        throw new Error(errorMsg)
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      console.error('💥 Exception in sendPlayerAction:', error)
      console.error('💥 Error details:', {
        message: errorMessage,
        stack: error instanceof Error ? error.stack : 'No stack trace'
      })
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      return null
    }
  }, [gameId, characterId])

  const rollDice = useCallback(async (diceData: {
    dice_type: string
    count?: number
    modifier?: number
    label?: string
  }): Promise<DiceRoll | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.rollDice(diceData)

      if (response.success && response.data) {
        const diceRoll: DiceRoll = {
          diceType: response.data.dice,
          count: diceData.count || 1,
          modifier: response.data.modifier,
          rolls: [response.data.result], // Backend should provide individual rolls
          total: response.data.total,
          label: diceData.label,
          critical: response.data.total === 20 && diceData.dice_type === 'd20',
          timestamp: new Date()
        }

        // Send via WebSocket for real-time updates
        apiClient.send('dice_roll', {
          game_id: gameId,
          character_id: characterId,
          roll: diceRoll
        })

        setState(prev => ({ ...prev, isLoading: false }))
        return diceRoll
      } else {
        throw new Error(response.error || 'Failed to roll dice')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to roll dice:', error)
      return null
    }
  }, [gameId, characterId])

  const updateCharacter = useCallback(async (updates: Partial<Character>): Promise<boolean> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.updateCharacter(characterId, updates)

      if (response.success) {
        // Send via WebSocket for real-time updates
        apiClient.send('character_update', {
          game_id: gameId,
          character_id: characterId,
          updates
        })

        setState(prev => ({ ...prev, isLoading: false }))
        return true
      } else {
        throw new Error(response.error || 'Failed to update character')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to update character:', error)
      return false
    }
  }, [gameId, characterId])

  const loadCharacter = useCallback(async (): Promise<Character | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.getCharacter(characterId)

      if (response.success && response.data) {
        setState(prev => ({ ...prev, isLoading: false }))
        return response.data
      } else {
        throw new Error(response.error || 'Failed to load character')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to load character:', error)
      return null
    }
  }, [characterId])

  const loadGameState = useCallback(async (): Promise<GameState | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.getGameState(gameId)

      if (response.success && response.data) {
        setState(prev => ({ ...prev, isLoading: false }))
        return response.data
      } else {
        throw new Error(response.error || 'Failed to load game state')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to load game state:', error)
      return null
    }
  }, [gameId])

  const generateSceneImage = useCallback(async (description: string): Promise<string | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.generateSceneImage(description)

      if (response.success && response.data) {
        setState(prev => ({ ...prev, isLoading: false }))
        return response.data.image_url
      } else {
        throw new Error(response.error || 'Failed to generate scene image')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to generate scene image:', error)
      return null
    }
  }, [])

  // NEW: Get game status including dice requirements
  const getGameStatus = useCallback(async (): Promise<{
    story_id: number
    story_completed: boolean
    current_stage: string
    character?: any
    world_state?: {
      current_location: string
      real_time_played: number
      story_time_elapsed: number
      waiting_for_dice: boolean
      pending_dice_requirement?: any
    }
    ai_available: boolean
  } | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      const response = await apiClient.getGameStatus(gameId)

      if (response.success && response.data) {
        setState(prev => ({ ...prev, isLoading: false }))
        return response.data
      } else {
        throw new Error(response.error || 'Failed to get game status')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to get game status:', error)
      return null
    }
  }, [gameId])

  // NEW: Start orchestration session
  const startOrchestrationSession = useCallback(async (userId: string): Promise<string | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      console.log('🚀 Starting orchestration session for character:', characterId)
      
      const response = await apiClient.startOrchestrationSession(userId, characterId)

      if (response.success && response.data) {
        const sessionId = response.data.session_id
        setState(prev => ({ 
          ...prev, 
          isLoading: false,
          sessionId: sessionId
        }))
        
        console.log('✅ Orchestration session started:', sessionId)
        
        // Handle initial narrative from session start
        if (response.data.narrative_text) {
          const initialMessage: ChatMessage = {
            id: `dm_start_${Date.now()}`,
            type: 'dm_narration' as any,
            content: response.data.narrative_text,
            timestamp: new Date(),
            metadata: {
              generated_by: 'orchestration',
              session_start: true,
              result_type: response.data.result_type
            }
          }
          onNewMessage?.(initialMessage)
        }
        
        return sessionId
      } else {
        throw new Error(response.error || 'Failed to start orchestration session')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      console.error('Failed to start orchestration session:', error)
      return null
    }
  }, [characterId, onNewMessage])

  // NEW: Fulfill dice requirement and continue narrative
  const fulfillDiceRequirement = useCallback(async (diceResult: {
    dice_type: string
    rolls: number[]
    modifier: number
    total: number
    advantage?: boolean
    disadvantage?: boolean
  }): Promise<ChatMessage | null> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }))

    try {
      console.log('🎲 Fulfilling dice requirement:', diceResult)
      
      // Use tracked sessionId, fallback to gameId if session not started yet
      const sessionId = state.sessionId || gameId
      
      if (!state.sessionId) {
        console.warn('⚠️ No orchestration session ID found, using gameId as fallback:', gameId)
      }
      
      const response = await apiClient.fulfillDiceRequirement(sessionId, diceResult)

      if (response.success && response.data) {
        console.log('✅ Dice requirement fulfilled successfully via orchestration')
        
        // Create AI response message from orchestration narrative
        let aiMessage: ChatMessage | null = null
        if (response.data.narrative_text) {
          aiMessage = {
            id: `dm_dice_${Date.now()}`,
            type: 'dm_narration' as any,
            content: response.data.narrative_text,
            timestamp: new Date(),
            metadata: {
              generated_by: 'orchestration',
              dice_continuation: true,
              result_type: response.data.result_type
            }
          }
          console.log('🤖 AI orchestration continuation message:', aiMessage)
          
          // Trigger callback for AI continuation
          onNewMessage?.(aiMessage)
        }

        // Handle game state updates from orchestration
        if (response.data.state_changes && response.data.state_changes.length > 0) {
          const stateUpdates = response.data.state_changes.reduce((acc, change) => {
            return { ...acc, ...change }
          }, {})
          onGameStateUpdate?.(stateUpdates)
        }

        // Send via WebSocket for real-time updates
        apiClient.send('dice_fulfilled', {
          session_id: sessionId,
          dice_result: diceResult,
          ai_response: aiMessage,
          orchestration_response: response.data
        })

        setState(prev => ({ ...prev, isLoading: false }))
        return aiMessage
      } else {
        throw new Error(response.error || 'Failed to fulfill dice requirement')
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      console.error('💥 Exception in fulfillDiceRequirement:', error)
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }))
      return null
    }
  }, [state.sessionId, gameId, onNewMessage, onGameStateUpdate])

  // Manual connection control
  const connect = useCallback(() => {
    if (!apiClient.isConnected) {
      // Force reconnection
      apiClient.disconnect()
      setTimeout(() => {
        // The apiClient will automatically try to reconnect
        updateConnectionStatus('connecting')
      }, 100)
    }
  }, [updateConnectionStatus])

  const disconnect = useCallback(() => {
    apiClient.disconnect()
    updateConnectionStatus('disconnected')
  }, [updateConnectionStatus])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (connectionCheckInterval.current) {
        clearInterval(connectionCheckInterval.current)
      }
      if (pingInterval.current) {
        clearInterval(pingInterval.current)
      }
    }
  }, [])

  return {
    // State
    ...state,
    
    // API Methods
    sendPlayerAction,
    rollDice,
    updateCharacter,
    loadCharacter,
    loadGameState,
    generateSceneImage,
    getGameStatus,
    startOrchestrationSession,
    fulfillDiceRequirement,
    
    // Connection Control
    connect,
    disconnect,
    
    // Utilities
    sendWebSocketMessage: (type: string, data: any) => apiClient.send(type, data),
    connectionState: apiClient.connectionState,
    apiClient
  }
} 