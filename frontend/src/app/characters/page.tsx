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
  SortAsc,
  SortDesc,
  User,
  Sword,
  Shield,
  Heart,
  Star,
  Clock,
  Calendar,
  Eye,
  Edit3,
  Trash2,
  Play,
  BookOpen
} from 'lucide-react';
import CharacterAvatar from '../../components/game/CharacterAvatar';

// Types
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  max_hp: number;
  current_hp: number;
  armor_class: number;
  background: string;
  created_at: string;
  updated_at: string;
  // Additional stats for display
  total_adventures?: number;
  completed_adventures?: number;
  total_playtime_hours?: number;
  last_played?: string;
}

type ViewMode = 'grid' | 'list';
type SortOption = 'name' | 'level' | 'created' | 'last_played' | 'adventures';
type SortDirection = 'asc' | 'desc';
type FilterOption = 'all' | 'low_level' | 'mid_level' | 'high_level' | 'active' | 'inactive';

export default function CharactersPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();

  // State management
  const [characters, setCharacters] = useState<Character[]>([]);
  const [filteredCharacters, setFilteredCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [loadingTimeout, setLoadingTimeout] = useState(false);
  
  // UI state
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('created');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [filterOption, setFilterOption] = useState<FilterOption>('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedCharacters, setSelectedCharacters] = useState<number[]>([]);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

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

  // Fetch characters
  useEffect(() => {
    const fetchCharacters = async () => {
      console.log('Starting fetchCharacters...');
      try {
        console.log('Getting token...');
        const token = await getToken();
        console.log('Token obtained:', token ? 'Present' : 'Missing');
        if (token) {
          console.log('Token length:', token.length);
          console.log('Token starts with:', token.substring(0, 20) + '...');
        } else {
          console.log('No token available - this will cause authentication failure');
        }
        
        console.log('Making API request to /api/characters...');
        const response = await fetch('http://localhost:8000/api/characters', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        console.log('Response status:', response.status, response.statusText);

        if (response.ok) {
          console.log('Parsing response JSON...');
          const charactersData = await response.json();
          console.log('Raw characters data:', charactersData);
          
          // Handle CharacterList response format from backend
          const charactersList = charactersData.characters || charactersData;
          console.log('Characters list:', charactersList);
          console.log('Is characters list an array?', Array.isArray(charactersList));
          
          if (!Array.isArray(charactersList)) {
            console.error('Characters list is not an array:', charactersList);
            setError('Invalid character data format received');
            return;
          }
          
          // Enhance characters with mock statistics for now
          console.log('Enhancing characters with mock data...');
          const enhancedCharacters = charactersList.map((char: Character) => ({
            ...char,
            total_adventures: Math.floor(Math.random() * 20) + 1,
            completed_adventures: Math.floor(Math.random() * 15) + 1,
            total_playtime_hours: Math.floor(Math.random() * 100) + 5,
            last_played: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString()
          }));
          
          console.log('Enhanced characters:', enhancedCharacters);
          setCharacters(enhancedCharacters);
          console.log('Characters state updated successfully');
        } else {
          console.error('Response not OK:', response.status, response.statusText);
          const errorText = await response.text();
          console.error('Error response body:', errorText);
          setError(`Failed to load characters: ${response.status} ${response.statusText}`);
        }
      } catch (err) {
        console.error('Error in fetchCharacters:', err);
        setError(`Failed to load characters: ${err instanceof Error ? err.message : 'Unknown error'}`);
      } finally {
        console.log('Setting isLoading to false');
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      console.log('User is loaded and signed in, fetching characters...');
      fetchCharacters();
    } else {
      console.log('User not loaded or not signed in:', { isLoaded, isSignedIn });
    }
  }, [isLoaded, isSignedIn, getToken]);

  // Filter and sort characters
  useEffect(() => {
    let filtered = [...characters];

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(char =>
        char.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        char.race.toLowerCase().includes(searchTerm.toLowerCase()) ||
        char.character_class.toLowerCase().includes(searchTerm.toLowerCase()) ||
        char.background.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply category filter
    switch (filterOption) {
      case 'low_level':
        filtered = filtered.filter(char => char.level <= 5);
        break;
      case 'mid_level':
        filtered = filtered.filter(char => char.level > 5 && char.level <= 15);
        break;
      case 'high_level':
        filtered = filtered.filter(char => char.level > 15);
        break;
      case 'active':
        filtered = filtered.filter(char => 
          char.last_played && 
          new Date(char.last_played) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        );
        break;
      case 'inactive':
        filtered = filtered.filter(char => 
          !char.last_played || 
          new Date(char.last_played) <= new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        );
        break;
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortOption) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'level':
          aValue = a.level;
          bValue = b.level;
          break;
        case 'created':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        case 'last_played':
          aValue = a.last_played ? new Date(a.last_played).getTime() : 0;
          bValue = b.last_played ? new Date(b.last_played).getTime() : 0;
          break;
        case 'adventures':
          aValue = a.total_adventures || 0;
          bValue = b.total_adventures || 0;
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    setFilteredCharacters(filtered);
  }, [characters, searchTerm, filterOption, sortOption, sortDirection]);

  // Utility functions
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatLastPlayed = (dateString?: string) => {
    if (!dateString) return 'Never';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return formatDate(dateString);
  };

  const getHealthPercentage = (current: number, max: number) => {
    return Math.round((current / max) * 100);
  };

  const getHealthColor = (percentage: number) => {
    if (percentage > 75) return 'text-green-400';
    if (percentage > 50) return 'text-yellow-400';
    if (percentage > 25) return 'text-orange-400';
    return 'text-red-400';
  };

  const getLevelBadgeColor = (level: number) => {
    if (level <= 5) return 'bg-green-900/50 text-green-300';
    if (level <= 15) return 'bg-blue-900/50 text-blue-300';
    return 'bg-purple-900/50 text-purple-300';
  };

  // Character actions
  const handleSelectCharacter = (characterId: number) => {
    setSelectedCharacters(prev => 
      prev.includes(characterId)
        ? prev.filter(id => id !== characterId)
        : [...prev, characterId]
    );
  };

  const handleDeleteSelected = async () => {
    if (selectedCharacters.length === 0) return;
    
    try {
      const token = await getToken();
      
      await Promise.all(
        selectedCharacters.map(id =>
          fetch(`http://localhost:8000/api/characters/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          })
        )
      );
      
      setCharacters(prev => prev.filter(char => !selectedCharacters.includes(char.id)));
      setSelectedCharacters([]);
      setShowDeleteConfirm(false);
    } catch (err) {
      setError('Failed to delete characters');
    }
  };

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">Loading characters...</div>
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
                <h1 className="text-2xl font-bold text-white">My Characters</h1>
                <p className="text-gray-300">
                  {characters.length} total characters • {filteredCharacters.length} showing
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/character/create')}
                className="flex items-center bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Plus className="w-5 h-5 mr-2" />
                Create Character
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Controls Bar */}
        <div className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search characters..."
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
                <option value="created_desc">Newest First</option>
                <option value="created_asc">Oldest First</option>
                <option value="name_asc">Name A-Z</option>
                <option value="name_desc">Name Z-A</option>
                <option value="level_desc">Highest Level</option>
                <option value="level_asc">Lowest Level</option>
                <option value="last_played_desc">Recently Played</option>
                <option value="adventures_desc">Most Adventures</option>
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
                  { value: 'all', label: 'All Characters' },
                  { value: 'low_level', label: 'Level 1-5' },
                  { value: 'mid_level', label: 'Level 6-15' },
                  { value: 'high_level', label: 'Level 16+' },
                  { value: 'active', label: 'Active (7 days)' },
                  { value: 'inactive', label: 'Inactive' }
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

          {/* Bulk Actions */}
          {selectedCharacters.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-600/50">
              <div className="flex items-center justify-between">
                <span className="text-gray-300">
                  {selectedCharacters.length} character{selectedCharacters.length !== 1 ? 's' : ''} selected
                </span>
                <div className="flex gap-2">
                  <button
                    onClick={() => setSelectedCharacters([])}
                    className="px-3 py-1 bg-gray-700/50 text-gray-300 rounded-md text-sm hover:bg-gray-600/50 transition-colors"
                  >
                    Clear Selection
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    className="px-3 py-1 bg-red-600 text-white rounded-md text-sm hover:bg-red-700 transition-colors"
                  >
                    Delete Selected
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Characters Display */}
        {filteredCharacters.length === 0 ? (
          <div className="text-center py-16">
            <User className="w-16 h-16 text-gray-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">
              {characters.length === 0 ? 'No characters yet' : 'No characters match your filters'}
            </h3>
            <p className="text-gray-400 mb-6">
              {characters.length === 0 
                ? 'Create your first character to begin your adventures!'
                : 'Try adjusting your search or filter criteria.'
              }
            </p>
            {characters.length === 0 && (
              <button
                onClick={() => router.push('/character/create')}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-md transition-colors"
              >
                Create Your First Character
              </button>
            )}
          </div>
        ) : viewMode === 'grid' ? (
          /* Grid View */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredCharacters.map((character) => (
              <div
                key={character.id}
                className="bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 hover:border-purple-400/50 transition-all duration-200 overflow-hidden"
              >
                {/* Character Header */}
                <div className="relative p-4">
                  {/* Selection Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedCharacters.includes(character.id)}
                    onChange={() => handleSelectCharacter(character.id)}
                    className="absolute top-2 right-2 w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                  />
                  
                  {/* Character Avatar & Info */}
                  <div className="text-center mb-4">
                    <CharacterAvatar character={character} size="lg" className="mx-auto mb-3" />
                    <h3 className="text-xl font-bold text-white mb-1">{character.name}</h3>
                    <p className="text-gray-300 text-sm">
                      Level {character.level} {character.race} {character.character_class}
                    </p>
                    <span className={`inline-block px-2 py-1 rounded text-xs mt-2 ${getLevelBadgeColor(character.level)}`}>
                      {character.level <= 5 ? 'Novice' : character.level <= 15 ? 'Experienced' : 'Master'}
                    </span>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 text-center text-sm mb-4">
                    <div>
                      <Heart className={`w-4 h-4 mx-auto mb-1 ${getHealthColor(getHealthPercentage(character.current_hp, character.max_hp))}`} />
                      <span className="block text-gray-300">{character.current_hp}/{character.max_hp}</span>
                    </div>
                    <div>
                      <Shield className="w-4 h-4 mx-auto mb-1 text-blue-400" />
                      <span className="block text-gray-300">AC {character.armor_class}</span>
                    </div>
                    <div>
                      <Star className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
                      <span className="block text-gray-300">{character.total_adventures || 0} adv</span>
                    </div>
                  </div>

                  {/* Last Played */}
                  <div className="text-center text-xs text-gray-400 mb-4">
                    <Clock className="w-3 h-3 inline mr-1" />
                    Last played {formatLastPlayed(character.last_played)}
                  </div>
                </div>

                {/* Actions */}
                <div className="bg-gray-800/50 px-4 py-3 border-t border-gray-700/50">
                  <div className="flex gap-2">
                    <button
                      onClick={() => router.push(`/character/${character.id}`)}
                      className="flex-1 flex items-center justify-center bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </button>
                    <button
                      onClick={() => router.push(`/adventure/create?character=${character.id}`)}
                      className="flex-1 flex items-center justify-center bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md transition-colors text-sm"
                    >
                      <Play className="w-4 h-4 mr-1" />
                      Play
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
              <div className="col-span-1">
                <input
                  type="checkbox"
                  checked={selectedCharacters.length === filteredCharacters.length && filteredCharacters.length > 0}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedCharacters(filteredCharacters.map(c => c.id));
                    } else {
                      setSelectedCharacters([]);
                    }
                  }}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                />
              </div>
              <div className="col-span-3">Character</div>
              <div className="col-span-2">Level & Class</div>
              <div className="col-span-2">Health</div>
              <div className="col-span-2">Last Played</div>
              <div className="col-span-2">Actions</div>
            </div>
            
            {filteredCharacters.map((character) => (
              <div
                key={character.id}
                className="grid grid-cols-12 gap-4 p-4 border-b border-gray-700/50 hover:bg-gray-800/30 transition-colors"
              >
                <div className="col-span-1">
                  <input
                    type="checkbox"
                    checked={selectedCharacters.includes(character.id)}
                    onChange={() => handleSelectCharacter(character.id)}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-600 focus:ring-purple-500"
                  />
                </div>
                
                <div className="col-span-3 flex items-center">
                  <CharacterAvatar character={character} size="sm" className="mr-3" />
                  <div>
                    <div className="font-medium text-white">{character.name}</div>
                    <div className="text-sm text-gray-400">{character.race}</div>
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center">
                  <div>
                    <div className="text-white">Level {character.level}</div>
                    <div className="text-sm text-gray-400">{character.character_class}</div>
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center">
                  <div className="flex items-center">
                    <Heart className={`w-4 h-4 mr-2 ${getHealthColor(getHealthPercentage(character.current_hp, character.max_hp))}`} />
                    <span className="text-white">{character.current_hp}/{character.max_hp}</span>
                    <span className="text-gray-400 ml-2">({getHealthPercentage(character.current_hp, character.max_hp)}%)</span>
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center">
                  <div className="text-gray-300">
                    {formatLastPlayed(character.last_played)}
                  </div>
                </div>
                
                <div className="col-span-2 flex items-center gap-2">
                  <button
                    onClick={() => router.push(`/character/${character.id}`)}
                    className="flex items-center bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    <Eye className="w-3 h-3 mr-1" />
                    View
                  </button>
                  <button
                    onClick={() => router.push(`/adventure/create?character=${character.id}`)}
                    className="flex items-center bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition-colors"
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Play
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold text-white mb-4">Delete Characters</h3>
            <p className="text-gray-300 mb-6">
              Are you sure you want to delete {selectedCharacters.length} character{selectedCharacters.length !== 1 ? 's' : ''}? 
              This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteSelected}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 