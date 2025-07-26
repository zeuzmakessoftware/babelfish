'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { apiService, TranslationRequest, TranslationResponse, AnalyticsMetrics } from '../services/api';

export interface BackendState {
  isConnected: boolean;
  isProcessing: boolean;
  lastTranslation: TranslationResponse | null;
  error: string | null;
  analytics: AnalyticsMetrics | null;
}

export function useBackendConnection() {
  const [state, setState] = useState<BackendState>({
    isConnected: false,
    isProcessing: false,
    lastTranslation: null,
    error: null,
    analytics: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(() => {
    try {
      const sessionId = apiService.getSessionId();
      const ws = apiService.createWebSocketConnection(sessionId);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setState(prev => ({ ...prev, isConnected: true, error: null }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setState(prev => ({ ...prev, isConnected: false }));
        
        // Attempt to reconnect after 3 seconds
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(() => {
          connectWebSocket();
        }, 3000);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setState(prev => ({ 
          ...prev, 
          isConnected: false, 
          error: 'WebSocket connection failed' 
        }));
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setState(prev => ({ 
        ...prev, 
        isConnected: false, 
        error: 'Failed to establish real-time connection' 
      }));
    }
  }, []);

  const handleWebSocketMessage = useCallback((data: Record<string, unknown>) => {
    const messageType = data.type as string;
    
    switch (messageType) {
      case 'status':
        if (data.status === 'processing') {
          setState(prev => ({ ...prev, isProcessing: true }));
        }
        break;
      
      case 'translation_complete':
        setState(prev => ({ 
          ...prev, 
          isProcessing: false,
          lastTranslation: data.data as TranslationResponse,
          error: null 
        }));
        break;
      
      case 'error':
        setState(prev => ({ 
          ...prev, 
          isProcessing: false,
          error: data.message as string 
        }));
        break;
      
      default:
        console.log('Unknown WebSocket message type:', messageType);
    }
  }, []);

  // Send translation request via WebSocket
  const sendTranslationRequest = useCallback((request: TranslationRequest) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'translate',
        data: request
      }));
      setState(prev => ({ ...prev, isProcessing: true }));
    } else {
      // Fallback to REST API
      translateTerm(request);
    }
  }, []);

  // REST API translation (fallback)
  const translateTerm = useCallback(async (request: TranslationRequest) => {
    try {
      setState(prev => ({ ...prev, isProcessing: true, error: null }));
      
      const response = await apiService.translateTerm(request);
      
      setState(prev => ({ 
        ...prev, 
        isProcessing: false,
        lastTranslation: response,
        error: null 
      }));
      
      return response;
    } catch (error) {
      console.error('Translation failed:', error);
      setState(prev => ({ 
        ...prev, 
        isProcessing: false,
        error: error instanceof Error ? error.message : 'Translation failed' 
      }));
      throw error;
    }
  }, []);

  // Get analytics data
  const fetchAnalytics = useCallback(async () => {
    try {
      const analytics = await apiService.getDashboardMetrics();
      setState(prev => ({ ...prev, analytics }));
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  }, []);

  // Get term suggestions
  const getSuggestions = useCallback(async (partialTerm: string) => {
    try {
      const result = await apiService.suggestTerms(partialTerm);
      return result.suggestions;
    } catch (error) {
      console.error('Failed to get suggestions:', error);
      return [];
    }
  }, []);

  // Initialize connection on mount
  useEffect(() => {
    connectWebSocket();
    fetchAnalytics();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connectWebSocket, fetchAnalytics]);

  return {
    ...state,
    translateTerm,
    sendTranslationRequest,
    getSuggestions,
    fetchAnalytics,
    reconnect: connectWebSocket,
  };
} 