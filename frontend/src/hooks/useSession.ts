// frontend/src/hooks/useSession.ts

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '@/lib/api/client';

interface SessionData {
  sessionId: string;
  userId: number;
  expiresIn: number;
}

export function useSession() {
  const { user, getIdToken } = useAuth();
  const [session, setSession] = useState<SessionData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Create session on login
  const createSession = useCallback(async () => {
    if (!user) return;

    try {
      const idToken = await getIdToken();
      const response = await apiClient.post('/auth/login', {
        firebase_token: idToken,
        channel: 'web'
      });

      const sessionData: SessionData = {
        sessionId: response.data.session_id,
        userId: response.data.user_id,
        expiresIn: response.data.expires_in
      };

      // Store session ID in localStorage
      localStorage.setItem('session_id', sessionData.sessionId);
      
      // Set up API client with session
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${sessionData.sessionId}`;
      
      setSession(sessionData);
      
      // Set up session refresh
      const refreshInterval = (sessionData.expiresIn - 3600) * 1000; // Refresh 1 hour before expiry
      setTimeout(() => refreshSession(), refreshInterval);
      
    } catch (error) {
      console.error('Failed to create session:', error);
    }
  }, [user, getIdToken]);

  // Refresh session
  const refreshSession = useCallback(async () => {
    const sessionId = localStorage.getItem('session_id');
    if (!sessionId) return;

    try {
      const response = await apiClient.post('/auth/refresh');
      
      // Update expiry and set new refresh timer
      if (session) {
        const newSession = { ...session, expiresIn: response.data.expires_in };
        setSession(newSession);
        
        const refreshInterval = (newSession.expiresIn - 3600) * 1000;
        setTimeout(() => refreshSession(), refreshInterval);
      }
    } catch (error) {
      console.error('Failed to refresh session:', error);
      // Session expired, need to re-login
      endSession();
    }
  }, [session]);

  // End session
  const endSession = useCallback(async () => {
    const sessionId = localStorage.getItem('session_id');
    
    if (sessionId) {
      try {
        await apiClient.post('/auth/logout');
      } catch (error) {
        console.error('Failed to end session:', error);
      }
    }
    
    localStorage.removeItem('session_id');
    delete apiClient.defaults.headers.common['Authorization'];
    setSession(null);
  }, []);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      const sessionId = localStorage.getItem('session_id');
      
      if (sessionId) {
        // Validate existing session
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${sessionId}`;
        
        try {
          const response = await apiClient.get('/auth/session');
          setSession({
            sessionId,
            userId: response.data.user_id,
            expiresIn: 86400 // Default to 24 hours
          });
        } catch (error) {
          // Session invalid, remove it
          localStorage.removeItem('session_id');
          delete apiClient.defaults.headers.common['Authorization'];
        }
      }
      
      setIsLoading(false);
    };

    initSession();
  }, []);

  // Create session when user logs in
  useEffect(() => {
    if (user && !session) {
      createSession();
    }
  }, [user, session, createSession]);

  return {
    session,
    isLoading,
    refreshSession,
    endSession
  };
}