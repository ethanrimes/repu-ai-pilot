// src/app/[locale]/page.tsx
// Path: src/app/[locale]/page.tsx

import { ChatInterface } from '@/components/chat/ChatInterface';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { Header } from '@/components/layout/Header';
import { getTranslations } from '@/i18n/config';

export default async function ChatPage({ 
  params: { locale } 
}: { 
  params: { locale: string } 
}) {
  const t = await getTranslations(locale);

  return (
    <AuthGuard>
      <div className="flex flex-col h-screen bg-gray-50">
        <Header locale={locale} />
        <main className="flex-1 container mx-auto px-4 py-6 max-w-4xl">
          <ChatInterface locale={locale} translations={t} />
        </main>
      </div>
    </AuthGuard>
  );
}