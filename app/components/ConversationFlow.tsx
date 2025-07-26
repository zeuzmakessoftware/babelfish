'use client';

import { useState, useRef, useEffect } from 'react';

interface ConversationEntry {
  id: string;
  userInput: string;
  aiResponse: string;
  timestamp: Date;
  audioBlob?: Blob;
  confidence: number;
  processingTime: number;
  category: string;
}

interface SessionMetrics {
  totalTranslations: number;
  averageConfidence: number;
  averageProcessingTime: number;
  successRate: number;
  categoriesHandled: string[];
}

interface ConversationFlowProps {
  conversationHistory?: Array<{
    user: string;
    fish: string;
    timestamp: Date;
    confidence?: number;
    category?: string;
  }>;
  isProcessing?: boolean;
  analytics?: Record<string, unknown> | null;
}

export default function ConversationFlow({ 
  conversationHistory = [], 
  isProcessing = false, 
  analytics 
}: ConversationFlowProps) {
  const [conversations, setConversations] = useState<ConversationEntry[]>([]);
  const [sessionMetrics, setSessionMetrics] = useState<SessionMetrics>({
    totalTranslations: 0,
    averageConfidence: 0,
    averageProcessingTime: 0,
    successRate: 100,
    categoriesHandled: []
  });
  
  // Sync conversationHistory prop with internal conversations state
  useEffect(() => {
    if (conversationHistory.length > 0) {
      const mappedConversations: ConversationEntry[] = conversationHistory.map((entry, index) => ({
        id: `history-${index}`,
        userInput: entry.user,
        aiResponse: entry.fish,
        timestamp: entry.timestamp,
        confidence: entry.confidence || 0.85,
        processingTime: 1200,
        category: entry.category || 'Technical'
      }));
      setConversations(mappedConversations);
    }
  }, [conversationHistory]);

  useEffect(() => {
    updateSessionMetrics();
  }, [conversations]);

  const updateSessionMetrics = () => {
    if (conversations.length === 0) return;

    const totalTranslations = conversations.length;
    const averageConfidence = conversations.reduce((sum, conv) => sum + conv.confidence, 0) / totalTranslations;
    const averageProcessingTime = conversations.reduce((sum, conv) => sum + conv.processingTime, 0) / totalTranslations;
    const successRate = (conversations.filter(conv => conv.confidence > 0.8).length / totalTranslations) * 100;
    const categoriesHandled = [...new Set(conversations.map(conv => conv.category))];

    setSessionMetrics({
      totalTranslations,
      averageConfidence,
      averageProcessingTime,
      successRate,
      categoriesHandled
    });
  };

  const formatTime = (ms: number) => {
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  const containerStyle = {
    position: 'absolute' as const,
    top: '20px',
    left: '20px',
    width: '420px',
    maxHeight: '65vh',
    zIndex: 50,
    background: 'rgba(0, 0, 0, 0.95)',
    backdropFilter: 'blur(20px)',
    border: '2px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.8)',
    overflow: 'hidden'
  };

  const titleStyle = {
    fontSize: '24px',
    fontWeight: '700' as const,
    color: '#ffffff',
    margin: '0 0 4px 0',
    textAlign: 'center' as const,
    letterSpacing: '-0.5px'
  };

  const subtitleStyle = {
    fontSize: '12px',
    color: '#a0a0a0',
    margin: '0 0 16px 0',
    textAlign: 'center' as const,
    fontWeight: '500' as const,
    textTransform: 'uppercase' as const,
    letterSpacing: '1px'
  };

  const metricsGridStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '8px',
    marginBottom: '16px'
  };

  const metricCardStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    padding: '12px',
    textAlign: 'center' as const
  };

  const metricValueStyle = {
    fontSize: '18px',
    fontWeight: '700' as const,
    color: '#00ff88',
    fontFamily: 'var(--font-mono)',
    lineHeight: '1'
  };

  const metricLabelStyle = {
    fontSize: '10px',
    color: '#888',
    marginTop: '4px',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    fontWeight: '600' as const
  };

  const buttonPrimaryStyle = {
    background: 'linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)',
    color: 'white',
    padding: '12px 20px',
    borderRadius: '8px',
    fontWeight: '600' as const,
    fontSize: '14px',
    border: 'none',
    cursor: 'pointer',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    transition: 'transform 0.2s ease',
    width: '100%'
  };

  const buttonDangerStyle = {
    background: '#ef4444',
    color: 'white',
    padding: '12px 20px',
    borderRadius: '8px',
    fontWeight: '600' as const,
    fontSize: '14px',
    border: 'none',
    cursor: 'pointer',
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px'
  };

  const statusProcessingStyle = {
    padding: '12px 20px',
    background: 'rgba(245, 158, 11, 0.2)',
    border: '1px solid rgba(245, 158, 11, 0.5)',
    borderRadius: '8px',
    color: '#f59e0b',
    fontSize: '14px',
    fontWeight: '600' as const,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px'
  };

  const conversationHistoryStyle = {
    maxHeight: '200px',
    overflowY: 'auto' as const,
    paddingRight: '8px',
    marginTop: '16px'
  };

  const conversationItemStyle = {
    background: 'rgba(255, 255, 255, 0.05)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    padding: '12px',
    marginBottom: '8px'
  };

  const userInputStyle = {
    background: 'rgba(100, 100, 100, 0.3)',
    borderRadius: '6px',
    padding: '8px',
    marginBottom: '8px',
    fontSize: '12px',
    color: '#ffffff',
    fontWeight: '500' as const
  };

  const aiResponseStyle = {
    borderLeft: '3px solid #8b5cf6',
    paddingLeft: '12px',
    fontSize: '11px',
    color: '#e0e0e0',
    lineHeight: '1.4'
  };

  return (
    <div style={containerStyle}>
      
      {/* Header */}
      <div>
        <h1 style={titleStyle}>Babelfish Enterprise AI</h1>
        <p style={subtitleStyle}>Technical Translation Platform</p>
      </div>

      {/* Metrics Dashboard */}
      <div style={metricsGridStyle}>
        <div style={metricCardStyle}>
          <div style={metricValueStyle}>{sessionMetrics.totalTranslations}</div>
          <div style={metricLabelStyle}>Sessions</div>
        </div>
        <div style={metricCardStyle}>
          <div style={metricValueStyle}>{formatPercentage(sessionMetrics.averageConfidence)}</div>
          <div style={metricLabelStyle}>Confidence</div>
        </div>
        <div style={metricCardStyle}>
          <div style={metricValueStyle}>{formatTime(sessionMetrics.averageProcessingTime)}</div>
          <div style={metricLabelStyle}>Avg Time</div>
        </div>
        <div style={metricCardStyle}>
          <div style={metricValueStyle}>{Math.round(sessionMetrics.successRate)}%</div>
          <div style={metricLabelStyle}>Success</div>
        </div>
      </div>

      {/* Processing Status */}
      {isProcessing && (
        <div style={{ marginBottom: '16px' }}>
          <div style={statusProcessingStyle}>
            <div style={{ width: '16px', height: '16px', border: '2px solid currentColor', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
            Processing Translation...
          </div>
        </div>
      )}

      {/* Conversation History */}
      {conversations.length > 0 && (
        <div>
          <div style={{ fontSize: '14px', color: '#ffffff', fontWeight: '600', marginBottom: '8px' }}>
            Recent Conversations ({conversations.length})
          </div>
          
          <div style={conversationHistoryStyle}>
            {conversations.slice(0, 3).map((conversation) => (
              <div key={conversation.id} style={conversationItemStyle}>
                
                {/* Header with metrics */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <div style={{ fontSize: '10px', color: '#888', fontWeight: '600' }}>
                    {conversation.category}
                  </div>
                  <div style={{ fontSize: '10px', color: '#00ff88' }}>
                    {formatPercentage(conversation.confidence)}
                  </div>
                </div>
                
                {/* User Input - Recorded Text */}
                <div style={userInputStyle}>
                  <div style={{ fontSize: '10px', color: '#888', marginBottom: '4px', fontWeight: '600' }}>
                    RECORDED TEXT:
                  </div>
                  &ldquo;{conversation.userInput}&rdquo;
                </div>

                {/* AI Response - Translation */}
                <div style={aiResponseStyle}>
                  <div style={{ fontSize: '10px', color: '#8b5cf6', marginBottom: '4px', fontWeight: '600' }}>
                    TRANSLATION:
                  </div>
                  <div>{conversation.aiResponse}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {conversations.length === 0 && (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>🚀</div>
          <div style={{ fontSize: '14px', color: '#ffffff', fontWeight: '600', marginBottom: '4px' }}>
            Ready for Enterprise Translation
          </div>
          <div style={{ fontSize: '11px', color: '#888', lineHeight: '1.4' }}>
            Speak technical terms and see both your recorded text and AI translation
          </div>
        </div>
      )}

      <style jsx>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
} 