// Babelfish Enterprise AI Frontend Configuration
export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  websocketUrl: (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace('http', 'ws'),
  features: {
    realTimeTranslation: true,
    voiceSynthesis: true,
    analytics: true,
    termSuggestions: true,
  },
  fallback: {
    enableLocalTranslation: true,
    enableMockData: true,
  }
}; 