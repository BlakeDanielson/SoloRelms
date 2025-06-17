'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';

interface CharacterOptions {
  races: string[];
  classes: string[];
  backgrounds: string[];
}

interface StatRoll {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  rolls: number[][];
}

interface CharacterFormData {
  name: string;
  race: string;
  character_class: string;
  background: string;
  backstory: string;
  stats?: StatRoll;
}

export default function CreateCharacterPage() {
  const { isLoaded, isSignedIn, user } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  
  const [step, setStep] = useState(1);
  const [options, setOptions] = useState<CharacterOptions | null>(null);
  const [formData, setFormData] = useState<CharacterFormData>({
    name: '',
    race: '',
    character_class: '',
    background: '',
    backstory: ''
  });
  const [rolledStats, setRolledStats] = useState<StatRoll | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  useEffect(() => {
    // Fetch character creation options
    const fetchOptions = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/characters/options');
        if (response.ok) {
          const data = await response.json();
          setOptions(data);
        } else {
          // Fallback data if API is not available
          setOptions({
            races: ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"],
            classes: ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"],
            backgrounds: ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier", "Charlatan", "Entertainer"]
          });
        }
      } catch (err) {
        // Fallback data if API is not available
        setOptions({
          races: ["Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", "Half-Orc", "Tiefling"],
          classes: ["Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"],
          backgrounds: ["Acolyte", "Criminal", "Folk Hero", "Noble", "Sage", "Soldier", "Charlatan", "Entertainer"]
        });
      }
    };

    fetchOptions();
  }, []);

  const rollStats = async () => {
    console.log('Rolling stats...');
    setIsLoading(true);
    setError(null);
    try {
      console.log('Making API request to roll-stats...');
      const response = await fetch('http://localhost:8000/api/characters/roll-stats', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response status:', response.status);
      
      if (response.ok) {
        const stats = await response.json();
        console.log('Received stats:', stats);
        setRolledStats(stats);
        setFormData(prev => ({ ...prev, stats }));
      } else {
        console.log('API request failed, using fallback...');
        // Fallback: generate random stats
        const generateRandomStat = () => {
          const rolls = Array.from({ length: 4 }, () => Math.floor(Math.random() * 6) + 1);
          rolls.sort((a, b) => b - a);
          return { value: rolls.slice(0, 3).reduce((sum, roll) => sum + roll, 0), rolls };
        };

        const stats = {
          strength: generateRandomStat().value,
          dexterity: generateRandomStat().value,
          constitution: generateRandomStat().value,
          intelligence: generateRandomStat().value,
          wisdom: generateRandomStat().value,
          charisma: generateRandomStat().value,
          rolls: []
        };
        
        console.log('Using fallback stats:', stats);
        setRolledStats(stats);
        setFormData(prev => ({ ...prev, stats }));
      }
    } catch (err) {
      console.error('Error rolling stats:', err);
      setError('Failed to roll stats. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const createCharacter = async () => {
    if (!rolledStats) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const characterData = {
        name: formData.name,
        race: formData.race,
        character_class: formData.character_class,
        background: formData.background,
        backstory: formData.backstory
      };

      const response = await fetch('http://localhost:8000/api/characters/quick-create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`
        },
        body: JSON.stringify(characterData)
      });

      if (response.ok) {
        const character = await response.json();
        router.push(`/character/${character.id}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create character');
      }
    } catch (err) {
      setError('Failed to create character. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const getModifier = (score: number) => {
    return Math.floor((score - 10) / 2);
  };

  const formatModifier = (modifier: number) => {
    return modifier >= 0 ? `+${modifier}` : `${modifier}`;
  };

  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-white hover:text-purple-300 mr-4"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-2xl font-bold text-white">Create Character</h1>
            </div>
            <div className="text-white">
              Step {step} of 4
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-8">
          
          {/* Step 1: Basic Information */}
          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-white mb-6">Basic Information</h2>
              
              <div>
                <label className="block text-white text-sm font-medium mb-2">
                  Character Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter your character's name"
                />
              </div>

              {options && (
                <>
                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Race
                    </label>
                    <select
                      value={formData.race}
                      onChange={(e) => setFormData(prev => ({ ...prev, race: e.target.value }))}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="">Select a race</option>
                      {options.races.map(race => (
                        <option key={race} value={race} className="bg-gray-800">{race}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Class
                    </label>
                    <select
                      value={formData.character_class}
                      onChange={(e) => setFormData(prev => ({ ...prev, character_class: e.target.value }))}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="">Select a class</option>
                      {options.classes.map(cls => (
                        <option key={cls} value={cls} className="bg-gray-800">{cls}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-white text-sm font-medium mb-2">
                      Background
                    </label>
                    <select
                      value={formData.background}
                      onChange={(e) => setFormData(prev => ({ ...prev, background: e.target.value }))}
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                    >
                      <option value="">Select a background</option>
                      {options.backgrounds.map(bg => (
                        <option key={bg} value={bg} className="bg-gray-800">{bg}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              <div className="flex justify-end">
                <button
                  onClick={() => setStep(2)}
                  disabled={!formData.name || !formData.race || !formData.character_class}
                  className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-6 py-2 rounded-md transition-colors"
                >
                  Next: Roll Stats
                </button>
              </div>
            </div>
          )}

          {/* Step 2: Ability Scores */}
          {step === 2 && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-white mb-6">Ability Scores</h2>
              
              {!rolledStats ? (
                <div className="text-center">
                  <p className="text-gray-300 mb-6">
                    Roll your ability scores using the traditional 4d6 drop lowest method.
                  </p>
                  <button
                    onClick={rollStats}
                    disabled={isLoading}
                    className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-8 py-3 rounded-md transition-colors text-lg font-semibold"
                  >
                    {isLoading ? 'Rolling...' : 'Roll Ability Scores'}
                  </button>
                </div>
              ) : (
                <div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
                    {Object.entries(rolledStats).filter(([key]) => key !== 'rolls').map(([ability, score]) => (
                      <div key={ability} className="bg-white/5 rounded-lg p-4 text-center">
                        <div className="text-white font-medium capitalize mb-1">{ability}</div>
                        <div className="text-2xl font-bold text-purple-300">{score as number}</div>
                        <div className="text-sm text-gray-300">
                          {formatModifier(getModifier(score as number))}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="flex justify-between">
                    <button
                      onClick={rollStats}
                      disabled={isLoading}
                      className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      {isLoading ? 'Rolling...' : 'Reroll Stats'}
                    </button>
                    <div className="space-x-4">
                      <button
                        onClick={() => setStep(1)}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
                      >
                        Back
                      </button>
                      <button
                        onClick={() => setStep(3)}
                        className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
                      >
                        Next: Backstory
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Backstory */}
          {step === 3 && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-white mb-6">Character Backstory</h2>
              
              <div>
                <label className="block text-white text-sm font-medium mb-2">
                  Backstory (Optional)
                </label>
                <textarea
                  value={formData.backstory}
                  onChange={(e) => setFormData(prev => ({ ...prev, backstory: e.target.value }))}
                  rows={6}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-md text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Tell us about your character's background, motivations, and history..."
                />
              </div>

              <div className="flex justify-between">
                <button
                  onClick={() => setStep(2)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={() => setStep(4)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
                >
                  Next: Review
                </button>
              </div>
            </div>
          )}

          {/* Step 4: Review and Create */}
          {step === 4 && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-white mb-6">Review Character</h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Basic Information</h3>
                    <div className="bg-white/5 rounded-lg p-4 space-y-2">
                      <div><span className="text-gray-300">Name:</span> <span className="text-white">{formData.name}</span></div>
                      <div><span className="text-gray-300">Race:</span> <span className="text-white">{formData.race}</span></div>
                      <div><span className="text-gray-300">Class:</span> <span className="text-white">{formData.character_class}</span></div>
                      <div><span className="text-gray-300">Background:</span> <span className="text-white">{formData.background}</span></div>
                    </div>
                  </div>
                  
                  {formData.backstory && (
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-2">Backstory</h3>
                      <div className="bg-white/5 rounded-lg p-4">
                        <p className="text-gray-300">{formData.backstory}</p>
                      </div>
                    </div>
                  )}
                </div>

                {rolledStats && (
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Ability Scores</h3>
                    <div className="bg-white/5 rounded-lg p-4">
                      <div className="grid grid-cols-2 gap-3">
                        {Object.entries(rolledStats).filter(([key]) => key !== 'rolls').map(([ability, score]) => (
                          <div key={ability} className="flex justify-between">
                            <span className="text-gray-300 capitalize">{ability}:</span>
                            <span className="text-white font-semibold">
                              {score as number} ({formatModifier(getModifier(score as number))})
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {error && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
                  <p className="text-red-300">{error}</p>
                </div>
              )}

              <div className="flex justify-between">
                <button
                  onClick={() => setStep(3)}
                  className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
                >
                  Back
                </button>
                <button
                  onClick={createCharacter}
                  disabled={isLoading}
                  className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-8 py-3 rounded-md transition-colors text-lg font-semibold"
                >
                  {isLoading ? 'Creating Character...' : 'Create Character'}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
} 