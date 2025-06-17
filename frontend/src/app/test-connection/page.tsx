'use client'

import React, { useState, useEffect } from 'react'
import { useGameCommunication } from '@/hooks/useGameCommunication'
import ConnectionStatusIndicator from '@/components/game/ConnectionStatus'

export default function TestConnectionPage() {
  const [messages, setMessages] = useState<string[]>([])
  const [testMessage, setTestMessage] = useState('')

  const gameCommunication = useGameCommunication({
    gameId: 'test-game-1',
    characterId: 1,
    onNewMessage: (message) => {
      addMessage(`📨 New message: ${JSON.stringify(message)}`)
    },
    onGameStateUpdate: (updates) => {
      addMessage(`🎮 Game state update: ${JSON.stringify(updates)}`)
    },
    onCharacterUpdate: (updates) => {
      addMessage(`👤 Character update: ${JSON.stringify(updates)}`)
    },
    onConnectionChange: (status) => {
      addMessage(`🔗 Connection status: ${status}`)
    }
  })

  const addMessage = (message: string) => {
    setMessages(prev => [...prev.slice(-10), `${new Date().toLocaleTimeString()}: ${message}`])
  }

  const testPlayerAction = async () => {
    addMessage('📤 Sending player action...')
    const result = await gameCommunication.sendPlayerAction('action', testMessage || 'I look around the area')
    if (result) {
      addMessage(`✅ Action sent successfully`)
    } else {
      addMessage(`❌ Failed to send action`)
    }
  }

  const testDiceRoll = async () => {
    addMessage('🎲 Rolling dice...')
    const result = await gameCommunication.rollDice({
      dice_type: 'd20',
      count: 1,
      modifier: 3,
      label: 'Investigation Check'
    })
    if (result) {
      addMessage(`✅ Dice rolled: ${result.total}`)
    } else {
      addMessage(`❌ Failed to roll dice`)
    }
  }

  const testLoadCharacter = async () => {
    addMessage('👤 Loading character...')
    const character = await gameCommunication.loadCharacter()
    if (character) {
      addMessage(`✅ Character loaded: ${character.name}`)
    } else {
      addMessage(`❌ Failed to load character`)
    }
  }

  const testLoadGameState = async () => {
    addMessage('🎮 Loading game state...')
    const gameState = await gameCommunication.loadGameState()
    if (gameState) {
      addMessage(`✅ Game state loaded: ${gameState.current_scene}`)
    } else {
      addMessage(`❌ Failed to load game state`)
    }
  }

  const sendWebSocketMessage = () => {
    gameCommunication.sendWebSocketMessage('ping', { test: 'Hello from frontend!' })
    addMessage('📡 Sent WebSocket ping')
  }

  useEffect(() => {
    addMessage('🚀 Connection test page loaded')
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-800 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">🔗 Communication System Test</h1>
        
        {/* Connection Status */}
        <div className="mb-8 p-6 bg-gray-800/50 rounded-lg border border-purple-500/30">
          <h2 className="text-xl font-semibold mb-4">Connection Status</h2>
          <ConnectionStatusIndicator
            status={gameCommunication.connectionStatus}
            isLoading={gameCommunication.isLoading}
            error={gameCommunication.error}
            onReconnect={gameCommunication.connect}
          />
        </div>

        {/* Test Controls */}
        <div className="mb-8 p-6 bg-gray-800/50 rounded-lg border border-purple-500/30">
          <h2 className="text-xl font-semibold mb-4">Test Controls</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
            <button
              onClick={testLoadCharacter}
              disabled={gameCommunication.isLoading}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition-colors disabled:opacity-50"
            >
              Load Character
            </button>
            
            <button
              onClick={testLoadGameState}
              disabled={gameCommunication.isLoading}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded transition-colors disabled:opacity-50"
            >
              Load Game State
            </button>
            
            <button
              onClick={testDiceRoll}
              disabled={gameCommunication.isLoading}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 rounded transition-colors disabled:opacity-50"
            >
              Roll d20+3
            </button>
            
            <button
              onClick={sendWebSocketMessage}
              disabled={!gameCommunication.isConnected}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded transition-colors disabled:opacity-50"
            >
              Send WebSocket Ping
            </button>
            
            <button
              onClick={gameCommunication.connect}
              className="px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded transition-colors"
            >
              Reconnect
            </button>
            
            <button
              onClick={gameCommunication.disconnect}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition-colors"
            >
              Disconnect
            </button>
          </div>

          {/* Player Action Test */}
          <div className="flex gap-2">
            <input
              type="text"
              value={testMessage}
              onChange={(e) => setTestMessage(e.target.value)}
              placeholder="Enter test action..."
              className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded text-white"
            />
            <button
              onClick={testPlayerAction}
              disabled={gameCommunication.isLoading}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded transition-colors disabled:opacity-50"
            >
              Send Action
            </button>
          </div>
        </div>

        {/* Messages Log */}
        <div className="p-6 bg-gray-800/50 rounded-lg border border-purple-500/30">
          <h2 className="text-xl font-semibold mb-4">Activity Log</h2>
          <div className="bg-gray-900 rounded p-4 h-64 overflow-y-auto font-mono text-sm">
            {messages.length === 0 ? (
              <p className="text-gray-400">No messages yet...</p>
            ) : (
              messages.map((message, index) => (
                <div key={index} className="mb-1 text-gray-300">
                  {message}
                </div>
              ))
            )}
          </div>
          <button
            onClick={() => setMessages([])}
            className="mt-2 px-3 py-1 bg-gray-600 hover:bg-gray-700 rounded text-sm transition-colors"
          >
            Clear Log
          </button>
        </div>

        {/* Debug Info */}
        <div className="mt-8 p-6 bg-gray-800/50 rounded-lg border border-purple-500/30">
          <h2 className="text-xl font-semibold mb-4">Debug Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p><strong>Connection Status:</strong> {gameCommunication.connectionStatus}</p>
              <p><strong>Is Connected:</strong> {gameCommunication.isConnected ? '✅' : '❌'}</p>
              <p><strong>Is Loading:</strong> {gameCommunication.isLoading ? '⏳' : '✅'}</p>
            </div>
            <div>
              <p><strong>Error:</strong> {gameCommunication.error || 'None'}</p>
              <p><strong>API Client State:</strong> {gameCommunication.connectionState}</p>
              <p><strong>Last Ping:</strong> {gameCommunication.lastPing?.toLocaleTimeString() || 'Never'}</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="mt-8 text-center">
          <a
            href="/game"
            className="inline-block px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
          >
            🎮 Back to Game
          </a>
        </div>
      </div>
    </div>
  )
} 