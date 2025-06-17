import React from 'react';
import { useTTS } from '@/hooks/useTTS';

interface TTSButtonProps {
  text: string;
  className?: string;
  voice?: 'alloy' | 'echo' | 'fable' | 'nova' | 'onyx' | 'shimmer';
  model?: 'tts-1' | 'tts-1-hd' | 'gpt-4o-mini-tts';
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

export const TTSButton: React.FC<TTSButtonProps> = ({ 
  text, 
  className = '', 
  voice = 'nova',
  model = 'gpt-4o-mini-tts',
  size = 'md',
  showText = true
}) => {
  const { speak, stop, pause, resume, isPlaying, isLoading, error } = useTTS();

  const handleClick = () => {
    if (isPlaying) {
      pause();
    } else if (isLoading) {
      stop();
    } else {
      speak(text, { voice, model });
    }
  };

  // Size classes
  const sizeClasses = {
    sm: 'p-1 text-sm',
    md: 'p-2 text-base',
    lg: 'p-3 text-lg'
  };

  // Icon size classes
  const iconSizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={handleClick}
        disabled={!text.trim()}
        className={`
          ${sizeClasses[size]}
          ${className}
          flex items-center justify-center
          bg-blue-600 hover:bg-blue-700 
          disabled:bg-gray-400 disabled:cursor-not-allowed
          text-white rounded-full
          transition-all duration-200
          shadow-lg hover:shadow-xl
          ${isPlaying ? 'bg-orange-600 hover:bg-orange-700' : ''}
          ${isLoading ? 'bg-yellow-600 hover:bg-yellow-700' : ''}
        `}
        title={
          isLoading ? 'Generating speech...' : 
          isPlaying ? 'Pause narration' : 
          'Play narration'
        }
      >
        {isLoading ? (
          // Loading spinner
          <svg className={`${iconSizeClasses[size]} animate-spin`} fill="none" viewBox="0 0 24 24">
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : isPlaying ? (
          // Pause icon
          <svg className={iconSizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
          </svg>
        ) : (
          // Play icon
          <svg className={iconSizeClasses[size]} fill="currentColor" viewBox="0 0 24 24">
            <path d="m8 5v14l11-7z"/>
          </svg>
        )}
      </button>

      {showText && (
        <span className="text-sm text-gray-600">
          {isLoading ? 'Generating...' : 
           isPlaying ? 'Playing...' : 
           'Listen'}
        </span>
      )}

      {error && (
        <span className="text-xs text-red-500" title={error}>
          ⚠️
        </span>
      )}
    </div>
  );
}; 