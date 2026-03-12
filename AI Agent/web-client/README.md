# Restaurant Agent Web Client

React-based chat application for the Restaurant Agent system.

## Overview

A modern web client built with React, TypeScript, and Tailwind CSS that provides:
- Natural language chat interface
- Real-time streaming responses (SSE)
- Responsive design
- JWT authentication

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

```bash
# Install dependencies
cd web-client
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

## Configuration

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Restaurant Agent
VITE_APP_VERSION=1.0.0
```

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.x | UI Library |
| Vite | 5.x | Build Tool |
| TypeScript | 5.x | Type Safety |
| Tailwind CSS | 3.x | Styling |
| Zustand | 4.x | State Management |
| Axios | 1.x | HTTP Client |
| React Router | 6.x | Routing |
| Lucide React | Latest | Icons |

## Project Structure

```
web-client/
├── src/
│   ├── features/
│   │   ├── chat/
│   │   │   ├── components/
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   └── ChatInput.tsx
│   │   │   └── stores/
│   │   │       └── chatStore.ts
│   │   └── auth/
│   │       └── stores/
│   │           └── authStore.ts
│   ├── shared/
│   │   ├── components/
│   │   │   ├── Button/
│   │   │   ├── Input/
│   │   │   ├── Spinner/
│   │   │   ├── Card/
│   │   │   └── Toast/
│   │   ├── utils/
│   │   └── types/
│   ├── services/
│   │   └── api/
│   │       ├── client.ts
│   │       ├── auth.ts
│   │       └── chat.ts
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   └── LoginPage.tsx
│   ├── config/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

## Features

### Chat
- Real-time streaming with SSE
- Message history with session persistence
- Auto-scroll to latest message
- Typing indicator

### Authentication
- JWT-based login
- Persistent sessions
- Protected routes

### UI Components
- Button (primary, secondary, ghost, danger variants)
- Input with validation
- Spinner for loading states
- Card container
- Toast notifications

## Running

### Development
```bash
npm run dev
```

### Production Build
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## API Integration

The client connects to the API Gateway running at `VITE_API_URL`:

- `POST /auth/login` - Authentication
- `POST /chat` - Send message
- `POST /chat/stream` - Stream response (SSE)

## License

MIT
