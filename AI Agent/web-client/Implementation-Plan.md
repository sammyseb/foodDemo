# Restaurant Agent Web Client - Implementation Plan

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Project Setup](#phase-1-project-setup)
4. [Phase 2: Shared Components](#phase-2-shared-components)
5. [Phase 3: Services & API Layer](#phase-3-services--api-layer)
6. [Phase 4: Authentication](#phase-4-authentication)
7. [Phase 5: Chat Feature](#phase-5-chat-feature)
8. [Phase 6: Restaurant Feature](#phase-6-restaurant-feature)
9. [Phase 7: Pages & Routing](#phase-7-pages--routing)
10. [Phase 8: Testing](#phase-8-testing)
11. [Phase 9: Production](#phase-9-production)
12. [Checklist](#checklist)

---

## 1. Overview

This implementation plan provides a step-by-step guide to building the Restaurant Agent Web Client. The plan is organized into phases, each building upon the previous one.

**Estimated Total Time**: 3-4 weeks
**Difficulty**: Intermediate

### 1.1 Implementation Order

```
Phase 1: Project Setup
    │
    ▼
Phase 2: Shared Components
    │
    ▼
Phase 3: Services & API Layer
    │
    ▼
Phase 4: Authentication
    │
    ▼
Phase 5: Chat Feature
    │
    ▼
Phase 6: Restaurant Feature
    │
    ▼
Phase 7: Pages & Routing
    │
    ▼
Phase 8: Testing
    │
    ▼
Phase 9: Production
```

---

## 2. Prerequisites

### 2.1 Required Tools

```bash
# Node.js (v18+)
node --version  # Should show v18.x or higher

# npm (comes with Node.js)
npm --version

# Git
git --version

# VS Code (recommended)
code --version
```

### 2.2 Required Accounts/Access

- [ ] API Gateway running locally (http://localhost:8000)
- [ ] OpenAI API key (for backend)
- [ ] Google Places API key (for MCP server)

### 2.3 Knowledge Requirements

- React 18+ fundamentals
- TypeScript basics
- Zustand state management
- Tailwind CSS
- REST APIs & SSE

---

## 3. Phase 1: Project Setup

**Duration**: 1-2 hours
**Goals**: Initialize project with Vite, configure tooling

### 3.1 Initialize Project

```bash
# Create new Vite project
cd web-client
npm create vite@latest . -- --template react-ts

# Install dependencies
npm install

# Install additional dependencies
npm install react-router-dom zustand axios lucide-react clsx tailwind-merge
npm install -D tailwindcss postcss autoprefixer
```

### 3.2 Configure Tailwind CSS

```bash
# Initialize Tailwind
npx tailwindcss init -p
```

Update `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounce-subtle 1s infinite',
      },
    },
  },
  plugins: [],
}
```

Update `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer utilities {
  .scrollbar-hide {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
  .scrollbar-hide::-webkit-scrollbar {
    display: none;
  }
}
```

### 3.3 Configure TypeScript

Update `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@features/*": ["./src/features/*"],
      "@shared/*": ["./src/shared/*"],
      "@services/*": ["./src/services/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@features': path.resolve(__dirname, './src/features'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@services': path.resolve(__dirname, './src/services'),
    },
  },
});
```

### 3.4 Create Environment File

Create `.env`:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1

# App Configuration
VITE_APP_NAME=Restaurant Agent
VITE_APP_VERSION=1.0.0
```

### 3.5 Verify Setup

```bash
npm run dev
```

Should see:
```
VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 4. Phase 2: Shared Components

**Duration**: 2-3 hours
**Goals**: Build reusable UI components library

### 4.1 Create Directory Structure

```bash
mkdir -p src/shared/components/{Button,Input,Modal,Spinner,Card,Toast}
mkdir -p src/shared/hooks
mkdir -p src/shared/utils
mkdir -p src/shared/types
```

### 4.2 Utility Functions

Create `src/shared/utils/index.ts`:

```typescript
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}
```

### 4.3 Button Component

Create `src/shared/components/Button/Button.tsx`:

```typescript
import React from 'react';
import { cn } from '../../utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const variants = {
      primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
      secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
      ghost: 'bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
      danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
    };

    const sizes = {
      sm: 'px-3 py-1.5 text-sm',
      md: 'px-4 py-2 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center rounded-lg font-medium',
          'focus:outline-none focus:ring-2 focus:ring-offset-2',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          'transition-colors duration-200',
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg
            className="animate-spin -ml-1 mr-2 h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {!isLoading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        {children}
        {!isLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

Create `src/shared/components/Button/index.ts`:

```typescript
export { Button } from './Button';
```

### 4.4 Input Component

Create `src/shared/components/Input/Input.tsx`:

```typescript
import React, { forwardRef } from 'react';
import { cn } from '../../utils';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, leftIcon, rightIcon, id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={inputId}
            className={cn(
              'block w-full rounded-lg border-gray-300 shadow-sm',
              'focus:border-primary-500 focus:ring-primary-500',
              'disabled:bg-gray-100 disabled:cursor-not-allowed',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-red-500 focus:border-red-500 focus:ring-red-500',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-gray-500">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        {helperText && !error && (
          <p className="mt-1 text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

Create `src/shared/components/Input/index.ts`:

```typescript
export { Input } from './Input';
```

### 4.5 Spinner Component

Create `src/shared/components/Spinner/Spinner.tsx`:

```typescript
import { cn } from '../../utils';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <svg
      className={cn('animate-spin text-primary-600', sizes[size], className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}
```

Create `src/shared/components/Spinner/index.ts`:

```typescript
export { Spinner } from './Spinner';
```

### 4.6 Export All Shared Components

Create `src/shared/components/index.ts`:

```typescript
export { Button } from './Button';
export { Input } from './Input';
export { Spinner } from './Spinner';
// Add more as you create them
```

### 4.7 Phase 1-2 Verification

```bash
# Test that the app compiles
npm run build

# Should complete without errors
```

---

## 5. Phase 3: Services & API Layer

**Duration**: 2-3 hours
**Goals**: Build API client, typed endpoints

### 5.1 Create API Types

Create `src/shared/types/api.ts`:

```typescript
// Base API types
export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Pagination
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}
```

Create `src/shared/types/common.ts`:

```typescript
// Common types
export interface Restaurant {
  id: string;
  name: string;
  address?: string;
  vicinity?: string;
  formatted_address?: string;
  rating?: number;
  price_level?: number;
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

export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}
```

### 5.2 Create API Client

Create `src/services/api/client.ts`:

```typescript
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 5.3 Create Chat Service

Create `src/services/api/chat.ts`:

```typescript
import { StreamChunk } from '@/features/chat/types';

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
}

export const chatService = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const { data } = await import('./client').then(m => 
      m.apiClient.post<ChatResponse>('/chat', request)
    );
    return data;
  },

  async *streamMessage(
    request: ChatRequest,
    signal?: AbortSignal
  ): AsyncGenerator<StreamChunk> {
    const token = localStorage.getItem('token');
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    
    const response = await fetch(`${baseUrl}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    if (!response.body) throw new Error('No response body');

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
            } catch {}
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },
};
```

### 5.4 Create Restaurant Service

Create `src/services/api/restaurants.ts`:

```typescript
import { apiClient } from './client';
import { Restaurant, Review } from '@/shared/types/common';

export interface SearchParams {
  query?: string;
  location?: string;
  cuisine?: string;
  lat?: number;
  lng?: number;
  radius?: number;
  limit?: number;
}

export const restaurantService = {
  async search(params: SearchParams) {
    const { data } = await apiClient.get<{ results: Restaurant[]; total: number }>(
      '/restaurants/search',
      { params }
    );
    return data;
  },

  async getById(placeId: string) {
    const { data } = await apiClient.get<Restaurant>(`/restaurants/${placeId}`);
    return data;
  },

  async getReviews(placeId: string, limit = 20) {
    const { data } = await apiClient.get<{ reviews: Review[] }>(
      `/restaurants/${placeId}/reviews`,
      { params: { limit } }
    );
    return data;
  },
};
```

### 5.5 Export Services

Create `src/services/index.ts`:

```typescript
export { apiClient } from './api/client';
export { chatService } from './api/chat';
export { restaurantService } from './api/restaurants';
```

---

## 6. Phase 4: Authentication

**Duration**: 2-3 hours
**Goals**: Auth store, login form, protected routes

### 6.1 Create Auth Store

Create `src/features/auth/stores/authStore.ts`:

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/shared/types/common';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
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
      
      login: (user, token) => {
        localStorage.setItem('token', token);
        set({ user, token, isAuthenticated: true });
      },
      
      logout: () => {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      },
      
      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user }),
    }
  )
);
```

### 6.2 Create Login Page

Create `src/pages/LoginPage.tsx`:

```typescript
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Input } from '@/shared/components';
import { useAuthStore } from '@/features/auth/stores/authStore';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // Simulate API call - replace with real auth
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock successful login
      login(
        { id: '1', email, name: 'Test User' },
        'mock-jwt-token'
      );
      navigate('/');
    } catch (err) {
      setError('Invalid email or password');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Sign in</h2>
          <p className="mt-2 text-gray-600">
            Access your restaurant assistant
          </p>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <Button type="submit" className="w-full" isLoading={isLoading}>
            Sign in
          </Button>

          <p className="text-center text-sm text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 hover:underline">
              Sign up
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
```

---

## 7. Phase 5: Chat Feature

**Duration**: 4-6 hours
**Goals**: Chat UI, streaming, message handling

### 7.1 Create Chat Types

Create `src/features/chat/types/index.ts`:

```typescript
import { Restaurant } from '@/shared/types/common';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  restaurants?: Restaurant[];
  isLoading?: boolean;
}

export interface ChatAction {
  type: 'search' | 'reserve' | 'details' | 'recommend';
  params?: Record<string, any>;
  status: 'pending' | 'success' | 'error';
}

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

### 7.2 Create Chat Store

Create `src/features/chat/stores/chatStore.ts`:

```typescript
import { create } from 'zustand';
import { Message } from '../types';

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  sessionId: string | null;
  error: string | null;

  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  setLoading: (loading: boolean) => void;
  setSessionId: (id: string) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
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
  clearChat: () => set({ messages: [], isLoading: false, error: null }),
}));
```

### 7.3 Create Chat Hook

Create `src/features/chat/hooks/useChat.ts`:

```typescript
import { useCallback, useRef } from 'react';
import { useChatStore } from '../stores/chatStore';
import { chatService } from '@/services';

export function useChat() {
  const { 
    messages, 
    addMessage, 
    updateLastMessage,
    setLoading, 
    sessionId, 
    setSessionId,
    setError,
    clearChat
  } = useChatStore();
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (content: string) => {
    addMessage({ role: 'user', content });
    setLoading(true);
    setError(null);

    abortControllerRef.current = new AbortController();

    try {
      const response = chatService.streamMessage(
        { message: content, session_id: sessionId || undefined },
        abortControllerRef.current.signal
      );

      // Add placeholder for assistant message
      const assistantMessageId = crypto.randomUUID();
      addMessage({ 
        role: 'assistant', 
        content: '', 
        id: assistantMessageId 
      });

      let fullContent = '';

      for await (const chunk of response) {
        if (chunk.type === 'session_id' && chunk.session_id) {
          setSessionId(chunk.session_id);
        } else if (chunk.type === 'content' && chunk.text) {
          fullContent += chunk.text;
          updateLastMessage({ content: fullContent });
        } else if (chunk.type === 'actions' && chunk.restaurants) {
          updateLastMessage({ restaurants: chunk.restaurants });
        } else if (chunk.type === 'error' && chunk.error) {
          setError(chunk.error);
          updateLastMessage({ content: 'Sorry, I encountered an error.' });
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setError(error.message);
        addMessage({
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        });
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, addMessage, updateLastMessage, setLoading, setSessionId, setError]);

  const cancelRequest = useCallback(() => {
    abortControllerRef.current?.abort();
    setLoading(false);
  }, [setLoading]);

  return { 
    messages, 
    sendMessage, 
    cancelRequest, 
    isLoading: useChatStore(s => s.isLoading),
    clearChat
  };
}
```

### 7.4 Create Chat Components

Create `src/features/chat/components/ChatInput.tsx`:

```typescript
import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/shared/components';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

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
            className="w-full px-4 py-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:bg-gray-100"
            rows={1}
          />
        </div>
        <Button type="submit" disabled={!message.trim() || disabled}>
          <Send className="w-5 h-5" />
        </Button>
      </div>
    </form>
  );
}
```

Create `src/features/chat/components/ChatMessage.tsx`:

```typescript
import { Message } from '../types';
import { RestaurantCard } from '@/features/restaurant/components';

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
            ? 'bg-primary-600 text-white'
            : 'bg-white border shadow-sm'
        }`}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>

        {message.restaurants && message.restaurants.length > 0 && (
          <div className="mt-3 space-y-2">
            {message.restaurants.map((restaurant) => (
              <RestaurantCard
                key={restaurant.id}
                restaurant={restaurant}
                variant="compact"
              />
            ))}
          </div>
        )}

        <div className={`text-xs mt-1 ${isUser ? 'text-primary-100' : 'text-gray-400'}`}>
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

Create `src/features/chat/components/ChatContainer.tsx`:

```typescript
import { useRef, useEffect } from 'react';
import { useChat } from '../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

export function ChatContainer() {
  const { messages, sendMessage, isLoading } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (message: string) => {
    await sendMessage(message);
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <header className="bg-white border-b p-4 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-800">
          🍽️ Restaurant Assistant
        </h1>
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <p className="text-lg">👋 Hello!</p>
            <p className="mt-2">
              I can help you find restaurants, get recommendations, 
              or make reservations. What would you like?
            </p>
          </div>
        )}

        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white border shadow-sm rounded-2xl px-4 py-2">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}
```

### 7.5 Export Chat Feature

Create `src/features/chat/index.ts`:

```typescript
export { ChatContainer } from './components/ChatContainer';
export { useChat } from './hooks/useChat';
export { useChatStore } from './stores/chatStore';
export * from './types';
```

---

## 8. Phase 6: Restaurant Feature

**Duration**: 2-3 hours
**Goals**: Restaurant cards, list, detail view

### 8.1 Create Restaurant Components

Create `src/features/restaurant/components/RestaurantCard.tsx`:

```typescript
import { Restaurant } from '@/shared/types/common';

interface RestaurantCardProps {
  restaurant: Restaurant;
  variant?: 'compact' | 'default' | 'detailed';
  onSelect?: () => void;
}

export function RestaurantCard({ restaurant, variant = 'default', onSelect }: RestaurantCardProps) {
  const priceDisplay = '$'.repeat(restaurant.price_level || 1);
  
  if (variant === 'compact') {
    return (
      <div 
        className="bg-gray-50 rounded-lg p-3 cursor-pointer hover:bg-gray-100"
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
    <div className="bg-white rounded-xl border shadow-sm overflow-hidden hover:shadow-md">
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
            className="px-4 py-2 bg-primary-600 text-white text-sm rounded-lg hover:bg-primary-700"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
}
```

Create `src/features/restaurant/index.ts`:

```typescript
export { RestaurantCard } from './components/RestaurantCard';
export { restaurantService } from '@/services';
export * from './types';
export * from '@/shared/types/common';
```

---

## 9. Phase 7: Pages & Routing

**Duration**: 1-2 hours
**Goals**: App routing, main layout

### 9.1 Create Main App

Update `src/App.tsx`:

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ChatContainer from './features/chat/components/ChatContainer';
import LoginPage from './pages/LoginPage';
import { useAuthStore } from './features/auth/stores/authStore';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <ChatContainer />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

Update `src/main.tsx`:

```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 10. Phase 8: Testing

**Duration**: 2-3 hours
**Goals**: Unit tests, E2E tests

### 10.1 Install Testing Dependencies

```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

### 10.2 Configure Vitest

Update `vite.config.ts`:

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

Create `src/test/setup.ts`:

```typescript
import '@testing-library/jest-dom';
```

### 10.3 Write Basic Tests

Create `src/features/chat/components/__tests__/ChatInput.test.tsx`:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { ChatInput } from '../ChatInput';

describe('ChatInput', () => {
  it('renders correctly', () => {
    render(<ChatInput onSend={jest.fn()} />);
    expect(screen.getByPlaceholderText('Ask me about restaurants...')).toBeInTheDocument();
  });

  it('calls onSend when form is submitted', () => {
    const onSend = jest.fn();
    render(<ChatInput onSend={onSend} />);
    
    const input = screen.getByPlaceholderText('Ask me about restaurants...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.submit(input);
    
    expect(onSend).toHaveBeenCalledWith('Test message');
  });

  it('does not call onSend when disabled', () => {
    const onSend = jest.fn();
    render(<ChatInput onSend={onSend} disabled />);
    
    const input = screen.getByPlaceholderText('Ask me about restaurants...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.submit(input);
    
    expect(onSend).not.toHaveBeenCalled();
  });
});
```

---

## 11. Phase 9: Production

**Duration**: 1-2 hours
**Goals**: Build optimization, deployment

### 11.1 Build Configuration

Update `vite.config.ts` for production:

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          state: ['zustand'],
          ui: ['lucide-react'],
        },
      },
    },
  },
});
```

### 11.2 Environment Variables

Create `.env.production`:

```bash
VITE_API_URL=https://api.production.com/api/v1
```

### 11.3 Build & Deploy

```bash
# Build for production
npm run build

# Preview build locally
npm run preview

# Deploy to Vercel
npm i -g vercel
vercel --prod
```

---

## 12. Checklist

Use this checklist to track your implementation progress:

### Phase 1: Project Setup
- [ ] Initialize Vite project with React + TypeScript
- [ ] Configure Tailwind CSS
- [ ] Configure TypeScript paths
- [ ] Create environment file

### Phase 2: Shared Components
- [ ] Button component
- [ ] Input component
- [ ] Spinner component
- [ ] Utility functions (cn, formatDate)

### Phase 3: Services & API Layer
- [ ] API client with interceptors
- [ ] Chat service with streaming
- [ ] Restaurant service

### Phase 4: Authentication
- [ ] Auth store with Zustand
- [ ] Login page

### Phase 5: Chat Feature
- [ ] Chat types
- [ ] Chat store
- [ ] useChat hook with streaming
- [ ] ChatInput component
- [ ] ChatMessage component
- [ ] ChatContainer component

### Phase 6: Restaurant Feature
- [ ] RestaurantCard component (compact & default variants)

### Phase 7: Pages & Routing
- [ ] App with React Router
- [ ] Protected routes
- [ ] Login route

### Phase 8: Testing
- [ ] Configure Vitest
- [ ] Write component tests

### Phase 9: Production
- [ ] Production build
- [ ] Environment configuration
- [ ] Deployment

---

## File Summary

| Phase | Files to Create |
|-------|-----------------|
| 1 | `package.json`, `vite.config.ts`, `tailwind.config.js`, `.env` |
| 2 | `src/shared/components/Button/`, `src/shared/components/Input/`, `src/shared/components/Spinner/` |
| 3 | `src/services/api/client.ts`, `src/services/api/chat.ts`, `src/services/api/restaurants.ts` |
| 4 | `src/features/auth/stores/authStore.ts`, `src/pages/LoginPage.tsx` |
| 5 | `src/features/chat/types/`, `src/features/chat/stores/`, `src/features/chat/hooks/`, `src/features/chat/components/` |
| 6 | `src/features/restaurant/components/RestaurantCard.tsx` |
| 7 | `src/App.tsx` |
| 8 | `src/test/setup.ts`, `src/**/__tests__/` |

---

## Next Steps

After completing implementation:

1. **Connect to real API**: Update API base URL in `.env`
2. **Add more features**: Reservation flow, user profile
3. **Improve UX**: Loading states, error handling, empty states
4. **Performance**: Add React Query, virtualized lists
5. **Analytics**: Track user interactions
