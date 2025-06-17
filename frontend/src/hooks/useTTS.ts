import { useState, useRef, useCallback } from 'react';

interface TTSOptions {
  voice?: string;
  model?: 'tts-1' | 'tts-1-hd' | 'gpt-4o-mini-tts';
}

interface TTSState {
  isPlaying: boolean;
  isLoading: boolean;
  error: string | null;
}

// Backend API URL configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useTTS = () => {
  const [state, setState] = useState<TTSState>({
    isPlaying: false,
    isLoading: false,
    error: null
  });
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentRequestRef = useRef<AbortController | null>(null);

  const speak = useCallback(async (text: string, options: TTSOptions = {}) => {
    try {
      console.log('🎤 TTS: Starting speak request', { text: text.substring(0, 50) + '...', options, API_BASE_URL });
      
      // Cancel any existing request
      if (currentRequestRef.current) {
        currentRequestRef.current.abort();
      }

      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }

      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Create new abort controller for this request
      currentRequestRef.current = new AbortController();

      const requestUrl = `${API_BASE_URL}/api/tts/generate`;
      const requestBody = {
        text,
        voice: options.voice || 'nova',
        model: options.model || 'gpt-4o-mini-tts'
      };

      console.log('🎤 TTS: Making request to', requestUrl, 'with body:', requestBody);

      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: currentRequestRef.current.signal
      });

      console.log('🎤 TTS: Response received', { 
        status: response.status, 
        statusText: response.statusText, 
        ok: response.ok,
        contentType: response.headers.get('content-type')
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🎤 TTS: Request failed', { status: response.status, statusText: response.statusText, errorText });
        throw new Error(`TTS request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      // Get audio blob
      const audioBlob = await response.blob();
      console.log('🎤 TTS: Audio blob received', { size: audioBlob.size, type: audioBlob.type });
      
      const audioUrl = URL.createObjectURL(audioBlob);

      // Create audio element
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      // Set up event listeners
      audio.onloadstart = () => {
        setState(prev => ({ ...prev, isLoading: true }));
      };

      audio.oncanplay = () => {
        setState(prev => ({ ...prev, isLoading: false }));
      };

      audio.onplay = () => {
        setState(prev => ({ ...prev, isPlaying: true }));
      };

      audio.onpause = () => {
        setState(prev => ({ ...prev, isPlaying: false }));
      };

      audio.onended = () => {
        setState(prev => ({ ...prev, isPlaying: false }));
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };

      audio.onerror = () => {
        setState(prev => ({ ...prev, isPlaying: false, isLoading: false, error: 'Audio playback failed' }));
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };

      // Start playing
      await audio.play();

    } catch (error: any) {
      if (error.name === 'AbortError') {
        // Request was cancelled, don't update state
        return;
      }
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        isPlaying: false, 
        error: error.message || 'TTS failed' 
      }));
    }
  }, []);

  const stop = useCallback(() => {
    // Cancel any ongoing request
    if (currentRequestRef.current) {
      currentRequestRef.current.abort();
    }

    // Stop any playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    setState(prev => ({ ...prev, isPlaying: false, isLoading: false }));
  }, []);

  const pause = useCallback(() => {
    if (audioRef.current && !audioRef.current.paused) {
      audioRef.current.pause();
    }
  }, []);

  const resume = useCallback(() => {
    if (audioRef.current && audioRef.current.paused) {
      audioRef.current.play();
    }
  }, []);

  return {
    speak,
    stop,
    pause,
    resume,
    isPlaying: state.isPlaying,
    isLoading: state.isLoading,
    error: state.error
  };
}; 