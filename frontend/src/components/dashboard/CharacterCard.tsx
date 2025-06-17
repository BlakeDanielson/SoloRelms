'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { Edit, MapPin, Star, Clock, Swords, Calendar } from 'lucide-react'
import CharacterAvatar from '../game/CharacterAvatar'

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

interface CharacterCardProps {
  character: Character
  className?: string
  showQuickActions?: boolean
}

const CharacterCard: React.FC<CharacterCardProps> = ({
  character,
  className = '',
  showQuickActions = true
}) => {
  const router = useRouter()

  // Calculate health percentage for health bar
  const healthPercentage = (character.hit_points / character.max_hit_points) * 100

  // Get health bar color based on percentage
  const getHealthBarColor = (percentage: number) => {
    if (percentage > 75) return 'bg-green-500'
    if (percentage > 50) return 'bg-yellow-500'
    if (percentage > 25) return 'bg-orange-500'
    return 'bg-red-500'
  }

  // Calculate ability modifier
  const getModifier = (score: number) => {
    const modifier = Math.floor((score - 10) / 2)
    return modifier >= 0 ? `+${modifier}` : `${modifier}`
  }

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    })
  }

  // Navigation handlers
  const handleViewCharacter = () => {
    router.push(`/character/${character.id}`)
  }

  const handleEditCharacter = () => {
    router.push(`/character/${character.id}/edit`)
  }

  const handleViewAdventures = () => {
    router.push(`/character/${character.id}/adventures`)
  }

  const handleStartAdventure = () => {
    router.push(`/adventure/create?character=${character.id}`)
  }

  return (
    <div className={`bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-all duration-200 hover:scale-105 hover:shadow-xl ${className}`}>
      {/* Header with Avatar and Basic Info */}
      <div className="flex items-start space-x-4 mb-4">
        <CharacterAvatar
          character={character}
          size="lg"
          showLevel={true}
          showClass={true}
          onClick={handleViewCharacter}
        />
        
        <div className="flex-1 min-w-0">
          <h3 
            className="text-lg font-bold text-white truncate cursor-pointer hover:text-purple-300 transition-colors"
            onClick={handleViewCharacter}
          >
            {character.name}
          </h3>
          <p className="text-sm text-gray-300">
            Level {character.level} {character.race} {character.character_class}
          </p>
          <p className="text-xs text-gray-400 capitalize">{character.background}</p>
        </div>

        {/* Quick Action Buttons */}
        {showQuickActions && (
          <div className="flex flex-col space-y-1">
            <button
              onClick={handleEditCharacter}
              className="p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-md transition-colors"
              title="Edit Character"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={handleViewAdventures}
              className="p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-md transition-colors"
              title="View Adventures"
            >
              <MapPin className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Health Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center text-xs text-gray-300 mb-1">
          <span>Health</span>
          <span>{character.hit_points}/{character.max_hit_points}</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${getHealthBarColor(healthPercentage)}`}
            style={{ width: `${healthPercentage}%` }}
          />
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-3 gap-2 mb-4">
        <div className="text-center">
          <div className="text-sm font-bold text-white">AC {character.armor_class}</div>
          <div className="text-xs text-gray-400">Armor Class</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-bold text-white">{character.experience_points.toLocaleString()}</div>
          <div className="text-xs text-gray-400">XP</div>
        </div>
        <div className="text-center">
          <div className="text-sm font-bold text-purple-400">
            {getModifier(character.strength)}
          </div>
          <div className="text-xs text-gray-400">STR</div>
        </div>
      </div>

      {/* Meta Information */}
      <div className="flex items-center justify-between text-xs text-gray-400 mb-4">
        <div className="flex items-center space-x-1">
          <Calendar className="w-3 h-3" />
          <span>Created {formatDate(character.created_at)}</span>
        </div>
        {character.last_played && (
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>Played {formatDate(character.last_played)}</span>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2">
        <button
          onClick={handleStartAdventure}
          className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-3 py-2 rounded-md transition-colors text-sm font-medium flex items-center justify-center space-x-1"
        >
          <Swords className="w-4 h-4" />
          <span>Adventure</span>
        </button>
        <button
          onClick={handleViewCharacter}
          className="bg-white/10 hover:bg-white/20 text-white px-3 py-2 rounded-md transition-colors text-sm font-medium border border-white/20"
        >
          View
        </button>
      </div>
    </div>
  )
}

export default CharacterCard 