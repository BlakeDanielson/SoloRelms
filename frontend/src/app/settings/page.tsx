'use client';

import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import {
  Settings,
  User,
  GamepadIcon,
  Eye,
  Volume2,
  Monitor,
  Shield,
  Database,
  Bell,
  Download,
  Trash2,
  Save,
  RotateCcw,
  Moon,
  Sun,
  Globe,
  Keyboard,
  MousePointer,
  Accessibility,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { TTSSettings as TTSSettingsType } from '@/components/game/TTSSettings';
import { useTTS } from '@/hooks/useTTS';

// Types
interface GameSettings {
  difficulty: 'easy' | 'normal' | 'hard' | 'expert';
  auto_save: boolean;
  combat_speed: 'slow' | 'normal' | 'fast';
  story_pacing: 'relaxed' | 'normal' | 'quick';
  character_death: 'story_consequences' | 'permanent_death' | 'resurrection_allowed';
  content_warnings: boolean;
  mature_content: boolean;
}

interface DisplaySettings {
  theme: 'light' | 'dark' | 'auto';
  font_size: 'small' | 'medium' | 'large' | 'xl';
  animation_speed: 'slow' | 'normal' | 'fast' | 'disabled';
  reduced_motion: boolean;
  high_contrast: boolean;
  color_blind_friendly: boolean;
}

interface AudioSettings {
  master_volume: number;
  sfx_volume: number;
  music_volume: number;
  voice_volume: number;
  mute_when_inactive: boolean;
}

interface NotificationSettings {
  email_notifications: boolean;
  adventure_reminders: boolean;
  achievement_notifications: boolean;
  weekly_summary: boolean;
  system_updates: boolean;
}

type SettingsTab = 'account' | 'game' | 'display' | 'audio' | 'notifications' | 'privacy' | 'data';

export default function SettingsPage() {
  const { user, isLoaded, isSignedIn } = useUser();
  const { getToken, signOut } = useAuth();
  const router = useRouter();

  // State management
  const [activeTab, setActiveTab] = useState<SettingsTab>('account');
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    difficulty: 'normal',
    auto_save: true,
    combat_speed: 'normal',
    story_pacing: 'normal',
    character_death: 'story_consequences',
    content_warnings: true,
    mature_content: false
  });
  const [displaySettings, setDisplaySettings] = useState<DisplaySettings>({
    theme: 'dark',
    font_size: 'medium',
    animation_speed: 'normal',
    reduced_motion: false,
    high_contrast: false,
    color_blind_friendly: false
  });
  const [audioSettings, setAudioSettings] = useState<AudioSettings>({
    master_volume: 80,
    sfx_volume: 75,
    music_volume: 60,
    voice_volume: 85,
    mute_when_inactive: true
  });
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    email_notifications: true,
    adventure_reminders: true,
    achievement_notifications: true,
    weekly_summary: false,
    system_updates: true
  });

  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // TTS Settings State
  const [ttsSettings, setTTSSettings] = useState<TTSSettingsType>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('tts-settings');
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch (e) {
          console.warn('Failed to parse saved TTS settings');
        }
      }
    }
    return {
      voice: 'nova',
      model: 'gpt-4o-mini-tts',
      autoPlay: false
    };
  });

  const [isTestingTTS, setIsTestingTTS] = useState(false);
  const { speak, isPlaying, isLoading } = useTTS();

  // Redirect if not authenticated
  useEffect(() => {
    if (isLoaded && !isSignedIn) {
      router.push('/sign-in');
    }
  }, [isLoaded, isSignedIn, router]);

  // Load settings from localStorage
  useEffect(() => {
    const loadSettings = () => {
      try {
        const savedGameSettings = localStorage.getItem('solo_realms_game_settings');
        const savedDisplaySettings = localStorage.getItem('solo_realms_display_settings');
        const savedAudioSettings = localStorage.getItem('solo_realms_audio_settings');
        const savedNotificationSettings = localStorage.getItem('solo_realms_notification_settings');

        if (savedGameSettings) {
          setGameSettings(JSON.parse(savedGameSettings));
        }
        if (savedDisplaySettings) {
          setDisplaySettings(JSON.parse(savedDisplaySettings));
        }
        if (savedAudioSettings) {
          setAudioSettings(JSON.parse(savedAudioSettings));
        }
        if (savedNotificationSettings) {
          setNotificationSettings(JSON.parse(savedNotificationSettings));
        }
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    };

    loadSettings();
  }, []);

  // Save settings
  const handleSaveSettings = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('solo_realms_game_settings', JSON.stringify(gameSettings));
      localStorage.setItem('solo_realms_display_settings', JSON.stringify(displaySettings));
      localStorage.setItem('solo_realms_audio_settings', JSON.stringify(audioSettings));
      localStorage.setItem('solo_realms_notification_settings', JSON.stringify(notificationSettings));

      // TODO: Save to backend when settings API is available
      // const token = await getToken();
      // await fetch('http://localhost:8000/api/user/settings', {
      //   method: 'PUT',
      //   headers: {
      //     'Authorization': `Bearer ${token}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({
      //     game_settings: gameSettings,
      //     display_settings: displaySettings,
      //     audio_settings: audioSettings,
      //     notification_settings: notificationSettings
      //   })
      // });

      setSaveMessage('Settings saved successfully!');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      setSaveMessage('Failed to save settings. Please try again.');
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  // Reset settings to defaults
  const handleResetSettings = () => {
    setGameSettings({
      difficulty: 'normal',
      auto_save: true,
      combat_speed: 'normal',
      story_pacing: 'normal',
      character_death: 'story_consequences',
      content_warnings: true,
      mature_content: false
    });
    setDisplaySettings({
      theme: 'dark',
      font_size: 'medium',
      animation_speed: 'normal',
      reduced_motion: false,
      high_contrast: false,
      color_blind_friendly: false
    });
    setAudioSettings({
      master_volume: 80,
      sfx_volume: 75,
      music_volume: 60,
      voice_volume: 85,
      mute_when_inactive: true
    });
    setNotificationSettings({
      email_notifications: true,
      adventure_reminders: true,
      achievement_notifications: true,
      weekly_summary: false,
      system_updates: true
    });
  };

  // Export user data
  const handleExportData = async () => {
    setIsExporting(true);
    try {
      const token = await getToken();
      
      // Fetch all user data
      const [charactersRes, storiesRes] = await Promise.all([
        fetch('http://localhost:8000/api/characters', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/stories', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      const characters = charactersRes.ok ? await charactersRes.json() : [];
      const stories = storiesRes.ok ? await storiesRes.json() : [];

      const exportData = {
        export_date: new Date().toISOString(),
        user_id: user?.id,
        characters,
        stories,
        settings: {
          game_settings: gameSettings,
          display_settings: displaySettings,
          audio_settings: audioSettings,
          notification_settings: notificationSettings
        }
      };

      // Create and download file
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `solo_realms_data_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      setSaveMessage('Data exported successfully!');
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      setSaveMessage('Failed to export data. Please try again.');
      setTimeout(() => setSaveMessage(null), 3000);
    } finally {
      setIsExporting(false);
    }
  };

  // Delete account
  const handleDeleteAccount = async () => {
    try {
      // This would delete all user data
      // For now, just sign out and clear localStorage
      localStorage.clear();
      await signOut();
      router.push('/');
    } catch (error) {
      setSaveMessage('Failed to delete account. Please contact support.');
      setTimeout(() => setSaveMessage(null), 3000);
    }
  };

  // Tab definitions
  const tabs = [
    { id: 'account', label: 'Account', icon: User },
    { id: 'game', label: 'Game', icon: GamepadIcon },
    { id: 'display', label: 'Display', icon: Monitor },
    { id: 'audio', label: 'Audio', icon: Volume2 },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'data', label: 'Data', icon: Database }
  ] as const;

  const handleTTSSettingsChange = (newSettings: TTSSettingsType) => {
    setTTSSettings(newSettings);
    if (typeof window !== 'undefined') {
      localStorage.setItem('tts-settings', JSON.stringify(newSettings));
    }
  };

  const testTTSVoice = async () => {
    if (isPlaying || isLoading) return;
    
    setIsTestingTTS(true);
    const testMessage = "Greetings, brave adventurer! This is a test of your chosen voice and model settings.";
    
    try {
      await speak(testMessage, {
        voice: ttsSettings.voice,
        model: ttsSettings.model
      });
    } catch (error) {
      console.error('TTS test failed:', error);
    } finally {
      setIsTestingTTS(false);
    }
  };

  // Loading state
  if (!isLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading settings...</div>
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
                <h1 className="text-2xl font-bold text-white">Settings</h1>
                <p className="text-gray-300">Customize your SoloRealms experience</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {saveMessage && (
                <div className={`flex items-center px-3 py-2 rounded-md text-sm ${
                  saveMessage.includes('success') 
                    ? 'bg-green-900/50 text-green-300' 
                    : 'bg-red-900/50 text-red-300'
                }`}>
                  {saveMessage.includes('success') ? (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  ) : (
                    <AlertCircle className="w-4 h-4 mr-2" />
                  )}
                  {saveMessage}
                </div>
              )}
              
              <button
                onClick={handleResetSettings}
                className="flex items-center bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Reset
              </button>
              
              <button
                onClick={handleSaveSettings}
                disabled={isSaving}
                className="flex items-center bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white px-4 py-2 rounded-md transition-colors"
              >
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8">
          {/* Sidebar Navigation */}
          <div className="w-64 bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-purple-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-3" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Content Area */}
          <div className="flex-1 bg-black/40 backdrop-blur-sm rounded-lg border border-white/10 p-6">
            {/* Account Settings */}
            {activeTab === 'account' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Account Settings</h2>
                
                <div className="space-y-6">
                  {/* Profile Information */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Profile Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Display Name
                        </label>
                        <input
                          type="text"
                          value={user?.firstName || ''}
                          readOnly
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Email
                        </label>
                        <input
                          type="email"
                          value={user?.primaryEmailAddress?.emailAddress || ''}
                          readOnly
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        />
                      </div>
                    </div>
                    <p className="text-sm text-gray-400 mt-2">
                      To update your profile information, please use the account management portal.
                    </p>
                  </div>

                  {/* Account Status */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Account Status</h3>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">Account Created</div>
                        <div className="text-sm text-gray-400">
                          {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'Unknown'}
                        </div>
                      </div>
                      <div className="flex items-center text-green-300">
                        <CheckCircle className="w-5 h-5 mr-2" />
                        Active
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Game Settings */}
            {activeTab === 'game' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Game Settings</h2>
                
                <div className="space-y-6">
                  {/* Difficulty */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Difficulty & Challenge</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Default Difficulty
                        </label>
                        <select
                          value={gameSettings.difficulty}
                          onChange={(e) => setGameSettings(prev => ({ ...prev, difficulty: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="easy">Easy - Forgiving gameplay, story focus</option>
                          <option value="normal">Normal - Balanced challenge</option>
                          <option value="hard">Hard - Challenging encounters</option>
                          <option value="expert">Expert - Maximum difficulty</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Character Death Handling
                        </label>
                        <select
                          value={gameSettings.character_death}
                          onChange={(e) => setGameSettings(prev => ({ ...prev, character_death: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="story_consequences">Story Consequences - Death impacts narrative</option>
                          <option value="resurrection_allowed">Resurrection Allowed - Death can be reversed</option>
                          <option value="permanent_death">Permanent Death - Character is lost forever</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Pacing */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Game Pacing</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Combat Speed
                        </label>
                        <select
                          value={gameSettings.combat_speed}
                          onChange={(e) => setGameSettings(prev => ({ ...prev, combat_speed: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="slow">Slow - Detailed descriptions</option>
                          <option value="normal">Normal - Balanced pace</option>
                          <option value="fast">Fast - Quick resolution</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Story Pacing
                        </label>
                        <select
                          value={gameSettings.story_pacing}
                          onChange={(e) => setGameSettings(prev => ({ ...prev, story_pacing: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="relaxed">Relaxed - Detailed world building</option>
                          <option value="normal">Normal - Standard pacing</option>
                          <option value="quick">Quick - Action-focused</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Content & Safety */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Content & Safety</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Auto-Save</div>
                          <div className="text-sm text-gray-400">Automatically save game progress</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={gameSettings.auto_save}
                            onChange={(e) => setGameSettings(prev => ({ ...prev, auto_save: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Content Warnings</div>
                          <div className="text-sm text-gray-400">Show warnings for potentially sensitive content</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={gameSettings.content_warnings}
                            onChange={(e) => setGameSettings(prev => ({ ...prev, content_warnings: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Mature Content</div>
                          <div className="text-sm text-gray-400">Allow mature themes and content</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={gameSettings.mature_content}
                            onChange={(e) => setGameSettings(prev => ({ ...prev, mature_content: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Display Settings */}
            {activeTab === 'display' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Display Settings</h2>
                
                <div className="space-y-6">
                  {/* Theme */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Theme & Appearance</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Theme
                        </label>
                        <select
                          value={displaySettings.theme}
                          onChange={(e) => setDisplaySettings(prev => ({ ...prev, theme: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="light">Light</option>
                          <option value="dark">Dark</option>
                          <option value="auto">Auto (System)</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                          Font Size
                        </label>
                        <select
                          value={displaySettings.font_size}
                          onChange={(e) => setDisplaySettings(prev => ({ ...prev, font_size: e.target.value as any }))}
                          className="w-full px-3 py-2 bg-gray-700/50 border border-gray-600/50 rounded-md text-white"
                        >
                          <option value="small">Small</option>
                          <option value="medium">Medium</option>
                          <option value="large">Large</option>
                          <option value="xl">Extra Large</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Accessibility */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Accessibility</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Reduced Motion</div>
                          <div className="text-sm text-gray-400">Minimize animations and transitions</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={displaySettings.reduced_motion}
                            onChange={(e) => setDisplaySettings(prev => ({ ...prev, reduced_motion: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">High Contrast</div>
                          <div className="text-sm text-gray-400">Increase contrast for better visibility</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={displaySettings.high_contrast}
                            onChange={(e) => setDisplaySettings(prev => ({ ...prev, high_contrast: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Color Blind Friendly</div>
                          <div className="text-sm text-gray-400">Use accessible color schemes</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={displaySettings.color_blind_friendly}
                            onChange={(e) => setDisplaySettings(prev => ({ ...prev, color_blind_friendly: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Audio Settings */}
            {activeTab === 'audio' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Audio Settings</h2>
                
                <div className="space-y-6">
                  {/* Volume Controls */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Volume Controls</h3>
                    <div className="space-y-4">
                      {Object.entries({
                        master_volume: 'Master Volume',
                        sfx_volume: 'Sound Effects',
                        music_volume: 'Music',
                        voice_volume: 'Voice & Narration'
                      }).map(([key, label]) => {
                        const value = audioSettings[key as keyof AudioSettings];
                        const numericValue = typeof value === 'number' ? value : 0;
                        return (
                          <div key={key}>
                            <div className="flex justify-between mb-2">
                              <label className="text-sm font-medium text-gray-300">{label}</label>
                              <span className="text-sm text-gray-300">{numericValue}%</span>
                            </div>
                            <input
                              type="range"
                              min="0"
                              max="100"
                              value={numericValue}
                              onChange={(e) => setAudioSettings(prev => ({ ...prev, [key]: parseInt(e.target.value) }))}
                              className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                            />
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Text-to-Speech Settings */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                      🎤 Text-to-Speech (TTS)
                    </h3>
                    <div className="space-y-4">
                      {/* TTS Enable/Disable */}
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">Auto-play DM Narration</div>
                          <div className="text-sm text-gray-400">Automatically read AI narration aloud</div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={ttsSettings.autoPlay}
                            onChange={(e) => handleTTSSettingsChange({ ...ttsSettings, autoPlay: e.target.checked })}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>

                      {/* Voice Selection */}
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Voice Selection</label>
                        <select
                          value={ttsSettings.voice}
                          onChange={(e) => handleTTSSettingsChange({ ...ttsSettings, voice: e.target.value as any })}
                          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="alloy">Alloy - Neutral, clear voice</option>
                          <option value="echo">Echo - Male voice</option>
                          <option value="fable">Fable - British accent</option>
                          <option value="nova">Nova - Female voice (recommended)</option>
                          <option value="onyx">Onyx - Deep male voice</option>
                          <option value="shimmer">Shimmer - Soft female voice</option>
                        </select>
                      </div>

                      {/* Model Selection */}
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">AI Model Quality</label>
                        <select
                          value={ttsSettings.model}
                          onChange={(e) => handleTTSSettingsChange({ ...ttsSettings, model: e.target.value as any })}
                          className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                        >
                          <option value="tts-1">Standard - Faster, lower cost</option>
                          <option value="tts-1-hd">HD - Higher quality, realistic</option>
                          <option value="gpt-4o-mini-tts">GPT-4o Mini TTS - Latest 2025 model ✨</option>
                        </select>
                      </div>

                      {/* Test Voice Button */}
                      <button
                        onClick={testTTSVoice}
                        disabled={isPlaying || isLoading || isTestingTTS}
                        className={`w-full px-4 py-3 rounded-lg font-medium transition-all ${
                          isPlaying || isLoading || isTestingTTS
                            ? 'bg-yellow-600/50 text-yellow-200 cursor-not-allowed'
                            : 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl'
                        }`}
                      >
                        {isLoading || isTestingTTS ? '🔄 Generating...' : 
                         isPlaying ? '🔊 Playing...' : 
                         '🎵 Test Voice & Model'}
                      </button>

                      {/* Usage Note */}
                      <div className="bg-blue-900/30 border border-blue-500/30 rounded p-3">
                        <div className="flex items-start gap-2">
                          <div className="text-blue-400 mt-0.5">ℹ️</div>
                          <div>
                            <p className="text-blue-200 text-sm font-medium">How to use TTS:</p>
                            <ul className="text-blue-300 text-xs mt-1 space-y-1">
                              <li>• Look for 🔊 buttons next to DM messages in-game</li>
                              <li>• Enable auto-play above for hands-free narration</li>
                              <li>• Higher quality models cost more but sound more natural</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Audio Preferences */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Audio Preferences</h3>
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">Mute When Inactive</div>
                        <div className="text-sm text-gray-400">Automatically mute audio when tab is not active</div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={audioSettings.mute_when_inactive}
                          onChange={(e) => setAudioSettings(prev => ({ ...prev, mute_when_inactive: e.target.checked }))}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Notification Settings */}
            {activeTab === 'notifications' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Notification Settings</h2>
                
                <div className="bg-gray-800/50 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-white mb-4">Email Notifications</h3>
                  <div className="space-y-4">
                    {Object.entries({
                      email_notifications: 'Enable Email Notifications',
                      adventure_reminders: 'Adventure Reminders',
                      achievement_notifications: 'Achievement Unlocks',
                      weekly_summary: 'Weekly Progress Summary',
                      system_updates: 'System Updates & News'
                    }).map(([key, label]) => (
                      <div key={key} className="flex items-center justify-between">
                        <div>
                          <div className="text-white font-medium">{label}</div>
                          <div className="text-sm text-gray-400">
                            {key === 'adventure_reminders' && 'Get reminded about unfinished adventures'}
                            {key === 'achievement_notifications' && 'Be notified when you unlock new achievements'}
                            {key === 'weekly_summary' && 'Receive a weekly summary of your progress'}
                            {key === 'system_updates' && 'Stay informed about new features and updates'}
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={notificationSettings[key as keyof NotificationSettings]}
                            onChange={(e) => setNotificationSettings(prev => ({ ...prev, [key]: e.target.checked }))}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Settings */}
            {activeTab === 'privacy' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Privacy Settings</h2>
                
                <div className="space-y-6">
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Data Collection</h3>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <Info className="w-5 h-5 text-blue-400 mt-0.5" />
                        <div>
                          <p className="text-gray-300 text-sm">
                            SoloRealms collects minimal data to provide and improve our service. This includes:
                          </p>
                          <ul className="text-gray-400 text-sm mt-2 space-y-1 ml-4">
                            <li>• Game progress and character data</li>
                            <li>• Usage analytics for feature improvement</li>
                            <li>• Account and authentication information</li>
                            <li>• Settings and preferences</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Your Rights</h3>
                    <div className="space-y-3">
                      <p className="text-gray-300 text-sm">
                        You have the right to access, modify, or delete your personal data at any time.
                      </p>
                      <div className="flex gap-3">
                        <button className="text-purple-400 hover:text-purple-300 text-sm underline">
                          View Privacy Policy
                        </button>
                        <button className="text-purple-400 hover:text-purple-300 text-sm underline">
                          Terms of Service
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Data Management */}
            {activeTab === 'data' && (
              <div>
                <h2 className="text-2xl font-bold text-white mb-6">Data Management</h2>
                
                <div className="space-y-6">
                  {/* Export Data */}
                  <div className="bg-gray-800/50 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-white mb-4">Export Your Data</h3>
                    <p className="text-gray-300 text-sm mb-4">
                      Download a complete backup of your SoloRealms data including characters, adventures, and settings.
                    </p>
                    <button
                      onClick={handleExportData}
                      disabled={isExporting}
                      className="flex items-center bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      {isExporting ? 'Exporting...' : 'Export Data'}
                    </button>
                  </div>

                  {/* Delete Account */}
                  <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-300 mb-4">Danger Zone</h3>
                    <p className="text-gray-300 text-sm mb-4">
                      Permanently delete your account and all associated data. This action cannot be undone.
                    </p>
                    <button
                      onClick={() => setShowDeleteConfirm(true)}
                      className="flex items-center bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-red-500/30">
            <h3 className="text-xl font-bold text-red-300 mb-4">Delete Account</h3>
            <p className="text-gray-300 mb-6">
              Are you absolutely sure you want to delete your account? This will permanently remove:
            </p>
            <ul className="text-gray-400 text-sm mb-6 space-y-1">
              <li>• All characters and their progression</li>
              <li>• All adventures and game history</li>
              <li>• All settings and preferences</li>
              <li>• Your account and profile data</li>
            </ul>
            <p className="text-red-300 text-sm mb-6 font-medium">
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
                onClick={handleDeleteAccount}
                className="flex-1 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Delete Account
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 