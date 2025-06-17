'use client';

import { UserButton, useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

// Types for the ongoing adventures
interface OngoingAdventure {
  id: number;
  title: string;
  character_id: number;
  character_name: string;
  current_stage: string;
  stages_completed: string[];
  created_at: string;
  story_seed?: string;
}

interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
}

export default function DashboardPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [ongoingAdventures, setOngoingAdventures] = useState<OngoingAdventure[]>([]);
  const [selectedAdventure, setSelectedAdventure] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch ongoing adventures and characters
  useEffect(() => {
    if (isSignedIn && isLoaded) {
      fetchOngoingAdventures();
    }
  }, [isSignedIn, isLoaded]);

  const fetchOngoingAdventures = async () => {
    try {
      setIsLoading(true);
      
      // Get authentication token
      const token = await getToken();
      if (!token) {
        console.error('No authentication token available');
        return;
      }

      // Fetch ongoing stories and characters in parallel
      const [storiesResponse, charactersResponse] = await Promise.all([
        fetch('http://localhost:8000/api/stories?active_only=true', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        }),
        fetch('http://localhost:8000/api/characters', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
        })
      ]);

      if (storiesResponse.ok && charactersResponse.ok) {
        const storiesData = await storiesResponse.json();
        const charactersData = await charactersResponse.json();
        
        // Handle both response formats
        const stories = Array.isArray(storiesData) ? storiesData : storiesData.stories || [];
        const charactersArray = Array.isArray(charactersData) ? charactersData : charactersData.characters || [];
        
        // Combine story and character data, limit to 3 most recent
        const recentAdventures = stories
          .slice(0, 3)
          .map((story: any) => {
            const character = charactersArray.find((char: Character) => char.id === story.character_id);
            return {
              id: story.id,
              title: story.title || `Adventure ${story.id}`,
              character_id: story.character_id,
              character_name: character?.name || 'Unknown Character',
              current_stage: story.current_stage,
              stages_completed: story.stages_completed || [],
              created_at: story.created_at,
              story_seed: story.story_seed
            };
          });

        setOngoingAdventures(recentAdventures);
        
        // Auto-select the first adventure if available
        if (recentAdventures.length > 0) {
          setSelectedAdventure(recentAdventures[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching ongoing adventures:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStageDisplayName = (stage: string) => {
    const stageNames: { [key: string]: string } = {
      'intro': 'Introduction',
      'inciting_incident': 'Inciting Incident',
      'first_combat': 'First Combat',
      'twist': 'Plot Twist',
      'final_conflict': 'Final Conflict',
      'resolution': 'Resolution'
    };
    return stageNames[stage] || stage;
  };

  const getProgressPercentage = (stages_completed: string[]) => {
    const totalStages = 6; // Based on StoryStage enum
    return Math.round((stages_completed.length / totalStages) * 100);
  };

  const handleLaunchGame = () => {
  if (selectedAdventure) {
    // Find the selected adventure to get the character_id
    const adventure = ongoingAdventures.find(adv => adv.id === selectedAdventure);
    if (adventure) {
      router.push(`/game?character=${adventure.character_id}&story=${selectedAdventure}`);
    } else {
      // Fallback if adventure not found
      router.push('/game');
    }
  } else {
    // Fallback to general game interface if no adventure selected
    router.push('/game');
  }
};

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
          {/* Enhanced Play Now Card - Featured */}
          <div className="md:col-span-2 lg:col-span-3 bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-sm rounded-lg border border-purple-400/30 p-8 hover:from-purple-600/30 hover:to-blue-600/30 transition-colors">
            <h3 className="text-3xl font-bold text-white mb-3">🎲 Play Now - AI Dungeon Master</h3>
            <p className="text-gray-200 mb-6 text-lg">Jump into an immersive AI-powered D&D adventure with our complete game interface featuring real-time character tracking, dynamic storytelling, and intelligent dice resolution!</p>
            
            {/* Ongoing Adventures Section */}
            {isLoading ? (
              <div className="text-white mb-6">Loading your adventures...</div>
            ) : ongoingAdventures.length > 0 ? (
              <div className="mb-6">
                <h4 className="text-xl font-semibold text-white mb-4">Your Ongoing Adventures</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  {ongoingAdventures.map((adventure) => (
                    <div
                      key={adventure.id}
                      onClick={() => setSelectedAdventure(adventure.id)}
                      className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                        selectedAdventure === adventure.id
                          ? 'border-blue-400 bg-blue-500/20'
                          : 'border-white/20 bg-white/10 hover:border-white/40'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h5 className="font-semibold text-white truncate">{adventure.title}</h5>
                        <div className={`w-3 h-3 rounded-full ${
                          selectedAdventure === adventure.id ? 'bg-blue-400' : 'bg-gray-400'
                        }`} />
                      </div>
                      <p className="text-sm text-gray-300 mb-2">Character: {adventure.character_name}</p>
                      <p className="text-sm text-gray-300 mb-2">Stage: {getStageDisplayName(adventure.current_stage)}</p>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                          style={{ width: `${getProgressPercentage(adventure.stages_completed)}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-400 mt-1">
                        {getProgressPercentage(adventure.stages_completed)}% Complete
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mb-6 p-4 bg-orange-500/20 border border-orange-400/30 rounded-lg">
                <p className="text-orange-200">
                  No ongoing adventures found. Create a character and start a new adventure to begin your journey!
                </p>
              </div>
            )}

            <div className="flex items-center gap-4">
              <button 
                onClick={handleLaunchGame}
                disabled={ongoingAdventures.length === 0}
                className={`px-8 py-3 rounded-md transition-colors text-lg font-semibold shadow-lg ${
                  ongoingAdventures.length > 0
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white'
                    : 'bg-gray-600 text-gray-300 cursor-not-allowed'
                }`}
              >
                🚀 {selectedAdventure ? 'Continue Selected Adventure' : 'Launch Game Interface'}
              </button>
              
              {ongoingAdventures.length > 0 && (
                <button 
                  onClick={() => router.push('/adventures')}
                  className="bg-white/10 hover:bg-white/20 text-white px-6 py-3 rounded-md transition-colors text-lg border border-white/20"
                >
                  View All Adventures
                </button>
              )}
            </div>
          </div>

          {/* Create Character Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Create Character</h3>
            <p className="text-gray-300 mb-4">Start your adventure by creating a new D&D character</p>
            <button 
              onClick={() => router.push('/character/create')}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Create New Character
            </button>
          </div>

          {/* My Characters Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">My Characters</h3>
            <p className="text-gray-300 mb-4">View and manage your existing characters</p>
            <button 
              onClick={() => router.push('/characters')}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              View Characters
            </button>
          </div>

          {/* Start Adventure Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Start Adventure</h3>
            <p className="text-gray-300 mb-4">Begin a new AI-powered D&D adventure</p>
            <button 
              onClick={() => router.push('/adventure/create')}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Start Adventure
            </button>
          </div>

          {/* Continue Story Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Continue Story</h3>
            <p className="text-gray-300 mb-4">Resume your ongoing adventures</p>
            <button 
              onClick={() => router.push('/adventures')}
              className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              Continue Story
            </button>
          </div>

          {/* Game History Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Game History</h3>
            <p className="text-gray-300 mb-4">Review your completed adventures</p>
            <button 
              onClick={() => router.push('/history')}
              className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              View History
            </button>
          </div>

          {/* Settings Card */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6 hover:bg-white/15 transition-colors cursor-pointer">
            <h3 className="text-xl font-bold text-white mb-2">Settings</h3>
            <p className="text-gray-300 mb-4">Customize your gaming experience</p>
            <button 
              onClick={() => router.push('/settings')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md transition-colors"
            >
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