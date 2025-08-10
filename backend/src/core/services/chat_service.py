# backend/src/core/services/chat_service.py

import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.core.models.chat import (
    ChatMessage, ChatRequest, ChatResponse, 
    ChatHistory, MessageRole, ChatStatusResponse
)
from src.infrastructure.cache.cache_manager import CacheManager
from src.infrastructure.llm.providers.openai_provider import OpenAIChatProvider
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class ChatService:
    """Service for managing chat conversations"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.llm_provider = OpenAIChatProvider()
        self.max_history_length = 20  # Maximum messages to keep in history
        self.chat_ttl = 86400  # 24 hours, same as session
    
    def _get_chat_key(self, session_id: str) -> str:
        """Generate Redis key for chat history"""
        return f"chat:{session_id}"
    
    async def get_chat_history(self, session_id: str) -> ChatHistory:
        """Get chat history for a session"""
        chat_key = self._get_chat_key(session_id)
        
        # Get from Redis
        history_data = await self.cache.get(chat_key)
        
        if not history_data:
            # Initialize empty history
            return ChatHistory(
                session_id=session_id,
                messages=[],
                total_messages=0
            )
        
        # Parse messages
        messages = []
        for msg_data in history_data.get('messages', []):
            messages.append(ChatMessage(**msg_data))
        
        return ChatHistory(
            session_id=session_id,
            messages=messages,
            total_messages=len(messages)
        )
    
    async def add_message(
        self, 
        session_id: str, 
        role: MessageRole, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a message to chat history"""
        
        # Create message
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Get current history
        chat_key = self._get_chat_key(session_id)
        history_data = await self.cache.get(chat_key) or {'messages': []}
        
        # Add message to history
        history_data['messages'].append(message.model_dump(mode='json'))
        
        # Trim history if too long (keep recent messages)
        if len(history_data['messages']) > self.max_history_length:
            history_data['messages'] = history_data['messages'][-self.max_history_length:]
        
        # Update last activity
        history_data['last_activity'] = datetime.utcnow().isoformat()
        
        # Save to Redis with TTL
        await self.cache.set(chat_key, history_data, ttl=self.chat_ttl)
        
        logger.debug(f"Added {role} message to session {session_id}")
        
        return message
    
    async def process_chat_message(
        self, 
        session_id: str, 
        request: ChatRequest
    ) -> ChatResponse:
        """Process a chat message and generate response"""
        
        logger.info(f"Processing chat message for session {session_id} (language: {request.language})")
        
        # Add user message to history
        user_message = await self.add_message(
            session_id=session_id,
            role=MessageRole.USER,
            content=request.message,
            metadata=request.context
        )
        
        # Get conversation history
        history = await self.get_chat_history(session_id)
        
        # Prepare messages for LLM (limit context window)
        context_messages = history.messages[-10:]  # Last 10 messages for context
        
        try:
            # Generate response with language parameter
            response_content, usage_info = await self.llm_provider.generate_response(
                messages=context_messages,
                language=request.language
            )
            
            # Add assistant response to history
            assistant_message = await self.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=response_content,
                metadata={
                    "usage": usage_info,
                    "language": request.language,
                    "model": usage_info.get("model", "unknown")
                }
            )
            
            # Create response
            return ChatResponse(
                message=response_content,
                message_id=str(assistant_message.id) if hasattr(assistant_message, 'id') else "temp-id",
                timestamp=assistant_message.timestamp,
                usage=usage_info
            )
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}")
            
            # Add error message to history
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            
            await self.add_message(
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=error_message,
                metadata={"error": str(e)}
            )
            
            return ChatResponse(
                message=error_message,
                message_id="error-id",
                timestamp=datetime.utcnow(),
                usage=None
            )
    
    async def clear_chat_history(self, session_id: str) -> bool:
        """Clear chat history for a session"""
        chat_key = self._get_chat_key(session_id)
        success = await self.cache.delete(chat_key)
        
        if success:
            logger.info(f"Cleared chat history for session {session_id}")
        
        return success
    
    async def get_chat_status(self, session_id: str) -> ChatStatusResponse:
        """Get chat session status"""
        history = await self.get_chat_history(session_id)
        
        last_activity = None
        if history.messages:
            last_activity = history.messages[-1].timestamp
        
        return ChatStatusResponse(
            session_id=session_id,
            message_count=history.total_messages,
            last_activity=last_activity
        )
    
    async def cleanup_expired_chats(self) -> int:
        """Clean up expired chat sessions (called by scheduler)"""
        # Redis handles expiry automatically with TTL
        # This method is for any additional cleanup if needed
        logger.info("Chat cleanup called (handled by Redis TTL)")
        return 0