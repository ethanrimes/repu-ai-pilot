# backend/src/core/conversation/fsm/states/__init__.py

from .base import BaseState
from .intent_menu import IntentMenuState

# Import the state registry and factory function from the parent states.py file
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from ..states import get_state_handler, STATE_REGISTRY
except ImportError:
    # Fallback if the main states.py doesn't exist
    from .base import BaseState
    from src.core.conversation.fsm.state_manager import ConversationState
    
    # Simple factory for states
    def get_state_handler(state: ConversationState) -> BaseState:
        if state == ConversationState.INTENT_MENU:
            return IntentMenuState()
        else:
            # Return a simple error state
            class SimpleErrorState(BaseState):
                def get_entry_message(self, language: str = "es") -> str:
                    return "Error occurred"
                async def process_message(self, session, user_message: str):
                    return "Error", None, None
            return SimpleErrorState()
    
    STATE_REGISTRY = {
        ConversationState.INTENT_MENU: IntentMenuState,
    }

__all__ = ['BaseState', 'IntentMenuState', 'get_state_handler', 'STATE_REGISTRY']
