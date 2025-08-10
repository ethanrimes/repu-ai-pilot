from typing import Dict, Any, Optional, Tuple
import yaml
from pathlib import Path

from src.core.conversation.models import ConversationSession, ConversationState, CustomerIntent
from src.core.conversation.utils.parser import IntentParser
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class IntentMenuState:
    """Intent menu state handler"""
    
    def __init__(self):
        # Load templates
        template_path = Path(__file__).parent / "templates.yaml"
        with open(template_path, 'r', encoding='utf-8') as f:
            self.templates = yaml.safe_load(f)
        
        self.parser = IntentParser()
    
    def get_entry_message(self, language: str = "es") -> str:
        """Get the intent menu message"""
        return self.templates[language]["menu"]
    
    async def process_message(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process menu selection"""
        
        language = session.context.language
        parsed = self.parser.parse_intent(user_message)
        
        if not parsed.intent:
            # Invalid selection
            response = self.templates[language]["invalid_selection"].format(
                user_input=user_message
            )
            return response, None, None
        
        if parsed.intent == CustomerIntent.PRODUCT_SEARCH:
            # Start product search
            response = self.templates[language]["product_search_selected"]
            new_state = ConversationState.PRODUCT_SEARCH_INIT
            context_updates = {
                "selected_intent": parsed.intent,
                "current_journey": "product_search"
            }
            return response, new_state, context_updates
        
        else:
            # Not implemented
            intent_names = self.templates[language]["intent_names"]
            intent_name = intent_names.get(parsed.intent.name, "Unknown")
            response = self.templates[language]["not_implemented"].format(
                intent_name=intent_name
            )
            return response, None, None
