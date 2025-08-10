// frontend/src/stores/languageStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Language = 'es' | 'en';

interface LanguageState {
  // State
  language: Language;
  
  // Actions
  setLanguage: (language: Language) => void;
  toggleLanguage: () => void;
}

export const useLanguageStore = create<LanguageState>()(
  persist(
    (set, get) => ({
      language: 'es',
      
      setLanguage: (language) => set({ language }),
      
      toggleLanguage: () => {
        const currentLanguage = get().language;
        const newLanguage = currentLanguage === 'es' ? 'en' : 'es';
        set({ language: newLanguage });
      }
    }),
    {
      name: 'language-storage',
      partialize: (state) => ({ language: state.language })
    }
  )
);
