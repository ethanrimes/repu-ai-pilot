'use client';
import { useState } from 'react';
import { useTranslations } from '@/hooks/useLanguage';
import styles from '@/styles/chat.module.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const { t } = useTranslations();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.messageInputForm}>
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={t('chat.interface.placeholder')}
        disabled={disabled}
        className={styles.messageInput}
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={styles.sendButton}
      >
        {t('chat.actions.send')}
      </button>
    </form>
  );
}