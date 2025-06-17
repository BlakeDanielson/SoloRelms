'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// Character interface (matching the existing one)
interface Character {
  id: number;
  name: string;
  race: string;
  character_class: string;
  background: string;
  level: number;
  experience_points: number;
  hit_points: number;
  max_hit_points: number;
  armor_class: number;
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
  backstory?: string;
  created_at: string;
}

// Form validation schema
const characterEditSchema = z.object({
  name: z.string().min(1, 'Character name is required').max(50, 'Name too long'),
  race: z.string().min(1, 'Race is required'),
  character_class: z.string().min(1, 'Class is required'),
  background: z.string().min(1, 'Background is required'),
  strength: z.number().min(1).max(20),
  dexterity: z.number().min(1).max(20),
  constitution: z.number().min(1).max(20),
  intelligence: z.number().min(1).max(20),
  wisdom: z.number().min(1).max(20),
  charisma: z.number().min(1).max(20),
  backstory: z.string().optional(),
});

type CharacterEditForm = z.infer<typeof characterEditSchema>;

export default function CharacterEditPage() {
  const { isLoaded, isSignedIn } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const characterId = params.id;

  const [character, setCharacter] = useState<Character | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue,
  } = useForm<CharacterEditForm>({
    resolver: zodResolver(characterEditSchema),
  });

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Fetch character data
  useEffect(() => {
    const fetchCharacter = async () => {
      if (!characterId) return;
      
      try {
        const token = await getToken();
        const response = await fetch(`http://localhost:8000/api/characters/${characterId}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (response.ok) {
          const data = await response.json();
          setCharacter(data);
          
          // Populate form with existing data
          reset({
            name: data.name,
            race: data.race,
            character_class: data.character_class,
            background: data.background,
            strength: data.strength,
            dexterity: data.dexterity,
            constitution: data.constitution,
            intelligence: data.intelligence,
            wisdom: data.wisdom,
            charisma: data.charisma,
            backstory: data.backstory || '',
          });
        } else if (response.status === 404) {
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
      fetchCharacter();
    }
  }, [characterId, isLoaded, isSignedIn, getToken, reset]);

  // Handle form submission
  const onSubmit = async (data: CharacterEditForm) => {
    setIsSaving(true);
    setError(null);
    setSuccessMessage(null);

    try {
      const token = await getToken();
      const response = await fetch(`http://localhost:8000/api/characters/${characterId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        setSuccessMessage('Character updated successfully!');
        setTimeout(() => {
          router.push(`/character/${characterId}`);
        }, 1500);
      } else {
        const errorData = await response.json();
        setError(errorData.message || 'Failed to update character');
      }
    } catch (err) {
      setError('Failed to update character');
    } finally {
      setIsSaving(false);
    }
  };

  // Loading states
  if (!isLoaded || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => router.push(`/character/${characterId}`)}
                className="text-white hover:text-purple-300 mr-4"
              >
                ← Back to Character
              </button>
              <h1 className="text-2xl font-bold text-white">
                Edit {character?.name || 'Character'}
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success/Error Messages */}
        {successMessage && (
          <div className="mb-6 bg-green-500/20 border border-green-500/30 rounded-lg p-4">
            <div className="text-green-200">{successMessage}</div>
          </div>
        )}
        
        {error && (
          <div className="mb-6 bg-red-500/20 border border-red-500/30 rounded-lg p-4">
            <div className="text-red-200">{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Basic Information */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Basic Information</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="character-name" className="block text-white font-medium mb-2">
                  Character Name <span className="text-red-400">*</span>
                </label>
                <input
                  {...register('name')}
                  id="character-name"
                  type="text"
                  className={`w-full bg-white/10 border rounded-md px-4 py-2 text-white placeholder-gray-300 focus:outline-none focus:ring-2 transition-colors ${
                    errors.name 
                      ? 'border-red-400 focus:ring-red-500' 
                      : 'border-white/20 focus:ring-purple-500'
                  }`}
                  placeholder="Enter character name"
                  aria-invalid={errors.name ? 'true' : 'false'}
                  aria-describedby={errors.name ? 'name-error' : undefined}
                />
                {errors.name && (
                  <p id="name-error" className="text-red-300 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="character-race" className="block text-white font-medium mb-2">
                  Race <span className="text-red-400">*</span>
                </label>
                <select
                  {...register('race')}
                  id="character-race"
                  className={`w-full bg-white/10 border rounded-md px-4 py-2 text-white focus:outline-none focus:ring-2 transition-colors ${
                    errors.race 
                      ? 'border-red-400 focus:ring-red-500' 
                      : 'border-white/20 focus:ring-purple-500'
                  }`}
                  aria-invalid={errors.race ? 'true' : 'false'}
                  aria-describedby={errors.race ? 'race-error' : undefined}
                >
                  <option value="" className="text-gray-900">Select Race</option>
                  <option value="Human" className="text-gray-900">Human</option>
                  <option value="Elf" className="text-gray-900">Elf</option>
                  <option value="Dwarf" className="text-gray-900">Dwarf</option>
                  <option value="Halfling" className="text-gray-900">Halfling</option>
                  <option value="Dragonborn" className="text-gray-900">Dragonborn</option>
                  <option value="Gnome" className="text-gray-900">Gnome</option>
                  <option value="Half-Elf" className="text-gray-900">Half-Elf</option>
                  <option value="Half-Orc" className="text-gray-900">Half-Orc</option>
                  <option value="Tiefling" className="text-gray-900">Tiefling</option>
                </select>
                {errors.race && (
                  <p id="race-error" className="text-red-300 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {errors.race.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="character-class" className="block text-white font-medium mb-2">
                  Class <span className="text-red-400">*</span>
                </label>
                <select
                  {...register('character_class')}
                  id="character-class"
                  className={`w-full bg-white/10 border rounded-md px-4 py-2 text-white focus:outline-none focus:ring-2 transition-colors ${
                    errors.character_class 
                      ? 'border-red-400 focus:ring-red-500' 
                      : 'border-white/20 focus:ring-purple-500'
                  }`}
                  aria-invalid={errors.character_class ? 'true' : 'false'}
                  aria-describedby={errors.character_class ? 'class-error' : undefined}
                >
                  <option value="" className="text-gray-900">Select Class</option>
                  <option value="Barbarian" className="text-gray-900">Barbarian</option>
                  <option value="Bard" className="text-gray-900">Bard</option>
                  <option value="Cleric" className="text-gray-900">Cleric</option>
                  <option value="Druid" className="text-gray-900">Druid</option>
                  <option value="Fighter" className="text-gray-900">Fighter</option>
                  <option value="Monk" className="text-gray-900">Monk</option>
                  <option value="Paladin" className="text-gray-900">Paladin</option>
                  <option value="Ranger" className="text-gray-900">Ranger</option>
                  <option value="Rogue" className="text-gray-900">Rogue</option>
                  <option value="Sorcerer" className="text-gray-900">Sorcerer</option>
                  <option value="Warlock" className="text-gray-900">Warlock</option>
                  <option value="Wizard" className="text-gray-900">Wizard</option>
                </select>
                {errors.character_class && (
                  <p id="class-error" className="text-red-300 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {errors.character_class.message}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="character-background" className="block text-white font-medium mb-2">
                  Background <span className="text-red-400">*</span>
                </label>
                <select
                  {...register('background')}
                  id="character-background"
                  className={`w-full bg-white/10 border rounded-md px-4 py-2 text-white focus:outline-none focus:ring-2 transition-colors ${
                    errors.background 
                      ? 'border-red-400 focus:ring-red-500' 
                      : 'border-white/20 focus:ring-purple-500'
                  }`}
                  aria-invalid={errors.background ? 'true' : 'false'}
                  aria-describedby={errors.background ? 'background-error' : undefined}
                >
                  <option value="" className="text-gray-900">Select Background</option>
                  <option value="Acolyte" className="text-gray-900">Acolyte</option>
                  <option value="Criminal" className="text-gray-900">Criminal</option>
                  <option value="Folk Hero" className="text-gray-900">Folk Hero</option>
                  <option value="Noble" className="text-gray-900">Noble</option>
                  <option value="Sage" className="text-gray-900">Sage</option>
                  <option value="Soldier" className="text-gray-900">Soldier</option>
                  <option value="Charlatan" className="text-gray-900">Charlatan</option>
                  <option value="Entertainer" className="text-gray-900">Entertainer</option>
                  <option value="Guild Artisan" className="text-gray-900">Guild Artisan</option>
                  <option value="Hermit" className="text-gray-900">Hermit</option>
                  <option value="Outlander" className="text-gray-900">Outlander</option>
                  <option value="Sailor" className="text-gray-900">Sailor</option>
                </select>
                {errors.background && (
                  <p id="background-error" className="text-red-300 text-sm mt-1 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    {errors.background.message}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Ability Scores */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Ability Scores</h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { name: 'strength', label: 'Strength', abbr: 'STR' },
                { name: 'dexterity', label: 'Dexterity', abbr: 'DEX' },
                { name: 'constitution', label: 'Constitution', abbr: 'CON' },
                { name: 'intelligence', label: 'Intelligence', abbr: 'INT' },
                { name: 'wisdom', label: 'Wisdom', abbr: 'WIS' },
                { name: 'charisma', label: 'Charisma', abbr: 'CHA' },
              ].map(({ name, label, abbr }) => (
                <div key={name} className="relative">
                  <label htmlFor={`ability-${name}`} className="block text-white font-medium mb-2">
                    {label} ({abbr}) <span className="text-red-400">*</span>
                  </label>
                  <div className="relative">
                    <input
                      {...register(name as keyof CharacterEditForm, { valueAsNumber: true })}
                      id={`ability-${name}`}
                      type="number"
                      min="1"
                      max="20"
                      className={`w-full bg-white/10 border rounded-md px-4 py-2 pr-16 text-white placeholder-gray-300 focus:outline-none focus:ring-2 transition-colors ${
                        errors[name as keyof CharacterEditForm]
                          ? 'border-red-400 focus:ring-red-500'
                          : 'border-white/20 focus:ring-purple-500'
                      }`}
                      placeholder="8-15"
                      aria-invalid={errors[name as keyof CharacterEditForm] ? 'true' : 'false'}
                      aria-describedby={errors[name as keyof CharacterEditForm] ? `${name}-error` : `${name}-help`}
                    />
                    <div className="absolute inset-y-0 right-0 flex items-center pr-3 text-gray-400 text-sm">
                      (1-20)
                    </div>
                  </div>
                  <p id={`${name}-help`} className="text-gray-400 text-xs mt-1">
                    Modifier: {name === 'strength' ? '+0' : name === 'dexterity' ? '+0' : '+0'}
                  </p>
                  {errors[name as keyof CharacterEditForm] && (
                    <p id={`${name}-error`} className="text-red-300 text-sm mt-1 flex items-center">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      {errors[name as keyof CharacterEditForm]?.message}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Backstory */}
          <div className="bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 p-6">
            <h2 className="text-2xl font-bold text-white mb-6">Backstory</h2>
            
            <div>
              <label htmlFor="character-backstory" className="block text-white font-medium mb-2">
                Character Backstory
              </label>
              <textarea
                {...register('backstory')}
                id="character-backstory"
                rows={6}
                maxLength={2000}
                className={`w-full bg-white/10 border rounded-md px-4 py-2 text-white placeholder-gray-300 focus:outline-none focus:ring-2 transition-colors resize-vertical ${
                  errors.backstory
                    ? 'border-red-400 focus:ring-red-500'
                    : 'border-white/20 focus:ring-purple-500'
                }`}
                placeholder="Tell your character's story, their background, motivations, and what drives them..."
                aria-invalid={errors.backstory ? 'true' : 'false'}
                aria-describedby={errors.backstory ? 'backstory-error' : 'backstory-help'}
              />
              <p id="backstory-help" className="text-gray-400 text-xs mt-1">
                Share your character's history, personality, and goals. This helps the DM create better adventures.
              </p>
              {errors.backstory && (
                <p id="backstory-error" className="text-red-300 text-sm mt-1 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  {errors.backstory.message}
                </p>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => router.push(`/character/${characterId}`)}
              className="px-6 py-3 border border-white/20 text-white rounded-md hover:bg-white/10 transition-colors"
              disabled={isSaving}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white rounded-md transition-colors font-semibold flex items-center"
            >
              {isSaving ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      </main>
    </div>
  );
} 