'use client'

import React, { useState, useEffect } from 'react'
import { Image, AlertCircle, Loader2, MapPin } from 'lucide-react'

interface SceneDisplayProps {
  sceneName: string
  sceneImageUrl?: string
  location: string
  sceneType?: 'combat' | 'exploration' | 'dialogue' | 'story_narration'
  className?: string
  onImageLoad?: () => void
  onImageError?: () => void
}

const SceneDisplay: React.FC<SceneDisplayProps> = ({
  sceneName,
  sceneImageUrl,
  location,
  sceneType = 'story_narration',
  className = '',
  onImageLoad,
  onImageError
}) => {
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error' | 'placeholder'>('loading')
  const [displayUrl, setDisplayUrl] = useState<string | null>(null)

  // Scene type color mappings
  const sceneTypeColors = {
    combat: 'from-red-900/80 to-orange-900/80 border-red-500/50',
    exploration: 'from-green-900/80 to-blue-900/80 border-green-500/50',
    dialogue: 'from-purple-900/80 to-pink-900/80 border-purple-500/50',
    story_narration: 'from-gray-900/80 to-slate-900/80 border-gray-500/50'
  }

  const sceneTypeIcons = {
    combat: '⚔️',
    exploration: '🗺️',
    dialogue: '💬',
    story_narration: '📜'
  }

  useEffect(() => {
    if (sceneImageUrl) {
      setImageState('loading')
      setDisplayUrl(sceneImageUrl)
    } else {
      // Generate a placeholder or fetch a scene image from backend
      generateSceneImage()
    }
  }, [sceneImageUrl, sceneName, sceneType])

  const generateSceneImage = async () => {
    try {
      setImageState('loading')
      
      // Try to generate image using backend API
      try {
        const response = await fetch('/api/scenes/generate-image', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            scene_name: sceneName,
            scene_description: `A ${sceneType.replace('_', ' ')} scene in ${location}`,
            scene_type: sceneType,
            style: 'fantasy'
          })
        })
        
        if (response.ok) {
          const data = await response.json()
          setDisplayUrl(data.image_url)
          setImageState('placeholder')
          return
        }
      } catch (apiError) {
        console.warn('API image generation failed, using fallback:', apiError)
      }
      
      // Fallback to local placeholder system
      const fallbackImages = {
        combat: '/api/placeholder/600/300?text=Combat+Scene&bg=8B0000',
        exploration: '/api/placeholder/600/300?text=Exploration&bg=006400',
        dialogue: '/api/placeholder/600/300?text=Dialogue&bg=4B0082',
        story_narration: '/api/placeholder/600/300?text=Story+Scene&bg=2F4F4F'
      }
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 500))
      
      setDisplayUrl(fallbackImages[sceneType] || fallbackImages.story_narration)
      setImageState('placeholder')
      
    } catch (error) {
      console.error('Failed to generate scene image:', error)
      setImageState('error')
    }
  }

  const handleImageLoad = () => {
    if (imageState === 'loading') {
      setImageState('loaded')
    }
    onImageLoad?.()
  }

  const handleImageError = () => {
    setImageState('error')
    onImageError?.()
  }

  const retryImageLoad = () => {
    if (sceneImageUrl) {
      setImageState('loading')
      setDisplayUrl(sceneImageUrl)
    } else {
      generateSceneImage()
    }
  }

  return (
    <div className={`h-48 rounded-t-lg overflow-hidden relative ${className}`}>
      {/* Loading State */}
      {imageState === 'loading' && (
        <div className="w-full h-full bg-gray-800/50 flex items-center justify-center">
          <div className="flex flex-col items-center space-y-2">
            <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
            <span className="text-sm text-gray-400">Loading scene...</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {imageState === 'error' && (
        <div className="w-full h-full bg-gray-800/50 flex items-center justify-center">
          <div className="flex flex-col items-center space-y-3">
            <AlertCircle className="w-8 h-8 text-red-400" />
            <span className="text-sm text-gray-400 text-center">
              Failed to load scene image
            </span>
            <button
              onClick={retryImageLoad}
              className="px-3 py-1 bg-purple-600/50 hover:bg-purple-600/70 text-xs rounded transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Image Display */}
      {(imageState === 'loaded' || imageState === 'placeholder') && displayUrl && (
        <>
          <img
            src={displayUrl}
            alt={sceneName}
            className="w-full h-full object-cover"
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
          
          {/* Scene Type Indicator */}
          <div className="absolute top-2 right-2">
            <div className={`px-2 py-1 rounded text-xs font-medium bg-gradient-to-r ${sceneTypeColors[sceneType]} backdrop-blur-sm border`}>
              <span className="mr-1">{sceneTypeIcons[sceneType]}</span>
              {sceneType.replace('_', ' ').toUpperCase()}
            </div>
          </div>

          {/* Scene Information Overlay */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
            <h2 className="text-xl font-bold text-white mb-1">{sceneName}</h2>
            <div className="flex items-center text-sm text-gray-300">
              <MapPin className="w-4 h-4 mr-1" />
              {location}
            </div>
          </div>

          {/* Placeholder Indicator */}
          {imageState === 'placeholder' && (
            <div className="absolute top-2 left-2">
              <div className="px-2 py-1 bg-black/50 backdrop-blur-sm rounded text-xs text-gray-300 border border-gray-600/50">
                <Image className="w-3 h-3 inline mr-1" />
                Generated Scene
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default SceneDisplay 