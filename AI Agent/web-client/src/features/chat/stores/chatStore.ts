import type { ChatMessage } from '@/shared/types';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ChatState {
  messages: ChatMessage[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;
  
  // Actions
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<ChatMessage>) => void;
  setLoading: (loading: boolean) => void;
  setSessionId: (id: string | null) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [],
      isLoading: false,
      sessionId: null,
      error: null,
      
      addMessage: (message) => set((state) => ({
        messages: [...state.messages, {
          ...message,
          id: crypto.randomUUID(),
          timestamp: new Date()
        }]
      })),
      
      updateLastMessage: (updates) => set((state) => ({
        messages: state.messages.map((m, i) => 
          i === state.messages.length - 1 ? { ...m, ...updates } : m
        )
      })),
      
      setLoading: (isLoading) => set({ isLoading }),
      setSessionId: (sessionId) => set({ sessionId }),
      setError: (error) => set({ error }),
      
      clearChat: () => set({ 
        messages: [], 
        isLoading: false, 
        error: null 
      })
    }),
    {
      name: 'chat-storage',
      partialize: (state) => ({ 
        sessionId: state.sessionId 
      })
    }
  )
);
