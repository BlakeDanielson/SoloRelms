'use client'

import { UserButton, useUser } from '@clerk/nextjs'
import { useRouter, useSearchParams } from 'next/navigation'
import { useEffect } from 'react'
import ImmersiveDnDInterface from '@/components/game/ImmersiveDnDInterface'

export default function GamePage() {
  const { isLoaded, isSignedIn, user } = useUser()
  const router = useRouter()
  const searchParams = useSearchParams()
  const characterId = searchParams.get('character')
  const storyId = searchParams.get('story')

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in')
    }
  }, [isLoaded, isSignedIn, router])

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    )
  }

  if (!isSignedIn) {
    return null // Will redirect via useEffect
  }

  return (
    <div className="min-h-screen">
      {/* Floating header for game mode */}
      <header className="absolute top-0 left-0 right-0 z-50 bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-12">
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => router.push('/dashboard')}
                className="text-white hover:text-purple-300 transition-colors text-sm"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-lg font-bold text-white">
                SoloRealms - Live Game
                {characterId && <span className="text-purple-300 ml-2">(Character #{characterId})</span>}
                {storyId && <span className="text-blue-300 ml-2">Story #{storyId}</span>}
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-white text-sm">
                {user?.firstName || 'Adventurer'}
              </span>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-8 h-8"
                  }
                }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Immersive Game Interface */}
      <div className="pt-12">
        <ImmersiveDnDInterface characterId={characterId} storyId={storyId} />
      </div>
    </div>
  )
} 