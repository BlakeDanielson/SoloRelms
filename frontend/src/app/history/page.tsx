'use client';

import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import {
  Calendar,
  Clock,
  Trophy,
  Star,
  Sword,
  Shield,
  MapPin,
  BookOpen,
  Target,
  Award,
  CheckCircle,
  User,
  Eye,
  Filter,
  Search,
  TrendingUp,
  BarChart3,
  Activity,
  Zap
} from 'lucide-react';
import CharacterAvatar from '../../components/game/CharacterAvatar';

// Types
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
}

interface CompletedAdventure {
  id: number;
  character_id: number;
  title?: string;
  story_type: 'short_form' | 'long_form';
  created_at: string;
  completed_at: string;
  // Enhanced fields
  character?: Character;
  playtime_hours: number;
  xp_gained: number;
  items_found: number;
  monsters_defeated: number;
  locations_discovered: number;
  major_decisions: Array<{
    stage: string;
    decision: string;
    timestamp: string;
  }>;
  final_outcome: 'victory' | 'defeat' | 'compromise' | 'escape';
  difficulty_rating: number; // 1-5
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: 'combat' | 'exploration' | 'roleplay' | 'progression' | 'completion';
  unlocked_at: string;
  character_id?: number;
  character?: Character;
  rarity: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
}

interface GameSession {
  id: string;
  adventure_id: number;
  character_id: number;
  started_at: string;
  ended_at: string;
  duration_minutes: number;
  xp_gained: number;
  major_events: string[];
  character?: Character;
  adventure_title?: string;
}

type ViewMode = 'adventures' | 'achievements' | 'sessions';
type TimeFilter = 'all' | 'week' | 'month' | 'year';

export default function HistoryPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();

  // State management
  const [completedAdventures, setCompletedAdventures] = useState<CompletedAdventure[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [sessions, setSessions] = useState<GameSession[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingTimeout, setLoadingTimeout] = useState(false);
  
  // UI state
  const [viewMode, setViewMode] = useState<ViewMode>('adventures');
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCharacter, setSelectedCharacter] = useState<number | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Add timeout for loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      if (isLoading) {
        console.log('Loading timeout reached after 10 seconds');
        setLoadingTimeout(true);
      }
    }, 10000); // 10 second timeout

    return () => clearTimeout(timer);
  }, [isLoading]);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      console.log('Starting fetchData for history...');
      try {
        console.log('Getting token...');
        const token = await getToken();
        console.log('Token obtained:', token ? 'Present' : 'Missing');
        
        if (!token) {
          console.error('No token available - this will cause authentication failure');
          setError('Authentication failed - no token available');
          return;
        }
        
        // Fetch characters
        console.log('Fetching characters...');
        const charactersResponse = await fetch('http://localhost:8000/api/characters', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        console.log('Characters response status:', charactersResponse.status);
        
        let charactersData = [];
        if (charactersResponse.ok) {
          const charactersRawData = await charactersResponse.json();
          console.log('Raw characters data:', charactersRawData);
          
          // Handle CharacterList response format from backend
          charactersData = charactersRawData.characters || charactersRawData;
          console.log('Processed characters data:', charactersData);
          
          if (!Array.isArray(charactersData)) {
            console.error('Characters data is not an array:', charactersData);
            setError('Invalid character data format received');
            return;
          }
          
          setCharacters(charactersData);
        } else {
          console.error('Characters fetch failed:', charactersResponse.status, charactersResponse.statusText);
          const errorText = await charactersResponse.text();
          console.error('Characters error response:', errorText);
          setError(`Failed to load characters: ${charactersResponse.status} ${charactersResponse.statusText}`);
          return;
        }

        // Fetch completed adventures (stories with story_completed = true)
        console.log('Fetching stories...');
        const storiesResponse = await fetch('http://localhost:8000/api/stories', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        console.log('Stories response status:', storiesResponse.status);

        if (storiesResponse.ok) {
          const storiesData = await storiesResponse.json();
          console.log('Stories data:', storiesData);
          
          if (!Array.isArray(storiesData)) {
            console.error('Stories data is not an array:', storiesData);
            setError('Invalid stories data format received');
            return;
          }
          
          const completed = storiesData
            .filter((story: any) => story.story_completed)
            .map((story: any) => {
              const character = charactersData.find((char: Character) => char.id === story.character_id);
              return {
                ...story,
                character,
                playtime_hours: Math.floor(Math.random() * 25) + 2,
                xp_gained: Math.floor(Math.random() * 5000) + 1000,
                items_found: Math.floor(Math.random() * 15) + 3,
                monsters_defeated: Math.floor(Math.random() * 20) + 5,
                locations_discovered: Math.floor(Math.random() * 8) + 2,
                major_decisions: [
                  { stage: 'intro', decision: 'Chose to help the village', timestamp: story.created_at },
                  { stage: 'climax', decision: 'Spared the villain', timestamp: story.created_at }
                ],
                final_outcome: ['victory', 'defeat', 'compromise', 'escape'][Math.floor(Math.random() * 4)] as any,
                difficulty_rating: Math.floor(Math.random() * 5) + 1
              };
            });
          console.log('Completed adventures:', completed);
          setCompletedAdventures(completed);
        } else {
          console.error('Stories fetch failed:', storiesResponse.status, storiesResponse.statusText);
          const errorText = await storiesResponse.text();
          console.error('Stories error response:', errorText);
          setError(`Failed to load stories: ${storiesResponse.status} ${storiesResponse.statusText}`);
          return;
        }

        // Generate mock achievements
        const mockAchievements: Achievement[] = [
          {
            id: 'first_adventure',
            title: 'First Steps',
            description: 'Complete your first adventure',
            icon: '🎯',
            category: 'completion',
            unlocked_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            rarity: 'common'
          },
          {
            id: 'dragon_slayer',
            title: 'Dragon Slayer',
            description: 'Defeat a dragon in combat',
            icon: '🐉',
            category: 'combat',
            unlocked_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            rarity: 'epic'
          },
          {
            id: 'diplomat',
            title: 'Silver Tongue',
            description: 'Resolve 5 conflicts through diplomacy',
            icon: '🎭',
            category: 'roleplay',
            unlocked_at: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            rarity: 'rare'
          },
          {
            id: 'explorer',
            title: 'Wanderer',
            description: 'Discover 20 unique locations',
            icon: '🗺️',
            category: 'exploration',
            unlocked_at: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            rarity: 'uncommon'
          }
        ];
        setAchievements(mockAchievements);

        // Generate mock game sessions
        const mockSessions: GameSession[] = Array.from({ length: 15 }, (_, i) => ({
          id: `session_${i}`,
          adventure_id: Math.floor(Math.random() * 5) + 1,
          character_id: charactersData[Math.floor(Math.random() * charactersData.length)]?.id || 1,
          started_at: new Date(Date.now() - (i + 1) * 24 * 60 * 60 * 1000).toISOString(),
          ended_at: new Date(Date.now() - (i + 1) * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
          duration_minutes: Math.floor(Math.random() * 180) + 30,
          xp_gained: Math.floor(Math.random() * 1000) + 200,
          major_events: [
            'Encountered bandits on the road',
            'Discovered ancient ruins',
            'Made alliance with local merchants'
          ].slice(0, Math.floor(Math.random() * 3) + 1),
          adventure_title: `Adventure #${Math.floor(Math.random() * 5) + 1}`
        })).map(session => ({
          ...session,
          character: charactersData.find((char: Character) => char.id === session.character_id)
        }));
        setSessions(mockSessions);

      } catch (err) {
        console.error('Error in fetchData:', err);
        setError(`Failed to load history data: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        console.log('Setting isLoading to false');
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      console.log('User is loaded and signed in, fetching history data...');
      fetchData();
    } else {
      console.log('User not loaded or not signed in:', { isLoaded, isSignedIn });
    }
  }, [isLoaded, isSignedIn, getToken]);

  // Utility functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}h ${mins}m`;
    }
    return `${mins}m`;
  };

  const getOutcomeBadge = (outcome: string) => {
    const badges: Record<string, { color: string; text: string }> = {
      victory: { color: 'bg-green-900/50 text-green-300', text: 'Victory' },
      defeat: { color: 'bg-red-900/50 text-red-300', text: 'Defeat' },
      compromise: { color: 'bg-yellow-900/50 text-yellow-300', text: 'Compromise' },
      escape: { color: 'bg-blue-900/50 text-blue-300', text: 'Escape' }
    };
    const badge = badges[outcome] || badges.victory;
    return <span className={`px-2 py-1 rounded text-xs ${badge.color}`}>{badge.text}</span>;
  };

  const getRarityColor = (rarity: string) => {
    const colors: Record<string, string> = {
      common: 'text-gray-300',
      uncommon: 'text-green-300',
      rare: 'text-blue-300',
      epic: 'text-purple-300',
      legendary: 'text-orange-300'
    };
    return colors[rarity] || colors.common;
  };

  const getDifficultyStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star 
        key={i} 
        className={`w-4 h-4 ${i < rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'}`} 
      />
    ));
  };

  // Filter data based on time and search
  const filterData = (data: any[], dateField: string) => {
    let filtered = [...data];

    // Time filter
    if (timeFilter !== 'all') {
      const now = new Date();
      const thresholds: Record<TimeFilter, number> = {
        week: 7 * 24 * 60 * 60 * 1000,
        month: 30 * 24 * 60 * 60 * 1000,
        year: 365 * 24 * 60 * 60 * 1000,
        all: 0
      };
      const threshold = now.getTime() - thresholds[timeFilter];
      filtered = filtered.filter(item => new Date(item[dateField]).getTime() > threshold);
    }

    // Character filter
    if (selectedCharacter) {
      filtered = filtered.filter(item => item.character_id === selectedCharacter);
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(item =>
        (item.title && item.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.character?.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (item.description && item.description.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    return filtered;
  };

  // Calculate stats
  const totalCompletedAdventures = completedAdventures.length;
  const totalPlaytime = completedAdventures.reduce((sum, adv) => sum + adv.playtime_hours, 0);
  const totalXP = completedAdventures.reduce((sum, adv) => sum + adv.xp_gained, 0);
  const totalAchievements = achievements.length;

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">Loading history...</div>
          <div className="text-gray-400 text-sm">
            Clerk loaded: {isLoaded ? 'Yes' : 'No'} | Signed in: {isSignedIn ? 'Yes' : 'No'}
          </div>
          <div className="text-gray-400 text-sm mt-2">
            Check browser console for detailed logs
          </div>
          {loadingTimeout && (
            <div className="mt-6 p-4 bg-red-900/50 border border-red-500 rounded-lg">
              <p className="text-red-300 font-medium">Loading is taking longer than expected</p>
              <p className="text-red-200 text-sm mt-2">
                This could be an authentication issue. Try refreshing the page or signing out and back in.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Refresh Page
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-300 text-xl mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-white hover:text-purple-300 mr-4"
              >
                ← Back to Dashboard
              </button>
              <div>
                <h1 className="text-2xl font-bold text-white">Game History</h1>
                <p className="text-gray-300">
                  Your completed adventures and achievements
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <Trophy className="w-8 h-8 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{totalCompletedAdventures}</div>
            <div className="text-sm text-gray-400">Completed Adventures</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <Clock className="w-8 h-8 text-blue-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{totalPlaytime}h</div>
            <div className="text-sm text-gray-400">Total Playtime</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <Star className="w-8 h-8 text-purple-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{totalXP.toLocaleString()}</div>
            <div className="text-sm text-gray-400">XP Earned</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <Award className="w-8 h-8 text-orange-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{totalAchievements}</div>
            <div className="text-sm text-gray-400">Achievements</div>
          </div>
        </div>

        {/* Controls */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* View Mode Tabs */}
            <div className="flex bg-gray-700/50 rounded-md border border-gray-600/50">
              <button
                onClick={() => setViewMode('adventures')}
                className={`px-4 py-2 text-sm font-medium rounded-l-md transition-colors ${
                  viewMode === 'adventures'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <BookOpen className="w-4 h-4 inline mr-2" />
                Adventures
              </button>
              <button
                onClick={() => setViewMode('achievements')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  viewMode === 'achievements'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <Trophy className="w-4 h-4 inline mr-2" />
                Achievements
              </button>
              <button
                onClick={() => setViewMode('sessions')}
                className={`px-4 py-2 text-sm font-medium rounded-r-md transition-colors ${
                  viewMode === 'sessions'
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                <Activity className="w-4 h-4 inline mr-2" />
                Sessions
              </button>
            </div>

            {/* Filters */}
            <div className="flex items-center gap-2">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 pr-4 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                />
              </div>

              {/* Time Filter */}
              <select
                value={timeFilter}
                onChange={(e) => setTimeFilter(e.target.value as TimeFilter)}
                className="px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="all">All Time</option>
                <option value="week">Past Week</option>
                <option value="month">Past Month</option>
                <option value="year">Past Year</option>
              </select>

              {/* Character Filter */}
              <select
                value={selectedCharacter || ''}
                onChange={(e) => setSelectedCharacter(e.target.value ? parseInt(e.target.value) : null)}
                className="px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Characters</option>
                {characters.map((character) => (
                  <option key={character.id} value={character.id}>
                    {character.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Content Display */}
        {viewMode === 'adventures' && (
          <div>
            {filterData(completedAdventures, 'completed_at').length === 0 ? (
              <div className="text-center py-16">
                <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">No completed adventures</h3>
                <p className="text-gray-400">Complete some adventures to see them here!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {filterData(completedAdventures, 'completed_at').map((adventure) => (
                  <div
                    key={adventure.id}
                    className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 hover:border-purple-400/50 transition-colors"
                  >
                    {/* Adventure Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-white mb-2">
                          {adventure.title || `Adventure #${adventure.id}`}
                        </h3>
                        <div className="flex gap-2 mb-3">
                          {getOutcomeBadge(adventure.final_outcome)}
                          <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs">
                            {adventure.story_type === 'short_form' ? 'Quick Adventure' : 'Epic Campaign'}
                          </span>
                        </div>
                      </div>
                      <div className="flex">
                        {getDifficultyStars(adventure.difficulty_rating)}
                      </div>
                    </div>

                    {/* Character Info */}
                    {adventure.character && (
                      <div className="flex items-center mb-4">
                        <CharacterAvatar character={adventure.character} size="sm" className="mr-3" />
                        <div>
                          <div className="font-medium text-white">{adventure.character.name}</div>
                          <div className="text-sm text-gray-400">
                            Level {adventure.character.level} {adventure.character.race} {adventure.character.character_class}
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-4 text-sm mb-4">
                      <div className="flex items-center text-gray-400">
                        <Clock className="w-4 h-4 mr-2" />
                        <span>{adventure.playtime_hours}h played</span>
                      </div>
                      <div className="flex items-center text-gray-400">
                        <Star className="w-4 h-4 mr-2" />
                        <span>{adventure.xp_gained.toLocaleString()} XP</span>
                      </div>
                      <div className="flex items-center text-gray-400">
                        <Sword className="w-4 h-4 mr-2" />
                        <span>{adventure.monsters_defeated} defeated</span>
                      </div>
                      <div className="flex items-center text-gray-400">
                        <MapPin className="w-4 h-4 mr-2" />
                        <span>{adventure.locations_discovered} locations</span>
                      </div>
                    </div>

                    {/* Completed Date */}
                    <div className="text-xs text-gray-500 mb-4">
                      Completed {formatDate(adventure.completed_at)}
                    </div>

                    {/* View Details Button */}
                    <button
                      onClick={() => router.push(`/adventure/${adventure.id}`)}
                      className="w-full flex items-center justify-center bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {viewMode === 'achievements' && (
          <div>
            {achievements.length === 0 ? (
              <div className="text-center py-16">
                <Trophy className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">No achievements yet</h3>
                <p className="text-gray-400">Start playing to unlock achievements!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {achievements.map((achievement) => (
                  <div
                    key={achievement.id}
                    className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 hover:border-purple-400/50 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="text-2xl">{achievement.icon}</div>
                      <div className="flex-1">
                        <h3 className={`font-bold mb-1 ${getRarityColor(achievement.rarity)}`}>
                          {achievement.title}
                        </h3>
                        <p className="text-sm text-gray-400 mb-2">{achievement.description}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-500">
                            {formatDate(achievement.unlocked_at)}
                          </span>
                          <span className={`text-xs ${getRarityColor(achievement.rarity)} capitalize`}>
                            {achievement.rarity}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {viewMode === 'sessions' && (
          <div>
            {filterData(sessions, 'started_at').length === 0 ? (
              <div className="text-center py-16">
                <Activity className="w-16 h-16 text-gray-500 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">No sessions found</h3>
                <p className="text-gray-400">Your game sessions will appear here!</p>
              </div>
            ) : (
              <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 overflow-hidden">
                <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 text-sm font-medium text-gray-300">
                  <div className="col-span-3">Session</div>
                  <div className="col-span-2">Character</div>
                  <div className="col-span-2">Duration</div>
                  <div className="col-span-2">XP Gained</div>
                  <div className="col-span-3">Date</div>
                </div>
                
                {filterData(sessions, 'started_at').map((session) => (
                  <div
                    key={session.id}
                    className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 hover:bg-gray-800/30 transition-colors"
                  >
                    <div className="col-span-3">
                      <div className="font-medium text-white">{session.adventure_title}</div>
                      <div className="text-sm text-gray-400">
                                                 {session.major_events.slice(0, 1).map((event: string) => event)}
                      </div>
                    </div>
                    
                    <div className="col-span-2 flex items-center">
                      {session.character && (
                        <div className="flex items-center">
                          <CharacterAvatar character={session.character} size="sm" className="mr-2" />
                          <div className="text-white text-sm">{session.character.name}</div>
                        </div>
                      )}
                    </div>
                    
                    <div className="col-span-2 flex items-center">
                      <div className="text-white">{formatDuration(session.duration_minutes)}</div>
                    </div>
                    
                    <div className="col-span-2 flex items-center">
                      <div className="text-green-300">+{session.xp_gained} XP</div>
                    </div>
                    
                    <div className="col-span-3 flex items-center">
                      <div className="text-gray-300">{formatDate(session.started_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 