// frontend/src/app/[locale]/page.tsx
'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { Header } from '@/components/layout/Header';
import { useEffect } from 'react';
import { useLanguageStore, Language } from '@/stores/languageStore';

export default function ChatPage({ 
  params: { locale } 
}: { 
  params: { locale: string } 
}) {
  const { setLanguage } = useLanguageStore();

  useEffect(() => {
    // Set language based on URL locale
    if (locale === 'en' || locale === 'es') {
      setLanguage(locale as Language);
    }
  }, [locale, setLanguage]);

  return (
    <AuthGuard>
      <div className="flex flex-col h-screen bg-gray-50">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-6 max-w-4xl">
          <ChatInterface />
        </main>
      </div>
    </AuthGuard>
  );
}