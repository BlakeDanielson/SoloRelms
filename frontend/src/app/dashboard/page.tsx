'use client';

import { UserButton, useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function DashboardPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null; // Will redirect via useEffect
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-white">SoloRealms</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-white">
                Welcome, {user?.firstName || user?.emailAddresses?.[0]?.emailAddress || 'Adventurer'}
              </span>
              <UserButton 
                appearance={{
                  elements: {
                    avatarBox: "w-10 h-10"
                  }
                }}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Create Character Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Create Character</h3>
            <p className="text-gray-300 mb-4">Start your adventure by creating a new D&D character</p>
            <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors">
              Create New Character
            </button>
          </div>

          {/* My Characters Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">My Characters</h3>
            <p className="text-gray-300 mb-4">View and manage your existing characters</p>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
              View Characters
            </button>
          </div>

          {/* Start Adventure Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Start Adventure</h3>
            <p className="text-gray-300 mb-4">Begin a new AI-powered D&D adventure</p>
            <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors">
              Start Adventure
            </button>
          </div>

          {/* Continue Story Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Continue Story</h3>
            <p className="text-gray-300 mb-4">Resume your ongoing adventures</p>
            <button className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-md transition-colors">
              Continue Story
            </button>
          </div>

          {/* Game History Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Game History</h3>
            <p className="text-gray-300 mb-4">Review your completed adventures</p>
            <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors">
              View History
            </button>
          </div>

          {/* Settings Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Settings</h3>
            <p className="text-gray-300 mb-4">Customize your gaming experience</p>
            <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors">
              Open Settings
            </button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="mt-8 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6">
          <h2 className="text-2xl font-bold text-white mb-4">Your Stats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-400">0</div>
              <div className="text-gray-300">Characters</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-400">0</div>
              <div className="text-gray-300">Adventures</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-400">0</div>
              <div className="text-gray-300">Hours Played</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-400">0</div>
              <div className="text-gray-300">XP Earned</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
} 