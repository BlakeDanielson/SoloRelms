'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { 
  Calendar, 
  Clock, 
  User, 
  Sword, 
  Users, 
  TrendingUp, 
  PlayCircle, 
  CheckCircle2, 
  AlertCircle,
  Trophy,
  Heart,
  Shield,
  Zap,
  MapPin,
  Settings,
  Trash2
} from 'lucide-react';

// Types
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
    description: string;
    timestamp: string;
    consequences: string[];
  }>;
  npc_status: Record<string, {
    status: string;
    health: string;
    location: string;
    disposition: string;
  }>;
  combat_outcomes: Array<{
    stage: string;
    encounter_type: string;
    result: string;
    damage_taken: number;
    loot_gained: string[];
    xp_gained: number;
    timestamp: string;
  }>;
  final_rewards: Record<string, any>;
}

interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  hit_points: number;
  max_hit_points: number;
}

// Story stages configuration
const STORY_STAGES = [
  { key: 'intro', name: 'Introduction', description: 'Setting the scene and meeting key characters' },
  { key: 'inciting_incident', name: 'Inciting Incident', description: 'The event that starts the main adventure' },
  { key: 'first_combat', name: 'First Combat', description: 'Initial challenge and combat encounter' },
  { key: 'twist', name: 'Plot Twist', description: 'Unexpected revelation or complication' },
  { key: 'final_conflict', name: 'Final Conflict', description: 'Climactic battle or challenge' },
  { key: 'resolution', name: 'Resolution', description: 'Story conclusion and rewards' }
];

export default function AdventureDetailsPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const adventureId = params.id;

  const [adventure, setAdventure] = useState<Adventure | null>(null);
  const [character, setCharacter] = useState<Character | null>(null);
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

  // Fetch adventure and character data
  useEffect(() => {
    const fetchData = async () => {
      if (!adventureId) return;
      
      try {
        const token = await getToken();
        
        // Fetch adventure details
        const adventureResponse = await fetch(`http://localhost:8000/api/stories/${adventureId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (adventureResponse.ok) {
          const adventureData = await adventureResponse.json();
          setAdventure(adventureData);
          
          // Fetch character details
          const characterResponse = await fetch(`http://localhost:8000/api/characters/${adventureData.character_id}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });

          if (characterResponse.ok) {
            const characterData = await characterResponse.json();
            setCharacter(characterData);
          }
        } else if (adventureResponse.status === 404) {
          setError('Adventure not found');
        } else {
          setError('Failed to load adventure');
        }
      } catch (err) {
        setError('Failed to load adventure');
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      fetchData();
    }
  }, [adventureId, isLoaded, isSignedIn, getToken]);

  // Delete adventure
  const handleDelete = async () => {
    if (!adventure) return;
    
    setIsDeleting(true);
    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/api/stories/${adventure.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        router.push('/dashboard');
      } else {
        setError('Failed to delete adventure');
      }
    } catch (err) {
      setError('Failed to delete adventure');
    } finally {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  // Helper functions
  const getCurrentStageIndex = () => {
    if (!adventure) return 0;
    return STORY_STAGES.findIndex(stage => stage.key === adventure.current_stage);
  };

  const getProgressPercentage = () => {
    if (!adventure) return 0;
    if (adventure.story_completed) return 100;
    return Math.round((getCurrentStageIndex() / STORY_STAGES.length) * 100);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTotalXP = () => {
    if (!adventure?.combat_outcomes) return 0;
    return adventure.combat_outcomes.reduce((total, combat) => total + (combat.xp_gained || 0), 0);
  };

  const getTotalDamage = () => {
    if (!adventure?.combat_outcomes) return 0;
    return adventure.combat_outcomes.reduce((total, combat) => total + (combat.damage_taken || 0), 0);
  };

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading adventure...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null;
  }

  if (error && !adventure) {
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

  if (!adventure || !character) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Adventure not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-white hover:text-purple-300 mr-4"
              >
                ← Back to Dashboard
              </button>
              <div>
                <h1 className="text-2xl font-bold text-white">
                  {adventure.title || 'Untitled Adventure'}
                </h1>
                <p className="text-gray-300 text-sm">
                  {character.name} - Level {character.level} {character.race} {character.character_class}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {!adventure.story_completed && (
                <button
                  onClick={() => router.push(`/game?character=${character.id}&story=${adventure.id}`)}
                  className="flex items-center bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                  <PlayCircle className="w-5 h-5 mr-2" />
                  Resume Adventure
                </button>
              )}
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

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Adventure Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Story Progress */}
          <div className="lg:col-span-2 space-y-6">
            {/* Progress Section */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Story Progress</h2>
                <div className="flex items-center space-x-2">
                  {adventure.story_completed ? (
                    <span className="flex items-center text-green-400">
                      <CheckCircle2 className="w-5 h-5 mr-1" />
                      Completed
                    </span>
                  ) : (
                    <span className="flex items-center text-yellow-400">
                      <Clock className="w-5 h-5 mr-1" />
                      In Progress
                    </span>
                  )}
                </div>
              </div>

              {/* Progress Bar */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-300">Overall Progress</span>
                  <span className="text-sm text-gray-300">{getProgressPercentage()}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${getProgressPercentage()}%` }}
                  />
                </div>
              </div>

              {/* Story Stages */}
              <div className="space-y-3">
                {STORY_STAGES.map((stage, index) => {
                  const isCompleted = adventure.stages_completed?.includes(stage.key);
                  const isCurrent = adventure.current_stage === stage.key;
                  const isUpcoming = index > getCurrentStageIndex();

                  return (
                    <div
                      key={stage.key}
                      className={`flex items-center p-3 rounded-lg border ${
                        isCompleted 
                          ? 'bg-green-900/30 border-green-500/30' 
                          : isCurrent 
                          ? 'bg-blue-900/30 border-blue-500/30' 
                          : 'bg-gray-900/30 border-gray-600/30'
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-4 ${
                        isCompleted 
                          ? 'bg-green-500' 
                          : isCurrent 
                          ? 'bg-blue-500' 
                          : 'bg-gray-600'
                      }`}>
                        {isCompleted ? (
                          <CheckCircle2 className="w-5 h-5 text-white" />
                        ) : isCurrent ? (
                          <PlayCircle className="w-5 h-5 text-white" />
                        ) : (
                          <span className="text-white text-sm font-bold">{index + 1}</span>
                        )}
                      </div>
                      <div className="flex-1">
                        <h3 className={`font-bold ${
                          isCompleted ? 'text-green-300' : isCurrent ? 'text-blue-300' : 'text-gray-300'
                        }`}>
                          {stage.name}
                        </h3>
                        <p className="text-gray-400 text-sm">{stage.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Major Decisions */}
            {adventure.major_decisions && adventure.major_decisions.length > 0 && (
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Major Decisions</h2>
                <div className="space-y-4">
                  {adventure.major_decisions.map((decision, index) => (
                    <div key={index} className="bg-black/60 rounded-lg p-4 border border-white/20">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-bold text-white">{decision.decision}</h3>
                        <span className="text-sm text-gray-400">{formatDate(decision.timestamp)}</span>
                      </div>
                      <p className="text-gray-300 mb-2">{decision.description}</p>
                      {decision.consequences && decision.consequences.length > 0 && (
                        <div className="flex flex-wrap gap-2">
                          {decision.consequences.map((consequence, i) => (
                            <span key={i} className="px-2 py-1 bg-purple-900/50 text-purple-300 text-xs rounded">
                              {consequence}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Combat History */}
            {adventure.combat_outcomes && adventure.combat_outcomes.length > 0 && (
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Combat History</h2>
                <div className="space-y-4">
                  {adventure.combat_outcomes.map((combat, index) => (
                    <div key={index} className="bg-black/60 rounded-lg p-4 border border-white/20">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-bold text-white">{combat.encounter_type}</h3>
                        <span className={`px-2 py-1 rounded text-sm ${
                          combat.result === 'victory' ? 'bg-green-900/50 text-green-300' : 
                          combat.result === 'defeat' ? 'bg-red-900/50 text-red-300' : 
                          'bg-yellow-900/50 text-yellow-300'
                        }`}>
                          {combat.result}
                        </span>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Damage Taken:</span>
                          <span className="text-red-300 ml-2">{combat.damage_taken}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">XP Gained:</span>
                          <span className="text-green-300 ml-2">{combat.xp_gained}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Date:</span>
                          <span className="text-gray-300 ml-2">{formatDate(combat.timestamp)}</span>
                        </div>
                      </div>
                      {combat.loot_gained && combat.loot_gained.length > 0 && (
                        <div className="mt-2">
                          <span className="text-gray-400 text-sm">Loot: </span>
                          {combat.loot_gained.map((item, i) => (
                            <span key={i} className="px-2 py-1 bg-yellow-900/50 text-yellow-300 text-xs rounded mr-1">
                              {item}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar Stats */}
          <div className="space-y-6">
            {/* Adventure Info */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Adventure Info</h2>
              <div className="space-y-4">
                <div className="flex items-center">
                  <Calendar className="w-5 h-5 text-purple-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-400">Created</div>
                    <div className="text-white">{formatDate(adventure.created_at)}</div>
                  </div>
                </div>
                
                {adventure.started_at && (
                  <div className="flex items-center">
                    <PlayCircle className="w-5 h-5 text-green-400 mr-3" />
                    <div>
                      <div className="text-sm text-gray-400">Started</div>
                      <div className="text-white">{formatDate(adventure.started_at)}</div>
                    </div>
                  </div>
                )}

                {adventure.completed_at && (
                  <div className="flex items-center">
                    <CheckCircle2 className="w-5 h-5 text-blue-400 mr-3" />
                    <div>
                      <div className="text-sm text-gray-400">Completed</div>
                      <div className="text-white">{formatDate(adventure.completed_at)}</div>
                    </div>
                  </div>
                )}

                <div className="flex items-center">
                  <Clock className="w-5 h-5 text-yellow-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-400">Type</div>
                    <div className="text-white capitalize">
                      {adventure.story_type === 'short_form' ? 'Quick Adventure' : 'Epic Campaign'}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Character Stats */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Character</h2>
              <div className="space-y-3">
                <div className="flex items-center">
                  <User className="w-5 h-5 text-blue-400 mr-3" />
                  <div>
                    <div className="text-white font-bold">{character.name}</div>
                    <div className="text-gray-400 text-sm">
                      Level {character.level} {character.race} {character.character_class}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center">
                  <Heart className="w-5 h-5 text-red-400 mr-3" />
                  <div>
                    <div className="text-sm text-gray-400">Health</div>
                    <div className="text-white">{character.hit_points}/{character.max_hit_points} HP</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Adventure Stats */}
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <h2 className="text-xl font-bold text-white mb-4">Statistics</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Trophy className="w-5 h-5 text-yellow-400 mr-2" />
                    <span className="text-gray-300">Total XP</span>
                  </div>
                  <span className="text-white font-bold">{getTotalXP()}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Sword className="w-5 h-5 text-red-400 mr-2" />
                    <span className="text-gray-300">Combats</span>
                  </div>
                  <span className="text-white font-bold">{adventure.combat_outcomes?.length || 0}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Zap className="w-5 h-5 text-orange-400 mr-2" />
                    <span className="text-gray-300">Damage Taken</span>
                  </div>
                  <span className="text-white font-bold">{getTotalDamage()}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Users className="w-5 h-5 text-purple-400 mr-2" />
                    <span className="text-gray-300">Decisions</span>
                  </div>
                  <span className="text-white font-bold">{adventure.major_decisions?.length || 0}</span>
                </div>
              </div>
            </div>

            {/* NPCs */}
            {adventure.npc_status && Object.keys(adventure.npc_status).length > 0 && (
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-xl font-bold text-white mb-4">NPCs Encountered</h2>
                <div className="space-y-3">
                  {Object.entries(adventure.npc_status).map(([npcId, npc]) => (
                    <div key={npcId} className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium capitalize">{npcId.replace('_', ' ')}</div>
                        <div className="text-gray-400 text-sm">{npc.disposition} • {npc.location}</div>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${
                        npc.status === 'ally' ? 'bg-green-900/50 text-green-300' : 
                        npc.status === 'hostile' ? 'bg-red-900/50 text-red-300' : 
                        'bg-gray-900/50 text-gray-300'
                      }`}>
                        {npc.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-black/80 border border-white/20 rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center mb-4">
              <AlertCircle className="w-6 h-6 text-red-400 mr-3" />
              <h3 className="text-xl font-bold text-white">Delete Adventure</h3>
            </div>
            <p className="text-gray-300 mb-6">
              Are you sure you want to delete this adventure? This action cannot be undone and all progress will be lost.
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
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 