import { apiClient } from './client';
import type {
  LoginRequest,
  LoginResponse,
  SessionResponse,
  ChatRequest,
  ChatResponse,
  SearchRequest,
  SearchResponse,
  User
} from './types';

// Auth endpoints
export const authApi = {
  login: (data: LoginRequest) => 
    apiClient.post<LoginResponse>('/auth/login', data),
  
  logout: () => 
    apiClient.post('/auth/logout'),
  
  getSession: () => 
    apiClient.get<SessionResponse>('/auth/session'),
  
  refreshSession: () => 
    apiClient.post<{ expires_in: number }>('/auth/refresh'),
  
  getCurrentUser: () => 
    apiClient.get<User>('/auth/me')
};

// Chat endpoints
export const chatApi = {
  sendMessage: (data: ChatRequest) => 
    apiClient.post<ChatResponse>('/chat/message', data),
  
  getHistory: (sessionId: string) => 
    apiClient.get(`/chat/history/${sessionId}`),
  
  clearHistory: (sessionId: string) => 
    apiClient.delete(`/chat/history/${sessionId}`)
};

// Document/Search endpoints
export const searchApi = {
  search: (data: SearchRequest) => 
    apiClient.post<SearchResponse>('/search', data),
  
  getDocument: (id: number) => 
    apiClient.get(`/documents/${id}`),
  
  getSimilarDocuments: (id: number) => 
    apiClient.get(`/documents/${id}/similar`)
};

// Health check
export const healthApi = {
  check: () => apiClient.get('/health')
};