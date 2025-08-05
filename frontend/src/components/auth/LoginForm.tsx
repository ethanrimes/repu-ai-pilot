'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase/config';
import { authApi } from '@/lib/api/endpoints';
import { apiClient } from '@/lib/api/client';
import styles from '@/styles/auth.module.css';

export function LoginForm() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      let userCredential;
      
      if (isSignUp) {
        // Create new user
        userCredential = await createUserWithEmailAndPassword(auth, email, password);
        
        // Optionally update the user's display name
        // if (name) {
        //     await updateProfile(userCredential.user, {
        //     displayName: name
        //     });
        // }
        } else {
        // Sign in existing user
        userCredential = await signInWithEmailAndPassword(auth, email, password);
    }

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();

      // Create backend session
      const response = await authApi.login({
        firebase_token: idToken,
        channel: 'web'
      });
      
      // Destructure response data (renamed email to userEmail to avoid conflict)
      const { session_id, user_id, email: userEmail } = response.data;

      // Store session ID in both localStorage and cookies
      localStorage.setItem('session_id', session_id);
      
      // Set cookie for middleware to detect
      document.cookie = `session_id=${session_id}; path=/; max-age=${response.data.expires_in}; SameSite=Lax`;
      
      // Set up API client with session
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${session_id}`;

      // Redirect to chat
      router.push('/chat');
      
    } catch (err: any) {
      console.error('Auth error:', err);
      setError(err.message || 'Authentication failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.formTitle}>
        {isSignUp ? 'Create Account' : 'Sign In'}
      </h2>
      
      <form onSubmit={handleSubmit} className={styles.form}>
        {isSignUp && (
          <div className={styles.inputGroup}>
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required={isSignUp}
              className={styles.input}
              placeholder="Your name"
            />
          </div>
        )}
        
        <div className={styles.inputGroup}>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className={styles.input}
            placeholder="you@example.com"
          />
        </div>
        
        <div className={styles.inputGroup}>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
            className={styles.input}
            placeholder="••••••••"
          />
        </div>
        
        {error && <div className={styles.error}>{error}</div>}
        
        <button
          type="submit"
          disabled={isLoading}
          className={styles.submitButton}
        >
          {isLoading ? 'Loading...' : (isSignUp ? 'Sign Up' : 'Sign In')}
        </button>
      </form>
      
      <p className={styles.switchMode}>
        {isSignUp ? 'Already have an account?' : "Don't have an account?"}
        <button
          type="button"
          onClick={() => setIsSignUp(!isSignUp)}
          className={styles.switchButton}
        >
          {isSignUp ? 'Sign In' : 'Sign Up'}
        </button>
      </p>
    </div>
  );
}