// frontend/src/hooks/useLanguage.ts
'use client';

import { useLanguageStore, Language } from '@/stores/languageStore';
import { useEffect, useState } from 'react';
import { 
  getTranslations, 
  getNestedTranslation, 
  Translations,
  UseTranslationsResult 
} from '@/i18n/config';

export function useLanguage() {
  const { language, setLanguage, toggleLanguage } = useLanguageStore();
  
  return {
    language,
    setLanguage,
    toggleLanguage
  };
}

export function useTranslations(): UseTranslationsResult & { isLoading: boolean } {
  const { language } = useLanguageStore();
  const [translations, setTranslations] = useState<Translations | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadTranslations = async () => {
      setIsLoading(true);
      try {
        const newTranslations = await getTranslations(language);
        setTranslations(newTranslations);
      } catch (error) {
        console.error('Failed to load translations:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadTranslations();
  }, [language]);

  const t = (key: string, variables?: Record<string, string | number>): string => {
    if (!translations) {
      return key;
    }
    return getNestedTranslation(translations, key, variables);
  };

  return {
    t,
    language,
    isLoading
  };
}
