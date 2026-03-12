export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  restaurants?: Restaurant[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  timestamp: string;
}

export interface Restaurant {
  id: string;
  name: string;
  address: string;
  rating?: number;
  review_count?: number;
  price_level?: number;
  cuisine_type?: string[];
  photo_url?: string;
  phone_number?: string;
  website?: string;
  opening_hours?: OpeningHours[];
  location?: {
    lat: number;
    lng: number;
  };
}

export interface OpeningHours {
  day: number;
  open: string;
  close: string;
  closed?: boolean;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
}
