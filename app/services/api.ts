export interface TranslationRequest {
  input_text: string;
  session_id?: string;
  business_context?: string;
  user_agent?: string;
}

export interface TranslationResponse {
  session_id: string;
  term: string;
  explanation: string;
  category: string;
  confidence: number;
  business_impact: string;
  related_terms: string[];
  sources: string[];
  processing_time: number;
}

export interface VoiceSynthesisRequest {
  text: string;
  voice_style?: string;
  speed?: number;
}

export interface AnalyticsMetrics extends Record<string, unknown> {
  total_translations: number;
  average_confidence: number;
  top_categories: Array<{ category: string; count: number }>;
  recent_activity: Array<{ term: string; timestamp: string; confidence: number }>;
}

import { config } from '../config';

class ApiService {
  private baseUrl: string;
  private sessionId: string;

  constructor() {
    // Use configuration
    this.baseUrl = config.apiUrl;
    this.sessionId = this.generateSessionId();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async translateTerm(request: TranslationRequest): Promise<TranslationResponse> {
    const payload = {
      ...request,
      session_id: request.session_id || this.sessionId,
      user_agent: navigator.userAgent,
    };

    return this.makeRequest<TranslationResponse>('/api/translate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async synthesizeSpeech(request: VoiceSynthesisRequest): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/voice/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Voice synthesis failed: ${response.status} ${response.statusText}`);
    }

    return response.blob();
  }

  async getSessionAnalytics(sessionId: string): Promise<Record<string, unknown>> {
    return this.makeRequest(`/api/analytics/session/${sessionId}`);
  }

  async getDashboardMetrics(): Promise<AnalyticsMetrics> {
    return this.makeRequest<AnalyticsMetrics>('/api/analytics/dashboard');
  }

  async suggestTerms(partialTerm: string, limit: number = 5): Promise<{ suggestions: string[] }> {
    return this.makeRequest<{ suggestions: string[] }>(`/api/terms/suggest/${partialTerm}?limit=${limit}`);
  }

  // WebSocket connection for real-time communication
  createWebSocketConnection(sessionId: string): WebSocket {
    return new WebSocket(`${config.websocketUrl}/ws/${sessionId}`);
  }

  getSessionId(): string {
    return this.sessionId;
  }
}

// Export singleton instance
export const apiService = new ApiService(); 