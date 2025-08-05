// frontend/src/lib/api/client.ts

import axios from 'axios';
import { auth } from '@/lib/firebase/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add session token
apiClient.interceptors.request.use(
  (config) => {
    // Session ID is set by useSession hook
    // Just ensure we have it
    const sessionId = localStorage.getItem('session_id');
    if (sessionId && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${sessionId}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      // Try to refresh session
      try {
        const response = await apiClient.post('/auth/refresh');
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('session_id');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    // Handle rate limiting
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 60;
      console.error(`Rate limited. Retry after ${retryAfter} seconds`);
    }

    return Promise.reject(error);
  }
);