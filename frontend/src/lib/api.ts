import { Character, GameState, ChatMessage } from '@/types/game'

// Base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
const WS_URL = API_BASE_URL.replace('http', 'ws')

// Response types
interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

interface DiceRollResponse {
  roll_type: string
  dice: string
  result: number
  modifier: number
  total: number
  breakdown: string
  timestamp: string
  individual_rolls: number[]
  critical: boolean
}

interface GameActionResponse {
  success: boolean
  message_id: string
  player_message: {
    id: string
    type: string
    content: string
    timestamp: string
    character_name: string
    metadata?: any
  }
  ai_response?: {
    id: string
    type: string
    content: string
    timestamp: string
    metadata?: any
  }
  game_state_updates?: {
    real_time_played?: number
    [key: string]: any
  }
}

// WebSocket event types
interface WebSocketMessage {
  type: 'chat_message' | 'game_state_update' | 'character_update' | 'scene_change' | 'system_notification'
  data: any
  timestamp: string
}

class ApiClient {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectInterval = 1000
  private wsEventListeners: Map<string, Function[]> = new Map()
  private authToken: string | null = null
  private tokenRefreshCallback: (() => Promise<string | null>) | null = null

  constructor() {
    // Don't initialize WebSocket immediately - wait until it's needed
    // This prevents connection attempts before the page is fully loaded
  }

  // Method to set authentication token
  setAuthToken(token: string | null) {
    this.authToken = token
  }

  // Method to set token refresh callback
  setTokenRefreshCallback(callback: () => Promise<string | null>) {
    this.tokenRefreshCallback = callback
  }

  // HTTP Methods with automatic token refresh
  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount: number = 0
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${API_BASE_URL}${endpoint}`
      const config: RequestInit = {
        headers: {
          'Content-Type': 'application/json',
          ...(this.authToken && { 'Authorization': `Bearer ${this.authToken}` }),
          ...options.headers,
        },
        ...options,
      }

      console.log('🌐 Making HTTP request:', {
        method: options.method || 'GET',
        url,
        hasAuthToken: !!this.authToken,
        headers: config.headers,
        body: options.body
      })

      const response = await fetch(url, config)
      
      console.log('🌐 HTTP response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      })
      
      const data = await response.json()
      
      console.log('🌐 Parsed response data:', data)

      // Handle authentication errors with token refresh
      if (response.status === 401 && retryCount === 0 && this.tokenRefreshCallback) {
        console.log('🔄 Token expired, attempting refresh...')
        try {
          const newToken = await this.tokenRefreshCallback()
          if (newToken) {
            this.setAuthToken(newToken)
            return this.request(endpoint, options, retryCount + 1)
          }
        } catch (refreshError) {
          console.error('❌ Token refresh failed:', refreshError)
        }
      }

      if (!response.ok) {
        const errorMessage = data.detail || `HTTP ${response.status}: ${response.statusText}`
        console.error('🌐 HTTP request failed:', errorMessage)
        throw new Error(errorMessage)
      }

      const result = {
        success: true,
        data: data.data || data,
        message: data.message
      }
      
      console.log('🌐 Final processed result:', result)
      
      return result
    } catch (error) {
      console.error(`🌐 API Error (${endpoint}):`, error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      }
    }
  }

  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }

  // Game-specific API methods
  async getCharacter(characterId: number): Promise<ApiResponse<Character>> {
    return this.get<Character>(`/characters/${characterId}`)
  }

  async updateCharacter(characterId: number, updates: Partial<Character>): Promise<ApiResponse<Character>> {
    return this.put<Character>(`/characters/${characterId}`, updates)
  }

  async getGameState(gameId: string): Promise<ApiResponse<GameState>> {
    return this.get<GameState>(`/games/${gameId}/state`)
  }

  async sendPlayerAction(gameId: string, action: {
    type: 'action' | 'speech' | 'thought'
    content: string
    character_id: number
  }): Promise<ApiResponse<GameActionResponse>> {
    // Transform to match new backend structure
    const requestData = {
      action_type: action.type,
      content: action.content,
      metadata: {
        character_id: action.character_id
      }
    }
    
    console.log('🎯 ApiClient.sendPlayerAction called:', {
      gameId,
      originalAction: action,
      transformedData: requestData,
      endpoint: `/api/games/${gameId}/actions`
    })
    
    const result = await this.post<GameActionResponse>(`/api/games/${gameId}/actions`, requestData)
    
    console.log('🎯 ApiClient.sendPlayerAction result:', {
      success: result.success,
      hasData: !!result.data,
      error: result.error,
      dataKeys: result.data ? Object.keys(result.data) : null
    })
    
    if (result.data) {
      console.log('🎯 Raw backend response data:', result.data)
    }
    
    return result
  }

  async rollDice(diceData: {
    dice_type: string
    count?: number
    modifier?: number
    label?: string
  }): Promise<ApiResponse<DiceRollResponse>> {
    return this.post('/api/dice/simple', diceData)
  }

  // NEW: Start orchestration session
  async startOrchestrationSession(userId: string, characterId: number, storyArcId?: number): Promise<ApiResponse<{
    session_id: string
    success: boolean
    result_type: string
    narrative_text: string
    state_changes: any[]
    dice_required: any[]
    next_actions: string[]
    character: any
  }>> {
    const requestData = {
      user_id: userId,
      character_id: characterId,
      story_arc_id: storyArcId
    }
    
    console.log('🚀 Starting orchestration session:', requestData)
    
    return this.post('/api/orchestration/sessions/start', requestData)
  }

  // NEW: Get game status including dice requirements
  async getGameStatus(storyId: string): Promise<ApiResponse<{
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
  }>> {
    return this.get(`/api/games/${storyId}/status`)
  }

  // NEW: Fulfill dice requirement
  async fulfillDiceRequirement(sessionId: string, diceResult: {
    dice_type: string
    rolls: number[]
    modifier: number
    total: number
    advantage?: boolean
    disadvantage?: boolean
  }): Promise<ApiResponse<{
    success: boolean
    result_type: string
    narrative_text: string
    state_changes: any[]
    next_actions: string[]
  }>> {
    // Convert single dice result to the array format expected by orchestration API
    const diceResults = [diceResult]
    
    console.log('🎲 Fulfilling dice requirement via orchestration API:', {
      sessionId,
      endpoint: `/api/orchestration/sessions/${sessionId}/continue`,
      diceResults
    })
    
    return this.post(`/api/orchestration/sessions/${sessionId}/continue`, diceResults)
  }

  async getScene(sceneId: string): Promise<ApiResponse<any>> {
    return this.get(`/scenes/${sceneId}`)
  }

  async generateSceneImage(sceneDescription: string): Promise<ApiResponse<{ image_url: string }>> {
    return this.post('/scenes/generate-image', { description: sceneDescription })
  }

  // Adventure Management
  async createAdventure(adventureData: any): Promise<ApiResponse<any>> {
    return this.post('/api/adventures/', adventureData)
  }

  async getAdventures(characterId?: number): Promise<ApiResponse<any[]>> {
    const params = characterId ? `?character_id=${characterId}` : ''
    return this.get(`/api/adventures/${params}`)
  }

  async getAdventure(adventureId: number): Promise<ApiResponse<any>> {
    return this.get(`/api/adventures/${adventureId}`)
  }

  async updateAdventureProgress(adventureId: number, progressData: any): Promise<ApiResponse<any>> {
    return this.put(`/api/adventures/${adventureId}/progress`, progressData)
  }

  async deleteAdventure(adventureId: number): Promise<ApiResponse<any>> {
    return this.delete(`/api/adventures/${adventureId}`)
  }

  // Character Progression
  async getCharacterProgression(characterId: number): Promise<ApiResponse<any>> {
    return this.get(`/api/character-progression/${characterId}`)
  }

  async addExperience(characterId: number, amount: number, reason: string): Promise<ApiResponse<any>> {
    return this.post(`/api/character-progression/${characterId}/experience`, { amount, reason })
  }

  async levelUpCharacter(characterId: number, chosenFeatures: string[]): Promise<ApiResponse<any>> {
    return this.post(`/api/character-progression/${characterId}/level-up`, { chosen_features: chosenFeatures })
  }

  async upgradeSkill(characterId: number, skillId: string): Promise<ApiResponse<any>> {
    return this.post(`/api/character-progression/${characterId}/skills/${skillId}/upgrade`)
  }

  async upgradeAttribute(characterId: number, attributeName: string): Promise<ApiResponse<any>> {
    return this.post(`/api/character-progression/${characterId}/attributes/${attributeName}/upgrade`)
  }

  // Quest Management
  async getQuests(characterId?: number, filters?: any): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams()
    if (characterId) params.append('character_id', characterId.toString())
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    const queryString = params.toString()
    return this.get(`/api/quests${queryString ? `?${queryString}` : ''}`)
  }

  async getCharacterQuests(characterId: number, status?: string): Promise<ApiResponse<any[]>> {
    const params = status ? `?status=${status}` : ''
    return this.get(`/api/quests/character/${characterId}${params}`)
  }

  async getQuest(questId: number): Promise<ApiResponse<any>> {
    return this.get(`/api/quests/${questId}`)
  }

  async acceptQuest(questId: number, characterId: number): Promise<ApiResponse<any>> {
    return this.post(`/api/quests/${questId}/accept`, { character_id: characterId })
  }

  async updateQuestProgress(questId: number, characterId: number, objectiveId: number, progress: number = 1): Promise<ApiResponse<any>> {
    return this.post(`/api/quests/${questId}/progress`, {
      character_id: characterId,
      objective_id: objectiveId,
      progress_amount: progress
    })
  }

  async completeQuest(questId: number, characterId: number): Promise<ApiResponse<any>> {
    return this.post(`/api/quests/${questId}/complete`, { character_id: characterId })
  }

  async abandonQuest(questId: number, characterId: number): Promise<ApiResponse<any>> {
    return this.post(`/api/quests/${questId}/abandon`, { character_id: characterId })
  }

  async generateDailyQuests(characterId: number, count: number = 3): Promise<ApiResponse<any[]>> {
    return this.post('/api/quests/generate/daily', { character_id: characterId, count })
  }

  // Journal Management
  async getJournalEntries(characterId: number, filters?: any): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams({ character_id: characterId.toString() })
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString())
        }
      })
    }
    return this.get(`/api/journal/entries?${params.toString()}`)
  }

  async createJournalEntry(entryData: any): Promise<ApiResponse<any>> {
    return this.post('/api/journal/entries', entryData)
  }

  async updateJournalEntry(entryId: number, updates: any): Promise<ApiResponse<any>> {
    return this.put(`/api/journal/entries/${entryId}`, updates)
  }

  async deleteJournalEntry(entryId: number): Promise<ApiResponse<any>> {
    return this.delete(`/api/journal/entries/${entryId}`)
  }

  async getDiscoveries(characterId: number, discoveryType?: string): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams({ character_id: characterId.toString() })
    if (discoveryType) params.append('discovery_type', discoveryType)
    return this.get(`/api/journal/discoveries?${params.toString()}`)
  }

  async createDiscovery(discoveryData: any): Promise<ApiResponse<any>> {
    return this.post('/api/journal/discoveries', discoveryData)
  }

  async updateDiscovery(discoveryId: number, updates: any): Promise<ApiResponse<any>> {
    return this.put(`/api/journal/discoveries/${discoveryId}`, updates)
  }

  async getTimelineEvents(characterId: number, eventType?: string): Promise<ApiResponse<any[]>> {
    const params = new URLSearchParams({ character_id: characterId.toString() })
    if (eventType) params.append('event_type', eventType)
    return this.get(`/api/journal/timeline?${params.toString()}`)
  }

  async createTimelineEvent(eventData: any): Promise<ApiResponse<any>> {
    return this.post('/api/journal/timeline', eventData)
  }

  // WebSocket Management
  private initializeWebSocket() {
    try {
      const wsUrl = `${WS_URL}/ws`
      console.log('🔗 Attempting WebSocket connection to:', wsUrl)
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = (event) => {
        console.log('🔗 WebSocket connected successfully')
        this.reconnectAttempts = 0
        this.emit('connection', { status: 'connected' })
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          console.log('📨 WebSocket message received:', message.type)
          this.emit(message.type, message.data)
          this.emit('message', message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error, 'Raw data:', event.data)
        }
      }

      this.ws.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean
        })
        this.emit('connection', { status: 'disconnected', reason: event.reason, code: event.code })
        this.handleReconnection()
      }

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', {
          error,
          readyState: this.ws?.readyState,
          url: wsUrl,
          timestamp: new Date().toISOString()
        })
        this.emit('connection', { status: 'error', error })
      }

    } catch (error) {
      console.error('Failed to initialize WebSocket:', {
        error,
        wsUrl: `${WS_URL}/ws`,
        apiBaseUrl: API_BASE_URL
      })
      this.handleReconnection()
    }
  }

  private handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1) // Exponential backoff
      console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`)
      
      setTimeout(() => {
        if (this.reconnectAttempts <= this.maxReconnectAttempts) {
          this.initializeWebSocket()
        }
      }, delay)
    } else {
      console.error('❌ Max reconnection attempts reached. WebSocket connection failed permanently.')
      console.log('💡 Troubleshooting tips:')
      console.log('  - Check if backend server is running on port 8000')
      console.log('  - Verify WebSocket endpoint is accessible')
      console.log('  - Check browser network tab for connection details')
      this.emit('connection', { status: 'failed', attempts: this.reconnectAttempts })
    }
  }

  // WebSocket Event System
  on(event: string, listener: Function) {
    this.ensureWebSocketConnection()
    if (!this.wsEventListeners.has(event)) {
      this.wsEventListeners.set(event, [])
    }
    this.wsEventListeners.get(event)!.push(listener)
  }

  off(event: string, listener: Function) {
    const listeners = this.wsEventListeners.get(event)
    if (listeners) {
      const index = listeners.indexOf(listener)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  private emit(event: string, data: any) {
    const listeners = this.wsEventListeners.get(event)
    if (listeners) {
      listeners.forEach(listener => {
        try {
          listener(data)
        } catch (error) {
          console.error(`Error in WebSocket listener for ${event}:`, error)
        }
      })
    }
  }

  // Send WebSocket message
  send(type: string, data: any) {
    this.ensureWebSocketConnection()
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        data,
        timestamp: new Date().toISOString()
      }
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket not connected. Message not sent:', { type, data })
      // Try to establish connection for next time
      if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
        this.ensureWebSocketConnection()
      }
    }
  }

  // Connection status
  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }

  get connectionState(): string {
    if (!this.ws) return 'disconnected'
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting'
      case WebSocket.OPEN: return 'connected'
      case WebSocket.CLOSING: return 'closing'
      case WebSocket.CLOSED: return 'disconnected'
      default: return 'unknown'
    }
  }

  // Cleanup
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.wsEventListeners.clear()
  }

  // Lazy WebSocket initialization
  private ensureWebSocketConnection() {
    if (!this.ws || this.ws.readyState === WebSocket.CLOSED) {
      this.initializeWebSocket()
    }
  }
}

// Create singleton instance
export const apiClient = new ApiClient()

// Export types for use in components
export type {
  ApiResponse,
  DiceRollResponse,
  GameActionResponse,
  WebSocketMessage
} 