'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ChevronLeft, ChevronRight, User, Clock, Wand2, Play, Sparkles, Sword, Shield, Heart, Eye } from 'lucide-react';

// Types
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  level: number;
  hit_points: number;
  max_hit_points: number;
}

interface StoryTheme {
  id: string;
  name: string;
  description: string;
  icon: any;
  tags: string[];
}

// Story themes configuration
const STORY_THEMES: StoryTheme[] = [
  {
    id: 'mystery',
    name: 'Mystery & Investigation',
    description: 'Uncover secrets, solve puzzles, and investigate strange occurrences',
    icon: Eye,
    tags: ['investigation', 'puzzles', 'secrets', 'urban']
  },
  {
    id: 'combat',
    name: 'Combat & Adventure',
    description: 'Face dangerous foes, explore dungeons, and test your combat skills',
    icon: Sword,
    tags: ['combat', 'dungeons', 'monsters', 'action']
  },
  {
    id: 'social',
    name: 'Social & Intrigue',
    description: 'Navigate complex relationships, political schemes, and social challenges',
    icon: Heart,
    tags: ['roleplay', 'politics', 'relationships', 'diplomacy']
  },
  {
    id: 'exploration',
    name: 'Exploration & Discovery',
    description: 'Venture into unknown lands, discover ancient ruins, and map new territories',
    icon: Shield,
    tags: ['exploration', 'wilderness', 'discovery', 'travel']
  }
];

// Form validation schema
const adventureSchema = z.object({
  character_id: z.number().min(1, 'Please select a character'),
  story_type: z.enum(['short_form', 'campaign'], {
    required_error: 'Please select an adventure type'
  }),
  theme: z.string().min(1, 'Please select a story theme'),
  custom_seed: z.string().optional(),
  difficulty: z.enum(['easy', 'medium', 'hard'], {
    required_error: 'Please select difficulty'
  }),
  include_combat: z.boolean(),
  include_roleplay: z.boolean(),
  include_exploration: z.boolean()
});

type AdventureForm = z.infer<typeof adventureSchema>;

export default function AdventureCreatePage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  
  // Check for character parameter in URL
  const searchParams = new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '');
  const preselectedCharacterId = searchParams.get('character');

  // State management
  const [currentStep, setCurrentStep] = useState(1);
  const [characters, setCharacters] = useState<Character[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form handling
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
    trigger
  } = useForm<AdventureForm>({
    resolver: zodResolver(adventureSchema),
    defaultValues: {
      story_type: 'short_form',
      difficulty: 'medium',
      include_combat: true,
      include_roleplay: true,
      include_exploration: true
    }
  });

  const watchedValues = watch();
  const selectedCharacterId = watch('character_id');
  
  // Debug: Log when character selection changes
  useEffect(() => {
    console.log('Character selection changed:', selectedCharacterId, 'type:', typeof selectedCharacterId);
    console.log('All watched values:', watchedValues);
  }, [selectedCharacterId, watchedValues]);

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch user's characters
  useEffect(() => {
    const fetchCharacters = async () => {
      try {
        const token = await getToken();
        const response = await fetch('http://localhost:8000/api/characters', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          // Handle CharacterList response format from backend
          const charactersList = data.characters || data;
          
          if (Array.isArray(charactersList)) {
            setCharacters(charactersList);
            
            // Auto-select character if specified in URL
            if (preselectedCharacterId) {
              const characterId = parseInt(preselectedCharacterId);
              const character = charactersList.find((c: Character) => c.id === characterId);
              if (character) {
                console.log('Auto-selecting character from URL:', characterId);
                setValue('character_id', characterId);
                trigger('character_id'); // Trigger validation
              }
            }
          } else {
            console.warn('Characters API returned unexpected data format:', data);
            setCharacters([]);
            setError('Invalid character data received');
          }
        } else {
          setError('Failed to load characters');
          setCharacters([]); // Ensure characters remains an array
        }
      } catch (err) {
        console.error('Error fetching characters:', err);
        setError('Failed to load characters');
        setCharacters([]); // Ensure characters remains an array
      } finally {
        setIsLoading(false);
      }
    };

    if (isLoaded && isSignedIn) {
      fetchCharacters();
    }
  }, [isLoaded, isSignedIn, getToken]);

  // Handle form submission
  const onSubmit = async (data: AdventureForm) => {
    setIsCreating(true);
    setError(null);

    try {
      // Generate story seed based on selections
      const selectedTheme = STORY_THEMES.find(t => t.id === data.theme);
      const character = characters.find(c => c.id === data.character_id);
      
      const storyElements = [];
      if (data.include_combat) storyElements.push('combat encounters');
      if (data.include_roleplay) storyElements.push('social interactions');
      if (data.include_exploration) storyElements.push('exploration challenges');

      const generatedSeed = data.custom_seed || 
        `A ${data.difficulty} ${selectedTheme?.name.toLowerCase()} adventure for ${character?.name}, 
         a level ${character?.level} ${character?.race} ${character?.character_class}. 
         Focus on ${selectedTheme?.description.toLowerCase()} with ${storyElements.join(', ')}.
         Style: ${data.story_type === 'short_form' ? '30-minute focused adventure' : 'campaign-length epic story'}.`;

      const token = await getToken();
      const response = await fetch('http://localhost:8000/api/stories', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          character_id: data.character_id,
          story_type: data.story_type,
          story_seed: generatedSeed
        }),
      });

      if (response.ok) {
        const story = await response.json();
        // Navigate to the game with the new story/character
        router.push(`/game?character=${data.character_id}&story=${story.id}`);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create adventure');
      }
    } catch (err) {
      setError('Failed to create adventure');
    } finally {
      setIsCreating(false);
    }
  };

  // Step navigation
  const nextStep = async () => {
    const fieldsToValidate = getFieldsForStep(currentStep);
    const isValid = await trigger(fieldsToValidate);
    if (isValid && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getFieldsForStep = (step: number): (keyof AdventureForm)[] => {
    switch (step) {
      case 1: return ['character_id'];
      case 2: return ['story_type'];
      case 3: return ['theme', 'difficulty'];
      case 4: return ['include_combat', 'include_roleplay', 'include_exploration'];
      default: return [];
    }
  };

  // Loading state
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading characters...</div>
      </div>
    );
  }

  if (!isSignedIn) {
    return null;
  }

  if (characters.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-center">
          <div className="text-white text-xl mb-4">No characters found</div>
          <p className="text-gray-300 mb-6">You need to create a character before starting an adventure.</p>
          <button
            onClick={() => router.push('/character/create')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
          >
            Create Character
          </button>
        </div>
      </div>
    );
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
              <h1 className="text-2xl font-bold text-white">Create New Adventure</h1>
            </div>
            <div className="text-sm text-gray-300">
              Step {currentStep} of 4
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-300">Progress</span>
            <span className="text-sm text-gray-300">{Math.round((currentStep / 4) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(currentStep / 4) * 100}%` }}
            />
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Step 1: Character Selection */}
          {currentStep === 1 && (
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="flex items-center mb-6">
                <User className="w-6 h-6 text-purple-400 mr-3" />
                <h2 className="text-2xl font-bold text-white">Choose Your Character</h2>
              </div>
              <p className="text-gray-300 mb-6">
                Select the character you want to take on this adventure.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Array.isArray(characters) && characters.length > 0 ? (
                  characters.map((character) => {
                    // Handle both string and number comparison safely
                    const isSelected = selectedCharacterId === character.id || 
                                     (typeof selectedCharacterId === 'string' && selectedCharacterId === character.id.toString()) ||
                                     (typeof selectedCharacterId === 'string' && parseInt(selectedCharacterId, 10) === character.id);
                    console.log(`Character ${character.id} (${character.name}) selected:`, isSelected, 'selectedId:', selectedCharacterId, 'selectedType:', typeof selectedCharacterId, 'characterId:', character.id, 'characterType:', typeof character.id);
                    
                    return (
                      <label
                        key={character.id}
                        className={`relative cursor-pointer group transition-all duration-200 rounded-lg select-none ${
                          isSelected
                            ? 'ring-2 ring-purple-500 bg-purple-500/10 scale-[1.02] shadow-lg shadow-purple-500/25'
                            : 'hover:ring-2 hover:ring-purple-400/50 hover:scale-[1.01] hover:shadow-lg hover:shadow-purple-400/10'
                        }`}
                      >
                        <input
                          type="radio"
                          value={character.id.toString()}
                          checked={selectedCharacterId === character.id}
                          onChange={(e) => {
                            console.log('Radio onChange triggered:', e.target.value);
                            const numValue = parseInt(e.target.value, 10);
                            console.log('Setting character_id to:', numValue);
                            setValue('character_id', numValue);
                            trigger('character_id');
                          }}
                          className="sr-only"
                        />
                        <div className={`rounded-lg p-4 border transition-all duration-200 ${
                          isSelected
                            ? 'bg-black/80 border-purple-500 shadow-lg shadow-purple-500/20'
                            : 'bg-black/60 border-white/20 hover:border-purple-400 group-hover:bg-black/70'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-xl font-bold text-white">{character.name}</h3>
                            <span className="text-sm text-purple-300">Level {character.level}</span>
                          </div>
                          <p className="text-gray-300 mb-2">
                            {character.race} {character.character_class}
                          </p>
                          <div className="flex items-center text-sm text-gray-400">
                            <span>HP: {character.hit_points}/{character.max_hit_points}</span>
                          </div>
                          {isSelected && (
                            <div className="mt-3 flex items-center justify-center text-sm text-purple-300 bg-purple-900/50 rounded py-2">
                              <span className="w-3 h-3 bg-purple-400 rounded-full mr-2 animate-pulse"></span>
                              <span className="font-medium">Selected</span>
                            </div>
                          )}
                        </div>
                      </label>
                    );
                  })
                ) : (
                  <div className="col-span-full bg-black/60 rounded-lg p-8 border border-white/20 text-center">
                    <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">No Characters Found</h3>
                    <p className="text-gray-300 mb-4">
                      You need to create a character before starting an adventure.
                    </p>
                    <button
                      onClick={() => router.push('/character/create')}
                      className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-md transition-colors"
                    >
                      Create Character
                    </button>
                  </div>
                )}
              </div>
              {errors.character_id && (
                <p className="text-red-400 text-sm mt-2">{errors.character_id.message}</p>
              )}
            </div>
          )}

          {/* Step 2: Adventure Type */}
          {currentStep === 2 && (
            <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
              <div className="flex items-center mb-6">
                <Clock className="w-6 h-6 text-purple-400 mr-3" />
                <h2 className="text-2xl font-bold text-white">Adventure Type</h2>
              </div>
              <p className="text-gray-300 mb-6">
                Choose the length and scope of your adventure.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <label className={`cursor-pointer group ${
                  watchedValues.story_type === 'short_form' ? 'ring-2 ring-purple-500' : ''
                }`}>
                  <input
                    type="radio"
                    value="short_form"
                    {...register('story_type')}
                    className="sr-only"
                  />
                  <div className="bg-black/60 rounded-lg p-6 border border-white/20 hover:border-purple-400 transition-all duration-200 group-hover:bg-black/70">
                    <div className="flex items-center mb-3">
                      <Sparkles className="w-6 h-6 text-yellow-400 mr-3" />
                      <h3 className="text-xl font-bold text-white">Quick Adventure</h3>
                    </div>
                    <p className="text-gray-300 mb-4">
                      A focused 30-minute adventure perfect for a quick gaming session.
                    </p>
                    <ul className="text-sm text-gray-400 space-y-1">
                      <li>• 30-45 minutes gameplay</li>
                      <li>• Single story arc</li>
                      <li>• Immediate action</li>
                      <li>• Quick resolution</li>
                    </ul>
                  </div>
                </label>

                <label className={`cursor-pointer group ${
                  watchedValues.story_type === 'campaign' ? 'ring-2 ring-purple-500' : ''
                }`}>
                  <input
                    type="radio"
                    value="campaign"
                    {...register('story_type')}
                    className="sr-only"
                  />
                  <div className="bg-black/60 rounded-lg p-6 border border-white/20 hover:border-purple-400 transition-all duration-200 group-hover:bg-black/70">
                    <div className="flex items-center mb-3">
                      <Wand2 className="w-6 h-6 text-blue-400 mr-3" />
                      <h3 className="text-xl font-bold text-white">Epic Campaign</h3>
                    </div>
                    <p className="text-gray-300 mb-4">
                      An extended adventure with multiple sessions and complex storylines.
                    </p>
                    <ul className="text-sm text-gray-400 space-y-1">
                      <li>• Multi-session gameplay</li>
                      <li>• Complex story arcs</li>
                      <li>• Character development</li>
                      <li>• Rich world building</li>
                    </ul>
                  </div>
                </label>
              </div>
              {errors.story_type && (
                <p className="text-red-400 text-sm mt-2">{errors.story_type.message}</p>
              )}
            </div>
          )}

          {/* Step 3: Theme & Difficulty */}
          {currentStep === 3 && (
            <div className="space-y-6">
              {/* Story Theme */}
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Story Theme</h2>
                <p className="text-gray-300 mb-6">
                  What type of adventure appeals to you?
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {STORY_THEMES.map((theme) => {
                    const IconComponent = theme.icon;
                    return (
                      <label
                        key={theme.id}
                        className={`cursor-pointer group ${
                          watchedValues.theme === theme.id ? 'ring-2 ring-purple-500' : ''
                        }`}
                      >
                        <input
                          type="radio"
                          value={theme.id}
                          {...register('theme')}
                          className="sr-only"
                        />
                        <div className="bg-black/60 rounded-lg p-4 border border-white/20 hover:border-purple-400 transition-all duration-200 group-hover:bg-black/70">
                          <div className="flex items-center mb-3">
                            <IconComponent className="w-6 h-6 text-purple-400 mr-3" />
                            <h3 className="text-lg font-bold text-white">{theme.name}</h3>
                          </div>
                          <p className="text-gray-300 text-sm mb-3">{theme.description}</p>
                          <div className="flex flex-wrap gap-1">
                            {theme.tags.map((tag) => (
                              <span
                                key={tag}
                                className="px-2 py-1 bg-purple-900/50 text-purple-300 text-xs rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </label>
                    );
                  })}
                </div>
                {errors.theme && (
                  <p className="text-red-400 text-sm mt-2">{errors.theme.message}</p>
                )}
              </div>

              {/* Difficulty */}
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Difficulty Level</h2>
                <p className="text-gray-300 mb-6">
                  How challenging do you want this adventure to be?
                </p>

                <div className="grid grid-cols-3 gap-4">
                  {[
                    { value: 'easy', label: 'Easy', desc: 'Relaxed gameplay, lower stakes', color: 'green' },
                    { value: 'medium', label: 'Medium', desc: 'Balanced challenge and story', color: 'yellow' },
                    { value: 'hard', label: 'Hard', desc: 'High stakes, tactical combat', color: 'red' }
                  ].map((difficulty) => (
                    <label
                      key={difficulty.value}
                      className={`cursor-pointer group ${
                        watchedValues.difficulty === difficulty.value ? 'ring-2 ring-purple-500' : ''
                      }`}
                    >
                      <input
                        type="radio"
                        value={difficulty.value}
                        {...register('difficulty')}
                        className="sr-only"
                      />
                      <div className="bg-black/60 rounded-lg p-4 border border-white/20 hover:border-purple-400 transition-all duration-200 group-hover:bg-black/70 text-center">
                        <div className={`w-3 h-3 rounded-full mx-auto mb-2 ${
                          difficulty.color === 'green' ? 'bg-green-400' :
                          difficulty.color === 'yellow' ? 'bg-yellow-400' : 'bg-red-400'
                        }`} />
                        <h3 className="text-lg font-bold text-white mb-1">{difficulty.label}</h3>
                        <p className="text-gray-300 text-sm">{difficulty.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
                {errors.difficulty && (
                  <p className="text-red-400 text-sm mt-2">{errors.difficulty.message}</p>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Preferences & Custom Seed */}
          {currentStep === 4 && (
            <div className="space-y-6">
              {/* Adventure Elements */}
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Adventure Elements</h2>
                <p className="text-gray-300 mb-6">
                  Customize what types of challenges you want to include.
                </p>

                <div className="space-y-4">
                  {[
                    { key: 'include_combat', label: 'Combat Encounters', desc: 'Battle monsters and opponents' },
                    { key: 'include_roleplay', label: 'Social Interactions', desc: 'Negotiate, persuade, and interact with NPCs' },
                    { key: 'include_exploration', label: 'Exploration Challenges', desc: 'Discover secrets and navigate environments' }
                  ].map((element) => (
                    <label key={element.key} className="flex items-center space-x-3 cursor-pointer group">
                      <input
                        type="checkbox"
                        {...register(element.key as keyof AdventureForm)}
                        className="w-5 h-5 text-purple-600 bg-black/60 border-gray-600 rounded focus:ring-purple-500"
                      />
                      <div>
                        <span className="text-white font-medium">{element.label}</span>
                        <p className="text-gray-400 text-sm">{element.desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Custom Story Seed */}
              <div className="bg-black/40 backdrop-blur-sm rounded-lg p-6 border border-white/10">
                <h2 className="text-2xl font-bold text-white mb-4">Custom Story Idea (Optional)</h2>
                <p className="text-gray-300 mb-4">
                  Have a specific story in mind? Describe it here and the AI will incorporate your ideas.
                </p>
                <textarea
                  {...register('custom_seed')}
                  className="w-full h-32 bg-black/60 border border-gray-600 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="e.g., I want to explore an abandoned wizard's tower and discover why they disappeared..."
                />
              </div>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              type="button"
              onClick={prevStep}
              disabled={currentStep === 1}
              className="flex items-center px-6 py-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:opacity-50 text-white rounded-lg transition-colors"
            >
              <ChevronLeft className="w-5 h-5 mr-2" />
              Previous
            </button>

            {currentStep < 4 ? (
              <button
                type="button"
                onClick={nextStep}
                className="flex items-center px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                Next
                <ChevronRight className="w-5 h-5 ml-2" />
              </button>
            ) : (
              <button
                type="submit"
                disabled={isCreating}
                className="flex items-center px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 text-white rounded-lg transition-all duration-200 shadow-lg"
              >
                {isCreating ? (
                  <>
                    <div className="animate-spin w-5 h-5 mr-2 border-2 border-white border-t-transparent rounded-full" />
                    Creating Adventure...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5 mr-2" />
                    Start Adventure
                  </>
                )}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
} 