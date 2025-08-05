'use client';

import { useState, useEffect } from 'react';
import { onAuthStateChanged, User, signOut } from 'firebase/auth';
import { auth } from '@/lib/firebase/config';
import { apiClient } from '@/lib/api/client';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (firebaseUser) => {
      setUser(firebaseUser);
      setIsLoading(false);
    });

    return unsubscribe;
  }, []);

  const logout = async () => {
    try {
      // End backend session
      const sessionId = localStorage.getItem('session_id');
      if (sessionId) {
        await apiClient.post('/auth/logout');
      }
      
      // Sign out from Firebase
      await signOut(auth);
      
      // Clear session
      localStorage.removeItem('session_id');
      delete apiClient.defaults.headers.common['Authorization'];
      
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const getIdToken = async () => {
    if (user) {
      return await user.getIdToken();
    }
    return null;
  };

  return {
    user,
    isLoading,
    logout,
    getIdToken
  };
}