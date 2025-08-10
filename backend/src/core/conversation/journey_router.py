# backend/src/core/conversation/journey_router.py

from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate

from src.core.conversation.fsm.state_manager import (
    ConversationStateManager, ConversationState, CustomerIntent,
    ConversationSession, is_valid_transition
)
from src.core.conversation.fsm.states import get_state_handler
from src.infrastructure.cache.cache_manager import CacheManager
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class CustomerJourneyRouter:
    """Routes customer conversations through different journey states using LangChain"""
    
    def __init__(self, cache_manager: CacheManager):
        self.state_manager = ConversationStateManager(cache_manager)
        self.cache = cache_manager
    
    async def process_message(self, session_id: str, user_message: str, language: str = "es") -> Tuple[str, Dict[str, Any]]:
        """
        Process user message and return appropriate response based on conversation state
        
        Returns:
            Tuple[response_message, metadata]
        """
        logger.info(f"Processing message for session {session_id} in language {language}")
        
        # Handle empty message (initial greeting request)
        if not user_message or user_message.strip() == "":
            return await self._handle_initial_greeting(session_id, language)
        
        # Get current conversation session
        session = await self.state_manager.get_conversation_session(session_id)
        
        # Update language in context if it has changed
        if session.context.language != language:
            logger.info(f"Language changed from {session.context.language} to {language}, resetting conversation")
            session = await self.state_manager.reset_conversation(session_id, language)
            return self._get_language_change_response(language)
        
        # Increment message count
        await self.state_manager.increment_message_count(session_id)
        
        try:
            # Get state handler and process message
            state_handler = get_state_handler(session.current_state)
            response, new_state, context_updates = await state_handler.process_message(session, user_message)
            
            # Update state if needed
            if new_state and new_state != session.current_state:
                if is_valid_transition(session.current_state, new_state):
                    await self.state_manager.transition_to_state(session_id, new_state, context_updates)
                    logger.info(f"Transitioned session {session_id} to state {new_state}")
                    
                    # If we transitioned to a new state, get its entry message
                    if new_state != session.current_state:
                        new_state_handler = get_state_handler(new_state)
                        entry_message = new_state_handler.get_entry_message(language)
                        if entry_message:
                            response = entry_message
                else:
                    logger.warning(f"Invalid state transition from {session.current_state} to {new_state}")
                    error_handler = get_state_handler(ConversationState.ERROR)
                    response = error_handler.get_entry_message(language)
                    new_state = ConversationState.ERROR
                    await self.state_manager.transition_to_state(session_id, new_state)
            
            # Prepare metadata
            metadata = {
                "conversation_state": new_state.value if new_state else session.current_state.value,
                "message_count": session.message_count + 1,
                "language": language,
                "context_updates": context_updates or {},
                "journey_routing": True
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {e}")
            # Transition to error state
            await self.state_manager.transition_to_state(session_id, ConversationState.ERROR)
            error_handler = get_state_handler(ConversationState.ERROR)
            error_response = error_handler.get_entry_message(language)
            metadata = {
                "conversation_state": ConversationState.ERROR.value,
                "error": str(e),
                "language": language
            }
            return error_response, metadata
    
    async def _handle_initial_greeting(self, session_id: str, language: str) -> Tuple[str, Dict[str, Any]]:
        """Handle initial greeting when no message is provided"""
        # Get or create conversation session
        session = await self.state_manager.get_conversation_session(session_id)
        
        # Update language if needed
        if session.context.language != language:
            session = await self.state_manager.reset_conversation(session_id, language)
        
        # Get the intent menu state handler and return its entry message
        intent_menu_handler = get_state_handler(ConversationState.INTENT_MENU)
        response = intent_menu_handler.get_entry_message(language)
        
        metadata = {
            "conversation_state": ConversationState.INTENT_MENU.value,
            "initial_greeting": True,
            "language": language,
            "journey_routing": True
        }
        
        return response, metadata
    
    def _get_language_change_response(self, language: str) -> Tuple[str, Dict[str, Any]]:
        """Get response for language change"""
        if language == "en":
            change_message = "Language has been changed to English. 🇺🇸\n\nLet's start over. How can I help you today?"
        else:
            change_message = "El idioma ha sido cambiado a español. 🇪🇸\n\nEmpecemos de nuevo. ¿En qué puedo ayudarte hoy?"
        
        # Add the greeting menu
        intent_menu_handler = get_state_handler(ConversationState.INTENT_MENU)
        greeting_menu = intent_menu_handler.get_entry_message(language)
        response = f"{change_message}\n\n{greeting_menu}"
        
        metadata = {
            "conversation_state": ConversationState.INTENT_MENU.value,
            "language_changed": True,
            "language": language,
            "journey_routing": True
        }
        
        return response, metadata
    
    async def reset_conversation_for_language_change(self, session_id: str, language: str) -> Tuple[str, Dict[str, Any]]:
        """Reset conversation when language changes"""
        await self.state_manager.reset_conversation(session_id, language)
        return self._get_language_change_response(language)
