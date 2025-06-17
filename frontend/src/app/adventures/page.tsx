'use client';

import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import {
  Plus,
  Search,
  Filter,
  Grid,
  List,
  Play,
  Eye,
  Clock,
  Star,
  Sword,
  MapPin,
  BookOpen,
  Trash2
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

interface Adventure {
  id: number;
  character_id: number;
  title?: string;
  story_type: 'short_form' | 'long_form';
  story_completed: boolean;
  current_stage: string;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  updated_at: string;
  // Enhanced fields
  character?: Character;
  total_sessions?: number;
  playtime_hours?: number;
  xp_gained?: number;
  items_found?: number;
  monsters_defeated?: number;
  locations_discovered?: number;
  major_decisions?: Array<{
    stage: string;
    decision: string;
    timestamp: string;
  }>;
}

type ViewMode = 'grid' | 'list';
type SortOption = 'created' | 'updated' | 'playtime' | 'xp' | 'character' | 'status';
type SortDirection = 'asc' | 'desc';
type FilterOption = 'all' | 'in_progress' | 'completed' | 'short_form' | 'long_form' | 'recent';

export default function AdventuresPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();

  // State management
  const [adventures, setAdventures] = useState<Adventure[]>([]);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [filteredAdventures, setFilteredAdventures] = useState<Adventure[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('updated');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filterOption, setFilterOption] = useState<FilterOption>('all');
  const [showFilters, setShowFilters] = useState(false);

  // Delete confirmation state
  const [deleteConfirmation, setDeleteConfirmation] = useState<{
    isOpen: boolean;
    adventureId: number | null;
    adventureTitle: string;
  }>({
    isOpen: false,
    adventureId: null,
    adventureTitle: ''
  });
  const [isDeleting, setIsDeleting] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = await getToken();
        
        if (!token) {
          setError('Authentication token not available');
          return;
        }
        
        // Fetch characters first
        const charactersResponse = await fetch('http://localhost:8000/api/characters', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        let charactersData = [];
        if (charactersResponse.ok) {
          const rawCharactersData = await charactersResponse.json();
          console.log('Characters API response:', rawCharactersData);
          console.log('Characters API response type:', typeof rawCharactersData);
          console.log('Is array?', Array.isArray(rawCharactersData));
          
          // Handle different response formats
          if (Array.isArray(rawCharactersData)) {
            charactersData = rawCharactersData;
          } else if (rawCharactersData && Array.isArray(rawCharactersData.characters)) {
            charactersData = rawCharactersData.characters;
          } else if (rawCharactersData && Array.isArray(rawCharactersData.data)) {
            charactersData = rawCharactersData.data;
          } else {
            console.error('Unexpected characters response format:', rawCharactersData);
            charactersData = [];
          }
          
          setCharacters(charactersData);
        } else {
          console.error('Failed to fetch characters:', charactersResponse.status, charactersResponse.statusText);
        }

        // Fetch adventures
        const adventuresResponse = await fetch('http://localhost:8000/api/stories', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (adventuresResponse.ok) {
          const rawAdventuresData = await adventuresResponse.json();
          console.log('Adventures API response:', rawAdventuresData);
          console.log('Adventures API response type:', typeof rawAdventuresData);
          console.log('Is array?', Array.isArray(rawAdventuresData));
          
          // Handle different response formats
          let adventuresData = [];
          if (Array.isArray(rawAdventuresData)) {
            adventuresData = rawAdventuresData;
          } else if (rawAdventuresData && Array.isArray(rawAdventuresData.stories)) {
            adventuresData = rawAdventuresData.stories;
          } else if (rawAdventuresData && Array.isArray(rawAdventuresData.data)) {
            adventuresData = rawAdventuresData.data;
          } else {
            console.error('Unexpected adventures response format:', rawAdventuresData);
            adventuresData = [];
          }
          
          // Enhance adventures with character data and mock statistics
          const enhancedAdventures = adventuresData.map((adv: Adventure) => {
            const character = charactersData.find((char: Character) => char.id === adv.character_id);
            return {
              ...adv,
              character,
              total_sessions: Math.floor(Math.random() * 15) + 1,
              playtime_hours: Math.floor(Math.random() * 30) + 1,
              xp_gained: Math.floor(Math.random() * 8000) + 500,
              items_found: Math.floor(Math.random() * 20) + 2,
              monsters_defeated: Math.floor(Math.random() * 35) + 3,
              locations_discovered: Math.floor(Math.random() * 12) + 1,
              major_decisions: [
                { 
                  stage: 'intro', 
                  decision: 'Chose to help the villagers', 
                  timestamp: adv.created_at 
                },
                { 
                  stage: 'first_combat', 
                  decision: 'Used diplomacy instead of fighting', 
                  timestamp: adv.created_at 
                }
              ]
            };
          });
          
          setAdventures(enhancedAdventures);
          setError(null); // Clear any previous errors
        } else {
          console.error('Failed to fetch adventures:', adventuresResponse.status, adventuresResponse.statusText);
          setError('Failed to load adventures');
        }
      } catch (err) {
        console.error('Error in fetchData:', err);
        setError('Failed to load data');
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      fetchData();
    }
  }, [isLoaded, isSignedIn, getToken]);

  // Filter and sort adventures
  useEffect(() => {
    let filtered = [...adventures];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(adv =>
        (adv.title && adv.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (adv.character?.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
        adv.current_stage.toLowerCase().includes(searchTerm.toLowerCase()) ||
        adv.story_type.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply category filter
    switch (filterOption) {
      case 'in_progress':
        filtered = filtered.filter(adv => !adv.story_completed);
        break;
      case 'completed':
        filtered = filtered.filter(adv => adv.story_completed);
        break;
      case 'short_form':
        filtered = filtered.filter(adv => adv.story_type === 'short_form');
        break;
      case 'long_form':
        filtered = filtered.filter(adv => adv.story_type === 'long_form');
        break;
      case 'recent':
        const recentThreshold = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
        filtered = filtered.filter(adv => new Date(adv.updated_at) > recentThreshold);
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortOption) {
        case 'created':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'updated':
          aValue = new Date(a.updated_at).getTime();
          bValue = new Date(b.updated_at).getTime();
          break;
        case 'playtime':
          aValue = a.playtime_hours || 0;
          bValue = b.playtime_hours || 0;
          break;
        case 'xp':
          aValue = a.xp_gained || 0;
          bValue = b.xp_gained || 0;
          break;
        case 'character':
          aValue = a.character?.name.toLowerCase() || '';
          bValue = b.character?.name.toLowerCase() || '';
          break;
        case 'status':
          aValue = a.story_completed ? 1 : 0;
          bValue = b.story_completed ? 1 : 0;
          break;
        default:
          aValue = new Date(a.updated_at).getTime();
          bValue = new Date(b.updated_at).getTime();
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredAdventures(filtered);
  }, [adventures, searchTerm, filterOption, sortOption, sortDirection]);

  // Utility functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatLastUpdated = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return formatDate(dateString);
  };

  const getStageDisplay = (stage: string) => {
    const stageMap: Record<string, string> = {
      'intro': 'Introduction',
      'inciting_incident': 'Inciting Incident',
      'first_combat': 'First Combat',
      'twist': 'Plot Twist',
      'final_conflict': 'Final Conflict',
      'resolution': 'Resolution'
    };
    return stageMap[stage] || stage.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStatusBadge = (adventure: Adventure) => {
    if (adventure.story_completed) {
      return <span className="px-2 py-1 bg-green-900/50 text-green-300 rounded text-xs">Completed</span>;
    }
    return <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">In Progress</span>;
  };

  const getTypeBadge = (type: string) => {
    return type === 'short_form' 
      ? <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs">Quick Adventure</span>
      : <span className="px-2 py-1 bg-orange-900/50 text-orange-300 rounded text-xs">Epic Campaign</span>;
  };

  // Delete adventure function
  const handleDeleteAdventure = async (adventureId: number) => {
    try {
      setIsDeleting(true);
      const token = await getToken();
      
      if (!token) {
        setError('Authentication token not available');
        return;
      }

      const response = await fetch(`http://localhost:8000/api/stories/${adventureId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // Remove the adventure from state
        setAdventures(prev => prev.filter(adv => adv.id !== adventureId));
        setDeleteConfirmation({ isOpen: false, adventureId: null, adventureTitle: '' });
        
        // Show success message (you could add a toast notification here)
        console.log('Adventure deleted successfully');
      } else {
        const errorData = await response.json();
        setError(`Failed to delete adventure: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('Error deleting adventure:', err);
      setError('Failed to delete adventure');
    } finally {
      setIsDeleting(false);
    }
  };

  const openDeleteConfirmation = (adventure: Adventure) => {
    setDeleteConfirmation({
      isOpen: true,
      adventureId: adventure.id,
      adventureTitle: adventure.title || `Adventure #${adventure.id}`
    });
  };

  const closeDeleteConfirmation = () => {
    setDeleteConfirmation({ isOpen: false, adventureId: null, adventureTitle: '' });
    setError(null); // Clear any error messages
  };

  // Stats calculation
  const totalAdventures = adventures.length;
  const completedAdventures = adventures.filter(adv => adv.story_completed).length;
  const inProgressAdventures = adventures.filter(adv => !adv.story_completed).length;
  const totalPlaytime = adventures.reduce((sum, adv) => sum + (adv.playtime_hours || 0), 0);
  const totalXP = adventures.reduce((sum, adv) => sum + (adv.xp_gained || 0), 0);

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
                <h1 className="text-2xl font-bold text-white">My Adventures</h1>
                <p className="text-gray-300">
                  {totalAdventures} total • {inProgressAdventures} in progress • {completedAdventures} completed
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/adventure/create')}
                className="flex items-center bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Plus className="w-5 h-5 mr-2" />
                New Adventure
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <div className="text-2xl font-bold text-blue-300">{inProgressAdventures}</div>
            <div className="text-sm text-gray-400">In Progress</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <div className="text-2xl font-bold text-green-300">{completedAdventures}</div>
            <div className="text-sm text-gray-400">Completed</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <div className="text-2xl font-bold text-yellow-300">{totalPlaytime}h</div>
            <div className="text-sm text-gray-400">Total Playtime</div>
          </div>
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4 text-center">
            <div className="text-2xl font-bold text-purple-300">{totalXP.toLocaleString()}</div>
            <div className="text-sm text-gray-400">XP Earned</div>
          </div>
        </div>

        {/* Controls Bar */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search adventures, characters..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Controls */}
            <div className="flex items-center gap-2">
              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center px-3 py-2 rounded-md text-sm transition-colors ${
                  showFilters
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </button>

              {/* Sort */}
              <select
                value={`${sortOption}_${sortDirection}`}
                onChange={(e) => {
                  const [option, direction] = e.target.value.split('_');
                  setSortOption(option as SortOption);
                  setSortDirection(direction as SortDirection);
                }}
                className="px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="updated_desc">Recently Updated</option>
                <option value="created_desc">Newest First</option>
                <option value="created_asc">Oldest First</option>
                <option value="playtime_desc">Most Playtime</option>
                <option value="xp_desc">Most XP</option>
                <option value="character_asc">Character A-Z</option>
                <option value="status_asc">By Status</option>
              </select>

              {/* View Mode */}
              <div className="flex bg-gray-700/50 rounded-md border border-gray-600/50">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 ${
                    viewMode === 'grid'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <Grid className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 ${
                    viewMode === 'list'
                      ? 'bg-purple-600 text-white'
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          {/* Expanded Filters */}
          {showFilters && (
            <div className="mt-4 pt-4 border-t border-gray-600/50">
              <div className="flex flex-wrap gap-2">
                {([
                  { value: 'all', label: 'All Adventures' },
                  { value: 'in_progress', label: 'In Progress' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'short_form', label: 'Quick Adventures' },
                  { value: 'long_form', label: 'Epic Campaigns' },
                  { value: 'recent', label: 'Recent (7 days)' }
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

        {/* Adventures Display */}
        {filteredAdventures.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">
              {adventures.length === 0 ? 'No adventures yet' : 'No adventures match your filters'}
            </h3>
            <p className="text-gray-400 mb-6">
              {adventures.length === 0 
                ? 'Start your first adventure to begin your epic journey!'
                : 'Try adjusting your search or filter criteria.'
              }
            </p>
            {adventures.length === 0 && (
              <button
                onClick={() => router.push('/adventure/create')}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-md transition-colors"
              >
                Start Your First Adventure
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAdventures.map((adventure) => (
              <div
                key={adventure.id}
                className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 hover:border-purple-400/50 transition-all duration-200 overflow-hidden"
              >
                {/* Adventure Header */}
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white mb-2">
                        {adventure.title || `Adventure #${adventure.id}`}
                      </h3>
                      <div className="flex gap-2 mb-3">
                        {getStatusBadge(adventure)}
                        {getTypeBadge(adventure.story_type)}
                      </div>
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

                  {/* Current Stage */}
                  <div className="mb-4">
                    <div className="text-sm text-gray-400 mb-1">Current Stage</div>
                    <div className="text-white font-medium">{getStageDisplay(adventure.current_stage)}</div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center text-gray-400">
                      <Clock className="w-4 h-4 mr-2" />
                      <span>{adventure.playtime_hours}h played</span>
                    </div>
                    <div className="flex items-center text-gray-400">
                      <Star className="w-4 h-4 mr-2" />
                      <span>{adventure.xp_gained?.toLocaleString()} XP</span>
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

                  {/* Last Updated */}
                  <div className="text-xs text-gray-500 mt-4">
                    Updated {formatLastUpdated(adventure.updated_at)}
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-gray-800/50 px-6 py-4 border-t border-gray-700/50">
                  <div className="flex gap-2">
                    <button
                      onClick={() => router.push(`/adventure/${adventure.id}`)}
                      className="flex items-center flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md transition-colors text-sm justify-center"
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

                    <button
                      onClick={() => openDeleteConfirmation(adventure)}
                      className="flex items-center bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                      title="Delete Adventure"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* List View */
          <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 overflow-hidden">
            <div className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 text-sm font-medium text-gray-300">
              <div className="col-span-4">Adventure</div>
              <div className="col-span-2">Character</div>
              <div className="col-span-2">Status</div>
              <div className="col-span-2">Progress</div>
              <div className="col-span-2">Actions</div>
            </div>
            
            {filteredAdventures.map((adventure) => (
              <div
                key={adventure.id}
                className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 hover:bg-gray-800/30 transition-colors"
              >
                <div className="col-span-4">
                  <div className="font-medium text-white mb-1">
                    {adventure.title || `Adventure #${adventure.id}`}
                  </div>
                  <div className="flex gap-2">
                    {getStatusBadge(adventure)}
                    {getTypeBadge(adventure.story_type)}
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center">
                  {adventure.character && (
                    <div className="flex items-center">
                                             <CharacterAvatar character={adventure.character} size="sm" className="mr-2" />
                      <div>
                        <div className="text-white text-sm">{adventure.character.name}</div>
                        <div className="text-gray-400 text-xs">Level {adventure.character.level}</div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="col-span-2 flex items-center">
                  <div>
                    <div className="text-white text-sm">{getStageDisplay(adventure.current_stage)}</div>
                    <div className="text-gray-400 text-xs">
                      {adventure.playtime_hours}h • {adventure.xp_gained?.toLocaleString()} XP
                    </div>
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center">
                  <div className="text-gray-300 text-sm">
                    {formatLastUpdated(adventure.updated_at)}
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center gap-2">
                  <button
                    onClick={() => router.push(`/adventure/${adventure.id}`)}
                    className="flex items-center bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    <Eye className="w-3 h-3 mr-1" />
                    View
                  </button>
                  {!adventure.story_completed && (
                    <button
                      onClick={() => router.push(`/game?character=${adventure.character_id}&story=${adventure.id}`)}
                      className="flex items-center bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                    >
                      <Play className="w-3 h-3 mr-1" />
                      Resume
                    </button>
                  )}
                  <button
                    onClick={() => openDeleteConfirmation(adventure)}
                    className="flex items-center bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-sm transition-colors"
                    title="Delete Adventure"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmation.isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              closeDeleteConfirmation();
            }
          }}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              closeDeleteConfirmation();
            }
          }}
          tabIndex={-1}
        >
          <div className="bg-gray-800 rounded-lg border border-gray-600 p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-red-600/20 rounded-full flex items-center justify-center mr-4">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Delete Adventure</h3>
                <p className="text-gray-400 text-sm">This action cannot be undone</p>
              </div>
            </div>
            
            <p className="text-gray-300 mb-6">
              Are you sure you want to delete <span className="font-semibold text-white">&quot;{deleteConfirmation.adventureTitle}&quot;</span>? 
              This will free up the character to start new adventures.
            </p>
            
            <div className="flex gap-3">
              <button
                onClick={closeDeleteConfirmation}
                disabled={isDeleting}
                className="flex-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-700 disabled:opacity-50 text-white px-4 py-2 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => deleteConfirmation.adventureId && handleDeleteAdventure(deleteConfirmation.adventureId)}
                disabled={isDeleting}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center"
              >
                {isDeleting ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                    Deleting...
                  </>
                ) : (
                  'Delete Adventure'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 