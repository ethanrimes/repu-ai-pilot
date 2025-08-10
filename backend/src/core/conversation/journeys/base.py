from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from src.core.conversation.models import ConversationSession, ConversationState

class BaseJourney(ABC):
    """Abstract base class for customer journeys"""
    
    @abstractmethod
    def handles_state(self, state: ConversationState) -> bool:
        """Check if this journey handles the given state"""
        pass
    
    @abstractmethod
    async def process_state(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process message for current state"""
        pass

class BaseState(ABC):
    """Abstract base class for individual states"""
    
    def __init__(self, templates: Dict[str, Any]):
        self.templates = templates
    
    @abstractmethod
    async def process(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process user message in this state"""
        pass
    
    def get_template(self, template_key: str, language: str = "es") -> str:
        """Get message template for language"""
        lang_templates = self.templates.get(language, self.templates.get("es", {}))
        return lang_templates.get(template_key, f"[Missing template: {template_key}]")

