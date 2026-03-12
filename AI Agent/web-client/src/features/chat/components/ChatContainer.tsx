import { Spinner } from '@/shared/components';
import { cn } from '@/shared/utils';
import { useEffect, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';

interface ChatContainerProps {
  className?: string;
}

export function ChatContainer({ className }: ChatContainerProps) {
  const { messages, isLoading, clearChat } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className={cn('flex flex-col h-full bg-gray-50', className)}>
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Restaurant Assistant</h2>
        <button
          onClick={clearChat}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Clear chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <p className="text-gray-500 mb-2">Ask me about restaurants!</p>
            <p className="text-sm text-gray-400">
              Try: "Find Italian restaurants in San Francisco"
            </p>
          </div>
        )}
        
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-500">
            <Spinner size="sm" />
            <span className="text-sm">Thinking...</span>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput />
    </div>
  );
}
