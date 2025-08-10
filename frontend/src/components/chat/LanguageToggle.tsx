// frontend/src/components/chat/LanguageToggle.tsx
'use client';

import { useLanguage, useTranslations } from '@/hooks/useLanguage';
import { languageNames } from '@/i18n/config';

export function LanguageToggle() {
  const { language, toggleLanguage } = useLanguage();
  const { t } = useTranslations();

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center space-x-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200 shadow-sm"
      title={`${t('common.language.label')}: ${languageNames[language]}`}
    >
      <span className="text-sm font-medium text-gray-700">
        {language.toUpperCase()}
      </span>
      <svg 
        className="w-4 h-4 text-gray-500" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" 
        />
      </svg>
    </button>
  );
}
