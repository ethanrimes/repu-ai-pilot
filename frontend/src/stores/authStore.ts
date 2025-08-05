// frontend/src/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  // State
  user: User | null;
  session: SessionInfo | null;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User | null) => void;
  setSession: (session: SessionInfo | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      session: null,
      isLoading: false,
      
      setUser: (user) => set({ user }),
      setSession: (session) => set({ session }),
      
      login: async (email, password) => {
        set({ isLoading: true });
        try {
          // Firebase auth
          const userCredential = await signInWithEmailAndPassword(auth, email, password);
          const idToken = await userCredential.user.getIdToken();
          
          // Backend session
          const response = await apiClient.post('/auth/login', {
            firebase_token: idToken,
            channel: 'web'
          });
          
          set({
            user: response.data.user,
            session: response.data.session,
            isLoading: false
          });
          
          // Set up session refresh
          const refreshInterval = (response.data.expires_in - 3600) * 1000;
          setTimeout(() => get().refreshSession(), refreshInterval);
          
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },
      
      logout: async () => {
        const session = get().session;
        if (session) {
          await apiClient.post('/auth/logout');
        }
        await signOut(auth);
        set({ user: null, session: null });
      },
      
      refreshSession: async () => {
        try {
          const response = await apiClient.post('/auth/refresh');
          set(state => ({
            session: { ...state.session, expiresIn: response.data.expires_in }
          }));
          
          // Schedule next refresh
          const refreshInterval = (response.data.expires_in - 3600) * 1000;
          setTimeout(() => get().refreshSession(), refreshInterval);
        } catch (error) {
          // Session expired, need to re-login
          get().logout();
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user }) // Only persist user
    }
  )
);