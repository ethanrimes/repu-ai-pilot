'use client';

import { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/api/endpoints';
import type { ChatMessage, ChatResponse } from '@/lib/api/types';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { useLanguage, useTranslations } from '@/hooks/useLanguage';
import { useLanguageStore } from '@/stores/languageStore';
import styles from '@/styles/chat.module.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const { language } = useLanguage();
  const { t } = useTranslations();
  const { changeLanguageWithReset, isChangingLanguage } = useLanguageStore();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(language);
  const [initialLoaded, setInitialLoaded] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load initial conversation state
  useEffect(() => {
    const loadInitialConversation = async () => {
      if (initialLoaded) return;
      
      try {
        // Send empty message to trigger greeting if conversation hasn't started
        const response = await chatApi.sendMessage({
          message: '',
          language: language
        });
        
        const data: ChatResponse = response.data;
        
        if (data.message) {
          const greetingMessage: Message = {
            id: 'initial-greeting',
            role: 'assistant',
            content: data.message,
            timestamp: new Date(data.timestamp)
          };
          setMessages([greetingMessage]);
        }
      } catch (error) {
        console.error('Failed to load initial conversation:', error);
        // Set a default greeting message if API fails
        const defaultGreeting = language === 'en' 
          ? "Hello! I'm RepuAI, your automotive parts assistant. How can I help you today?"
          : "¡Hola! Soy RepuAI, tu asistente de repuestos automotrices. ¿En qué puedo ayudarte hoy?";
        
        setMessages([{
          id: 'fallback-greeting',
          role: 'assistant',
          content: defaultGreeting,
          timestamp: new Date()
        }]);
      } finally {
        setInitialLoaded(true);
      }
    };

    // Only load initial conversation if we don't have messages yet
    if (messages.length === 0 && !isChangingLanguage && !initialLoaded) {
      loadInitialConversation();
    }
  }, [language, messages.length, isChangingLanguage, initialLoaded]);

  // Handle language changes
  useEffect(() => {
    const handleLanguageChange = async () => {
      if (language !== currentLanguage && initialLoaded) {
        console.log(`Language changed from ${currentLanguage} to ${language}`);
        
        try {
          // Reset conversation and get greeting message
          const greetingMessage = await changeLanguageWithReset(language);
          
          if (greetingMessage) {
            // Clear existing messages and show the new greeting
            setMessages([{
              id: 'language-change-' + Date.now(),
              role: 'assistant',
              content: greetingMessage,
              timestamp: new Date()
            }]);
          }
          
          setCurrentLanguage(language);
        } catch (error) {
          console.error('Failed to handle language change:', error);
        }
      }
    };

    handleLanguageChange();
  }, [language, currentLanguage, changeLanguageWithReset, initialLoaded]);

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
        language: language // Pass the current language to the API
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
        content: t('chat.messages.errorMessage'),
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
        {(isLoading || isChangingLanguage) && (
          <div className={styles.thinkingIndicator}>
            {isChangingLanguage ? (
              <span>Changing language...</span>
            ) : (
              <>
                <span></span>
                <span></span>
                <span></span>
              </>
            )}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <MessageInput onSend={sendMessage} disabled={isLoading || isChangingLanguage} />
    </div>
  );
}