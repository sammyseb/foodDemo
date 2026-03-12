import { ChatContainer } from '@/features/chat/components';

export function HomePage() {
  return (
    <div className="h-[calc(100vh-3.5rem)]">
      <ChatContainer className="h-full" />
    </div>
  );
}
