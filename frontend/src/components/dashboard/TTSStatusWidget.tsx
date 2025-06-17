import React, { useState, useEffect } from 'react';
import { useTTS } from '@/hooks/useTTS';
import { TTSSettings } from '@/components/game/TTSSettings';

interface TTSStatusWidgetProps {
  className?: string;
}

export const TTSStatusWidget: React.FC<TTSStatusWidgetProps> = ({ className = '' }) => {
  const [ttsSettings, setTTSSettings] = useState<any>(() => {
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

  const [isTestPlaying, setIsTestPlaying] = useState(false);
  const { speak, isPlaying, isLoading } = useTTS();

  const handleToggleAutoPlay = () => {
    const newSettings = { ...ttsSettings, autoPlay: !ttsSettings.autoPlay };
    setTTSSettings(newSettings);
    localStorage.setItem('tts-settings', JSON.stringify(newSettings));
  };

  const testVoice = async () => {
    if (isPlaying || isLoading) return;
    
    setIsTestPlaying(true);
    const testMessage = "Hello! This is a test of your TTS settings.";
    
    try {
      await speak(testMessage, {
        voice: ttsSettings.voice,
        model: ttsSettings.model
      });
    } catch (error) {
      console.error('TTS test failed:', error);
    } finally {
      setIsTestPlaying(false);
    }
  };

  return (
    <div className={`bg-gray-800/50 rounded-lg p-4 border border-gray-700/50 ${className}`}>
      <div className="flex items-center gap-3 mb-3">
        <div className="text-purple-400">
          🎤
        </div>
        <div>
          <h3 className="text-white font-semibold">Text-to-Speech</h3>
          <p className="text-gray-400 text-sm">AI narration audio</p>
        </div>
      </div>

      <div className="space-y-3">
        {/* Status Display */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">Auto-play</span>
          <div className="flex items-center gap-2">
            {ttsSettings.autoPlay && (
              <span className="text-xs bg-green-600/30 text-green-300 px-2 py-0.5 rounded">ON</span>
            )}
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={ttsSettings.autoPlay}
                onChange={handleToggleAutoPlay}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-600 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </div>

        {/* Voice & Model Info */}
        <div className="text-xs text-gray-400 bg-gray-700/30 rounded p-2">
          <div>Voice: <span className="text-gray-300 capitalize">{ttsSettings.voice}</span></div>
          <div>Model: <span className="text-gray-300">{
            ttsSettings.model === 'gpt-4o-mini-tts' ? 'GPT-4o Mini' : 
            ttsSettings.model === 'tts-1-hd' ? 'HD' : 
            'Standard'
          }</span></div>
        </div>

        {/* Quick Actions */}
        <div className="flex gap-2">
          <button
            onClick={testVoice}
            disabled={isPlaying || isLoading || isTestPlaying}
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-all ${
              isPlaying || isLoading || isTestPlaying
                ? 'bg-yellow-600/50 text-yellow-200 cursor-not-allowed'
                : 'bg-green-600/80 hover:bg-green-600 text-white'
            }`}
          >
            {isLoading || isTestPlaying ? '🔄' : isPlaying ? '🔊' : '🎵'} Test
          </button>
          
          <button
            onClick={() => window.location.href = '/settings#audio'}
            className="flex-1 px-3 py-2 rounded text-sm font-medium bg-gray-600/50 hover:bg-gray-600 text-gray-300 transition-colors"
          >
            ⚙️ Settings
          </button>
        </div>

        {/* Usage Tip */}
        {!ttsSettings.autoPlay && (
          <div className="text-xs text-blue-300 bg-blue-900/20 border border-blue-500/20 rounded p-2">
            💡 Tip: Enable auto-play for hands-free gaming, or look for 🔊 buttons next to DM messages in-game!
          </div>
        )}
      </div>
    </div>
  );
}; 