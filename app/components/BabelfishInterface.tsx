'use client';

import { useState, useEffect } from 'react';
import { useVoiceInterface } from '../hooks/useVoiceInterface';
import { useBackendConnection } from '../hooks/useBackendConnection';
import { findTranslation, generateFallbackResponse, getRandomTranslation } from '../utils/translations';
import GoldfishBowlScene from './GoldfishBowl';
import ConversationFlow from './ConversationFlow';

export default function BabelfishInterface() {
  const {
    isListening,
    isSpeaking,
    transcript,
    isSupported,
    error: voiceError,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
  } = useVoiceInterface();

  const {
    isConnected,
    isProcessing,
    lastTranslation,
    error: backendError,
    analytics,
    translateTerm,
    sendTranslationRequest,
    getSuggestions,
  } = useBackendConnection();

  const [currentTranslation, setCurrentTranslation] = useState<string>('');
  const [conversationHistory, setConversationHistory] = useState<Array<{
    user: string;
    fish: string;
    timestamp: Date;
    confidence?: number;
    category?: string;
  }>>([]);

  // Process speech when listening stops
  useEffect(() => {
    console.log('Transcript changed:', transcript, 'isListening:', isListening);
    if (transcript && !isListening && transcript.trim().length > 0) {
      console.log('Processing transcript:', transcript);
      processUserInput(transcript);
    }
  }, [transcript, isListening]);

  // Update current translation when backend responds
  useEffect(() => {
    if (lastTranslation) {
      const response = `"${lastTranslation.term}" - ${lastTranslation.explanation}. Business impact: ${lastTranslation.business_impact}. Confidence: ${Math.round(lastTranslation.confidence * 100)}% (pretty sure about this one! 😎)`;
      setCurrentTranslation(response);
      speak(response, 'female');
      
      // Add to conversation history with the actual recorded text
      setConversationHistory(prev => [
        {
          user: transcript || lastTranslation.term, // Use the actual recorded text
          fish: response,
          timestamp: new Date(),
          confidence: lastTranslation.confidence,
          category: lastTranslation.category,
        },
        ...prev
      ].slice(0, 10));
    }
  }, [lastTranslation, speak, transcript]);

  // Professional welcome message
  useEffect(() => {
    if (isSupported) {
      setTimeout(() => {
        const welcomeMessage = "Hey there! I'm your AI translator - I turn tech jargon into human speak. Try saying stuff like 'microservices', 'technical debt', or 'DevOps' and watch the magic happen! 🎭";
        speak(welcomeMessage, 'female');
        setCurrentTranslation(welcomeMessage);
      }, 2000);
    } else {
      console.log('Speech recognition not supported');
    }
  }, [isSupported, speak]);

  const processUserInput = async (input: string) => {
    try {
      console.log('Processing user input:', input);
      
      // Always use fallback for now to ensure it works
      const translation = findTranslation(input);
      let response: string;

      if (translation) {
        response = `"${translation.jargon}" - ${translation.explanation}. TL;DR: It's ${translation.category} stuff that makes computers do cool things. 🎯`;
      } else {
        response = generateFallbackResponse(input);
      }

      console.log('Generated response:', response);
      setCurrentTranslation(response);
      speak(response, 'female');

      // Add to conversation history with the actual recorded text
      setConversationHistory(prev => [
        {
          user: input,
          fish: response,
          timestamp: new Date(),
          confidence: 0.85,
          category: translation?.category || 'Technical'
        },
        ...prev
      ].slice(0, 10));
      
      // Also try backend if connected (but don't wait for it)
      if (isConnected) {
        try {
          sendTranslationRequest({
            input_text: input,
            business_context: 'enterprise_technical_translation'
          });
        } catch (error) {
          console.log('Backend request failed, using local fallback');
        }
      }
    } catch (error) {
      console.error('Translation error:', error);
      const fallbackResponse = generateFallbackResponse(input);
      setCurrentTranslation(fallbackResponse);
      speak(fallbackResponse, 'female');
    }
  };

  const handleRandomExample = () => {
    const randomTranslation = getRandomTranslation();
    const response = `Random tech term: "${randomTranslation.jargon}" - ${randomTranslation.explanation}. Basically, it's ${randomTranslation.category} magic that makes your apps not crash (hopefully). ✨`;
    setCurrentTranslation(response);
    speak(response, 'female');
  };

  const handleStopAll = () => {
    stopListening();
    stopSpeaking();
  };

  const containerStyle = {
    width: '100vw',
    height: '100vh',
    position: 'relative' as const,
    overflow: 'hidden',
    background: 'linear-gradient(135deg, #111111 0%, #000000 100%)'
  };

  const errorContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100vw',
    height: '100vh',
    background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 30%, #2a2a2a 70%, #333333 100%)'
  };

  const errorPanelStyle = {
    textAlign: 'center' as const,
    background: 'rgba(0, 0, 0, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '2px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '16px',
    padding: '40px',
    maxWidth: '600px',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.8)'
  };

  const errorIconStyle = {
    width: '80px',
    height: '80px',
    background: 'rgba(239, 68, 68, 0.2)',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    margin: '0 auto 24px auto'
  };

  const errorTitleStyle = {
    fontSize: '28px',
    fontWeight: '700' as const,
    color: '#ffffff',
    margin: '0 0 16px 0',
    letterSpacing: '-0.5px'
  };

  const errorSubtitleStyle = {
    fontSize: '16px',
    color: '#cccccc',
    margin: '0 0 24px 0',
    lineHeight: '1.5'
  };

  const errorDetailStyle = {
    color: '#999999',
    fontSize: '14px',
    margin: '8px 0',
    lineHeight: '1.4'
  };

  const retryButtonStyle = {
    background: 'linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)',
    color: 'white',
    padding: '12px 24px',
    borderRadius: '8px',
    fontWeight: '600' as const,
    fontSize: '14px',
    border: 'none',
    cursor: 'pointer',
    marginTop: '24px',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    transition: 'transform 0.2s ease'
  };

  const sceneContainerStyle = {
    position: 'absolute' as const,
    inset: '0',
    width: '100%',
    height: '100%'
  };

  const floatingControlsStyle = {
    position: 'absolute' as const,
    bottom: '30px',
    right: '30px',
    zIndex: 40,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '12px'
  };

  const floatingButtonStyle = {
    background: 'rgba(0, 0, 0, 0.9)',
    color: 'white',
    padding: '12px 16px',
    borderRadius: '8px',
    fontWeight: '600' as const,
    fontSize: '12px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    cursor: 'pointer',
    boxShadow: '0 8px 20px rgba(0, 0, 0, 0.6)',
    backdropFilter: 'blur(10px)',
    transition: 'all 0.2s ease',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px'
  };

  const floatingButtonDangerStyle = {
    ...floatingButtonStyle,
    background: 'rgba(239, 68, 68, 0.9)',
    border: '1px solid rgba(239, 68, 68, 0.4)'
  };

  const statusIndicatorStyle = {
    position: 'absolute' as const,
    top: '30px',
    right: '30px',
    zIndex: 40,
    background: 'rgba(0, 0, 0, 0.9)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '12px',
    padding: '16px',
    boxShadow: '0 8px 20px rgba(0, 0, 0, 0.6)'
  };

  const statusItemStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px'
  };

  const statusActiveStyle = {
    padding: '6px 12px',
    background: 'rgba(16, 185, 129, 0.2)',
    border: '1px solid rgba(16, 185, 129, 0.5)',
    borderRadius: '20px',
    color: '#10b981',
    fontSize: '10px',
    fontWeight: '600' as const,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    position: 'relative' as const
  };

  const statusActiveIndicatorStyle = {
    position: 'absolute' as const,
    left: '8px',
    top: '50%',
    transform: 'translateY(-50%)',
    width: '6px',
    height: '6px',
    background: '#10b981',
    borderRadius: '50%',
    animation: 'pulse 2s infinite'
  };

  const statusTextStyle = {
    fontSize: '11px',
    color: '#cccccc',
    fontWeight: '500' as const
  };

  const listeningIndicatorStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 12px',
    background: 'rgba(34, 197, 94, 0.2)',
    border: '1px solid rgba(34, 197, 94, 0.5)',
    borderRadius: '20px'
  };

  const speakingIndicatorStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 12px',
    background: 'rgba(59, 130, 246, 0.2)',
    border: '1px solid rgba(59, 130, 246, 0.5)',
    borderRadius: '20px'
  };

  const pulseStyle = {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    animation: 'pulse 2s infinite'
  };

  if (!isSupported) {
    return (
      <div style={errorContainerStyle}>
        <div style={errorPanelStyle}>
          <div style={errorIconStyle}>
            <span style={{ fontSize: '36px' }}>⚠️</span>
          </div>
          <h1 style={errorTitleStyle}>Browser Compatibility Required</h1>
          <p style={errorSubtitleStyle}>
            Babelfish Enterprise AI requires advanced browser capabilities for optimal performance.
          </p>
          <div>
            <p style={errorDetailStyle}>✅ Recommended: Chrome 90+, Safari 14+, Edge 90+</p>
            <p style={errorDetailStyle}>🔧 Features: Web Speech API, Audio Context, Modern ES6+</p>
            <p style={errorDetailStyle}>🚀 For best experience: Use latest browser version</p>
          </div>
        </div>
      </div>
    );
  }

  if (voiceError) {
    return (
      <div style={errorContainerStyle}>
        <div style={errorPanelStyle}>
          <div style={{ ...errorIconStyle, background: 'rgba(245, 158, 11, 0.2)' }}>
            <span style={{ fontSize: '36px' }}>🔧</span>
          </div>
          <h1 style={errorTitleStyle}>System Configuration</h1>
          <p style={errorSubtitleStyle}>
            Please enable microphone access to experience Babelfish Enterprise AI.
          </p>
          <div>
            <p style={errorDetailStyle}>🎤 Microphone access required for voice translation</p>
            <p style={errorDetailStyle}>🔒 Your privacy is protected - audio processed locally</p>
            <p style={errorDetailStyle}>⚡ Real-time processing for instant business insights</p>
          </div>
          <button 
            onClick={() => window.location.reload()} 
            style={retryButtonStyle}
            onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
          >
            Retry System Configuration
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Enterprise Conversation Dashboard - Small, positioned to not block bowl */}
      <ConversationFlow 
        conversationHistory={conversationHistory}
        isProcessing={isProcessing}
        analytics={analytics}
      />
      
      {/* Advanced 3D Visualization - Full Screen Background */}
      <div style={sceneContainerStyle}>
        <GoldfishBowlScene 
          isSpeaking={isSpeaking} 
          isListening={isListening} 
        />
      </div>

      {/* Floating Action Controls - Compact and unobtrusive */}
      <div style={floatingControlsStyle}>
        {!isListening ? (
          <button
            onClick={startListening}
            style={floatingButtonStyle}
            title="Start Voice Translation"
            onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
          >
            🎤 Start Voice
          </button>
        ) : (
          <button
            onClick={stopListening}
            style={floatingButtonDangerStyle}
            title="Stop Voice Recording"
            onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
          >
            ⏹️ Stop Voice
          </button>
        )}
        
        {isSpeaking && (
          <button
            onClick={handleStopAll}
            style={floatingButtonDangerStyle}
            title="Stop Current Translation"
            onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
            onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
          >
            ⏹️ Stop
          </button>
        )}
        
        <button
          onClick={handleRandomExample}
          style={floatingButtonStyle}
          title="Show Enterprise Example"
          onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
        >
          💡 Demo
        </button>
        
        <button
          onClick={() => {
            console.log('Testing voice interface...');
            const testInput = "microservices";
            processUserInput(testInput);
          }}
          style={floatingButtonStyle}
          title="Test Voice Interface"
          onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
        >
          🧪 Test
        </button>
        
        <button
          onClick={async () => {
            console.log('Testing microphone permission...');
            try {
              const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
              console.log('Microphone permission granted');
              stream.getTracks().forEach(track => track.stop());
              
              console.log('Testing speech recognition directly...');
              if (window.SpeechRecognition || window.webkitSpeechRecognition) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = 'en-US';
                
                recognition.onstart = () => console.log('Direct recognition started');
                recognition.onresult = (event: any) => {
                  const transcript = Array.from(event.results)
                    .map((result: any) => result[0].transcript)
                    .join('');
                  console.log('Direct recognition result:', transcript);
                };
                recognition.onend = () => console.log('Direct recognition ended');
                recognition.onerror = (event: any) => console.log('Direct recognition error:', event.error);
                
                recognition.start();
              } else {
                console.log('Speech recognition not available');
              }
            } catch (error) {
              console.log('Microphone permission denied:', error);
            }
          }}
          style={floatingButtonStyle}
          title="Test Direct Speech Recognition"
          onMouseOver={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => (e.target as HTMLButtonElement).style.transform = 'translateY(0)'}
        >
          🎤 Direct Test
        </button>
      </div>

      {/* System Status Indicator - Compact corner display */}
      <div style={statusIndicatorStyle}>
        <div>
          <div style={statusActiveStyle}>
            {isConnected ? 'Enterprise Mode' : 'Offline Mode'}
          </div>
        </div>
        {isProcessing && (
          <div style={listeningIndicatorStyle}>
            <span style={{ fontSize: '10px', color: '#f59e0b', fontWeight: '600' }}>PROCESSING</span>
          </div>
        )}
        {isListening && (
          <div style={listeningIndicatorStyle}>
            <span style={{ fontSize: '10px', color: '#22c55e', fontWeight: '600' }}>LISTENING</span>
          </div>
        )}
        {backendError && (
          <div style={{ ...listeningIndicatorStyle, background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.5)' }}>
            <span style={{ fontSize: '10px', color: '#ef4444', fontWeight: '600' }}>ERROR</span>
          </div>
        )}
      </div>

      {/* Live Transcript Display */}
      {isListening && transcript && (
        <div style={{
          position: 'absolute',
          bottom: '120px',
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 40,
          background: 'rgba(0, 0, 0, 0.9)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '12px',
          padding: '16px 24px',
          boxShadow: '0 8px 20px rgba(0, 0, 0, 0.6)',
          maxWidth: '600px',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '12px', color: '#888', marginBottom: '4px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Recording...
          </div>
          <div style={{ fontSize: '16px', color: '#ffffff', fontWeight: '500', lineHeight: '1.4' }}>
            "{transcript}"
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes pulse {
          0%, 100% { 
            opacity: 1;
            transform: translateY(-50%) scale(1);
          }
          50% { 
            opacity: 0.5;
            transform: translateY(-50%) scale(1.2);
          }
        }
      `}</style>
    </div>
  );
}