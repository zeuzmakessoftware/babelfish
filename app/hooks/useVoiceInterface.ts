'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export interface VoiceState {
  isListening: boolean;
  isSpeaking: boolean;
  transcript: string;
  isSupported: boolean;
  error: string | null;
}

export function useVoiceInterface() {
  const [state, setState] = useState<VoiceState>({
    isListening: false,
    isSpeaking: false,
    transcript: '',
    isSupported: false,
    error: null,
  });

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    // Check if speech recognition is supported
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesis = window.speechSynthesis;

    console.log('SpeechRecognition available:', !!SpeechRecognition);
    console.log('SpeechSynthesis available:', !!speechSynthesis);

    if (SpeechRecognition && speechSynthesis) {
      setState(prev => ({ ...prev, isSupported: true }));
      
      // Initialize speech recognition
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setState(prev => ({ ...prev, isListening: true, error: null }));
      };

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0].transcript)
          .join('');
        
        console.log('Speech recognition result:', transcript);
        setState(prev => ({ ...prev, transcript }));
      };

      recognition.onend = () => {
        setState(prev => ({ ...prev, isListening: false }));
      };

      recognition.onerror = (event: any) => {
        setState(prev => ({ 
          ...prev, 
          isListening: false, 
          error: `Speech recognition error: ${event.error}` 
        }));
      };

      recognitionRef.current = recognition;
      synthRef.current = speechSynthesis;
    } else {
      setState(prev => ({ 
        ...prev, 
        isSupported: false, 
        error: 'Speech recognition not supported in this browser' 
      }));
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
      if (currentUtteranceRef.current && synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, []);

  const startListening = useCallback(() => {
    console.log('Starting speech recognition...');
    if (recognitionRef.current && !state.isListening) {
      setState(prev => ({ ...prev, transcript: '' }));
      recognitionRef.current.start();
    }
  }, [state.isListening]);

  const stopListening = useCallback(() => {
    console.log('Stopping speech recognition...');
    if (recognitionRef.current && state.isListening) {
      recognitionRef.current.stop();
    }
  }, [state.isListening]);

  const speak = useCallback(async (text: string, voice?: 'female' | 'male') => {
    if (!text.trim()) return;

    try {
      setState(prev => ({ ...prev, isSpeaking: true }));

      // Use backend Rime Voice AI for high-quality synthesis
      const response = await fetch('/api/voice/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice_style: voice === 'female' ? 'professional_female' : 'professional_male',
          speed: 1.0
        }),
      });

      if (!response.ok) {
        throw new Error(`Voice synthesis failed: ${response.status}`);
      }

      // Convert response to audio blob
      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Create and play audio
      const audio = new Audio(audioUrl);
      
      audio.onloadstart = () => {
        setState(prev => ({ ...prev, isSpeaking: true }));
      };

      audio.onended = () => {
        setState(prev => ({ ...prev, isSpeaking: false }));
        URL.revokeObjectURL(audioUrl); // Clean up
      };

      audio.onerror = (error) => {
        console.error('Audio playback error:', error);
        setState(prev => ({ ...prev, isSpeaking: false }));
        URL.revokeObjectURL(audioUrl);
      };

      // Try to play the audio with user interaction check
      try {
        await audio.play();
      } catch (playError: any) {
        if (playError.name === 'NotAllowedError') {
          // Audio autoplay blocked - show user-friendly message
          console.log('Audio autoplay blocked. Please click the page to enable audio.');
          setState(prev => ({ 
            ...prev, 
            isSpeaking: false,
            error: 'Please click the page to enable audio playback'
          }));
          
          // Set up a one-time click listener to enable audio
          const enableAudio = async () => {
            try {
              await audio.play();
              document.removeEventListener('click', enableAudio);
            } catch (e) {
              console.error('Still cannot play audio:', e);
            }
          };
          
          document.addEventListener('click', enableAudio, { once: true });
        } else {
          throw playError;
        }
      }
      
    } catch (error) {
      console.error('Voice synthesis error:', error);
      setState(prev => ({ 
        ...prev, 
        isSpeaking: false, 
        error: `Voice synthesis failed: ${error}` 
      }));
      
      // Fallback to browser speech synthesis if backend fails
      if (synthRef.current) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = voice === 'female' ? 1.2 : 0.8;
        utterance.volume = 0.8;
        
        utterance.onstart = () => {
          setState(prev => ({ ...prev, isSpeaking: true }));
        };

        utterance.onend = () => {
          setState(prev => ({ ...prev, isSpeaking: false }));
        };

        utterance.onerror = () => {
          setState(prev => ({ ...prev, isSpeaking: false }));
        };

        synthRef.current.speak(utterance);
      }
    }
  }, []);

  const stopSpeaking = useCallback(() => {
    // Stop browser speech synthesis
    if (synthRef.current) {
      synthRef.current.cancel();
    }
    
    // Stop any playing audio elements
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
      audio.pause();
      audio.currentTime = 0;
    });
    
    setState(prev => ({ ...prev, isSpeaking: false }));
  }, []);

  return {
    ...state,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
} 