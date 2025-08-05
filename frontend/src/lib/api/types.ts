// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

// Auth Types
export interface LoginRequest {
  firebase_token: string;
  channel: 'web' | 'whatsapp';
}

export interface LoginResponse {
  session_id: string;
  user_id: number;
  email: string;
  name: string;
  expires_in: number;
}

export interface SessionResponse {
  session_id: string;
  user_id: number;
  firebase_uid: string;
  channel: string;
  created_at: string;
  last_activity: string;
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface ChatRequest {
  message: string;
  language: 'es' | 'en';
  session_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  response: string;
  intent?: string;
  confidence?: number;
  suggestions?: string[];
  metadata?: Record<string, any>;
}

// Document Types
export interface Document {
  id: number;
  title: string;
  content: string;
  type: string;
  category: string;
  language: string;
  created_at: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  filters?: {
    type?: string;
    category?: string;
    language?: string;
  };
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

export interface SearchResult {
  document: Document;
  score: number;
  highlights: string[];
}

// User Types
export interface User {
  id: number;
  email: string;
  name: string;
  firebase_uid: string;
  language: 'es' | 'en';
  created_at: string;
}