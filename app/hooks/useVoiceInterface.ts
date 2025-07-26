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

  const speak = useCallback((text: string, voice?: 'female' | 'male') => {
    if (!synthRef.current) return;

    // Cancel any current speech
    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    
    // Try to find a suitable voice
    const voices = synthRef.current.getVoices();
    if (voices.length > 0) {
      const preferredVoice = voices.find(v => 
        voice === 'female' 
          ? v.name.toLowerCase().includes('female') || v.name.toLowerCase().includes('zira') || v.name.toLowerCase().includes('samantha')
          : v.name.toLowerCase().includes('male') || v.name.toLowerCase().includes('david') || v.name.toLowerCase().includes('alex')
      );
      
      if (preferredVoice) {
        utterance.voice = preferredVoice;
      } else {
        // Fallback to first available voice
        utterance.voice = voices[0];
      }
    }

    utterance.rate = 0.9;
    utterance.pitch = voice === 'female' ? 1.2 : 0.8;
    utterance.volume = 0.8;

    utterance.onstart = () => {
      setState(prev => ({ ...prev, isSpeaking: true }));
    };

    utterance.onend = () => {
      setState(prev => ({ ...prev, isSpeaking: false }));
      currentUtteranceRef.current = null;
    };

    utterance.onerror = () => {
      setState(prev => ({ ...prev, isSpeaking: false }));
      currentUtteranceRef.current = null;
    };

    currentUtteranceRef.current = utterance;
    synthRef.current.speak(utterance);
  }, []);

  const stopSpeaking = useCallback(() => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setState(prev => ({ ...prev, isSpeaking: false }));
    }
  }, []);

  return {
    ...state,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  };
} 