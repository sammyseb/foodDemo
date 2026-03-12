import { streamChatMessage } from '@/services/api/chat';
import { Button } from '@/shared/components';
import { Send } from 'lucide-react';
import React, { useRef, useState } from 'react';
import { useChatStore } from '../stores/chatStore';

export function ChatInput() {
  const [input, setInput] = useState('');
  const { addMessage, setLoading, setSessionId, sessionId } = useChatStore();
  const abortControllerRef = useRef<AbortController | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || useChatStore.getState().isLoading) return;

    const userMessage = input.trim();
    setInput('');
    
    // Add user message
    addMessage({
      role: 'user',
      content: userMessage,
    });

    // Add empty assistant message for streaming
    addMessage({
      role: 'assistant',
      content: '',
    });

    setLoading(true);

    try {
      await streamChatMessage(
        { message: userMessage, session_id: sessionId || undefined },
        (data) => {
          if (data.type === 'content') {
            const messages = useChatStore.getState().messages;
            const lastMessage = messages[messages.length - 1];
            useChatStore.setState({
              messages: messages.map((m, i) =>
                i === messages.length - 1
                  ? { ...m, content: m.content + (data.content || '') }
                  : m
              ),
            });
          } else if (data.type === 'start' && data.session_id) {
            setSessionId(data.session_id);
          }
        },
        (error) => {
          console.error('Stream error:', error);
          useChatStore.setState({ error: error.message });
        }
      );
    } catch (error) {
      console.error('Chat error:', error);
      useChatStore.setState({
        error: error instanceof Error ? error.message : 'Failed to send message',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about restaurants..."
          className="flex-1 px-4 py-3 rounded-xl border border-gray-300 focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-colors"
          disabled={useChatStore.getState().isLoading}
        />
        <Button
          type="submit"
          disabled={!input.trim() || useChatStore.getState().isLoading}
          className="px-4"
        >
          <Send className="w-5 h-5" />
        </Button>
      </div>
    </form>
  );
}
