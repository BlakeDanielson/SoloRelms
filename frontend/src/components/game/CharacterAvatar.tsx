'use client'

import React, { useState } from 'react'
import { User, Crown, Shield, Sword } from 'lucide-react'

interface CharacterAvatarProps {
  character: {
    name: string
    race: string
    character_class?: string
    class?: string
    avatar_url?: string
    level?: number
  }
  size?: 'sm' | 'md' | 'lg' | 'xl'
  showLevel?: boolean
  showClass?: boolean
  className?: string
  onClick?: () => void
}

const CharacterAvatar: React.FC<CharacterAvatarProps> = ({
  character,
  size = 'md',
  showLevel = false,
  showClass = false,
  className = '',
  onClick
}) => {
  const [imageError, setImageError] = useState(false)

  // Size mappings
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-base',
    xl: 'w-24 h-24 text-2xl'
  }

  const badgeSizes = {
    sm: 'text-xs px-1 py-0.5',
    md: 'text-xs px-1.5 py-0.5',
    lg: 'text-sm px-2 py-1',
    xl: 'text-sm px-2 py-1'
  }

  // Class-based color schemes
  const classColors: Record<string, string> = {
    // Core classes
    'barbarian': 'from-red-600 to-orange-600',
    'bard': 'from-purple-600 to-pink-600',
    'cleric': 'from-yellow-600 to-white',
    'druid': 'from-green-600 to-brown-600',
    'fighter': 'from-gray-600 to-blue-600',
    'monk': 'from-orange-600 to-yellow-600',
    'paladin': 'from-blue-600 to-yellow-600',
    'ranger': 'from-green-600 to-brown-600',
    'rogue': 'from-gray-800 to-purple-600',
    'sorcerer': 'from-red-600 to-purple-600',
    'warlock': 'from-purple-800 to-black',
    'wizard': 'from-blue-600 to-purple-600',
    // Fallback
    'default': 'from-purple-600 to-blue-600'
  }

  const characterClass = character.character_class || character.class || 'default'
  const colorScheme = classColors[characterClass.toLowerCase()] || classColors.default

  const getClassIcon = (className: string) => {
    const iconMap: Record<string, React.ReactElement> = {
      'paladin': <Shield className="w-3 h-3" />,
      'fighter': <Sword className="w-3 h-3" />,
      'cleric': <Crown className="w-3 h-3" />,
      'rogue': <User className="w-3 h-3" />,
      'wizard': <Crown className="w-3 h-3" />,
      'default': <User className="w-3 h-3" />
    }
    return iconMap[className.toLowerCase()] || iconMap.default
  }

  const handleImageError = () => {
    setImageError(true)
  }

  const renderAvatar = () => {
    if (character.avatar_url && !imageError) {
      return (
        <img
          src={character.avatar_url}
          alt={`${character.name} avatar`}
          className="w-full h-full object-cover"
          onError={handleImageError}
        />
      )
    }

    // Fallback to initials with class-based gradient
    return (
      <div className={`w-full h-full bg-gradient-to-br ${colorScheme} flex items-center justify-center font-bold text-white`}>
        {character.name.charAt(0).toUpperCase()}
      </div>
    )
  }

  return (
    <div className={`relative ${className}`}>
      {/* Main Avatar */}
      <div
        className={`${sizeClasses[size]} rounded-full overflow-hidden cursor-pointer transition-transform hover:scale-105 border-2 border-white/20`}
        onClick={onClick}
      >
        {renderAvatar()}
      </div>

      {/* Level Badge */}
      {showLevel && character.level && (
        <div className="absolute -top-1 -right-1">
          <div className={`bg-green-600 text-white rounded-full ${badgeSizes[size]} font-bold border border-white/20`}>
            {character.level}
          </div>
        </div>
      )}

      {/* Class Badge */}
      {showClass && characterClass !== 'default' && (
        <div className="absolute -bottom-1 -right-1">
          <div className={`bg-purple-600 text-white rounded-full ${badgeSizes[size]} flex items-center justify-center border border-white/20`}>
            {getClassIcon(characterClass)}
          </div>
        </div>
      )}
    </div>
  )
}

export default CharacterAvatar 