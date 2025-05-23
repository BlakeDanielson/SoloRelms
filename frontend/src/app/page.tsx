'use client';

import { SignInButton, SignUpButton, UserButton, useUser } from '@clerk/nextjs';
import Link from 'next/link';

export default function Home() {
  const { isSignedIn, isLoaded } = useUser();

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
              {isLoaded && (
                <>
                  {isSignedIn ? (
                    <>
                      <Link 
                        href="/dashboard" 
                        className="text-white hover:text-purple-300 transition-colors"
                      >
                        Dashboard
                      </Link>
                      <UserButton 
                        appearance={{
                          elements: {
                            avatarBox: "w-8 h-8"
                          }
                        }}
                      />
                    </>
                  ) : (
                    <>
                      <SignInButton mode="modal">
                        <button className="text-white hover:text-purple-300 transition-colors">
                          Sign In
                        </button>
                      </SignInButton>
                      <SignUpButton mode="modal">
                        <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors">
                          Sign Up
                        </button>
                      </SignUpButton>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            Solo<span className="text-purple-400">Realms</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Experience epic D&D adventures powered by AI. Create your character, 
            embark on quests, and forge your own legendary destiny.
          </p>
          
          {isLoaded && (
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              {isSignedIn ? (
                <Link 
                  href="/dashboard"
                  className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors"
                >
                  Enter Your Realm
                </Link>
              ) : (
                <>
                  <SignUpButton mode="modal">
                    <button className="bg-purple-600 hover:bg-purple-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors">
                      Start Your Adventure
                    </button>
                  </SignUpButton>
                  <SignInButton mode="modal">
                    <button className="border border-white/30 text-white hover:bg-white/10 px-8 py-3 rounded-lg text-lg font-semibold transition-colors">
                      Continue Your Journey
                    </button>
                  </SignInButton>
                </>
              )}
            </div>
          )}
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">🎭</div>
            <h3 className="text-xl font-bold text-white mb-2">AI Dungeon Master</h3>
            <p className="text-gray-300">
              Experience dynamic storytelling with an AI DM that adapts to your choices
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">⚔️</div>
            <h3 className="text-xl font-bold text-white mb-2">Epic Combat</h3>
            <p className="text-gray-300">
              Engage in tactical turn-based combat with full D&D 5e rules
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-bold text-white mb-2">Rich Stories</h3>
            <p className="text-gray-300">
              30-minute adventures that fit into your schedule, with deeper campaigns available
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">🎲</div>
            <h3 className="text-xl font-bold text-white mb-2">Character Creation</h3>
            <p className="text-gray-300">
              Create unique characters with full D&D 5e customization
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">🌟</div>
            <h3 className="text-xl font-bold text-white mb-2">Permadeath Stakes</h3>
            <p className="text-gray-300">
              Experience real consequences with meaningful character progression
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 text-center">
            <div className="text-4xl mb-4">🏰</div>
            <h3 className="text-xl font-bold text-white mb-2">Solo Play</h3>
            <p className="text-gray-300">
              Adventure on your own schedule, no coordination required
            </p>
          </div>
        </div>

        {/* Call to Action */}
        {isLoaded && !isSignedIn && (
          <div className="mt-16 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Begin Your Legend?
            </h2>
            <p className="text-gray-300 mb-8">
              Join thousands of adventurers exploring AI-powered realms
            </p>
            <SignUpButton mode="modal">
              <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-12 py-4 rounded-lg text-xl font-bold transition-all transform hover:scale-105">
                Create Your Hero
              </button>
            </SignUpButton>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-black/20 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-400">
            <p>&copy; 2024 SoloRealms. Embark on your solo D&D journey.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
