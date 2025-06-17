'use client'

import React, { useState } from 'react'
import { Image, Download, Maximize2, AlertCircle, Loader2 } from 'lucide-react'

interface GameImageProps {
  src: string
  alt: string
  title?: string
  type?: 'scene' | 'character' | 'item' | 'map' | 'misc'
  size?: 'sm' | 'md' | 'lg'
  showActions?: boolean
  className?: string
  onLoad?: () => void
  onError?: () => void
  onClick?: () => void
}

const GameImage: React.FC<GameImageProps> = ({
  src,
  alt,
  title,
  type = 'misc',
  size = 'md',
  showActions = false,
  className = '',
  onLoad,
  onError,
  onClick
}) => {
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error'>('loading')
  const [showModal, setShowModal] = useState(false)

  const sizeClasses = {
    sm: 'max-w-32 max-h-20',
    md: 'max-w-48 max-h-32',
    lg: 'max-w-64 max-h-48'
  }

  const typeStyles = {
    scene: 'border-blue-500/30 shadow-blue-500/20',
    character: 'border-purple-500/30 shadow-purple-500/20',
    item: 'border-yellow-500/30 shadow-yellow-500/20',
    map: 'border-green-500/30 shadow-green-500/20',
    misc: 'border-gray-500/30 shadow-gray-500/20'
  }

  const typeIcons = {
    scene: '🖼️',
    character: '👤',
    item: '📦',
    map: '🗺️',
    misc: '🖼️'
  }

  const handleImageLoad = () => {
    setImageState('loaded')
    onLoad?.()
  }

  const handleImageError = () => {
    setImageState('error')
    onError?.()
  }

  const handleDownload = async (e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      const response = await fetch(src)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${alt.replace(/[^a-z0-9]/gi, '_').toLowerCase()}.png`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to download image:', error)
    }
  }

  const handleMaximize = (e: React.MouseEvent) => {
    e.stopPropagation()
    setShowModal(true)
  }

  return (
    <>
      <div className={`relative inline-block ${className}`}>
        <div 
          className={`
            ${sizeClasses[size]} 
            rounded-lg overflow-hidden border-2 ${typeStyles[type]} 
            shadow-lg cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-xl
            ${imageState === 'loading' ? 'bg-gray-800/50' : ''}
          `}
          onClick={onClick || (() => setShowModal(true))}
        >
          {/* Loading State */}
          {imageState === 'loading' && (
            <div className="w-full h-full min-h-[80px] flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
            </div>
          )}

          {/* Error State */}
          {imageState === 'error' && (
            <div className="w-full h-full min-h-[80px] flex flex-col items-center justify-center bg-gray-800/50 p-4">
              <AlertCircle className="w-6 h-6 text-red-400 mb-2" />
              <span className="text-xs text-gray-400 text-center">Failed to load image</span>
            </div>
          )}

          {/* Loaded Image */}
          {imageState === 'loaded' && (
            <>
              <img
                src={src}
                alt={alt}
                className="w-full h-full object-cover"
                onLoad={handleImageLoad}
                onError={handleImageError}
              />
              
              {/* Type Badge */}
              <div className="absolute top-1 left-1">
                <div className="px-1.5 py-0.5 bg-black/70 backdrop-blur-sm rounded text-xs text-white">
                  {typeIcons[type]}
                </div>
              </div>

              {/* Action Buttons */}
              {showActions && (
                <div className="absolute top-1 right-1 flex space-x-1">
                  <button
                    onClick={handleDownload}
                    className="p-1 bg-black/70 backdrop-blur-sm rounded hover:bg-black/90 transition-colors"
                    title="Download"
                  >
                    <Download className="w-3 h-3 text-white" />
                  </button>
                  <button
                    onClick={handleMaximize}
                    className="p-1 bg-black/70 backdrop-blur-sm rounded hover:bg-black/90 transition-colors"
                    title="Expand"
                  >
                    <Maximize2 className="w-3 h-3 text-white" />
                  </button>
                </div>
              )}
            </>
          )}

          {/* Hidden image for loading detection */}
          <img
            src={src}
            alt=""
            className="hidden"
            onLoad={handleImageLoad}
            onError={handleImageError}
          />
        </div>

        {/* Title */}
        {title && (
          <div className="mt-1 text-xs text-gray-400 text-center max-w-full truncate">
            {title}
          </div>
        )}
      </div>

      {/* Modal for expanded view */}
      {showModal && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowModal(false)}
        >
          <div className="relative max-w-4xl max-h-full">
            <img
              src={src}
              alt={alt}
              className="max-w-full max-h-full object-contain rounded-lg"
            />
            
            {/* Close button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-2 right-2 p-2 bg-black/70 backdrop-blur-sm rounded-full hover:bg-black/90 transition-colors"
            >
              <span className="text-white text-xl">×</span>
            </button>

            {/* Image info */}
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
              <h3 className="text-white font-semibold">{title || alt}</h3>
              <p className="text-gray-300 text-sm capitalize">{type} image</p>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default GameImage 