# backend/src/core/conversation/manager.py
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .models import ConversationSession, ConversationState, ConversationContext
from .transitions import is_valid_transition
from .journeys import get_journey_handler
from .journeys.menu.state import IntentMenuState
from src.infrastructure.cache.cache_manager import CacheManager
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class ConversationManager:
    """Main conversation manager - handles all state management and routing"""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache = cache_manager
        self.session_ttl = 86400  # 24 hours
        self.intent_menu = IntentMenuState()
    
    async def process_message(
        self, 
        session_id: str, 
        user_message: str, 
        language: str = "es"
    ) -> Tuple[str, Dict[str, Any]]:
        """Process user message and return response"""
        
        # Handle initial greeting
        if not user_message or user_message.strip() == "":
            return await self._handle_initial_greeting(session_id, language)
        
        # Get or create session
        session = await self._get_or_create_session(session_id, language)
        
        # Handle language change
        if session.context.language != language:
            session = await self._reset_for_language(session_id, language)
            return self._get_language_change_response(session)
        
        # Route to appropriate handler
        try:
            if session.current_state == ConversationState.INTENT_MENU:
                # Handle menu selection
                response, new_state, context_updates = await self.intent_menu.process_message(
                    session, user_message
                )
            else:
                # Get journey handler for current state
                journey = get_journey_handler(session.current_state)
                if journey:
                    response, new_state, context_updates = await journey.process_state(
                        session, user_message
                    )
                else:
                    # Fallback to menu
                    response = "Sorry, this feature is not implemented yet."
                    new_state = ConversationState.INTENT_MENU
                    context_updates = None
            
            # Update state if needed
            if new_state and new_state != session.current_state:
                if is_valid_transition(session.current_state, new_state):
                    await self._transition_state(session, new_state, context_updates)
                else:
                    logger.warning(f"Invalid transition: {session.current_state} -> {new_state}")
                    response = self._get_error_message(language)
                    await self._transition_state(session, ConversationState.ERROR)
            
            # Prepare metadata
            metadata = {
                "state": session.current_state.value,
                "journey": session.context.current_journey,
                "language": language,
                "message_count": session.message_count
            }
            
            return response, metadata
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._transition_state(session, ConversationState.ERROR)
            return self._get_error_message(language), {"error": str(e)}
    
    async def _get_or_create_session(self, session_id: str, language: str) -> ConversationSession:
        """Get existing or create new session"""
        session_key = f"conversation:{session_id}"
        session_data = await self.cache.get(session_key)
        
        if session_data:
            return ConversationSession.from_dict(session_data)
        
        # Create new session
        session = ConversationSession(
            session_id=session_id,
            current_state=ConversationState.INTENT_MENU,
            context=ConversationContext(language=language)
        )
        
        await self._save_session(session)
        return session
    
    async def _save_session(self, session: ConversationSession):
        """Save session to cache"""
        session.updated_at = datetime.utcnow()
        session_key = f"conversation:{session.session_id}"
        await self.cache.set(session_key, session.to_dict(), ttl=self.session_ttl)
    
    async def _transition_state(
        self, 
        session: ConversationSession,
        new_state: ConversationState,
        context_updates: Optional[Dict[str, Any]] = None
    ):
        """Transition to new state"""
        session.current_state = new_state
        
        if context_updates:
            for key, value in context_updates.items():
                if hasattr(session.context, key):
                    setattr(session.context, key, value)
        
        await self._save_session(session)
    
    async def _handle_initial_greeting(self, session_id: str, language: str) -> Tuple[str, Dict[str, Any]]:
        """Handle initial greeting"""
        session = await self._get_or_create_session(session_id, language)
        response = self.intent_menu.get_entry_message(language)
        
        return response, {
            "state": ConversationState.INTENT_MENU.value,
            "initial_greeting": True,
            "language": language
        }
    
    async def _reset_for_language(self, session_id: str, language: str) -> ConversationSession:
        """Reset session for language change"""
        session = ConversationSession(
            session_id=session_id,
            current_state=ConversationState.INTENT_MENU,
            context=ConversationContext(language=language)
        )
        await self._save_session(session)
        return session
    
    def _get_language_change_response(self, session: ConversationSession) -> Tuple[str, Dict[str, Any]]:
        """Get language change response"""
        lang = session.context.language
        if lang == "es":
            msg = "El idioma ha sido cambiado a español. 🇪🇸\n\n"
        else:
            msg = "Language has been changed to English. 🇺🇸\n\n"
        
        msg += self.intent_menu.get_entry_message(lang)
        
        return msg, {"language_changed": True, "language": lang}
    
    def _get_error_message(self, language: str) -> str:
        """Get error message"""
        if language == "es":
            return "Lo siento, ocurrió un error. Por favor intenta de nuevo."
        return "Sorry, an error occurred. Please try again."
    
    async def reset_conversation_for_language_change(self, session_id: str, language: str) -> tuple[str, Dict[str, Any]]:
        """Reset conversation when language changes and return greeting
        
        This is a convenience method that combines reset and greeting retrieval.
        Used by ChatService when language changes.
        """
        # Reset the session with new language
        session = await self._reset_for_language(session_id, language)
        
        # Get the greeting message in the new language
        response = self._get_language_change_response(session)
        
        # response is already a tuple (message, metadata)
        return response