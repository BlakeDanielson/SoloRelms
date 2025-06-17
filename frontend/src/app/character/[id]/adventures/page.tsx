'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { 
  Search, 
  Filter, 
  Calendar, 
  Clock, 
  Trophy, 
  Play, 
  Eye, 
  Archive,
  MoreVertical,
  CheckCircle2,
  AlertCircle,
  Star,
  Users,
  MapPin,
  Sword,
  BookOpen,
  Plus,
  SortAsc,
  SortDesc
} from 'lucide-react';
import CharacterAvatar from '@/components/game/CharacterAvatar';
import StoryProgressTracker from '@/components/game/StoryProgressTracker';

// Types
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
}

interface Adventure {
  id: number;
  character_id: number;
  title?: string;
  current_stage: string;
  stages_completed: string[];
  story_completed: boolean;
  completion_type?: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  story_seed?: string;
  story_type: string;
  major_decisions: Array<{
    stage: string;
    decision: string;
    timestamp: string;
  }>;
  total_sessions?: number;
  playtime_hours?: number;
  xp_gained?: number;
  items_found?: number;
  monsters_defeated?: number;
  locations_discovered?: number;
}

type SortOption = 'created' | 'completed' | 'playtime' | 'xp' | 'title';
type FilterOption = 'all' | 'completed' | 'in_progress' | 'short_form' | 'long_form';

export default function CharacterAdventuresPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const characterId = params.id;

  const [character, setCharacter] = useState<Character | null>(null);
  const [adventures, setAdventures] = useState<Adventure[]>([]);
  const [filteredAdventures, setFilteredAdventures] = useState<Adventure[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters and search
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOption, setFilterOption] = useState<FilterOption>('all');
  const [sortOption, setSortOption] = useState<SortOption>('created');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [showFilters, setShowFilters] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      if (!characterId) return;
      
      try {
        const token = await getToken();
        
        // Fetch character
        const characterResponse = await fetch(`http://localhost:8000/api/characters/${characterId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (characterResponse.ok) {
          const characterData = await characterResponse.json();
          setCharacter(characterData);
        }

        // Fetch adventures
        const adventuresResponse = await fetch(`http://localhost:8000/api/characters/${characterId}/adventures`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (adventuresResponse.ok) {
          const adventuresData = await adventuresResponse.json();
          
          // Enhance adventures with mock data for now
          const enhancedAdventures = adventuresData.map((adv: Adventure) => ({
            ...adv,
            total_sessions: Math.floor(Math.random() * 10) + 1,
            playtime_hours: Math.floor(Math.random() * 20) + 1,
            xp_gained: Math.floor(Math.random() * 5000) + 500,
            items_found: Math.floor(Math.random() * 15) + 3,
            monsters_defeated: Math.floor(Math.random() * 25) + 5,
            locations_discovered: Math.floor(Math.random() * 8) + 2,
            major_decisions: [
              { stage: 'intro', decision: 'Chose to help the villagers', timestamp: adv.created_at },
              { stage: 'first_combat', decision: 'Used diplomacy instead of fighting', timestamp: adv.created_at }
            ]
          }));
          
          setAdventures(enhancedAdventures);
        }
      } catch (err) {
        setError('Failed to load adventures');
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      fetchData();
    }
  }, [characterId, isLoaded, isSignedIn, getToken]);

  // Filter and sort adventures
  useEffect(() => {
    let filtered = [...adventures];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(adv => 
        (adv.title && adv.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
        adv.story_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        adv.current_stage.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply status filter
    switch (filterOption) {
      case 'completed':
        filtered = filtered.filter(adv => adv.story_completed);
        break;
      case 'in_progress':
        filtered = filtered.filter(adv => !adv.story_completed);
        break;
      case 'short_form':
        filtered = filtered.filter(adv => adv.story_type === 'short_form');
        break;
      case 'long_form':
        filtered = filtered.filter(adv => adv.story_type === 'long_form');
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortOption) {
        case 'created':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'completed':
          aValue = a.completed_at ? new Date(a.completed_at).getTime() : 0;
          bValue = b.completed_at ? new Date(b.completed_at).getTime() : 0;
          break;
        case 'playtime':
          aValue = a.playtime_hours || 0;
          bValue = b.playtime_hours || 0;
          break;
        case 'xp':
          aValue = a.xp_gained || 0;
          bValue = b.xp_gained || 0;
          break;
        case 'title':
          aValue = a.title || `Adventure #${a.id}`;
          bValue = b.title || `Adventure #${b.id}`;
          break;
        default:
          return 0;
      }

      if (sortOption === 'title') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
    });

    setFilteredAdventures(filtered);
  }, [adventures, searchTerm, filterOption, sortOption, sortDirection]);

  // Helper functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getCompletionRate = (adventure: Adventure) => {
    const totalStages = 6; // Based on our story stages
    return Math.round((adventure.stages_completed.length / totalStages) * 100);
  };

  const getAdventureTypeIcon = (type: string) => {
    return type === 'short_form' ? '⚡' : '📖';
  };

  const getAdventureTypeLabel = (type: string) => {
    return type === 'short_form' ? 'Quick Adventure' : 'Epic Campaign';
  };

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading adventures...</div>
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
            onClick={() => router.push('/dashboard')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
          >
            Back to Dashboard
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
                onClick={() => router.push(`/character/${characterId}`)}
                className="text-white hover:text-purple-300 mr-4"
              >
                ← Back to Character
              </button>
              {character && (
                <div className="flex items-center">
                  <CharacterAvatar character={character} size="md" />
                  <div className="ml-4">
                    <h1 className="text-2xl font-bold text-white">{character.name}'s Adventures</h1>
                    <p className="text-gray-300">
                      {adventures.length} total adventures • {adventures.filter(a => a.story_completed).length} completed
                    </p>
                  </div>
                </div>
              )}
            </div>
            
            <button
              onClick={() => router.push(`/adventure/create?character=${characterId}`)}
              className="flex items-center bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
            >
              <Plus className="w-5 h-5 mr-2" />
              New Adventure
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters and Search */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10 mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search adventures..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-800/50 border border-gray-600/50 rounded-md text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
              />
            </div>

            {/* Filter and Sort Controls */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center bg-gray-700/50 hover:bg-gray-600/50 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </button>

              <select
                value={sortOption}
                onChange={(e) => setSortOption(e.target.value as SortOption)}
                className="bg-gray-800/50 border border-gray-600/50 rounded-md text-white px-3 py-2 focus:outline-none focus:border-purple-400"
              >
                <option value="created">Created Date</option>
                <option value="completed">Completed Date</option>
                <option value="playtime">Playtime</option>
                <option value="xp">XP Gained</option>
                <option value="title">Title</option>
              </select>

              <button
                onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
                className="bg-gray-700/50 hover:bg-gray-600/50 text-white p-2 rounded-md transition-colors"
              >
                {sortDirection === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Filter Options */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-600/50">
              <div className="flex flex-wrap gap-2">
                {([
                  { value: 'all', label: 'All Adventures' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'in_progress', label: 'In Progress' },
                  { value: 'short_form', label: 'Quick Adventures' },
                  { value: 'long_form', label: 'Epic Campaigns' }
                ] as const).map((filter) => (
                  <button
                    key={filter.value}
                    onClick={() => setFilterOption(filter.value)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      filterOption === filter.value
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Adventures Grid */}
        {filteredAdventures.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">
              {adventures.length === 0 ? 'No adventures yet' : 'No adventures match your filters'}
            </h3>
            <p className="text-gray-400 mb-6">
              {adventures.length === 0 
                ? 'Start your first adventure to begin your journey!'
                : 'Try adjusting your search or filter criteria.'
              }
            </p>
            {adventures.length === 0 && (
              <button
                onClick={() => router.push(`/adventure/create?character=${characterId}`)}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-md transition-colors"
              >
                Start Your First Adventure
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAdventures.map((adventure) => (
              <div
                key={adventure.id}
                className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 overflow-hidden hover:border-purple-400/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20"
              >
                {/* Adventure Header */}
                <div className="p-6 pb-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-lg">{getAdventureTypeIcon(adventure.story_type)}</span>
                        <span className="text-xs text-gray-400 uppercase tracking-wide">
                          {getAdventureTypeLabel(adventure.story_type)}
                        </span>
                      </div>
                      <h3 className="text-lg font-bold text-white mb-1">
                        {adventure.title || `Adventure #${adventure.id}`}
                      </h3>
                      <p className="text-sm text-gray-400 capitalize">
                        Current: {adventure.current_stage.replace(/_/g, ' ')}
                      </p>
                    </div>
                    
                    <div className="flex items-center">
                      {adventure.story_completed ? (
                        <CheckCircle2 className="w-6 h-6 text-green-400" />
                      ) : (
                        <div className="w-6 h-6 bg-blue-500 rounded-full animate-pulse" />
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-gray-400">Progress</span>
                      <span className="text-xs text-gray-400">{getCompletionRate(adventure)}%</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          adventure.story_completed ? 'bg-green-500' : 'bg-blue-500'
                        }`}
                        style={{ width: `${getCompletionRate(adventure)}%` }}
                      />
                    </div>
                  </div>

                  {/* Story Progress Tracker - Compact */}
                  <StoryProgressTracker
                    currentStage={adventure.current_stage}
                    stagesCompleted={adventure.stages_completed}
                    storyCompleted={adventure.story_completed}
                    compact={true}
                    className="mb-4"
                  />
                </div>

                {/* Adventure Stats */}
                <div className="px-6 pb-4">
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="flex items-center text-gray-400">
                      <Clock className="w-4 h-4 mr-1" />
                      <span>{adventure.playtime_hours || 0}h played</span>
                    </div>
                    <div className="flex items-center text-gray-400">
                      <Star className="w-4 h-4 mr-1" />
                      <span>{adventure.xp_gained || 0} XP</span>
                    </div>
                    <div className="flex items-center text-gray-400">
                      <Sword className="w-4 h-4 mr-1" />
                      <span>{adventure.monsters_defeated || 0} defeated</span>
                    </div>
                    <div className="flex items-center text-gray-400">
                      <MapPin className="w-4 h-4 mr-1" />
                      <span>{adventure.locations_discovered || 0} locations</span>
                    </div>
                  </div>
                </div>

                {/* Adventure Footer */}
                <div className="bg-gray-800/50 px-6 py-4 border-t border-gray-700/50">
                  <div className="flex items-center justify-between text-sm text-gray-400 mb-3">
                    <span>Created {formatDate(adventure.created_at)}</span>
                    {adventure.completed_at && (
                      <span>Completed {formatDate(adventure.completed_at)}</span>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => router.push(`/adventure/${adventure.id}`)}
                      className="flex items-center flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </button>
                    
                    {!adventure.story_completed && (
                      <button
                        onClick={() => router.push(`/game?character=${adventure.character_id}&story=${adventure.id}`)}
                        className="flex items-center bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                      >
                        <Play className="w-4 h-4 mr-1" />
                        Resume
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 