# Restaurant Agent - Simplified Design

## Overview

This document outlines a streamlined design for an AI-powered restaurant assistant. The system uses a web-based chat interface, an API gateway for security and routing, and LangGraph for agent orchestration. The MCP server using Google Places API is already implemented.

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Web App Client](#web-app-client)
3. [API Gateway](#api-gateway)
4. [LangGraph Agent Design](#langgraph-agent-design)
5. [Configuration](#configuration)
6. [Data Models](#data-models)

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB APP CLIENT                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Chat UI    │  │  Restaurant │  │    User Profile         │ │
│  │  Component  │  │  Cards       │  │    Management           │ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │
└─────────┼────────────────┼─────────────────────┼──────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                              │
│  • Authentication  • Rate Limiting  • Request Validation         │
│  • SSL Termination • Request Routing • Logging                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LANGGRAPH ORCHESTRATION                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Agent State                          │   │
│  │  messages → intent → entities → tools → response         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Router    │→ │   Search    │→ │   Response Generator   │ │
│  │   Agent     │  │   Agent     │  │                         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP CLIENT LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        Google Places MCP Server (Already Implemented)     │   │
│  │  • search_restaurants  • get_restaurant_details           │   │
│  │  • get_reviews         • get_place_details                 │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Web App Client

### 2.1 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 18+ | UI Library |
| Build Tool | Vite | Fast development |
| Styling | Tailwind CSS | Styling |
| State | Zustand | Lightweight state |
| HTTP Client | Axios | API communication |
| Real-time | SSE | Streaming responses |

### 2.2 Project Structure

```
src/
├── components/
│   ├── chat/
│   │   ├── ChatContainer.tsx      # Main chat wrapper
│   │   ├── ChatMessage.tsx        # Individual message
│   │   ├── ChatInput.tsx          # Input area with send
│   │   ├── MessageBubble.tsx      # User/AI message styling
│   │   └── TypingIndicator.tsx    # Loading state
│   ├── restaurant/
│   │   ├── RestaurantCard.tsx    # Restaurant display card
│   │   ├── RestaurantList.tsx     # Grid of results
│   │   └── RestaurantDetail.tsx   # Full details modal
│   └── common/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Modal.tsx
├── hooks/
│   ├── useChat.ts                 # Chat logic hook
│   ├── useChatStream.ts           # SSE streaming hook
│   └── useRestaurantSearch.ts    # Search functionality
├── services/
│   ├── api.ts                     # API client setup
│   └── auth.ts                    # Authentication
├── stores/
│   └── chatStore.ts               # Zustand chat state
├── types/
│   └── index.ts                   # TypeScript types
├── App.tsx
└── main.tsx
```

### 2.3 Chat Features

#### Chat State Management (Zustand)

```typescript
// src/stores/chatStore.ts
import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: ChatAction[];
  restaurants?: Restaurant[];
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  setLoading: (loading: boolean) => void;
  setSessionId: (id: string) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  sessionId: null,

  addMessage: (message) => set((state) => ({
    messages: [...state.messages, {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date()
    }]
  })),

  setLoading: (isLoading) => set({ isLoading }),
  
  setSessionId: (sessionId) => set({ sessionId }),
  
  clearChat: () => set({ messages: [], sessionId: null })
}));
```

#### Chat Hook with Streaming

```typescript
// src/hooks/useChat.ts
import { useCallback, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import { api } from '../services/api';

export function useChat() {
  const { messages, addMessage, setLoading, sessionId, setSessionId } = useChatStore();
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    // Add user message
    addMessage({ role: 'user', content });
    setLoading(true);

    // Create abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      // Use streaming endpoint
      const response = await api.chatStream(
        { message: content, session_id: sessionId },
        abortControllerRef.current.signal
      );

      // Create assistant message placeholder
      const assistantMessageId = crypto.randomUUID();
      addMessage({ 
        role: 'assistant', 
        content: '',  // Will be updated incrementally
        id: assistantMessageId 
      });

      // Handle streaming response
      let fullContent = '';
      let currentSessionId = sessionId;

      for await (const chunk of response) {
        if (chunk.type === 'session_id') {
          currentSessionId = chunk.session_id;
          setSessionId(currentSessionId);
        } else if (chunk.type === 'content') {
          fullContent += chunk.text;
          // Update the message incrementally
          useChatStore.setState((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMessageId
                ? { ...m, content: fullContent }
                : m
            )
          }));
        } else if (chunk.type === 'actions') {
          // Update with restaurant data or actions
          useChatStore.setState((state) => ({
            messages: state.messages.map((m) =>
              m.id === assistantMessageId
                ? { ...m, actions: chunk.actions, restaurants: chunk.restaurants }
                : m
            )
          }));
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        addMessage({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        });
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, addMessage, setLoading, setSessionId]);

  const cancelRequest = useCallback(() => {
    abortControllerRef.current?.abort();
    setLoading(false);
  }, [setLoading]);

  return { messages, sendMessage, cancelRequest, isLoading: useChatStore(s => s.isLoading) };
}
```

#### Streaming Hook (SSE)

```typescript
// src/hooks/useChatStream.ts
import { useCallback, useRef } from 'react';

interface StreamChunk {
  type: 'session_id' | 'content' | 'actions' | 'done' | 'error';
  session_id?: string;
  text?: string;
  actions?: any[];
  restaurants?: any[];
  error?: string;
}

export function useChatStream() {
  const readerRef = useRef<ReadableStreamDefaultReader | null>(null);

  const createStream = useCallback(async (
    body: RequestInit['body'],
    signal: AbortSignal
  ): Promise<AsyncGenerator<StreamChunk>> => {
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body,
      signal
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    readerRef.current = reader;
    const decoder = new TextDecoder();
    let buffer = '';

    async function* generator(): AsyncGenerator<StreamChunk> {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                yield { type: 'done' };
                return;
              }
              try {
                const parsed = JSON.parse(data);
                yield parsed as StreamChunk;
              } catch {
                // Skip invalid JSON
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }
    }

    return generator();
  }, []);

  const cancel = useCallback(() => {
    readerRef.current?.cancel();
  }, []);

  return { createStream, cancel };
}
```

### 2.4 Chat UI Components

#### Chat Container

```tsx
// src/components/chat/ChatContainer.tsx
import React, { useRef, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { TypingIndicator } from './TypingIndicator';

export function ChatContainer() {
  const { messages, sendMessage, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message: string) => {
    if (message.trim()) {
      await sendMessage(message);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      {/* Header */}
      <header className="bg-white border-b p-4 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-800">
          🍽️ Restaurant Assistant
        </h1>
        <p className="text-sm text-gray-500">Find and book the perfect restaurant</p>
      </header>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg">👋 Hello!</p>
            <p className="mt-2">
              I can help you find restaurants, get recommendations, 
              or make reservations. What would you like?
            </p>
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              <button 
                onClick={() => handleSend('Find Italian restaurants near me')}
                className="px-3 py-1 bg-white border rounded-full text-sm hover:bg-gray-100"
              >
                🍝 Find Italian restaurants
              </button>
              <button 
                onClick={() => handleSend('Recommend a romantic restaurant')}
                className="px-3 py-1 bg-white border rounded-full text-sm hover:bg-gray-100"
              >
                💕 Romantic dinner
              </button>
              <button 
                onClick={() => handleSend('Book a table for 4 tonight')}
                className="px-3 py-1 bg-white border rounded-full text-sm hover:bg-gray-100"
              >
                📅 Make a reservation
              </button>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
```

#### Chat Input Component

```tsx
// src/components/chat/ChatInput.tsx
import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border-t p-4">
      <div className="flex gap-2 items-end">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me about restaurants..."
            disabled={disabled}
            className="w-full px-4 py-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            rows={1}
          />
        </div>
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Send
        </button>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
}
```

#### Chat Message with Restaurant Cards

```tsx
// src/components/chat/ChatMessage.tsx
import React from 'react';
import { Message } from '../../types';
import { RestaurantCard } from '../restaurant/RestaurantCard';

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-white border shadow-sm'
        }`}
      >
        {/* Message Content */}
        <div className="whitespace-pre-wrap">{message.content}</div>

        {/* Restaurant Results */}
        {message.restaurants && message.restaurants.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.restaurants.map((restaurant) => (
              <RestaurantCard
                key={restaurant.id}
                restaurant={restaurant}
                compact
              />
            ))}
          </div>
        )}

        {/* Timestamp */}
        <div
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-400'
          }`}
        >
          {message.timestamp.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </div>
      </div>
    </div>
  );
}
```

#### Restaurant Card Component

```tsx
// src/components/restaurant/RestaurantCard.tsx
import React from 'react';
import { Restaurant } from '../../types';

interface RestaurantCardProps {
  restaurant: Restaurant;
  compact?: boolean;
  onSelect?: () => void;
}

export function RestaurantCard({ restaurant, compact, onSelect }: RestaurantCardProps) {
  const priceDisplay = '$'.repeat(restaurant.price_level || 1);
  
  if (compact) {
    return (
      <div 
        className="bg-gray-50 rounded-lg p-3 cursor-pointer hover:bg-gray-100 transition-colors"
        onClick={onSelect}
      >
        <div className="flex gap-3">
          {restaurant.photo_url && (
            <img
              src={restaurant.photo_url}
              alt={restaurant.name}
              className="w-16 h-16 rounded object-cover"
            />
          )}
          <div className="flex-1 min-w-0">
            <h4 className="font-medium text-gray-900 truncate">
              {restaurant.name}
            </h4>
            <p className="text-sm text-gray-600 truncate">
              {restaurant.vicinity || restaurant.formatted_address}
            </p>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-yellow-500">⭐</span>
              <span className="text-sm text-gray-700">
                {restaurant.rating?.toFixed(1) || 'N/A'}
              </span>
              <span className="text-sm text-gray-500">•</span>
              <span className="text-sm text-gray-500">{priceDisplay}</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden hover:shadow-md transition-shadow">
      {restaurant.photo_url && (
        <div className="h-48 overflow-hidden">
          <img
            src={restaurant.photo_url}
            alt={restaurant.name}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      <div className="p-4">
        <div className="flex justify-between items-start">
          <h3 className="font-semibold text-lg text-gray-900">
            {restaurant.name}
          </h3>
          <span className="text-yellow-500 font-medium">
            ⭐ {restaurant.rating?.toFixed(1) || 'N/A'}
          </span>
        </div>
        
        <p className="text-gray-600 mt-1">
          {restaurant.vicinity || restaurant.formatted_address}
        </p>
        
        {restaurant.types && restaurant.types.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {restaurant.types.slice(0, 3).map((type) => (
              <span
                key={type}
                className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full"
              >
                {type.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        )}
        
        <div className="flex justify-between items-center mt-4 pt-3 border-t">
          <span className="font-medium text-gray-700">{priceDisplay}</span>
          <button
            onClick={onSelect}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}
```

### 2.5 API Service

```typescript
// src/services/api.ts
const API_BASE = '/api/v1';

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string) {
    this.token = token;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers
    };

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Chat endpoint (non-streaming)
  async chat(body: { message: string; session_id?: string }) {
    return this.request<{ message: string; session_id: string }>('/chat', {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  // Streaming chat endpoint
  async *chatStream(
    body: { message: string; session_id?: string },
    signal?: AbortSignal
  ): AsyncGenerator<any> {
    const response = await fetch(`${this.baseUrl}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` })
      },
      body: JSON.stringify(body),
      signal
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) throw new Error('No response body');

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            try {
              yield JSON.parse(data);
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // Direct restaurant search
  async searchRestaurants(params: {
    query?: string;
    location?: string;
    cuisine?: string;
    lat?: number;
    lng?: number;
    radius?: number;
  }) {
    const query = new URLSearchParams(params as any).toString();
    return this.request<{ results: any[] }>(`/restaurants/search?${query}`);
  }

  // Get restaurant details
  async getRestaurant(placeId: string) {
    return this.request<any>(`/restaurants/${placeId}`);
  }
}

export const api = new ApiClient(API_BASE);
```

---

## 3. API Gateway

### 3.1 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | Python async web framework |
| Server | Uvicorn | ASGI server |
| Auth | JWT | Token-based authentication |
| Rate Limiting | SlowAPI | Per-user rate limiting |
| CORS | FastAPI CORS | Cross-origin requests |
| Validation | Pydantic | Request/response models |
| Logging | Structlog | Structured logging |

### 3.2 Gateway Implementation

```python
# gateway/main.py
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
from typing import Optional
import structlog
import jwt
from contextlib import asynccontextmanager

from .config import settings
from .routers import chat, restaurants

# Structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("api_gateway_starting", version=settings.version)
    yield
    # Shutdown
    logger.info("api_gateway_shutting_down")

app = FastAPI(
    title="Restaurant Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Security
security = HTTPBearer()

# Dependency: Get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Include routers
app.include_router(
    chat.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    restaurants.router,
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)]
)

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 3.3 Chat Router

```python
# gateway/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional
import json
import uuid

from ..dependencies import get_current_user, get_agent_executor

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Non-streaming chat endpoint."""
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    
    # Process through agent
    agent_executor = await get_agent_executor()
    
    result = await agent_executor.ainvoke({
        "input": request.message,
        "session_id": session_id,
        "user_id": current_user.get("sub")
    })
    
    return ChatResponse(
        message=result.get("output", ""),
        session_id=session_id
    )

@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    agent_executor = Depends(get_agent_executor)
):
    """Streaming chat endpoint using SSE."""
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_generator():
        # Send session ID first
        yield f"data: {json.dumps({'type': 'session_id', 'session_id': session_id})}\n\n"
        
        try:
            async for chunk in agent_executor.astream({
                "input": request.message,
                "session_id": session_id,
                "user_id": current_user.get("sub")
            }):
                # Stream agent output
                if "output" in chunk:
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk['output']})}\n\n"
                
                # Stream any tool results (like restaurants)
                if "tool_outputs" in chunk:
                    for tool_output in chunk["tool_outputs"]:
                        if tool_output.get("tool") == "search_restaurants":
                            yield f"data: {json.dumps({
                                'type': 'actions',
                                'restaurants': tool_output.get("output", [])
                            })}\n\n"
                            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

### 3.4 Restaurant Router

```python
# gateway/routers/restaurants.py
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional, List

from ..dependencies import get_current_user, get_mcp_client

router = APIRouter()

class Restaurant(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    photo_url: Optional[str] = None
    types: List[str] = []

class SearchResponse(BaseModel):
    results: List[Restaurant]
    total: int

@router.get("/restaurants/search", response_model=SearchResponse)
async def search_restaurants(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    radius: int = Query(5000, ge=100, le=50000),
    current_user: dict = Depends(get_current_user)
):
    """Search for restaurants using Google Places MCP."""
    mcp_client = await get_mcp_client()
    
    # Build search params
    params = {
        "query": query or cuisine or "restaurant",
        "location": f"{lat},{lng}" if lat and lng else location,
        "radius": radius
    }
    
    # Call MCP tool
    results = []
    async for chunk in mcp_client.call_tool("search_restaurants", params):
        results.append(chunk)
    
    return SearchResponse(
        results=[Restaurant(**r) for r in results],
        total=len(results)
    )

@router.get("/restaurants/{place_id}")
async def get_restaurant(
    place_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get detailed restaurant information."""
    mcp_client = await get_mcp_client()
    
    result = await mcp_client.call_tool("get_place_details", {
        "place_id": place_id,
        "fields": ["name", "formatted_address", "rating", "price_level", 
                   "photos", "reviews", "opening_hours", "website", "phone"]
    })
    
    return result
```

### 3.5 Dependencies

```python
# gateway/dependencies.py
from fastapi import Request
from typing import Optional
import asyncio

# MCP Client singleton
_mcp_client: Optional["MCPClient"] = None
_agent_executor: Optional["AgentExecutor"] = None

async def get_mcp_client() -> "MCPClient":
    """Get or create MCP client singleton."""
    global _mcp_client
    
    if _mcp_client is None:
        from .mcp import MCPClient
        _mcp_client = MCPClient(
            server_url=settings.mcp_server_url,
            api_key=settings.mcp_api_key
        )
        await _mcp_client.initialize()
    
    return _mcp_client

async def get_agent_executor() -> "AgentExecutor":
    """Get or create agent executor singleton."""
    global _agent_executor
    
    if _agent_executor is None:
        from .agents import create_agent_executor
        _agent_executor = await create_agent_executor()
    
    return _agent_executor
```

---

## 4. LangGraph Agent Design

### 4.1 Architecture Overview

The LangGraph agent orchestration is designed for **easy configuration**. Agents are defined declaratively using configuration files, making it simple to add new capabilities or modify behavior without changing code.

```
┌─────────────────────────────────────────────────────────────────┐
│                      LANGGRAPH AGENT                             │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   START     │───▶│   ROUTER    │───▶│  Tool Executor      │  │
│  └─────────────┘    └─────────────┘    └──────────┬──────────┘  │
│                                                    │             │
│                                    ┌───────────────┼───────────┐ │
│                                    ▼               ▼           ▼ │
│                             ┌──────────┐  ┌──────────┐ ┌──────┐ │
│                             │ Search   │  │  Detail  │ │ More │ │
│                             │ Agent    │  │  Agent   │ │Tools │ │
│                             └─────┬────┘  └─────┬────┘ └──┬───┘ │
│                                   │              │         │    │
│                                   └──────────────┼─────────┘    │
│                                                  ▼              │
│                                        ┌─────────────────────┐   │
│                                        │  Response Generator │   │
│                                        └──────────┬──────────┘   │
│                                                   │              │
│                                                   ▼              │
│                                              ┌─────────┐        │
│                                              │   END    │        │
│                                              └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Agent Configuration (YAML-based)

Agents are configured via YAML files for easy modification:

```yaml
# config/agents.yaml
version: "1.0"

# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4o"
  temperature: 0.7
  max_tokens: 2000

# Agent Behavior
agents:
  # Main router agent
  router:
    description: "Routes user requests to appropriate handlers"
    system_prompt: |
      You are a restaurant assistant router. Analyze the user's message 
      and determine what they want to do:
      - search: Looking for restaurants
      - details: Want specific restaurant info
      - reserve: Want to make a reservation
      - compare: Want to compare restaurants
      - recommend: Want personalized recommendations
      - chat: General conversation
      
      Extract any entities like location, cuisine, date, time, party size.
    
    tools: []  # Router doesn't need tools, uses LLM reasoning

  # Search agent
  search:
    description: "Searches for restaurants using available tools"
    system_prompt: |
      You are a restaurant search specialist. Use the search_restaurants 
      tool to find restaurants matching user preferences. Present results 
      in a clear, helpful format.
    
    tools:
      - search_restaurants
      - get_restaurant_details
    
    # Tool configuration
    tool_config:
      search_restaurants:
        max_results: 10
        default_radius: 5000
        default_cuisine: null
      get_restaurant_details:
        fields:
          - name
          - rating
          - price_level
          - photos
          - reviews

  # Details agent
  details:
    description: "Gets detailed restaurant information"
    system_prompt: |
      You provide detailed information about restaurants including 
      reviews, hours, menu highlights, and more.
    
    tools:
      - get_restaurant_details
      - get_restaurant_reviews

  # Reservation agent
  reservation:
    description: "Helps make restaurant reservations"
    system_prompt: |
      Help users make reservations. Collect: restaurant, date, time, 
      party size, contact info. Confirm all details before booking.
    
    tools:
      - create_reservation
      - check_availability
      - cancel_reservation

# Tool Definitions (connects to MCP)
tools:
  search_restaurants:
    mcp_server: "google_places"
    mcp_tool: "search_restaurants"
    description: "Search for restaurants by query, location, cuisine"
    
  get_restaurant_details:
    mcp_server: "google_places"
    mcp_tool: "get_place_details"
    description: "Get detailed information about a restaurant"
    
  get_restaurant_reviews:
    mcp_server: "google_places"
    mcp_tool: "get_reviews"
    description: "Get reviews for a restaurant"

# Intent Classification
intents:
  search:
    keywords: ["find", "search", "look for", "recommend", "suggest"]
    patterns:
      - "find.*restaurants?"
      - "search for.*(?:italian|mexican|japanese|...)"
      - "best.*(?:near|around|in)"
    
  reserve:
    keywords: ["book", "reserve", "reservation", "table"]
    patterns:
      - "book.*table"
      - "make.*reservation"
      - "reserve.*for.*people"
    
  details:
    keywords: ["details", "info", "information", "hours", "menu"]
    patterns:
      - "what are the hours"
      - "show me the menu"
```

### 4.3 Agent Implementation

```python
# agents/factory.py
from typing import Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel
import yaml
from pathlib import Path

class AgentConfig(BaseModel):
    """Agent configuration model."""
    version: str = "1.0"
    llm: dict
    agents: dict
    tools: dict
    intents: dict
    
    @classmethod
    def load(cls, path: str = "config/agents.yaml") -> "AgentConfig":
        """Load configuration from YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

class AgentFactory:
    """Factory for creating configured agents."""
    
    def __init__(self, config: AgentConfig, mcp_pool: "MCPPool"):
        self.config = config
        self.mcp_pool = mcp_pool
        self._llm: Optional[ChatOpenAI] = None
        self._tools: list = []
        self._agents: dict = {}
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get or create LLM instance."""
        if self._llm is None:
            llm_config = self.config.llm
            self._llm = ChatOpenAI(
                model=llm_config.get("model", "gpt-4o"),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 2000)
            )
        return self._llm
    
    def get_tools(self) -> list:
        """Get or create tools from configuration."""
        if not self._tools:
            for tool_name, tool_config in self.config.tools.items():
                mcp_server = tool_config["mcp_server"]
                mcp_tool = tool_config["mcp_tool"]
                
                # Create tool wrapper for MCP call
                tool = self._create_mcp_tool(tool_name, mcp_server, mcp_tool)
                self._tools.append(tool)
        
        return self._tools
    
    def _create_mcp_tool(self, name: str, server: str, mcp_tool: str):
        """Create a LangChain tool from MCP configuration."""
        from langchain.tools import Tool
        
        async def execute(input_str: str) -> str:
            client = await self.mcp_pool.get_server(server)
            
            # Parse input (JSON string from agent)
            try:
                import json
                params = json.loads(input_str) if input_str else {}
            except json.JSONDecodeError:
                params = {"query": input_str}
            
            # Call MCP tool
            results = []
            async for chunk in client.call_tool(mcp_tool, params):
                results.append(chunk)
            
            return str(results)
        
        return Tool(
            name=name,
            description=self.config.tools[name].get("description", ""),
            func=execute,
            coroutine=execute
        )
    
    def create_agent(self, agent_name: str) -> AgentExecutor:
        """Create a specific agent by name from configuration."""
        if agent_name in self._agents:
            return self._agents[agent_name]
        
        agent_config = self.config.agents.get(agent_name)
        if not agent_config:
            raise ValueError(f"Agent '{agent_name}' not found in config")
        
        # Build prompt
        system_prompt = agent_config.get("system_prompt", "")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Get tools for this agent
        tool_names = agent_config.get("tools", [])
        agent_tools = [t for t in self.get_tools() if t.name in tool_names]
        
        # Create agent
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=agent_tools,
            prompt=prompt
        )
        
        # Create executor
        executor = AgentExecutor(
            agent=agent,
            tools=agent_tools,
            verbose=True,
            max_iterations=agent_config.get("max_iterations", 10),
            handle_parsing_errors=agent_config.get("error_handler", True)
        )
        
        self._agents[agent_name] = executor
        return executor
```

### 4.4 Main Graph Orchestration

```python
# agents/orchestrator.py
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import json

class AgentState(TypedDict):
    """State managed by the main LangGraph orchestration."""
    messages: Annotated[list, add_messages]
    current_agent: str
    session_id: str
    user_id: str
    intent: str
    entities: dict
    tool_outputs: list
    final_response: str

class RestaurantAgentOrchestrator:
    """Main orchestrator for the restaurant agent."""
    
    def __init__(self, factory: "AgentFactory"):
        self.factory = factory
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("classify_intent", self._classify_intent)
        graph.add_node("route_to_agent", self._route_to_agent)
        graph.add_node("execute_agent", self._execute_agent)
        graph.add_node("generate_response", self._generate_response)
        
        # Set entry point
        graph.set_entry_point("classify_intent")
        
        # Add edges
        graph.add_edge("classify_intent", "route_to_agent")
        
        # Conditional routing based on intent
        graph.add_conditional_edges(
            "route_to_agent",
            self._route_by_intent,
            {
                "search": "execute_agent",
                "details": "execute_agent",
                "reserve": "execute_agent",
                "recommend": "execute_agent",
                "chat": "generate_response"  # No tools needed
            }
        )
        
        graph.add_edge("execute_agent", "generate_response")
        graph.add_edge("generate_response", END)
        
        return graph.compile()
    
    async def _classify_intent(self, state: AgentState) -> AgentState:
        """Classify user intent using the router agent."""
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Use router agent to classify
        router = self.factory.create_agent("router")
        result = await router.ainvoke({
            "input": last_message,
            "chat_history": messages[:-1] if len(messages) > 1 else []
        })
        
        # Parse intent from response (simplified - could use structured output)
        intent = self._parse_intent(result.get("output", ""))
        
        # Extract entities
        entities = self._extract_entities(last_message)
        
        return {
            **state,
            "intent": intent,
            "entities": entities,
            "current_agent": intent
        }
    
    def _route_by_intent(self, state: AgentState) -> str:
        """Route to appropriate agent based on intent."""
        intent = state.get("intent", "chat")
        
        # Map intents to agents
        intent_to_agent = {
            "search": "search",
            "details": "details",
            "reserve": "reservation",
            "recommend": "search",  # Use search for recommendations
            "compare": "search"
        }
        
        return intent_to_agent.get(intent, "chat")
    
    async def _route_to_agent(self, state: AgentState) -> AgentState:
        """Prepare state for agent execution."""
        return state
    
    async def _execute_agent(self, state: AgentState) -> AgentState:
        """Execute the appropriate agent with tools."""
        agent_name = state.get("current_agent", "search")
        agent = self.factory.create_agent(agent_name)
        
        messages = state["messages"]
        last_message = messages[-1].content if messages else ""
        
        # Build context for agent
        context = {
            "input": last_message,
            "chat_history": messages[:-1] if len(messages) > 1 else [],
            **state.get("entities", {})
        }
        
        # Execute agent
        result = await agent.ainvoke(context)
        
        return {
            **state,
            "tool_outputs": [result],
            "final_response": result.get("output", "")
        }
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate final response to user."""
        # If we already have a response from agent, use it
        if state.get("final_response"):
            return state
        
        # Otherwise generate from LLM
        messages = state["messages"]
        
        response = await self.factory.llm.ainvoke([
            SystemMessage(content="You are a helpful restaurant assistant. Provide a friendly, concise response."),
            *messages
        ])
        
        return {
            **state,
            "final_response": response.content
        }
    
    def _parse_intent(self, response: str) -> str:
        """Parse intent from router response."""
        response_lower = response.lower()
        
        intents = {
            "search": ["search", "find", "look for", "recommend"],
            "details": ["details", "information", "hours", "menu"],
            "reserve": ["reserve", "book", "reservation"],
            "recommend": ["recommend", "suggestion", "best for"],
            "compare": ["compare", "vs", "versus"]
        }
        
        for intent, keywords in intents.items():
            if any(kw in response_lower for kw in keywords):
                return intent
        
        return "chat"
    
    def _extract_entities(self, text: str) -> dict:
        """Extract entities from user message."""
        # Simplified entity extraction
        # Could use NLP or LLM for better extraction
        entities = {}
        
        # Common patterns
        import re
        
        # Location
        location_match = re.search(r'(?:in|near|around|at)\s+([A-Za-z\s]+?)(?:\s|$|\?)', text)
        if location_match:
            entities["location"] = location_match.group(1).strip()
        
        # Cuisine
        cuisines = ["italian", "mexican", "japanese", "chinese", "indian", 
                    "thai", "french", "american", "korean", "vietnamese"]
        for cuisine in cuisines:
            if cuisine in text.lower():
                entities["cuisine"] = cuisine
                break
        
        # Date
        date_match = re.search(r'(today|tonight|tomorrow|\d{1,2}/\d{1,2}|\w+\s+\d{1,2})', text)
        if date_match:
            entities["date"] = date_match.group(1)
        
        # Time
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2}\s*(?:am|pm))', text, re.IGNORECASE)
        if time_match:
            entities["time"] = time_match.group(1)
        
        # Party size
        party_match = re.search(r'(\d+)\s*(?:people|people|guests)', text)
        if party_match:
            entities["party_size"] = int(party_match.group(1))
        
        return entities
    
    async def ainvoke(self, input: str, session_id: str, user_id: str) -> dict:
        """Invoke the agent orchestrator."""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=input)],
            "current_agent": "router",
            "session_id": session_id,
            "user_id": user_id,
            "intent": "",
            "entities": {},
            "tool_outputs": [],
            "final_response": ""
        }
        
        result = await self.graph.ainvoke(initial_state)
        
        return {
            "output": result.get("final_response", ""),
            "intent": result.get("intent", ""),
            "entities": result.get("entities", {}),
            "tool_outputs": result.get("tool_outputs", [])
        }
    
    async def astream(self, input: str, session_id: str, user_id: str):
        """Stream agent execution for SSE."""
        initial_state: AgentState = {
            "messages": [HumanMessage(content=input)],
            "current_agent": "router",
            "session_id": session_id,
            "user_id": user_id,
            "intent": "",
            "entities": {},
            "tool_outputs": [],
            "final_response": ""
        }
        
        async for chunk in self.graph.astream(initial_state):
            yield chunk
```

### 4.5 Easy Agent Configuration Example

Adding a new agent is as simple as updating the YAML config:

```yaml
# Example: Adding a new "Reviews" agent

agents:
  reviews:
    description: "Analyzes restaurant reviews and sentiments"
    system_prompt: |
      You are a restaurant review analyst. Help users understand 
      what others are saying about restaurants.
    
    tools:
      - get_restaurant_reviews
      - analyze_sentiment
    
    tool_config:
      get_restaurant_reviews:
        max_reviews: 20
        sort_by: "most_relevant"
    
    max_iterations: 5
    error_handler: "Could not fetch reviews. Please try again."

# Add new tool connection
tools:
  analyze_sentiment:
    mcp_server: "sentiment_service"  # New MCP server
    mcp_tool: "analyze"
    description: "Analyze sentiment of review text"
```

---

## 5. Configuration

### 5.1 Environment Variables

```bash
# .env

# API Gateway
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# LLM
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# MCP Server (Google Places - already implemented)
MCP_SERVER_URL=http://localhost:8001
MCP_API_KEY=your-mcp-api-key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5.2 Settings

```python
# gateway/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    version: str = "1.0.0"
    
    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    
    # LLM
    openai_api_key: str
    
    # MCP
    mcp_server_url: str
    mcp_api_key: str
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 6. Data Models

### 6.1 Core Types

```typescript
// src/types/index.ts

export interface Restaurant {
  id: string;
  name: string;
  address?: string;
  vicinity?: string;
  formatted_address?: string;
  rating?: number;
  price_level?: number;  // 1-4 ($ to $$$$)
  photo_url?: string;
  types?: string[];
  opening_hours?: OpeningHours;
  website?: string;
  phone?: string;
}

export interface OpeningHours {
  weekday_text?: string[];
  open_now?: boolean;
}

export interface Review {
  id: string;
  author_name: string;
  rating: number;
  text: string;
  time: number;
  relative_time_description?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  actions?: ChatAction[];
  restaurants?: Restaurant[];
}

export interface ChatAction {
  type: 'search' | 'reserve' | 'details' | 'recommend';
  params?: Record<string, any>;
  status: 'pending' | 'success' | 'error';
  result?: any;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}

export interface SearchParams {
  query?: string;
  location?: string;
  cuisine?: string;
  lat?: number;
  lng?: number;
  radius?: number;
  limit?: number;
}
```

### 6.2 Python Models

```python
# gateway/models.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class RestaurantSearchQuery(BaseModel):
    """Restaurant search query."""
    query: Optional[str] = None
    location: Optional[str] = None
    cuisine: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius: int = Field(5000, ge=100, le=50000)
    limit: int = Field(10, ge=1, le=50)

class RestaurantResponse(BaseModel):
    """Restaurant response model."""
    id: str
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    photo_url: Optional[str] = None
    types: List[str] = []

class SearchResponse(BaseModel):
    """Search response."""
    results: List[RestaurantResponse]
    total: int
    query: RestaurantSearchQuery

class ChatRequest(BaseModel):
    """Chat request."""
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response."""
    message: str
    session_id: str
    intent: Optional[str] = None
```

---

## Summary

This simplified design provides:

1. **Web App Client**: A React-based chat application with streaming support, restaurant cards, and intuitive UI
2. **API Gateway**: FastAPI-based gateway with JWT authentication, rate limiting, and proper routing
3. **LangGraph Agents**: Declarative YAML-based configuration for easy agent creation and modification
4. **MCP Integration**: Ready to connect to the existing Google Places MCP server

The design is modular and allows for easy extension of capabilities without major code changes.
