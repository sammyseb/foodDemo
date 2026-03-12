export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'Restaurant Agent';
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '1.0.0';

export const API_ENDPOINTS = {
  AUTH_LOGIN: '/auth/login',
  AUTH_LOGOUT: '/auth/logout',
  CHAT: '/chat',
  CHAT_STREAM: '/chat/stream',
  HEALTH: '/health',
} as const;

export const SSE_EVENT_TYPES = {
  START: 'start',
  CONTENT: 'content',
  TOOL_CALL: 'tool_call',
  TOOL_RESULT: 'tool_result',
  ERROR: 'error',
  END: 'end',
} as const;

export const CHAT_SUGGESTIONS = [
  'Find Italian restaurants in San Francisco',
  'What are the best sushi places near me?',
  'Show me Thai restaurants with outdoor seating',
  'Find romantic dinner spots in downtown',
  'What are good vegan restaurants?',
] as const;
