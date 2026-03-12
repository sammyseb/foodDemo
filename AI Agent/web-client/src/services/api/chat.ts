import { API_ENDPOINTS, API_URL } from '@/config';
import type { ChatRequest, ChatResponse } from '@/shared/types';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}${API_ENDPOINTS.CHAT}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  return response.json();
}

export type StreamCallback = (data: { type: string; content?: string; session_id?: string }) => void;

export async function streamChatMessage(
  request: ChatRequest,
  onChunk: StreamCallback,
  onError: (error: Error) => void
): Promise<string> {
  const response = await fetch(`${API_URL}${API_ENDPOINTS.CHAT_STREAM}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error('Failed to stream message');
  }

  if (!response.body) {
    throw new Error('Response body is null');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let sessionId = '';

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n').filter((line) => line.startsWith('data: '));

      for (const line of lines) {
        const data = line.slice(6);
        try {
          const parsed = JSON.parse(data);
          onChunk(parsed);
          if (parsed.session_id) {
            sessionId = parsed.session_id;
          }
        } catch {
          // Skip invalid JSON
        }
      }
    }
  } catch (error) {
    onError(error instanceof Error ? error : new Error('Stream error'));
  }

  return sessionId;
}
