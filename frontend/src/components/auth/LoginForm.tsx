'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  deleteUser,
} from 'firebase/auth';
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
  const [inviteCode, setInviteCode] = useState(''); // NEW
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    let userCredential: Awaited<ReturnType<typeof signInWithEmailAndPassword>> | null = null;

    try {
      if (isSignUp) {
        // Require invite code client-side for UX
        if (!inviteCode.trim()) {
          setIsLoading(false);
          return setError('Invite code is required to create an account.');
        }
        // Create new Firebase user
        userCredential = await createUserWithEmailAndPassword(auth, email, password);
        // Optional: set display name if you want it in Firebase profile
        // if (name) await updateProfile(userCredential.user, { displayName: name });
      } else {
        // Sign in existing user
        userCredential = await signInWithEmailAndPassword(auth, email, password);
      }

      // Get Firebase ID token
      const idToken = await userCredential.user.getIdToken();

      // Create backend session (include invite_code only for sign-up)
      const response = await authApi.login({
        firebase_token: idToken,
        channel: 'web',
        ...(isSignUp ? { invite_code: inviteCode.trim() } : {}),
      });

      const { session_id, expires_in } = response.data;

      // Persist session for middleware + API client
      localStorage.setItem('session_id', session_id);
      document.cookie = `session_id=${session_id}; path=/; max-age=${expires_in}; SameSite=Lax`;
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${session_id}`;

      router.push('/chat');
    } catch (err: any) {
      console.error('Auth error:', err);

      // If sign-up failed due to invalid invite, delete the just-created Firebase user to avoid orphan accounts
      const isInviteFailure =
        isSignUp &&
        (err?.response?.status === 403 ||
          /invite code/i.test(err?.response?.data?.detail || '') ||
          /invite/i.test(err?.message || ''));

      if (isInviteFailure && userCredential?.user) {
        try {
          await deleteUser(userCredential.user);
        } catch (delErr) {
          console.warn('Failed to delete orphan Firebase user after invite failure:', delErr);
        }
      }

      setError(
        err?.response?.data?.detail ||
          err?.message ||
          (isSignUp ? 'Sign up failed' : 'Sign in failed')
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.formContainer}>
      <h2 className={styles.formTitle}>{isSignUp ? 'Create Account' : 'Sign In'}</h2>

      <form onSubmit={handleSubmit} className={styles.form}>
        {isSignUp && (
          <>
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

            {/* NEW: Invite code */}
            <div className={styles.inputGroup}>
              <label htmlFor="invite">Invite code</label>
              <input
                id="invite"
                type="text"
                value={inviteCode}
                onChange={(e) => setInviteCode(e.target.value)}
                required
                className={styles.input}
                placeholder="e.g., MY-SPECIAL-CODE-123"
                autoComplete="one-time-code"
              />
            </div>
          </>
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
            autoComplete="email"
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
            autoComplete={isSignUp ? 'new-password' : 'current-password'}
          />
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <button type="submit" disabled={isLoading} className={styles.submitButton}>
          {isLoading ? 'Loading...' : isSignUp ? 'Sign Up' : 'Sign In'}
        </button>
      </form>

      <p className={styles.switchMode}>
        {isSignUp ? 'Already have an account?' : "Don't have an account?"}
        <button
          type="button"
          onClick={() => {
            setIsSignUp(!isSignUp);
            setError('');
          }}
          className={styles.switchButton}
        >
          {isSignUp ? 'Sign In' : 'Sign Up'}
        </button>
      </p>
    </div>
  );
}