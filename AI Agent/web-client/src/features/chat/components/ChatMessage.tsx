import type { ChatMessage as ChatMessageType } from '@/shared/types';
import { cn, formatTime } from '@/shared/utils';
import { Bot, User } from 'lucide-react';

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div
      className={cn(
        'flex gap-3',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary-100' : 'bg-gray-100'
        )}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary-600" />
        ) : (
          <Bot className="w-5 h-5 text-gray-600" />
        )}
      </div>

      {/* Content */}
      <div
        className={cn(
          'flex flex-col max-w-[70%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        <div
          className={cn(
            'px-4 py-2 rounded-2xl',
            isUser
              ? 'bg-primary-600 text-white rounded-br-md'
              : 'bg-white border border-gray-200 rounded-bl-md'
          )}
        >
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        </div>
        
        <span className="text-xs text-gray-400 mt-1">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
