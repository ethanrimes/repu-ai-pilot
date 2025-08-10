'use client';

import { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/api/endpoints';
import type { ChatMessage, ChatResponse } from '@/lib/api/types';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import styles from '@/styles/chat.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: content,
        language: 'es'
      });

      const data: ChatResponse = response.data;

      const assistantMessage: Message = {
        id: data.message_id || (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message, // map backend 'message' field
        timestamp: new Date(data.timestamp)
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Lo siento, ocurrió un error. Por favor intenta de nuevo.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messagesContainer}>
        <MessageList messages={messages} />
        {isLoading && (
          <div className={styles.thinkingIndicator}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}