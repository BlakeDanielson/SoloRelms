import React, { useState, useEffect } from 'react';
import { useTTS } from '@/hooks/useTTS';

interface TTSSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSettingsChange: (settings: TTSSettings) => void;
  currentSettings?: TTSSettings;
}

export interface TTSSettings {
  voice: 'alloy' | 'echo' | 'fable' | 'nova' | 'onyx' | 'shimmer';
  model: 'tts-1' | 'tts-1-hd' | 'gpt-4o-mini-tts';
  autoPlay: boolean;
}

const TTSSettings: React.FC<TTSSettingsProps> = ({
  isOpen,
  onClose,
  onSettingsChange,
  currentSettings = {
    voice: 'nova',
    model: 'gpt-4o-mini-tts',
    autoPlay: false
  }
}) => {
  const [settings, setSettings] = useState<TTSSettings>(currentSettings);
  const [isTestPlaying, setIsTestPlaying] = useState(false);
  const { speak, isPlaying, isLoading } = useTTS();

  const voices = [
    { id: 'alloy', name: 'Alloy', description: 'Neutral, clear voice' },
    { id: 'echo', name: 'Echo', description: 'Male voice' },
    { id: 'fable', name: 'Fable', description: 'British accent' },
    { id: 'nova', name: 'Nova', description: 'Female voice (recommended for DM)' },
    { id: 'onyx', name: 'Onyx', description: 'Deep male voice' },
    { id: 'shimmer', name: 'Shimmer', description: 'Soft female voice' }
  ];

  const models = [
    { id: 'tts-1', name: 'Standard', description: 'Faster, lower quality', price: 'Lower cost' },
    { id: 'tts-1-hd', name: 'HD', description: 'Higher quality, more realistic', price: 'Medium cost' },
    { id: 'gpt-4o-mini-tts', name: 'GPT-4o Mini TTS', description: 'Latest 2025 model, enhanced naturalness', price: 'Premium cost' }
  ];

  const testMessage = "Greetings, brave adventurer! Your quest begins in the mystical forest where ancient magic still lingers in the air.";

  const handleTestVoice = async () => {
    if (isPlaying || isLoading) return;
    
    setIsTestPlaying(true);
    try {
      await speak(testMessage, { 
        voice: settings.voice, 
        model: settings.model 
      });
    } catch (error) {
      console.error('Test voice failed:', error);
    } finally {
      setIsTestPlaying(false);
    }
  };

  const handleSave = () => {
    onSettingsChange(settings);
    onClose();
  };

  const handleReset = () => {
    const defaultSettings: TTSSettings = {
      voice: 'nova',
      model: 'gpt-4o-mini-tts',
      autoPlay: false
    };
    setSettings(defaultSettings);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg border border-purple-500/30 p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-purple-300 flex items-center gap-2">
            🎤 Text-to-Speech Settings
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Voice Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Voice Selection</h3>
          <div className="grid grid-cols-2 gap-3">
            {voices.map((voice) => (
              <button
                key={voice.id}
                onClick={() => setSettings(prev => ({ ...prev, voice: voice.id as any }))}
                className={`p-3 rounded-lg border text-left transition-all ${
                  settings.voice === voice.id
                    ? 'bg-purple-600/30 border-purple-400/50 text-purple-200'
                    : 'bg-gray-700/50 border-gray-600/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                <div className="font-medium">{voice.name}</div>
                <div className="text-sm text-gray-400">{voice.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Model Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">AI Model Selection</h3>
          <div className="space-y-3">
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => setSettings(prev => ({ ...prev, model: model.id as any }))}
                className={`w-full p-4 rounded-lg border text-left transition-all ${
                  settings.model === model.id
                    ? 'bg-blue-600/30 border-blue-400/50 text-blue-200'
                    : 'bg-gray-700/50 border-gray-600/50 text-gray-300 hover:bg-gray-600/50'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="font-medium">{model.name}</div>
                  <div className="text-xs bg-gray-600/50 px-2 py-1 rounded text-gray-300">
                    {model.price}
                  </div>
                </div>
                <div className="text-sm text-gray-400">{model.description}</div>
                {model.id === 'gpt-4o-mini-tts' && (
                  <div className="text-xs text-green-400 mt-1">✨ Newest Model (2025)</div>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Settings */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Playback Settings</h3>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.autoPlay}
              onChange={(e) => setSettings(prev => ({ ...prev, autoPlay: e.target.checked }))}
              className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500"
            />
            <div>
              <div className="text-white">Auto-play DM messages</div>
              <div className="text-sm text-gray-400">Automatically read AI narration aloud</div>
            </div>
          </label>
        </div>

        {/* Test Voice */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-white mb-3">Test Voice</h3>
          <div className="bg-gray-700/50 rounded p-3 mb-3">
            <p className="text-sm text-gray-300 italic">"{testMessage}"</p>
          </div>
          <button
            onClick={handleTestVoice}
            disabled={isPlaying || isLoading}
            className={`w-full px-4 py-3 rounded-lg font-medium transition-all ${
              isPlaying || isLoading
                ? 'bg-yellow-600/50 text-yellow-200 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isLoading ? '🔄 Generating...' : isPlaying ? '🔊 Playing...' : '🎵 Test Voice & Model'}
          </button>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleReset}
            className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
          >
            Reset to Defaults
          </button>
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
};

export default TTSSettings; 