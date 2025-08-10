# backend/src/core/conversation/fsm/states/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from src.core.conversation.fsm.state_manager import ConversationState, ConversationSession

class BaseState(ABC):
    """Base class for all conversation states"""
    
    def __init__(self):
        self.state_name = None
    
    @abstractmethod
    async def process_message(self, session: ConversationSession, user_message: str) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """
        Process user message in this state
        
        Returns:
            Tuple[response_message, new_state, context_updates]
        """
        pass
    
    @abstractmethod
    def get_entry_message(self, language: str = "es") -> str:
        """Get the message to show when entering this state"""
        pass
