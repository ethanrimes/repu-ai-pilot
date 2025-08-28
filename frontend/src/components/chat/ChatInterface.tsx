// frontend/src/components/chat/ChatInterface.tsx

'use client';

import { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/api/endpoints';
import type { ChatMessage, ChatResponse } from '@/lib/api/types';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { VehicleSelectionModal } from './VehicleSelectionModal';
import { CategorySelectionModal } from './CategorySelectionModal';
import { useLanguage, useTranslations } from '@/hooks/useLanguage';
import { useLanguageStore } from '@/stores/languageStore';
import styles from '@/styles/chat.module.css';

// ==================== INTERFACES ====================
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  buttons?: Array<{
    id: string;
    text: string;
    disabled?: boolean;
    note?: string;
  }>;
}

interface VehicleType {
  id: number;
  vehicleType: string;
}

interface CategoryModalData {
  vehicleId: number;
  manufacturerId: number;
  categoryLevels: number;
}

// ==================== COMPONENT ====================
export function ChatInterface() {
  // ========== LANGUAGE HOOKS ==========
  const { language } = useLanguage();
  const { t } = useTranslations();
  const { changeLanguageWithReset, isChangingLanguage } = useLanguageStore();

  // ========== STATE ==========
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(language);
  const [initialLoaded, setInitialLoaded] = useState(false);
  
  // Vehicle Modal State
  const [showVehicleModal, setShowVehicleModal] = useState(false);
  const [vehicleTypes, setVehicleTypes] = useState<VehicleType[]>([]);
  
  // Category Modal State
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [categoryModalData, setCategoryModalData] = useState<CategoryModalData>({
    vehicleId: 0,
    manufacturerId: 0,
    categoryLevels: 3
  });

  // ========== REFS ==========
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const modalDataHandlerRef = useRef<((data: any) => void) | null>(null);
  const categoryModalDataHandlerRef = useRef<((data: any) => void) | null>(null);

  // ========== HELPER FUNCTIONS ==========
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const setModalDataHandler = (handler: (data: any) => void) => {
    modalDataHandlerRef.current = handler;
  };

  const setCategoryModalDataHandler = (handler: (data: any) => void) => {
    categoryModalDataHandlerRef.current = handler;
  };

  const handleModalDataUpdate = (data: any) => {
    if (modalDataHandlerRef.current) {
      modalDataHandlerRef.current(data);
    }
  };

  // ========== MESSAGE PARSING ==========
  const parseAndHandleResponse = (messageContent: string) => {
    // Split by newlines and check each part for JSON
    const parts = messageContent.split('\n\n');
    let regularMessage = '';
    let messageButtons = undefined;
    
    for (const part of parts) {
      const trimmed = part.trim();
      if (!trimmed) continue;
      
      try {
        const parsed = JSON.parse(trimmed);
        
        // Handle different JSON response types
        switch (parsed.type) {
          case 'VEHICLE_ID_OPTIONS':
            messageButtons = parsed.buttons;
            if (parsed.message) {
              regularMessage += (regularMessage ? '\n\n' : '') + parsed.message;
            }
            break;
            
          case 'OPEN_VEHICLE_MODAL':
            setVehicleTypes(parsed.vehicleTypes || []);
            setShowVehicleModal(true);
            if (parsed.message) {
              regularMessage += (regularMessage ? '\n\n' : '') + parsed.message;
            }
            break;
            
          case 'OPEN_CATEGORY_MODAL':
            setCategoryModalData({
              vehicleId: parsed.vehicleId,
              manufacturerId: parsed.manufacturerId,
              categoryLevels: parsed.categoryLevels || 3
            });
            setShowCategoryModal(true);
            if (parsed.message) {
              regularMessage += (regularMessage ? '\n\n' : '') + parsed.message;
            }
            break;
            
          case 'CATEGORIES_DATA':
          case 'ARTICLES_DATA':
            if (categoryModalDataHandlerRef.current) {
              categoryModalDataHandlerRef.current(parsed);
            }
            break;
            
          case 'NO_ARTICLES':
            setShowCategoryModal(false);
            if (parsed.message) {
              regularMessage += (regularMessage ? '\n\n' : '') + parsed.message;
            }
            break;
            
          case 'MANUFACTURERS_DATA':
          case 'MODELS_DATA':
          case 'VEHICLES_DATA':
            handleModalDataUpdate(parsed);
            break;
            
          case 'ERROR':
            if (categoryModalDataHandlerRef.current) {
              categoryModalDataHandlerRef.current(parsed);
            } else {
              handleModalDataUpdate(parsed);
            }
            break;
            
          default:
            // Unknown JSON type, add message if present
            if (parsed.message) {
              regularMessage += (regularMessage ? '\n\n' : '') + parsed.message;
            }
        }
      } catch (e) {
        // Not JSON, treat as regular message
        regularMessage += (regularMessage ? '\n\n' : '') + trimmed;
      }
    }
    
    return { messageContent: regularMessage, messageButtons };
  };

  // ========== EVENT HANDLERS ==========
  const sendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send message to API
      const response = await chatApi.sendMessage({
        message: content,
        language: language
      });

      const data: ChatResponse = response.data;
      
      // Parse and handle response using the new function
      const parsedResponse = parseAndHandleResponse(data.message);
      
      // Only add message if there's content to display
      if (parsedResponse.messageContent) {
        const assistantMessage: Message = {
          id: data.message_id || (Date.now() + 1).toString(),
          role: 'assistant',
          content: parsedResponse.messageContent,
          timestamp: new Date(data.timestamp),
          buttons: parsedResponse.messageButtons
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
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

  const handleButtonClick = (buttonId: string) => {
    sendMessage(buttonId);
  };

  const handleVehicleSelect = (vehicle: any) => {
    const vehicleMessage = `VEHICLE_SELECTED:${JSON.stringify(vehicle)}`;
    sendMessage(vehicleMessage);
    setShowVehicleModal(false);
  };

  const handleCategorySelect = (categoryData: any) => {
    const categoryMessage = `CATEGORY_SELECTED:${JSON.stringify(categoryData)}`;
    sendMessage(categoryMessage);
    setShowCategoryModal(false);
  };

  // ========== EFFECTS ==========
  
  // Auto-scroll on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load initial conversation state
  useEffect(() => {
    const loadInitialConversation = async () => {
      if (initialLoaded) return;
      
      try {
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
          const greetingMessage = await changeLanguageWithReset(language);
          
          if (greetingMessage) {
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

  // ========== RENDER ==========
  return (
    <div className={styles.chatContainer}>
      <div className={styles.messagesContainer}>
        <MessageList 
          messages={messages} 
          onButtonClick={handleButtonClick} 
        />
        
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
      
      <MessageInput 
        onSend={sendMessage} 
        disabled={isLoading || isChangingLanguage} 
      />
      
      <VehicleSelectionModal
        isOpen={showVehicleModal}
        onClose={() => setShowVehicleModal(false)}
        onVehicleSelect={handleVehicleSelect}
        vehicleTypes={vehicleTypes}
        onSendMessage={sendMessage}
        onDataHandlerReady={setModalDataHandler}
      />

      <CategorySelectionModal
        isOpen={showCategoryModal}
        onClose={() => setShowCategoryModal(false)}
        onCategorySelect={handleCategorySelect}
        vehicleId={categoryModalData.vehicleId}
        manufacturerId={categoryModalData.manufacturerId}
        categoryLevels={categoryModalData.categoryLevels}
        onSendMessage={sendMessage}
        onDataHandlerReady={setCategoryModalDataHandler}
      />
    </div>
  );
}