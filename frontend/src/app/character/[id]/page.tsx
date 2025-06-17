'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { 
  User, 
  Sword, 
  Shield, 
  Heart, 
  Star, 
  Trophy, 
  MapPin, 
  Calendar,
  Edit3,
  Play,
  Trash2,
  Plus,
  Settings,
  TrendingUp,
  Award,
  Crown,
  Zap,
  Target,
  BookOpen,
  Package,
  Clock,
  AlertCircle
} from 'lucide-react';
import CharacterAvatar from '@/components/game/CharacterAvatar';

// Types
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  hit_points: number;
  max_hit_points: number;
  armor_class: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  proficiency_bonus: number;
  background?: string;
  created_at: string;
  last_played?: string;
  total_xp?: number;
  inventory?: Array<{
    id: number;
    name: string;
    description: string;
    type: string;
    rarity: string;
    quantity: number;
  }>;
}

interface Adventure {
  id: number;
  title?: string;
  story_type: string;
  current_stage: string;
  story_completed: boolean;
  created_at: string;
  completion_type?: string;
  completed_at?: string;
}

interface CharacterStats {
  total_adventures: number;
  completed_adventures: number;
  total_playtime_hours: number;
  highest_level_reached: number;
  favorite_adventure_type: string;
  achievements_unlocked: number;
}

// Achievement definitions
const ACHIEVEMENTS = [
  { id: 'first_adventure', name: 'First Steps', description: 'Complete your first adventure', icon: '🎯' },
  { id: 'level_5', name: 'Veteran Adventurer', description: 'Reach level 5', icon: '⭐' },
  { id: 'level_10', name: 'Hero of the Realm', description: 'Reach level 10', icon: '👑' },
  { id: 'combat_master', name: 'Combat Master', description: 'Win 10 combat encounters', icon: '⚔️' },
  { id: 'explorer', name: 'World Explorer', description: 'Complete 5 exploration adventures', icon: '🗺️' },
  { id: 'diplomat', name: 'Silver Tongue', description: 'Complete 3 social adventures', icon: '💬' },
  { id: 'collector', name: 'Treasure Hunter', description: 'Collect 50 items', icon: '💎' },
  { id: 'survivor', name: 'Death Defier', description: 'Survive with 1 HP', icon: '💀' }
];

export default function CharacterOverviewPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const characterId = params.id;

  const [character, setCharacter] = useState<Character | null>(null);
  const [adventures, setAdventures] = useState<Adventure[]>([]);
  const [stats, setStats] = useState<CharacterStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch character data
  useEffect(() => {
    const fetchData = async () => {
      if (!characterId) return;
      
      try {
        const token = await getToken();
        
        // Fetch character details
        const characterResponse = await fetch(`http://localhost:8000/api/characters/${characterId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (characterResponse.ok) {
          const characterData = await characterResponse.json();
          setCharacter(characterData);
          
          // Fetch character's adventures
          const adventuresResponse = await fetch(`http://localhost:8000/api/characters/${characterId}/adventures`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (adventuresResponse.ok) {
            const adventuresData = await adventuresResponse.json();
            setAdventures(adventuresData);
            
            // Calculate stats
            const totalAdventures = adventuresData.length;
            const completedAdventures = adventuresData.filter((adv: Adventure) => adv.story_completed).length;
            const mockStats: CharacterStats = {
              total_adventures: totalAdventures,
              completed_adventures: completedAdventures,
              total_playtime_hours: Math.round(totalAdventures * 1.5), // Mock calculation
              highest_level_reached: characterData.level,
              favorite_adventure_type: 'exploration', // Mock
              achievements_unlocked: Math.min(completedAdventures + characterData.level, ACHIEVEMENTS.length)
            };
            setStats(mockStats);
          }
        } else if (characterResponse.status === 404) {
          setError('Character not found');
        } else {
          setError('Failed to load character');
        }
      } catch (err) {
        setError('Failed to load character');
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      fetchData();
    }
  }, [characterId, isLoaded, isSignedIn, getToken]);

  // Delete character
  const handleDelete = async () => {
    if (!character) return;
    
    setIsDeleting(true);
    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/api/characters/${character.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        router.push('/dashboard');
      } else {
        setError('Failed to delete character');
      }
    } catch (err) {
      setError('Failed to delete character');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  // Helper functions
  const getStatModifier = (score: number) => {
    return Math.floor((score - 10) / 2);
  };

  const formatModifier = (modifier: number) => {
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getUnlockedAchievements = () => {
    if (!stats || !character) return [];
    
    const unlocked = [];
    if (stats.completed_adventures > 0) unlocked.push(ACHIEVEMENTS[0]);
    if (character.level >= 5) unlocked.push(ACHIEVEMENTS[1]);
    if (character.level >= 10) unlocked.push(ACHIEVEMENTS[2]);
    if (stats.completed_adventures >= 5) unlocked.push(ACHIEVEMENTS[4]);
    
    return unlocked.slice(0, stats.achievements_unlocked);
  };

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading character...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null;
  }

  if (error && !character) {
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

  if (!character) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Character not found</div>
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
              <div className="flex items-center">
                <CharacterAvatar character={character} size="md" showLevel={true} />
                <div className="ml-4">
                  <h1 className="text-2xl font-bold text-white">{character.name}</h1>
                  <p className="text-gray-300">
                    Level {character.level} {character.race} {character.character_class}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push(`/adventure/create?character=${character.id}`)}
                className="flex items-center bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Play className="w-5 h-5 mr-2" />
                Start Adventure
              </button>
              <button
                onClick={() => router.push(`/character/${character.id}/edit`)}
                className="flex items-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Edit3 className="w-5 h-5 mr-2" />
                Edit Character
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Trash2 className="w-5 h-5 mr-2" />
                Delete
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Character Stats - Left Column */}
          <div className="space-y-6">
            {/* Core Stats */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Core Stats</h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Heart className="w-5 h-5 text-red-400 mr-2" />
                    <span className="text-sm text-gray-300">Health</span>
                  </div>
                  <div className="text-2xl font-bold text-red-300">
                    {character.hit_points}/{character.max_hit_points}
                  </div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Shield className="w-5 h-5 text-blue-400 mr-2" />
                    <span className="text-sm text-gray-300">Armor Class</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-300">{character.armor_class}</div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Star className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="text-sm text-gray-300">Level</span>
                  </div>
                  <div className="text-2xl font-bold text-yellow-300">{character.level}</div>
                </div>
                <div className="text-center">
                  <div className="flex items-center justify-center mb-2">
                    <Zap className="w-5 h-5 text-purple-400 mr-2" />
                    <span className="text-sm text-gray-300">Prof. Bonus</span>
                  </div>
                  <div className="text-2xl font-bold text-purple-300">
                    +{character.proficiency_bonus || Math.ceil(character.level / 4) + 1}
                  </div>
                </div>
              </div>
            </div>

            {/* Ability Scores */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Ability Scores</h2>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { name: 'STR', value: character.strength, label: 'Strength' },
                  { name: 'DEX', value: character.dexterity, label: 'Dexterity' },
                  { name: 'CON', value: character.constitution, label: 'Constitution' },
                  { name: 'INT', value: character.intelligence, label: 'Intelligence' },
                  { name: 'WIS', value: character.wisdom, label: 'Wisdom' },
                  { name: 'CHA', value: character.charisma, label: 'Charisma' }
                ].map((ability) => (
                  <div key={ability.name} className="bg-gray-700/50 rounded p-3 text-center">
                    <div className="text-xs text-gray-400 mb-1">{ability.label}</div>
                    <div className="text-lg font-bold text-white">{ability.value}</div>
                    <div className="text-sm text-gray-300">
                      {formatModifier(getStatModifier(ability.value))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Character Info */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Character Info</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-sm text-gray-400">Background:</span>
                  <span className="text-white ml-2">{character.background || 'Unknown'}</span>
                </div>
                <div>
                  <span className="text-sm text-gray-400">Created:</span>
                  <span className="text-white ml-2">{formatDate(character.created_at)}</span>
                </div>
                {character.last_played && (
                  <div>
                    <span className="text-sm text-gray-400">Last Played:</span>
                    <span className="text-white ml-2">{formatDate(character.last_played)}</span>
                  </div>
                )}
                {character.total_xp && (
                  <div>
                    <span className="text-sm text-gray-400">Total XP:</span>
                    <span className="text-white ml-2">{character.total_xp.toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Adventures & Progress - Center Column */}
          <div className="space-y-6">
            {/* Adventure Statistics */}
            {stats && (
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-xl font-bold text-white mb-4">Adventure Statistics</h2>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-300">{stats.completed_adventures}</div>
                    <div className="text-sm text-gray-400">Completed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-300">{stats.total_adventures}</div>
                    <div className="text-sm text-gray-400">Total Adventures</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-yellow-300">{stats.total_playtime_hours}h</div>
                    <div className="text-sm text-gray-400">Playtime</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-purple-300">{stats.achievements_unlocked}</div>
                    <div className="text-sm text-gray-400">Achievements</div>
                  </div>
                </div>
              </div>
            )}

            {/* Recent Adventures */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white">Recent Adventures</h2>
                <button
                  onClick={() => router.push(`/character/${character.id}/adventures`)}
                  className="text-purple-300 hover:text-purple-200 text-sm"
                >
                  View All →
                </button>
              </div>
              
              {adventures.length === 0 ? (
                <div className="text-center py-8">
                  <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                  <p className="text-gray-400 mb-4">No adventures yet</p>
                  <button
                    onClick={() => router.push(`/adventure/create?character=${character.id}`)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    Start Your First Adventure
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {adventures.slice(0, 5).map((adventure) => (
                    <div
                      key={adventure.id}
                      className="bg-gray-700/50 rounded-lg p-4 border border-gray-600/50 hover:border-purple-400/50 transition-colors cursor-pointer"
                      onClick={() => router.push(`/adventure/${adventure.id}`)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-bold text-white">
                          {adventure.title || `Adventure #${adventure.id}`}
                        </h3>
                        <span className={`px-2 py-1 rounded text-xs ${
                          adventure.story_completed 
                            ? 'bg-green-900/50 text-green-300' 
                            : 'bg-blue-900/50 text-blue-300'
                        }`}>
                          {adventure.story_completed ? 'Completed' : 'In Progress'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-400">
                        <span className="capitalize">
                          {adventure.story_type === 'short_form' ? 'Quick Adventure' : 'Epic Campaign'}
                        </span>
                        <span>{formatDate(adventure.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Achievements */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Achievements</h2>
              <div className="grid grid-cols-2 gap-3">
                {ACHIEVEMENTS.slice(0, 8).map((achievement) => {
                  const isUnlocked = getUnlockedAchievements().some(a => a.id === achievement.id);
                  return (
                    <div
                      key={achievement.id}
                      className={`p-3 rounded-lg border text-center ${
                        isUnlocked
                          ? 'bg-yellow-900/30 border-yellow-500/30'
                          : 'bg-gray-900/30 border-gray-600/30'
                      }`}
                    >
                      <div className={`text-2xl mb-1 ${isUnlocked ? '' : 'grayscale opacity-50'}`}>
                        {achievement.icon}
                      </div>
                      <div className={`text-sm font-medium ${
                        isUnlocked ? 'text-yellow-300' : 'text-gray-400'
                      }`}>
                        {achievement.name}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {achievement.description}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Inventory & Equipment - Right Column */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button
                  onClick={() => router.push(`/adventure/create?character=${character.id}`)}
                  className="w-full flex items-center justify-center bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-md transition-colors"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Start New Adventure
                </button>
                <button
                  onClick={() => router.push(`/character/${character.id}/edit`)}
                  className="w-full flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-md transition-colors"
                >
                  <Edit3 className="w-5 h-5 mr-2" />
                  Edit Character
                </button>
                <button
                  onClick={() => router.push(`/character/${character.id}/adventures`)}
                  className="w-full flex items-center justify-center bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-md transition-colors"
                >
                  <BookOpen className="w-5 h-5 mr-2" />
                  View All Adventures
                </button>
              </div>
            </div>

            {/* Equipment Summary */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Equipment</h2>
              {character.inventory && character.inventory.length > 0 ? (
                <div className="space-y-2">
                  <div className="text-sm text-gray-400 mb-3">
                    {character.inventory.length} items total
                  </div>
                  {character.inventory.slice(0, 6).map((item) => (
                    <div key={item.id} className="bg-gray-700/50 rounded p-2 border border-gray-600/50">
                      <div className="flex justify-between items-start">
                        <span className={`text-sm font-medium ${
                          item.rarity === 'epic' ? 'text-orange-300' :
                          item.rarity === 'rare' ? 'text-purple-300' :
                          item.rarity === 'uncommon' ? 'text-blue-300' :
                          'text-gray-300'
                        }`}>
                          {item.name}
                        </span>
                        {item.quantity > 1 && (
                          <span className="text-xs text-gray-400">x{item.quantity}</span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 capitalize">{item.type}</div>
                    </div>
                  ))}
                  {character.inventory.length > 6 && (
                    <div className="text-center pt-2">
                      <span className="text-xs text-gray-400">
                        +{character.inventory.length - 6} more items
                      </span>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <Package className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No items yet</p>
                </div>
              )}
            </div>

            {/* Character Notes */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Notes</h2>
              <div className="text-center py-4">
                <Settings className="w-8 h-8 text-gray-500 mx-auto mb-2" />
                <p className="text-gray-400 text-sm">Character notes coming soon</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-black/80 border border-white/20 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <AlertCircle className="w-6 h-6 text-red-400 mr-3" />
              <h3 className="text-xl font-bold text-white">Delete Character</h3>
            </div>
            <p className="text-gray-300 mb-6">
              Are you sure you want to delete <strong>{character.name}</strong>? This action cannot be undone and all character data and adventures will be permanently lost.
            </p>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="flex-1 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:opacity-50 text-white px-4 py-2 rounded-md transition-colors"
              >
                {isDeleting ? 'Deleting...' : 'Delete Character'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 