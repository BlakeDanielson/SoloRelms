'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  MapPin, 
  Target, 
  Clock, 
  CheckCircle2, 
  Circle, 
  Star, 
  Coins, 
  Package,
  Scroll,
  Sword,
  Users,
  Eye,
  ArrowRight,
  Plus,
  AlertCircle,
  Calendar,
  Trophy,
  Gift
} from 'lucide-react';

// Types
interface QuestObjective {
  id: string;
  description: string;
  completed: boolean;
  progress_current?: number;
  progress_required?: number;
  type: 'kill' | 'collect' | 'visit' | 'talk' | 'deliver' | 'explore' | 'survive';
}

interface QuestReward {
  type: 'xp' | 'gold' | 'item' | 'ability';
  amount?: number;
  name?: string;
  description?: string;
  rarity?: 'common' | 'uncommon' | 'rare' | 'epic' | 'legendary';
}

interface Quest {
  id: number;
  title: string;
  description: string;
  quest_giver?: string;
  location?: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'legendary';
  status: 'available' | 'active' | 'completed' | 'failed' | 'turned_in';
  objectives: QuestObjective[];
  rewards: QuestReward[];
  time_limit?: string;
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  category: 'main' | 'side' | 'daily' | 'hidden';
  prerequisites?: number[];
}

interface QuestManagerProps {
  isOpen: boolean;
  onClose: () => void;
  character: {
    id: number;
    name: string;
    level: number;
  };
}

export default function QuestManager({ isOpen, onClose, character }: QuestManagerProps) {
  const [activeTab, setActiveTab] = useState<'active' | 'available' | 'completed'>('active');
  const [quests, setQuests] = useState<Quest[]>([]);
  const [selectedQuest, setSelectedQuest] = useState<Quest | null>(null);
  const [loading, setLoading] = useState(false);

  // Mock quest data - would come from API
  useEffect(() => {
    const mockQuests: Quest[] = [
      {
        id: 1,
        title: "The Missing Merchant",
        description: "A local merchant has gone missing on the road to Millbrook. The town guard suspects bandits, but strange tracks suggest something more sinister.",
        quest_giver: "Captain Thorne",
        location: "Riverdale",
        difficulty: 'medium',
        status: 'active',
        objectives: [
          { id: '1', description: "Investigate the merchant's last known location", completed: true, type: 'visit' },
          { id: '2', description: "Follow the strange tracks", completed: true, type: 'explore' },
          { id: '3', description: "Defeat the owlbear threatening travelers", completed: false, progress_current: 0, progress_required: 1, type: 'kill' },
          { id: '4', description: "Rescue the merchant", completed: false, type: 'talk' }
        ],
        rewards: [
          { type: 'xp', amount: 150 },
          { type: 'gold', amount: 75 },
          { type: 'item', name: "Traveler's Cloak", description: "+1 AC, advantage on stealth checks", rarity: 'uncommon' }
        ],
        progress_percentage: 50,
        started_at: '2024-01-15T10:30:00Z',
        category: 'main'
      },
      {
        id: 2,
        title: "Ancient Ruins Survey",
        description: "The local historian needs someone to map and document newly discovered ruins. Dangerous, but potentially very rewarding.",
        quest_giver: "Scholar Meridia",
        location: "Whispering Woods",
        difficulty: 'hard',
        status: 'available',
        objectives: [
          { id: '1', description: "Enter the ancient ruins", completed: false, type: 'visit' },
          { id: '2', description: "Map the first three chambers", completed: false, progress_current: 0, progress_required: 3, type: 'explore' },
          { id: '3', description: "Collect runic inscriptions", completed: false, progress_current: 0, progress_required: 5, type: 'collect' },
          { id: '4', description: "Survive the guardians", completed: false, type: 'survive' }
        ],
        rewards: [
          { type: 'xp', amount: 300 },
          { type: 'gold', amount: 150 },
          { type: 'item', name: "Ancient Spellbook", description: "Learn one new cantrip", rarity: 'rare' }
        ],
        progress_percentage: 0,
        category: 'side',
        prerequisites: [1]
      },
      {
        id: 3,
        title: "Daily: Herb Gathering",
        description: "Collect medicinal herbs for the town healer. Fresh herbs are always needed.",
        quest_giver: "Healer Rosalind",
        location: "Forest Outskirts",
        difficulty: 'easy',
        status: 'available',
        objectives: [
          { id: '1', description: "Collect moonbell flowers", completed: false, progress_current: 2, progress_required: 10, type: 'collect' },
          { id: '2', description: "Find dragon's breath moss", completed: false, progress_current: 0, progress_required: 5, type: 'collect' }
        ],
        rewards: [
          { type: 'xp', amount: 50 },
          { type: 'gold', amount: 25 },
          { type: 'item', name: "Healing Potion", description: "Restore 2d4+2 HP", rarity: 'common' }
        ],
        time_limit: '24:00:00',
        progress_percentage: 20,
        category: 'daily'
      },
      {
        id: 4,
        title: "The Dragon's Hoard",
        description: "Legends speak of an ancient red dragon's treasure hidden in the Burning Peaks. Only the bravest dare to seek it.",
        quest_giver: "Old Tom the Storyteller",
        location: "Burning Peaks",
        difficulty: 'legendary',
        status: 'completed',
        objectives: [
          { id: '1', description: "Reach the Burning Peaks", completed: true, type: 'visit' },
          { id: '2', description: "Find the dragon's lair", completed: true, type: 'explore' },
          { id: '3', description: "Defeat the ancient red dragon", completed: true, type: 'kill' },
          { id: '4', description: "Claim the treasure", completed: true, type: 'collect' }
        ],
        rewards: [
          { type: 'xp', amount: 1000 },
          { type: 'gold', amount: 5000 },
          { type: 'item', name: "Dragonscale Armor", description: "+2 AC, Fire Resistance", rarity: 'legendary' },
          { type: 'ability', name: "Dragon's Breath", description: "Once per day, breathe fire for 3d6 damage" }
        ],
        progress_percentage: 100,
        started_at: '2024-01-10T08:00:00Z',
        completed_at: '2024-01-14T16:45:00Z',
        category: 'main'
      }
    ];

    setQuests(mockQuests);
  }, []);

  const filteredQuests = quests.filter(quest => {
    if (activeTab === 'active') return quest.status === 'active';
    if (activeTab === 'available') return quest.status === 'available';
    if (activeTab === 'completed') return quest.status === 'completed' || quest.status === 'turned_in';
    return false;
  });

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'hard': return 'text-orange-400';
      case 'legendary': return 'text-purple-400';
      default: return 'text-gray-400';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'main': return <Star className="w-4 h-4 text-yellow-400" />;
      case 'side': return <Circle className="w-4 h-4 text-blue-400" />;
      case 'daily': return <Clock className="w-4 h-4 text-green-400" />;
      case 'hidden': return <Eye className="w-4 h-4 text-purple-400" />;
      default: return <Scroll className="w-4 h-4 text-gray-400" />;
    }
  };

  const getRewardIcon = (type: string) => {
    switch (type) {
      case 'xp': return <Star className="w-4 h-4 text-blue-400" />;
      case 'gold': return <Coins className="w-4 h-4 text-yellow-400" />;
      case 'item': return <Package className="w-4 h-4 text-purple-400" />;
      case 'ability': return <Sword className="w-4 h-4 text-red-400" />;
      default: return <Gift className="w-4 h-4 text-gray-400" />;
    }
  };

  const handleAcceptQuest = (quest: Quest) => {
    setQuests(quests.map(q => 
      q.id === quest.id ? { ...q, status: 'active' as const, started_at: new Date().toISOString() } : q
    ));
  };

  const handleCompleteObjective = (questId: number, objectiveId: string) => {
    setQuests(quests.map(quest => {
      if (quest.id === questId) {
        const updatedObjectives = quest.objectives.map(obj =>
          obj.id === objectiveId ? { ...obj, completed: true } : obj
        );
        const completedCount = updatedObjectives.filter(obj => obj.completed).length;
        const progressPercentage = Math.round((completedCount / updatedObjectives.length) * 100);
        
        return {
          ...quest,
          objectives: updatedObjectives,
          progress_percentage: progressPercentage,
          status: progressPercentage === 100 ? 'completed' as const : quest.status
        };
      }
      return quest;
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg border border-gray-700 w-full max-w-6xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <Scroll className="w-6 h-6 text-yellow-400" />
            <h2 className="text-2xl font-bold text-white">Quest Journal</h2>
            <span className="text-sm text-gray-400">- {character.name}</span>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Quest List */}
          <div className="w-1/2 border-r border-gray-700 flex flex-col">
            {/* Tabs */}
            <div className="flex border-b border-gray-700">
              {[
                { key: 'active', label: 'Active', count: quests.filter(q => q.status === 'active').length },
                { key: 'available', label: 'Available', count: quests.filter(q => q.status === 'available').length },
                { key: 'completed', label: 'Completed', count: quests.filter(q => q.status === 'completed' || q.status === 'turned_in').length }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex-1 px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
                    activeTab === tab.key
                      ? 'text-blue-400 border-blue-400'
                      : 'text-gray-400 border-transparent hover:text-gray-300'
                  }`}
                >
                  {tab.label} ({tab.count})
                </button>
              ))}
            </div>

            {/* Quest List */}
            <div className="flex-1 overflow-y-auto">
              {filteredQuests.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                  <Scroll className="w-12 h-12 mb-4 opacity-50" />
                  <p>No {activeTab} quests</p>
                </div>
              ) : (
                <div className="p-4 space-y-3">
                  {filteredQuests.map(quest => (
                    <div
                      key={quest.id}
                      onClick={() => setSelectedQuest(quest)}
                      className={`bg-gray-800 rounded-lg border p-4 cursor-pointer transition-all hover:bg-gray-750 ${
                        selectedQuest?.id === quest.id ? 'border-blue-500 bg-gray-750' : 'border-gray-600'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          {getCategoryIcon(quest.category)}
                          <h3 className="font-semibold text-white">{quest.title}</h3>
                        </div>
                        <span className={`text-xs font-medium ${getDifficultyColor(quest.difficulty)}`}>
                          {quest.difficulty.toUpperCase()}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-400 mb-3 line-clamp-2">{quest.description}</p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {quest.quest_giver && (
                            <div className="flex items-center space-x-1">
                              <Users className="w-3 h-3 text-gray-500" />
                              <span className="text-xs text-gray-500">{quest.quest_giver}</span>
                            </div>
                          )}
                          {quest.location && (
                            <div className="flex items-center space-x-1">
                              <MapPin className="w-3 h-3 text-gray-500" />
                              <span className="text-xs text-gray-500">{quest.location}</span>
                            </div>
                          )}
                        </div>
                        
                        {quest.status === 'active' && (
                          <div className="flex items-center space-x-2">
                            <div className="w-16 h-1 bg-gray-600 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-blue-500 transition-all duration-500"
                                style={{ width: `${quest.progress_percentage}%` }}
                              />
                            </div>
                            <span className="text-xs text-gray-400">{quest.progress_percentage}%</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Quest Details */}
          <div className="w-1/2 flex flex-col">
            {selectedQuest ? (
              <>
                <div className="p-6 border-b border-gray-700">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center space-x-2 mb-2">
                        {getCategoryIcon(selectedQuest.category)}
                        <h3 className="text-xl font-bold text-white">{selectedQuest.title}</h3>
                        <span className={`text-sm font-medium ${getDifficultyColor(selectedQuest.difficulty)}`}>
                          {selectedQuest.difficulty.toUpperCase()}
                        </span>
                      </div>
                      <p className="text-gray-300">{selectedQuest.description}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {selectedQuest.quest_giver && (
                      <div>
                        <span className="text-gray-400">Quest Giver:</span>
                        <span className="text-white ml-2">{selectedQuest.quest_giver}</span>
                      </div>
                    )}
                    {selectedQuest.location && (
                      <div>
                        <span className="text-gray-400">Location:</span>
                        <span className="text-white ml-2">{selectedQuest.location}</span>
                      </div>
                    )}
                    {selectedQuest.time_limit && (
                      <div>
                        <span className="text-gray-400">Time Limit:</span>
                        <span className="text-yellow-400 ml-2">{selectedQuest.time_limit}</span>
                      </div>
                    )}
                    {selectedQuest.status === 'active' && (
                      <div>
                        <span className="text-gray-400">Progress:</span>
                        <span className="text-blue-400 ml-2">{selectedQuest.progress_percentage}% Complete</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6">
                  {/* Objectives */}
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <Target className="w-5 h-5 mr-2" />
                      Objectives
                    </h4>
                    <div className="space-y-2">
                      {selectedQuest.objectives.map(objective => (
                        <div 
                          key={objective.id}
                          className={`flex items-center space-x-3 p-3 rounded ${
                            objective.completed ? 'bg-green-900/30' : 'bg-gray-800'
                          }`}
                        >
                          <button
                            onClick={() => selectedQuest.status === 'active' && handleCompleteObjective(selectedQuest.id, objective.id)}
                            disabled={objective.completed || selectedQuest.status !== 'active'}
                            className="text-green-400 hover:text-green-300 disabled:opacity-50"
                          >
                            {objective.completed ? (
                              <CheckCircle2 className="w-5 h-5" />
                            ) : (
                              <Circle className="w-5 h-5" />
                            )}
                          </button>
                          <div className="flex-1">
                            <p className={`text-sm ${objective.completed ? 'text-gray-400 line-through' : 'text-white'}`}>
                              {objective.description}
                            </p>
                            {objective.progress_current !== undefined && objective.progress_required && (
                              <div className="flex items-center space-x-2 mt-1">
                                <div className="flex-1 h-1 bg-gray-600 rounded-full overflow-hidden">
                                  <div 
                                    className="h-full bg-blue-500"
                                    style={{ width: `${(objective.progress_current / objective.progress_required) * 100}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-400">
                                  {objective.progress_current}/{objective.progress_required}
                                </span>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Rewards */}
                  <div className="mb-6">
                    <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
                      <Trophy className="w-5 h-5 mr-2" />
                      Rewards
                    </h4>
                    <div className="grid grid-cols-1 gap-2">
                      {selectedQuest.rewards.map((reward, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 bg-gray-800 rounded">
                          {getRewardIcon(reward.type)}
                          <div className="flex-1">
                            {reward.type === 'xp' && (
                              <span className="text-blue-400">{reward.amount} Experience Points</span>
                            )}
                            {reward.type === 'gold' && (
                              <span className="text-yellow-400">{reward.amount} Gold</span>
                            )}
                            {reward.type === 'item' && (
                              <div>
                                <span className={`font-medium ${
                                  reward.rarity === 'legendary' ? 'text-orange-400' :
                                  reward.rarity === 'epic' ? 'text-purple-400' :
                                  reward.rarity === 'rare' ? 'text-blue-400' :
                                  reward.rarity === 'uncommon' ? 'text-green-400' :
                                  'text-gray-300'
                                }`}>
                                  {reward.name}
                                </span>
                                {reward.description && (
                                  <p className="text-sm text-gray-400">{reward.description}</p>
                                )}
                              </div>
                            )}
                            {reward.type === 'ability' && (
                              <div>
                                <span className="text-red-400 font-medium">{reward.name}</span>
                                {reward.description && (
                                  <p className="text-sm text-gray-400">{reward.description}</p>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Action Button */}
                  {selectedQuest.status === 'available' && (
                    <button
                      onClick={() => handleAcceptQuest(selectedQuest)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors flex items-center justify-center space-x-2"
                    >
                      <Plus className="w-5 h-5" />
                      <span>Accept Quest</span>
                    </button>
                  )}
                </div>
              </>
            ) : (
              <div className="flex-1 flex items-center justify-center text-gray-400">
                <div className="text-center">
                  <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Select a quest to view details</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 