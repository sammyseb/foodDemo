# Restaurant Agent Web Client - Architecture

## Table of Contents

1. [Overview](#overview)
2. [Architecture Pattern](#architecture-pattern)
3. [Project Structure](#project-structure)
4. [Component Architecture](#component-architecture)
5. [State Management](#state-management)
6. [API Layer](#api-layer)
7. [Data Flow](#data-flow)
8. [Security](#security)
9. [Performance](#performance)
10. [Accessibility](#accessibility)

---

## 1. Overview

The Restaurant Agent Web Client is a React-based chat application that provides users with an intuitive interface to interact with the AI-powered restaurant assistant. The client communicates with the backend API Gateway using REST and Server-Sent Events (SSE) for real-time streaming responses.

### 1.1 Core Features

- **Natural Language Chat**: Users can ask questions about restaurants in plain language
- **Real-time Streaming**: Responses stream in as they're generated for a smooth UX
- **Restaurant Discovery**: Search and view restaurant details with photos, ratings, and reviews
- **Conversational Context**: Maintains chat history within a session for contextual responses
- **Responsive Design**: Works on desktop and mobile devices

### 1.2 Tech Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Framework | React | 18.x | UI Library |
| Build Tool | Vite | 5.x | Development & Build |
| Language | TypeScript | 5.x | Type Safety |
| Styling | Tailwind CSS | 3.x | Utility-first CSS |
| State | Zustand | 4.x | Lightweight state management |
| HTTP | Axios | 1.x | API client |
| Routing | React Router | 6.x | Client-side routing |
| Icons | Lucide React | Latest | Icon library |
| Forms | React Hook Form | 7.x | Form handling |
| Testing | Vitest | 1.x | Unit testing |
| E2E | Playwright | 1.x | End-to-end testing |

---

## 2. Architecture Pattern

### 2.1 Design Philosophy

We use a **Feature-Based Architecture** with Clean Architecture principles:

```
┌─────────────────────────────────────────────────────────────────┐
│                         PAGES/Layouts                            │
│  (Route components, Layouts)                                    │
├─────────────────────────────────────────────────────────────────┤
│                         FEATURES                                 │
│  (Business logic, Components, Hooks)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │    Chat     │  │  Restaurant │  │      Auth              │ │
│  │  Feature    │  │   Feature   │  │     Feature            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      SHARED LAYER                                │
│  (Components, Hooks, Utils, Types)                              │
├─────────────────────────────────────────────────────────────────┤
│                       SERVICES                                   │
│  (API Client, Auth Service)                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Why This Architecture?

| Benefit | Description |
|---------|-------------|
| **Scalability** | Features are self-contained modules that can grow independently |
| **Maintainability** | Clear separation makes code easier to understand and modify |
| **Testability** | Features can be tested in isolation |
| **Team Collaboration** | Different teams can work on different features |
| **Reusability** | Shared components and hooks are easily reused across features |
| **Ease of Implementation** | Simple folder structure, minimal boilerplate |

### 2.3 Component Hierarchy

```
App
├── AuthProvider (Context)
│   └── Router
│       ├── Layout
│       │   ├── Header
│       │   ├── Sidebar (optional)
│       │   └── Outlet
│       │       ├── HomePage
│       │       │   └── ChatFeature
│       │       │       ├── ChatContainer
│       │       │       ├── ChatMessage
│       │       │       ├── ChatInput
│       │       │       └── RestaurantCard
│       │       ├── SearchPage
│       │       │   └── SearchFeature
│       │       ├── RestaurantDetailPage
│       │       │   └── RestaurantDetail
│       │       ├── ProfilePage
│       │       └── SettingsPage
```

---

## 3. Project Structure

```
web-client/
├── public/
│   └── favicon.svg
├── src/
│   ├── features/
│   │   ├── chat/
│   │   │   ├── components/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatInput.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── TypingIndicator.tsx
│   │   │   │   ├── SuggestionChips.tsx
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useChat.ts
│   │   │   │   ├── useChatStream.ts
│   │   │   │   └── index.ts
│   │   │   ├── stores/
│   │   │   │   └── chatStore.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── restaurant/
│   │   │   ├── components/
│   │   │   │   ├── RestaurantCard.tsx
│   │   │   │   ├── RestaurantList.tsx
│   │   │   │   ├── RestaurantDetail.tsx
│   │   │   │   ├── RestaurantFilters.tsx
│   │   │   │   ├── RestaurantMap.tsx (optional)
│   │   │   │   └── index.ts
│   │   │   ├── hooks/
│   │   │   │   ├── useRestaurantSearch.ts
│   │   │   │   ├── useRestaurantDetail.ts
│   │   │   │   └── index.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   └── auth/
│   │       ├── components/
│   │       │   ├── LoginForm.tsx
│   │       │   ├── RegisterForm.tsx
│   │       │   └── index.ts
│   │       ├── hooks/
│   │       │   ├── useAuth.ts
│   │       │   └── index.ts
│   │       ├── stores/
│   │       │   └── authStore.ts
│   │       ├── types/
│   │       │   └── index.ts
│   │       └── index.ts
│   ├── shared/
│   │   ├── components/
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   │   ├── Input.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Modal/
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Spinner/
│   │   │   │   ├── Spinner.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Card/
│   │   │   │   ├── Card.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Toast/
│   │   │   │   ├── Toast.tsx
│   │   │   │   ├── ToastContainer.tsx
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   ├── hooks/
│   │   │   ├── useDebounce.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   ├── useMediaQuery.ts
│   │   │   └── index.ts
│   │   ├── utils/
│   │   │   ├── formatDate.ts
│   │   │   ├── formatCurrency.ts
│   │   │   ├── validation.ts
│   │   │   └── index.ts
│   │   ├── types/
│   │   │   ├── api.ts
│   │   │   └── common.ts
│   │   └── index.ts
│   ├── services/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── chat.ts
│   │   │   ├── restaurants.ts
│   │   │   ├── auth.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── config/
│   │   ├── constants.ts
│   │   ├── environment.ts
│   │   └── index.ts
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── SearchPage.tsx
│   │   ├── RestaurantDetailPage.tsx
│   │   ├── ProfilePage.tsx
│   │   ├── LoginPage.tsx
│   │   ├── RegisterPage.tsx
│   │   └── NotFoundPage.tsx
│   ├── layouts/
│   │   ├── MainLayout.tsx
│   │   ├── AuthLayout.tsx
│   │   └── index.ts
│   ├── context/
│   │   ├── AuthContext.tsx
│   │   ├── ToastContext.tsx
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── .env.example
├── .gitignore
├── index.html
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.ts
```

### 3.1 Feature Folder Pattern

Each feature follows the same pattern:

```
feature-name/
├── components/     # Feature-specific UI components
├── hooks/          # Feature-specific hooks
├── stores/         # Feature-specific state (if needed)
├── types/          # Feature-specific types
├── services/       # Feature-specific services (if needed)
├── utils/         # Feature-specific utilities (if needed)
└── index.ts       # Public API exports
```

---

## 4. Component Architecture

### 4.1 Chat Feature Components

```
ChatFeature
├── ChatContainer (Main)
│   ├── ChatHeader
│   ├── MessageList
│   │   ├── ChatMessage × N
│   │   │   ├── MessageBubble
│   │   │   └── RestaurantCards (optional)
│   │   └── TypingIndicator (conditional)
│   ├── ChatInput
│   │   ├── Textarea
│   │   ├── SendButton
│   │   └── VoiceButton (optional)
│   └── SuggestionChips (conditional)
└── useChat Hook
    ├── State: messages, isLoading, sessionId
    └── Actions: sendMessage, cancelRequest, clearChat
```

### 4.2 Component Specifications

#### ChatContainer

```typescript
// features/chat/components/ChatContainer.tsx
interface ChatContainerProps {
  className?: string;
  initialMessage?: string;
  onRestaurantSelect?: (restaurant: Restaurant) => void;
}

// Responsibilities:
// - Manages chat message list
// - Handles scrolling to bottom
// - Renders chat header and input
// - Manages loading states
// - Displays restaurant cards when received

// Props:
// - className: Additional CSS classes
// - initialMessage: Optional welcome message
// - onRestaurantSelect: Callback when user selects a restaurant
```

#### ChatMessage

```typescript
// features/chat/components/ChatMessage.tsx
interface ChatMessageProps {
  message: Message;
  onRestaurantClick?: (restaurant: Restaurant) => void;
  onActionClick?: (action: ChatAction) => void;
}

// Responsibilities:
// - Renders single message (user or AI)
// - Displays restaurant cards if present
// - Shows timestamp
// - Handles interactive elements
```

#### RestaurantCard

```typescript
// features/restaurant/components/RestaurantCard.tsx
interface RestaurantCardProps {
  restaurant: Restaurant;
  variant?: 'compact' | 'default' | 'detailed';
  onSelect?: () => void;
  onReserve?: () => void;
}

// Variants:
// - compact: Used in chat messages (smaller, horizontal layout)
// - default: Used in search results (standard card)
// - detailed: Used in detail page (full information)
```

### 4.3 Shared Components Library

| Component | Description | Props |
|-----------|-------------|-------|
| Button | Primary, secondary, ghost variants | variant, size, disabled, loading |
| Input | Text input with label and error | label, error, type, placeholder |
| Textarea | Multi-line input | rows, maxLength, resize |
| Modal | Overlay dialog | isOpen, onClose, title, size |
| Spinner | Loading indicator | size, color |
| Toast | Notification popups | type, message, duration |
| Card | Content container | padding, hover, clickable |
| Avatar | User/profile image | src, size, fallback |
| Badge | Status/count indicator | variant, count |
| Dropdown | Selection menu | options, onSelect, multiple |

---

## 5. State Management

### 5.1 Zustand Stores

We use Zustand for its simplicity and minimal boilerplate. Each feature has its own store.

#### Chat Store

```typescript
// features/chat/stores/chatStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  restaurants?: Restaurant[];
  actions?: ChatAction[];
  isLoading?: boolean;
}

interface ChatState {
  // State
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;
  
  // Computed
  lastMessage: Message | null;
  hasMessages: boolean;
  
  // Actions
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  setLoading: (loading: boolean) => void;
  setSessionId: (id: string) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      // Initial state
      messages: [],
      isLoading: false,
      sessionId: null,
      error: null,
      
      // Computed (getters)
      get lastMessage() {
        const { messages } = get();
        return messages[messages.length - 1] || null;
      },
      get hasMessages() {
        return get().messages.length > 0;
      },
      
      // Actions
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
        // Only persist session, not messages
        sessionId: state.sessionId 
      })
    }
  )
);
```

#### Auth Store

```typescript
// features/auth/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

interface AuthState {
  // State
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      
      login: (user, token) => set({ 
        user, 
        token, 
        isAuthenticated: true 
      }),
      
      logout: () => set({ 
        user: null, 
        token: null, 
        isAuthenticated: false 
      }),
      
      setLoading: (isLoading) => set({ isLoading })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token,
        user: state.user 
      })
    }
  )
);
```

### 5.2 State Flow Diagram

```
User Input
    │
    ▼
┌─────────────────┐
│  ChatInput      │
└────────┬────────┘
         │ onSubmit
         ▼
┌─────────────────┐     ┌─────────────────┐
│  useChat Hook  │────▶│  Chat Store     │
└────────┬────────┘     └────────┬────────┘
         │                      │
         │ addMessage           │
         │                      ▼
         │              ┌─────────────────┐
         │              │  React State    │
         │              │  (re-render)    │
         │              └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  API Service    │     │  ChatContainer  │
└────────┬────────┘     └─────────────────┘
         │
         │ POST /chat/stream
         ▼
┌─────────────────┐
│  API Gateway    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph      │
│  Agents         │
└─────────────────┘
```

---

## 6. API Layer

### 6.1 API Client Architecture

```
services/api/
├── client.ts        # Axios instance with interceptors
├── chat.ts         # Chat endpoints
├── restaurants.ts  # Restaurant endpoints
├── auth.ts         # Authentication endpoints
└── index.ts       # Re-exports
```

### 6.2 Axios Client

```typescript
// services/api/client.ts
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../../features/auth/stores/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Handle 401 - Unauthorized
    if (error.response?.status === 401 && originalRequest) {
      // Could implement token refresh here
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);
```

### 6.3 Chat Service

```typescript
// services/api/chat.ts
import { apiClient } from './client';
import { StreamChunk } from '../../features/chat/types';

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

export const chatService = {
  /**
   * Send a chat message and get a non-streaming response
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const { data } = await apiClient.post<ChatResponse>('/chat', request);
    return data;
  },

  /**
   * Send a chat message and get a streaming response via SSE
   * Returns an async generator for streaming
   */
  async *streamMessage(
    request: ChatRequest,
    signal?: AbortSignal
  ): AsyncGenerator<StreamChunk> {
    const response = await fetch(`${apiClient.defaults.baseURL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${useAuthStore.getState().token}`,
      },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
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
              yield JSON.parse(data) as StreamChunk;
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};
```

### 6.4 Restaurant Service

```typescript
// services/api/restaurants.ts
import { apiClient } from './client';
import { Restaurant, SearchParams } from '../../features/restaurant/types';

export const restaurantService = {
  /**
   * Search for restaurants
   */
  async search(params: SearchParams) {
    const { data } = await apiClient.get<{ results: Restaurant[]; total: number }>(
      '/restaurants/search',
      { params }
    );
    return data;
  },

  /**
   * Get restaurant details by place ID
   */
  async getById(placeId: string) {
    const { data } = await apiClient.get<Restaurant>(`/restaurants/${placeId}`);
    return data;
  },

  /**
   * Get restaurant reviews
   */
  async getReviews(placeId: string, limit = 20) {
    const { data } = await apiClient.get<{ reviews: Review[] }>(
      `/restaurants/${placeId}/reviews`,
      { params: { limit } }
    );
    return data;
  },
};
```

---

## 7. Data Flow

### 7.1 Chat Flow

```
1. User types message in ChatInput
                    │
                    ▼
2. onSubmit calls useChat().sendMessage()
                    │
                    ▼
3. addMessage() adds user message to store
                    │
                    ▼
4. State updates, ChatContainer re-renders
                    │
                    ▼
5. useChat calls chatService.streamMessage()
                    │
                    ├──────────────────────┐
                    │                      │
                    ▼                      ▼
6. Server responds     6. Process stream chunks
   with session_id       │
                         ▼
                    7. Handle each chunk type:
                       - session_id: Update session
                       - content: Update message
                       - actions: Show restaurants
                       - error: Show error
                    │
                    ▼
8. Message appears in chat
                    │
                    ▼
9. Auto-scroll to bottom
```

### 7.2 Stream Chunk Types

```typescript
// features/chat/types/index.ts
export type StreamChunkType = 
  | 'session_id' 
  | 'content' 
  | 'actions' 
  | 'done' 
  | 'error';

export interface StreamChunk {
  type: StreamChunkType;
  session_id?: string;
  text?: string;
  actions?: ChatAction[];
  restaurants?: Restaurant[];
  error?: string;
}
```

---

## 8. Security

### 8.1 Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────▶│   API       │────▶│   JWT       │
│   Page      │     │   Gateway   │     │   Token     │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Store     │◀────│  Auth       │◀────│  Local      │
│   User      │     │  Context    │     │  Storage    │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 8.2 Security Measures

| Measure | Implementation |
|---------|---------------|
| **HTTPS** | Enforced in production |
| **JWT Tokens** | Short-lived access tokens |
| **Token Storage** | httpOnly cookies preferred, localStorage as fallback |
| **XSS Prevention** | React's built-in escaping, Content Security Policy |
| **CSRF Protection** | Same-origin requests, CSRF tokens |
| **Rate Limiting** | Handled by API Gateway |
| **Input Validation** | Client and server-side validation |

### 8.3 Content Security Policy

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  font-src 'self';
">
```

---

## 9. Performance

### 9.1 Optimization Strategies

| Optimization | Technique |
|--------------|-----------|
| **Code Splitting** | React.lazy() for routes |
| **Bundle Size** | Tree shaking, dynamic imports |
| **Image Optimization** | Lazy loading, appropriate formats |
| **API Caching** | React Query for server state |
| **Memoization** | useMemo, useCallback for expensive ops |
| **Virtualization** | react-window for long lists |

### 9.2 Lazy Loading Routes

```typescript
// App.tsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Spinner } from './shared/components';

const HomePage = lazy(() => import('./pages/HomePage'));
const SearchPage = lazy(() => import('./pages/SearchPage'));
const RestaurantDetailPage = lazy(() => import('./pages/RestaurantDetailPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/restaurant/:id" element={<RestaurantDetailPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>
    </Suspense>
  );
}
```

### 9.3 Virtualization for Long Lists

```typescript
// For restaurant lists with many results
import { FixedSizeGrid } from 'react-window';

function RestaurantList({ restaurants }) {
  return (
    <FixedSizeGrid
      columnCount={2}
      rowCount={Math.ceil(restaurants.length / 2)}
      columnWidth={300}
      rowHeight={350}
      width={800}
      height={600}
    >
      {({ columnIndex, rowIndex, style }) => {
        const index = rowIndex * 2 + columnIndex;
        const restaurant = restaurants[index];
        if (!restaurant) return null;
        return (
          <div style={style}>
            <RestaurantCard restaurant={restaurant} />
          </div>
        );
      }}
    </FixedSizeGrid>
  );
}
```

---

## 10. Accessibility

### 10.1 WCAG 2.1 AA Compliance

| Requirement | Implementation |
|-------------|---------------|
| **Keyboard Navigation** | All interactive elements focusable |
| **Screen Reader Support** | ARIA labels, roles |
| **Color Contrast** | 4.5:1 minimum ratio |
| **Focus Indicators** | Visible focus rings |
| **Error Messages** | Associated with form fields |
| **Touch Targets** | Minimum 44×44px |

### 10.2 ARIA Example

```tsx
// ChatInput.tsx
<form
  onSubmit={handleSubmit}
  aria-label="Chat message form"
>
  <label htmlFor="chat-input" className="sr-only">
    Type your message
  </label>
  <textarea
    id="chat-input"
    ref={textareaRef}
    value={message}
    onChange={(e) => setMessage(e.target.value)}
    placeholder="Ask about restaurants..."
    aria-describedby="input-hint"
    aria-invalid={!!error}
    rows={1}
  />
  <span id="input-hint" className="sr-only">
    Press Enter to send, Shift+Enter for new line
  </span>
  <button
    type="submit"
    aria-label="Send message"
    disabled={!message.trim() || isLoading}
  >
    <SendIcon />
  </button>
</form>
```

### 10.3 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Enter | Send message |
| Shift+Enter | New line |
| Escape | Close modal/cancel |
| / | Focus search (in chat) |

---

## Appendix: File Summary

| File | Purpose |
|------|---------|
| `src/App.tsx` | Main app component with routing |
| `src/main.tsx` | Entry point |
| `src/features/chat/` | Chat feature module |
| `src/features/restaurant/` | Restaurant feature module |
| `src/features/auth/` | Authentication module |
| `src/shared/components/` | Reusable UI components |
| `src/services/api/` | API client layer |
| `src/config/` | Configuration |
| `src/pages/` | Page components |
| `src/layouts/` | Layout components |
| `src/context/` | React contexts |

---

## Next Steps

- See [Implementation Plan](./Implementation-Plan.md) for detailed step-by-step guide
- Review API contracts in [API Documentation](../api-gateway/README.md)
- Set up development environment following [Setup Guide](./SETUP.md)
