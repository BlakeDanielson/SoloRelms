'use client'

import React from 'react'
import { Plus, Users } from 'lucide-react'
import { useRouter } from 'next/navigation'
import CharacterCard from './CharacterCard'

interface Character {
  id: number
  name: string
  race: string
  character_class: string
  background: string
  level: number
  experience_points: number
  hit_points: number
  max_hit_points: number
  armor_class: number
  strength: number
  dexterity: number
  constitution: number
  intelligence: number
  wisdom: number
  charisma: number
  backstory?: string
  avatar_url?: string
  created_at: string
  last_played?: string
}

interface CharacterGridProps {
  characters: Character[]
  loading?: boolean
  error?: string | null
  className?: string
}

const CharacterGrid: React.FC<CharacterGridProps> = ({
  characters,
  loading = false,
  error = null,
  className = ''
}) => {
  const router = useRouter()

  const handleCreateCharacter = () => {
    router.push('/character/create')
  }

  // Loading skeleton
  if (loading) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Users className="w-6 h-6" />
            <span>Your Characters</span>
          </h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(3)].map((_, index) => (
            <div
              key={index}
              className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 animate-pulse"
            >
              <div className="flex items-start space-x-4 mb-4">
                <div className="w-16 h-16 bg-gray-600 rounded-full"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-600 rounded mb-2"></div>
                  <div className="h-3 bg-gray-600 rounded w-3/4 mb-1"></div>
                  <div className="h-3 bg-gray-600 rounded w-1/2"></div>
                </div>
              </div>
              <div className="h-2 bg-gray-600 rounded mb-4"></div>
              <div className="grid grid-cols-3 gap-2 mb-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-8 bg-gray-600 rounded"></div>
                ))}
              </div>
              <div className="flex space-x-2">
                <div className="flex-1 h-8 bg-gray-600 rounded"></div>
                <div className="h-8 w-16 bg-gray-600 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={`space-y-6 ${className}`}>
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Users className="w-6 h-6" />
            <span>Your Characters</span>
          </h2>
        </div>
        
        <div className="bg-red-500/20 border border-red-500/30 rounded-lg p-6 text-center">
          <p className="text-red-300 mb-4">Error loading characters: {error}</p>
          <button
            onClick={() => window.location.reload()}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
          <Users className="w-6 h-6" />
          <span>Your Characters</span>
          <span className="text-sm font-normal text-gray-400">({characters.length})</span>
        </h2>
        
        <button
          onClick={handleCreateCharacter}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-4 py-2 rounded-md transition-colors flex items-center space-x-2 font-medium"
        >
          <Plus className="w-4 h-4" />
          <span>Create Character</span>
        </button>
      </div>

      {/* Characters Grid */}
      {characters.length === 0 ? (
        // Empty state
        <div className="text-center py-12">
          <div className="bg-white/5 backdrop-blur-sm rounded-lg border border-white/10 p-8 max-w-md mx-auto">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">No Characters Yet</h3>
            <p className="text-gray-300 mb-6">
              Create your first D&D character to start your adventure!
            </p>
            <button
              onClick={handleCreateCharacter}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-3 rounded-md transition-colors font-medium flex items-center space-x-2 mx-auto"
            >
              <Plus className="w-5 h-5" />
              <span>Create Your First Character</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {characters.map((character) => (
            <CharacterCard
              key={character.id}
              character={character}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default CharacterGrid 