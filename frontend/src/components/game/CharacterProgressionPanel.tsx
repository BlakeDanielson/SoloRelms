'use client';

import { useState, useEffect } from 'react';
import { 
  X, 
  Star, 
  TrendingUp, 
  Award, 
  Target, 
  Zap, 
  Crown, 
  Plus, 
  Check,
  Lock,
  Sparkles,
  Shield,
  Sword,
  Heart,
  Brain,
  Eye,
  ArrowUp,
  BookOpen,
  Gift
} from 'lucide-react';

// Types
interface Skill {
  id: string;
  name: string;
  current_level: number;
  max_level: number;
  xp_current: number;
  xp_required: number;
  icon: any;
  description: string;
  bonuses: string[];
}

interface CharacterLevel {
  level: number;
  xp_required: number;
  hit_points_gained: number;
  proficiency_bonus: number;
  features_gained: string[];
  spell_slots?: { [key: number]: number };
}

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: any;
  unlocked: boolean;
  unlock_date?: string;
  xp_reward: number;
  category: 'combat' | 'exploration' | 'social' | 'magic' | 'character';
}

interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  xp_current: number;
  xp_to_next_level: number;
  hit_points: number;
  max_hit_points: number;
  armor_class: number;
  proficiency_bonus: number;
  abilities: {
    strength: number;
    dexterity: number;
    constitution: number;
    intelligence: number;
    wisdom: number;
    charisma: number;
  };
}

interface CharacterProgressionPanelProps {
  character: Character;
  isOpen: boolean;
  onClose: () => void;
  onLevelUp: () => void;
  onSkillUpgrade: (skillId: string) => void;
  onAllocateAttributePoint: (attribute: string) => void;
}

// Mock data for character progression
const SKILLS_DATA: Skill[] = [
  {
    id: 'athletics',
    name: 'Athletics',
    current_level: 3,
    max_level: 10,
    xp_current: 450,
    xp_required: 600,
    icon: TrendingUp,
    description: 'Physical prowess and strength-based activities',
    bonuses: ['+3 to Strength checks', 'Improved climbing speed', 'Enhanced jumping distance']
  },
  {
    id: 'perception',
    name: 'Perception',
    current_level: 4,
    max_level: 10,
    xp_current: 800,
    xp_required: 1000,
    icon: Eye,
    description: 'Awareness and ability to notice hidden details',
    bonuses: ['+4 to Wisdom (Perception)', 'Passive Perception +2', 'Spot hidden objects easily']
  },
  {
    id: 'arcana',
    name: 'Arcana',
    current_level: 2,
    max_level: 10,
    xp_current: 180,
    xp_required: 400,
    icon: Sparkles,
    description: 'Knowledge of magical theories and spell identification',
    bonuses: ['+2 to Intelligence (Arcana)', 'Identify magical items', 'Understand spell effects']
  },
  {
    id: 'survival',
    name: 'Survival',
    current_level: 5,
    max_level: 10,
    xp_current: 1200,
    xp_required: 1500,
    icon: Target,
    description: 'Wilderness navigation and tracking abilities',
    bonuses: ['+5 to Wisdom (Survival)', 'Track creatures', 'Find food/shelter', 'Weather prediction']
  },
  {
    id: 'stealth',
    name: 'Stealth',
    current_level: 1,
    max_level: 10,
    xp_current: 50,
    xp_required: 200,
    icon: Eye,
    description: 'Moving quietly and remaining hidden',
    bonuses: ['+1 to Dexterity (Stealth)', 'Move silently']
  },
  {
    id: 'intimidation',
    name: 'Intimidation',
    current_level: 3,
    max_level: 10,
    xp_current: 500,
    xp_required: 600,
    icon: Crown,
    description: 'Using force of personality to influence others',
    bonuses: ['+3 to Charisma (Intimidation)', 'Frighten enemies', 'Command respect']
  }
];

const LEVEL_PROGRESSION: CharacterLevel[] = [
  { level: 1, xp_required: 0, hit_points_gained: 0, proficiency_bonus: 2, features_gained: ['Divine Sense', 'Lay on Hands'] },
  { level: 2, xp_required: 300, hit_points_gained: 10, proficiency_bonus: 2, features_gained: ['Fighting Style', 'Spellcasting'] },
  { level: 3, xp_required: 900, hit_points_gained: 10, proficiency_bonus: 2, features_gained: ['Divine Health', 'Sacred Oath'] },
  { level: 4, xp_required: 2700, hit_points_gained: 10, proficiency_bonus: 2, features_gained: ['Ability Score Improvement'] },
  { level: 5, xp_required: 6500, hit_points_gained: 10, proficiency_bonus: 3, features_gained: ['Extra Attack'] },
  { level: 6, xp_required: 14000, hit_points_gained: 10, proficiency_bonus: 3, features_gained: ['Aura of Protection'] }
];

const ACHIEVEMENTS_DATA: Achievement[] = [
  {
    id: 'first_kill',
    name: 'First Blood',
    description: 'Defeat your first enemy in combat',
    icon: Sword,
    unlocked: true,
    unlock_date: '2024-01-15',
    xp_reward: 50,
    category: 'combat'
  },
  {
    id: 'level_5',
    name: 'Seasoned Adventurer',
    description: 'Reach character level 5',
    icon: Star,
    unlocked: true,
    unlock_date: '2024-01-20',
    xp_reward: 100,
    category: 'character'
  },
  {
    id: 'spell_master',
    name: 'Spell Weaver',
    description: 'Cast 50 spells successfully',
    icon: Sparkles,
    unlocked: false,
    xp_reward: 150,
    category: 'magic'
  },
  {
    id: 'treasure_hunter',
    name: 'Treasure Hunter',
    description: 'Find 10 magical items',
    icon: Gift,
    unlocked: false,
    xp_reward: 75,
    category: 'exploration'
  },
  {
    id: 'diplomat',
    name: 'Silver Tongue',
    description: 'Successfully negotiate peace in 5 conflicts',
    icon: Crown,
    unlocked: false,
    xp_reward: 125,
    category: 'social'
  },
  {
    id: 'survivor',
    name: 'Against All Odds',
    description: 'Survive with 1 HP or less in combat',
    icon: Heart,
    unlocked: true,
    unlock_date: '2024-01-18',
    xp_reward: 100,
    category: 'combat'
  }
];

export default function CharacterProgressionPanel({
  character,
  isOpen,
  onClose,
  onLevelUp,
  onSkillUpgrade,
  onAllocateAttributePoint
}: CharacterProgressionPanelProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'achievements'>('overview');
  const [availableAttributePoints, setAvailableAttributePoints] = useState(2);
  const [availableSkillPoints, setAvailableSkillPoints] = useState(3);
  const [skills, setSkills] = useState<Skill[]>(SKILLS_DATA);
  const [achievements, setAchievements] = useState<Achievement[]>(ACHIEVEMENTS_DATA);

  // Calculate XP progress
  const currentLevelData = LEVEL_PROGRESSION.find(l => l.level === character.level);
  const nextLevelData = LEVEL_PROGRESSION.find(l => l.level === character.level + 1);
  const xpProgress = nextLevelData 
    ? ((character.xp_current - (currentLevelData?.xp_required || 0)) / (nextLevelData.xp_required - (currentLevelData?.xp_required || 0))) * 100
    : 100;

  const canLevelUp = nextLevelData && character.xp_current >= nextLevelData.xp_required;

  // Helper functions
  const getAbilityModifier = (score: number) => Math.floor((score - 10) / 2);

  const getSkillProgress = (skill: Skill) => (skill.xp_current / skill.xp_required) * 100;

  const canUpgradeSkill = (skill: Skill) => {
    return availableSkillPoints > 0 && skill.current_level < skill.max_level && skill.xp_current >= skill.xp_required;
  };

  const handleSkillUpgrade = (skillId: string) => {
    if (availableSkillPoints > 0) {
      setSkills(prev => prev.map(skill => 
        skill.id === skillId && canUpgradeSkill(skill)
          ? { 
              ...skill, 
              current_level: skill.current_level + 1,
              xp_current: 0,
              xp_required: skill.xp_required + 200 // Increase requirement for next level
            }
          : skill
      ));
      setAvailableSkillPoints(prev => prev - 1);
      onSkillUpgrade(skillId);
    }
  };

  const handleAttributeUpgrade = (attribute: string) => {
    if (availableAttributePoints > 0) {
      setAvailableAttributePoints(prev => prev - 1);
      onAllocateAttributePoint(attribute);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'combat': return Sword;
      case 'exploration': return Target;
      case 'social': return Crown;
      case 'magic': return Sparkles;
      case 'character': return Star;
      default: return Award;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900/95 backdrop-blur-sm border border-purple-500/30 rounded-lg w-full max-w-6xl h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700/50">
          <div className="flex items-center">
            <Star className="w-6 h-6 text-yellow-400 mr-3" />
            <div>
              <h2 className="text-2xl font-bold text-white">{character.name} - Character Progression</h2>
              <p className="text-sm text-gray-400">
                Level {character.level} {character.race} {character.character_class}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {canLevelUp && (
              <button
                onClick={onLevelUp}
                className="flex items-center bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <ArrowUp className="w-4 h-4 mr-2" />
                Level Up!
              </button>
            )}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b border-gray-700/50">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'skills', label: 'Skills', icon: Target },
            { id: 'achievements', label: 'Achievements', icon: Award }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as any)}
              className={`flex items-center px-6 py-4 text-sm font-medium transition-colors ${
                activeTab === id
                  ? 'text-purple-300 border-b-2 border-purple-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto">
          
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="p-6 space-y-6">
              
              {/* XP Progress */}
              <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white">Experience Progress</h3>
                  <div className="text-sm text-gray-400">
                    {character.xp_current} / {nextLevelData?.xp_required || 'Max'} XP
                  </div>
                </div>
                
                <div className="space-y-3">
                  <div className="w-full bg-gray-700 rounded-full h-4">
                    <div 
                      className={`h-4 rounded-full transition-all duration-500 ${
                        canLevelUp ? 'bg-yellow-500 animate-pulse' : 'bg-blue-500'
                      }`}
                      style={{ width: `${Math.min(xpProgress, 100)}%` }}
                    />
                  </div>
                  
                  {canLevelUp && (
                    <div className="flex items-center justify-center bg-yellow-600/20 border border-yellow-400/30 rounded-lg p-3">
                      <Crown className="w-5 h-5 text-yellow-400 mr-2" />
                      <span className="text-yellow-300 font-medium">Ready to Level Up!</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Attribute Points */}
              {availableAttributePoints > 0 && (
                <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white">Available Attribute Points</h3>
                    <div className="bg-green-600 text-white px-3 py-1 rounded-full text-sm">
                      {availableAttributePoints} Points
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {Object.entries(character.abilities).map(([attr, value]) => (
                      <div key={attr} className="bg-gray-700/50 rounded-lg p-4 text-center">
                        <div className="text-sm text-gray-400 uppercase mb-1">{attr}</div>
                        <div className="text-2xl font-bold text-white mb-2">{value}</div>
                        <div className="text-xs text-gray-400 mb-3">
                          Modifier: {getAbilityModifier(value) >= 0 ? '+' : ''}{getAbilityModifier(value)}
                        </div>
                        <button
                          onClick={() => handleAttributeUpgrade(attr)}
                          disabled={availableAttributePoints === 0}
                          className="flex items-center justify-center bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-3 py-1 rounded text-xs transition-colors w-full"
                        >
                          <Plus className="w-3 h-3 mr-1" />
                          Upgrade
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Skill Points */}
              {availableSkillPoints > 0 && (
                <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-white">Available Skill Points</h3>
                    <div className="bg-purple-600 text-white px-3 py-1 rounded-full text-sm">
                      {availableSkillPoints} Points
                    </div>
                  </div>
                  <p className="text-gray-400 text-sm">
                    Use these points to upgrade your skills in the Skills tab.
                  </p>
                </div>
              )}

              {/* Character Stats Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700/50">
                  <Heart className="w-6 h-6 text-red-400 mx-auto mb-2" />
                  <div className="text-sm text-gray-400">Hit Points</div>
                  <div className="text-xl font-bold text-white">{character.hit_points}/{character.max_hit_points}</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700/50">
                  <Shield className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                  <div className="text-sm text-gray-400">Armor Class</div>
                  <div className="text-xl font-bold text-white">{character.armor_class}</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700/50">
                  <Plus className="w-6 h-6 text-green-400 mx-auto mb-2" />
                  <div className="text-sm text-gray-400">Proficiency</div>
                  <div className="text-xl font-bold text-white">+{character.proficiency_bonus}</div>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4 text-center border border-gray-700/50">
                  <Crown className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
                  <div className="text-sm text-gray-400">Level</div>
                  <div className="text-xl font-bold text-white">{character.level}</div>
                </div>
              </div>

              {/* Next Level Features */}
              {nextLevelData && (
                <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
                  <h3 className="text-lg font-bold text-white mb-4">Next Level ({character.level + 1}) Features</h3>
                  <div className="space-y-2">
                    <div className="flex items-center text-sm">
                      <Plus className="w-4 h-4 text-green-400 mr-2" />
                      <span className="text-gray-300">+{nextLevelData.hit_points_gained} Hit Points</span>
                    </div>
                    {nextLevelData.proficiency_bonus > (currentLevelData?.proficiency_bonus || 0) && (
                      <div className="flex items-center text-sm">
                        <Plus className="w-4 h-4 text-green-400 mr-2" />
                        <span className="text-gray-300">Proficiency Bonus increases to +{nextLevelData.proficiency_bonus}</span>
                      </div>
                    )}
                    {nextLevelData.features_gained.map((feature, index) => (
                      <div key={index} className="flex items-center text-sm">
                        <Sparkles className="w-4 h-4 text-purple-400 mr-2" />
                        <span className="text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Skills Tab */}
          {activeTab === 'skills' && (
            <div className="p-6">
              {availableSkillPoints > 0 && (
                <div className="bg-purple-600/20 border border-purple-400/30 rounded-lg p-4 mb-6">
                  <div className="flex items-center">
                    <Zap className="w-5 h-5 text-purple-400 mr-2" />
                    <span className="text-purple-300 font-medium">
                      You have {availableSkillPoints} skill points available!
                    </span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {skills.map((skill) => {
                  const IconComponent = skill.icon;
                  const canUpgrade = canUpgradeSkill(skill);
                  
                  return (
                    <div key={skill.id} className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center">
                          <IconComponent className="w-6 h-6 text-blue-400 mr-3" />
                          <div>
                            <h3 className="text-lg font-bold text-white">{skill.name}</h3>
                            <p className="text-sm text-gray-400">Level {skill.current_level}/{skill.max_level}</p>
                          </div>
                        </div>
                        
                        {canUpgrade && (
                          <button
                            onClick={() => handleSkillUpgrade(skill.id)}
                            className="flex items-center bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded text-sm transition-colors"
                          >
                            <ArrowUp className="w-3 h-3 mr-1" />
                            Upgrade
                          </button>
                        )}
                      </div>

                      <p className="text-sm text-gray-300 mb-4">{skill.description}</p>

                      {/* Skill Progress */}
                      <div className="mb-4">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-xs text-gray-400">Progress to Next Level</span>
                          <span className="text-xs text-gray-400">{skill.xp_current}/{skill.xp_required} XP</span>
                        </div>
                        <div className="w-full bg-gray-700 rounded-full h-2">
                          <div 
                            className="h-2 bg-blue-500 rounded-full transition-all duration-300"
                            style={{ width: `${getSkillProgress(skill)}%` }}
                          />
                        </div>
                      </div>

                      {/* Current Bonuses */}
                      <div>
                        <h4 className="text-sm font-medium text-gray-300 mb-2">Current Bonuses:</h4>
                        <div className="space-y-1">
                          {skill.bonuses.slice(0, skill.current_level).map((bonus, index) => (
                            <div key={index} className="flex items-center text-xs">
                              <Check className="w-3 h-3 text-green-400 mr-2 flex-shrink-0" />
                              <span className="text-gray-300">{bonus}</span>
                            </div>
                          ))}
                          {skill.bonuses.slice(skill.current_level).map((bonus, index) => (
                            <div key={index} className="flex items-center text-xs opacity-50">
                              <Lock className="w-3 h-3 text-gray-500 mr-2 flex-shrink-0" />
                              <span className="text-gray-500">{bonus}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Achievements Tab */}
          {activeTab === 'achievements' && (
            <div className="p-6">
              <div className="mb-6">
                <h3 className="text-lg font-bold text-white mb-2">Progress Summary</h3>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-300">
                    Unlocked: {achievements.filter(a => a.unlocked).length}/{achievements.length}
                  </span>
                  <span className="text-gray-300">
                    Total XP Earned: {achievements.filter(a => a.unlocked).reduce((sum, a) => sum + a.xp_reward, 0)}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {achievements.map((achievement) => {
                  const IconComponent = achievement.icon;
                  const CategoryIcon = getCategoryIcon(achievement.category);
                  
                  return (
                    <div
                      key={achievement.id}
                      className={`rounded-lg p-4 border transition-all ${
                        achievement.unlocked
                          ? 'bg-green-600/20 border-green-400/30'
                          : 'bg-gray-800/50 border-gray-700/50'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center">
                          <IconComponent className={`w-6 h-6 mr-3 ${
                            achievement.unlocked ? 'text-green-400' : 'text-gray-500'
                          }`} />
                          <div>
                            <h4 className={`font-bold ${
                              achievement.unlocked ? 'text-white' : 'text-gray-400'
                            }`}>
                              {achievement.name}
                            </h4>
                            <div className="flex items-center text-xs text-gray-400">
                              <CategoryIcon className="w-3 h-3 mr-1" />
                              <span className="capitalize">{achievement.category}</span>
                            </div>
                          </div>
                        </div>
                        
                        {achievement.unlocked ? (
                          <Check className="w-5 h-5 text-green-400" />
                        ) : (
                          <Lock className="w-5 h-5 text-gray-500" />
                        )}
                      </div>

                      <p className={`text-sm mb-3 ${
                        achievement.unlocked ? 'text-gray-300' : 'text-gray-500'
                      }`}>
                        {achievement.description}
                      </p>

                      <div className="flex items-center justify-between text-xs">
                        <span className={`font-medium ${
                          achievement.unlocked ? 'text-yellow-400' : 'text-gray-500'
                        }`}>
                          +{achievement.xp_reward} XP
                        </span>
                        {achievement.unlocked && achievement.unlock_date && (
                          <span className="text-gray-400">
                            {new Date(achievement.unlock_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 