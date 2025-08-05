import { useState } from 'react';
import styles from '@/styles/chat.module.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function MessageInput({ onSend, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('');

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
        placeholder="Escribe tu mensaje..."
        disabled={disabled}
        className={styles.messageInput}
      />
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={styles.sendButton}
      >
        Enviar
      </button>
    </form>
  );
}