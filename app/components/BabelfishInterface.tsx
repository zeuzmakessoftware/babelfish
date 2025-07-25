'use client';

import { useState, useEffect } from 'react';
import { useVoiceInterface } from '../hooks/useVoiceInterface';
import { findTranslation, generateFallbackResponse, getRandomTranslation } from '../utils/translations';
import GoldfishBowlScene from './GoldfishBowl';
import ConversationFlow from './ConversationFlow';

export default function BabelfishInterface() {
  const {
    isListening,
    isSpeaking,
    transcript,
    isSupported,
    error,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  } = useVoiceInterface();

  const [currentTranslation, setCurrentTranslation] = useState<string>('');
  const [conversationHistory, setConversationHistory] = useState<Array<{
    user: string;
    fish: string;
    timestamp: Date;
  }>>([]);

  // Process speech when listening stops
  useEffect(() => {
    if (transcript && !isListening && transcript.trim().length > 0) {
      processUserInput(transcript);
    }
  }, [transcript, isListening]);

  // Welcome message on load
  useEffect(() => {
    if (isSupported) {
      setTimeout(() => {
        const welcomeMessage = "Welcome to Babelfish! I'm your friendly tech jargon translator. Try saying terms like 'microservices', 'technical debt', or 'serverless' and I'll explain what they really mean in plain English!";
        speak(welcomeMessage, 'female');
        setCurrentTranslation(welcomeMessage);
      }, 1500);
    }
  }, [isSupported, speak]);

  const processUserInput = (input: string) => {
    const translation = findTranslation(input);
    let response: string;

    if (translation) {
      response = `Ah, "${translation.jargon}"! That's ${translation.category} jargon that means: ${translation.explanation}`;
    } else {
      response = generateFallbackResponse(input);
    }

    setCurrentTranslation(response);
    speak(response, 'female');

    // Add to conversation history
    setConversationHistory(prev => [
      {
        user: input,
        fish: response,
        timestamp: new Date()
      },
      ...prev
    ].slice(0, 8)); // Keep last 8 conversations
  };

  const handleRandomExample = () => {
    const randomTranslation = getRandomTranslation();
    const response = `Here's an example: "${randomTranslation.jargon}" means ${randomTranslation.explanation}`;
    setCurrentTranslation(response);
    speak(response, 'female');
  };

  const handleStopAll = () => {
    stopListening();
    stopSpeaking();
  };

  if (!isSupported) {
    return (
      <div className="flex items-center justify-center w-screen h-screen bg-gray-900 text-white">
        <div className="text-center glass-panel max-w-lg">
          <h1 className="text-3xl font-bold mb-4 gradient-text">🐠 Babelfish</h1>
          <p className="text-red-400 text-lg">
            Sorry, your browser doesn't support speech recognition.
            Please use Chrome, Safari, or Edge for the full experience.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-screen h-screen overflow-hidden">
      {/* Conversation Flow UI - Above the fish bowl */}
      <ConversationFlow />
      
      {/* Background 3D Scene - Full Screen */}
      <div className="absolute inset-0 w-full h-full">
        <GoldfishBowlScene 
          isSpeaking={isSpeaking} 
          isListening={isListening} 
        />
      </div>
    </div>
  );
} 