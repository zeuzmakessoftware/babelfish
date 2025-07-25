'use client';

import { useState, useRef } from 'react';
import Typewriter from 'typewriter-effect';

interface ConversationEntry {
  id: string;
  userInput: string;
  aiResponse: string;
  timestamp: Date;
  audioBlob?: Blob;
}

export default function ConversationFlow() {
  const [conversations, setConversations] = useState<ConversationEntry[]>([]);
  const [isRecording, setIsRecording] = useState(false);
  const [currentInput, setCurrentInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [playingAudio, setPlayingAudio] = useState<string | null>(null);
  const [showTypewriter, setShowTypewriter] = useState<string | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const mockResponses = [
    "That's DevOps jargon! It means combining development and operations teams.",
    "Microservices! Breaking down applications into small, independent services.",
    "Technical debt - shortcuts in code that make future changes harder.",
    "Serverless means you don't manage servers - the cloud provider does!",
    "Agile methodology - iterative development with short cycles.",
  ];

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        processRecording(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processRecording = async (audioBlob: Blob) => {
    setIsProcessing(true);
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    const mockTranscript = "microservices and serverless architecture";
    const mockResponse = mockResponses[Math.floor(Math.random() * mockResponses.length)];
    
    const newConversation: ConversationEntry = {
      id: Date.now().toString(),
      userInput: mockTranscript,
      aiResponse: mockResponse,
      timestamp: new Date(),
      audioBlob
    };

    setConversations(prev => [newConversation, ...prev]);
    setCurrentInput(mockTranscript);
    setShowTypewriter(newConversation.id);
    setIsProcessing(false);
  };

  const playAudio = (conversationId: string, audioBlob?: Blob) => {
    if (!audioBlob) return;
    
    if (audioRef.current) {
      audioRef.current.pause();
    }
    
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    audioRef.current = audio;
    
    audio.onplay = () => setPlayingAudio(conversationId);
    audio.onended = () => {
      setPlayingAudio(null);
      URL.revokeObjectURL(audioUrl);
    };
    
    audio.play();
  };

  return (
    <div style={{
      position: 'absolute',
      top: 0,
      left: 0,
      right: 0,
      zIndex: 50,
      padding: '6px'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        position: 'relative'
      }}>
        
        {/* Main Panel - Speech Bubble */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.4)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: '24px',
          padding: '10px',
          color: 'white',
          position: 'relative',
          marginBottom: '20px' // Space for the pointer
        }}>
          {/* Speech Bubble Pointer */}
          <div style={{
            position: 'absolute',
            bottom: '-20px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '20px solid transparent',
            borderRight: '20px solid transparent',
            borderTop: '20px solid rgba(0, 0, 0, 0.4)',
            filter: 'blur(0.5px)', // Matches the bubble's blur effect slightly
            zIndex: 1
          }}></div>
          {/* Border Pointer - slightly larger to create border effect */}
          <div style={{
            position: 'absolute',
            bottom: '-21px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 0,
            height: 0,
            borderLeft: '21px solid transparent',
            borderRight: '21px solid transparent',
            borderTop: '21px solid rgba(6, 182, 212, 0.3)',
            zIndex: 0
          }}></div>

          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '20px' }}>
            <h2 style={{
              fontSize: '40px',
              fontWeight: 'normal',
              color: 'white',
              letterSpacing: '-2px',
              margin: '0 0 4px 0',
            }}>
              Babelfish
            </h2>
            <p style={{
              color: 'white',
              fontSize: '16px',
              letterSpacing: '-0.5px',
              margin: '0 0 4px 0',
            }}>
              Enterprise tech jargon translator
            </p>
          </div>

          {/* Controls Row */}
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            
            {/* Recording Button */}
            <div>
              {!isRecording && !isProcessing ? (
                <button
                  onClick={startRecording}
                  style={{
                    background: 'black',
                    color: 'white',
                    padding: '9px 9px',
                    borderRadius: '8px',
                    fontSize: '16px',
                    border: 'none',
                    cursor: 'pointer',
                    marginBottom: '10px',
                    transition: 'background-color 0.1s'
                  }}
                  onMouseOver={(e) => (e.target as HTMLButtonElement).style.background = '#444444'}
                  onMouseOut={(e) => (e.target as HTMLButtonElement).style.background = 'black'}
                >
                  Record
                </button>
              ) : isRecording ? (
                <button
                  onClick={stopRecording}
                  style={{
                    background: '#dc2626',
                    color: 'white',
                    padding: '12px 20px',
                    borderRadius: '8px',
                    fontWeight: '600',
                    border: 'none',
                    cursor: 'pointer',
                    marginBottom: '10px',
                    animation: 'pulse 2s infinite'
                  }}
                >
                  ⏹️ Stop
                </button>
              ) : (
                <div style={{
                  background: '#d97706',
                  color: 'white',
                  padding: '12px 20px',
                  borderRadius: '8px',
                  marginBottom: '10px',
                  fontWeight: '600'
                }}>
                  ⏳ Processing...
                </div>
              )}
            </div>
          </div>

          {/* Conversations */}
          {conversations.length > 0 && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              maxHeight: '120px',  // Reduced from 300px
              overflowY: 'auto'
            }}>
              {conversations.slice(0, 3).map((conversation) => (
                <div key={conversation.id} style={{
                  background: 'rgba(51, 65, 85, 0.5)',
                  borderRadius: '8px',
                  padding: '12px'  // Reduced from 16px
                }}>
                  
                  {/* User Input */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '6px'  // Reduced from 8px
                  }}>
                    <span style={{ color: '#67e8f9', fontWeight: '500' }}>🎤 You:</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {conversation.audioBlob && (
                        <button
                          onClick={() => playAudio(conversation.id, conversation.audioBlob)}
                          style={{
                            background: '#0e7490',
                            color: 'white',
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '12px',
                            border: 'none',
                            cursor: 'pointer'
                          }}
                        >
                          {playingAudio === conversation.id ? '⏸️' : '▶️'}
                        </button>
                      )}
                      <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                        {conversation.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  <p style={{
                    color: '#e5e7eb',
                    fontSize: '14px',
                    margin: '0 0 8px 0'  // Reduced from 12px
                  }}>
                    "{conversation.userInput}"
                  </p>

                  {/* AI Response */}
                  <div style={{
                    borderLeft: '2px solid #a855f7',
                    paddingLeft: '12px'
                  }}>
                    <span style={{ color: '#c084fc', fontWeight: '500' }}>🐠 Babelfish:</span>
                    <div style={{
                      color: '#e5e7eb',
                      fontSize: '14px',
                      marginTop: '4px'
                    }}>
                      {showTypewriter === conversation.id ? (
                        <Typewriter
                          options={{
                            strings: [conversation.aiResponse],
                            autoStart: true,
                            loop: false,
                            delay: 1,
                            cursor: '',
                            deleteSpeed: 999999999  // Effectively prevents deletion
                          }}
                        />
                      ) : (
                        <p style={{ margin: 0 }}>{conversation.aiResponse}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Empty State */}
          {conversations.length === 0 && (
            <div style={{ textAlign: 'center', padding: '24px 0' }}>  {/* Reduced from 32px */}
              <p style={{ color: 'white', margin: 0 }}>Ready for your first translation!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 