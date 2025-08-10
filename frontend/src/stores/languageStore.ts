// frontend/src/stores/languageStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { chatApi } from '@/lib/api/endpoints';

export type Language = 'es' | 'en';

interface LanguageState {
  // State
  language: Language;
  isChangingLanguage: boolean;
  
  // Actions
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
  changeLanguageWithReset: (language: Language) => Promise<string | null>;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set, get) => ({
      language: 'es',
      isChangingLanguage: false,
      
      setLanguage: (language) => set({ language }),
      
      toggleLanguage: () => {
        const currentLanguage = get().language;
        const newLanguage = currentLanguage === 'es' ? 'en' : 'es';
        set({ language: newLanguage });
      },
      
      changeLanguageWithReset: async (language: Language) => {
        const currentLanguage = get().language;
        
        // Don't do anything if language hasn't changed
        if (currentLanguage === language) {
          return null;
        }
        
        set({ isChangingLanguage: true });
        
        try {
          // Update language in store first
          set({ language });
          
          // Call API to reset conversation
          const response = await chatApi.changeLanguage({ language });
          
          // Return the greeting message from the backend
          return response.data.message;
          
        } catch (error) {
          console.error('Failed to change language:', error);
          // Revert language change on error
          set({ language: currentLanguage });
          return null;
        } finally {
          set({ isChangingLanguage: false });
        }
      }
    }),
    {
      name: 'language-storage',
      partialize: (state) => ({ language: state.language })
    }
  )
);
