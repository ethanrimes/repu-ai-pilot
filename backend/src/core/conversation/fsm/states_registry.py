# backend/src/core/conversation/fsm/states_registry.py

from typing import Dict, Type
from src.core.conversation.fsm.state_manager import ConversationState
from src.core.conversation.fsm.states.base import BaseState
from src.core.conversation.fsm.states.intent_menu import IntentMenuState
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class ProductSearchInitState(BaseState):
    """State for initializing product search and collecting vehicle info"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.PRODUCT_SEARCH_INIT
    
    def get_entry_message(self, language: str = "es") -> str:
        """This state doesn't show an entry message as it's handled by the previous state"""
        return ""
    
    async def process_message(self, session, user_message: str):
        """Handle vehicle information collection"""
        from typing import Dict, Any, Optional, Tuple
        from datetime import datetime
        from src.core.conversation.utils.message_formatter import MessageFormatter
        
        language = session.context.language
        
        # For now, we'll transition to a more advanced state handling
        # This is where we would extract vehicle information from the message
        
        if language == "en":
            content = """Great! I received your vehicle information. Let me help you find the right brake parts.

What type of brake component are you looking for?

1. 🛠️ Brake Pads
2. 💿 Brake Discs/Rotors  
3. 🔧 Brake Calipers
4. 🧴 Brake Fluid
5. 🔗 Other brake components

Please select a number (1-5) or describe what you need."""
        else:
            content = """¡Excelente! Recibí la información de tu vehículo. Te ayudo a encontrar las piezas de freno correctas.

¿Qué tipo de componente de freno estás buscando?

1. 🛠️ Pastillas de Freno
2. 💿 Discos de Freno
3. 🔧 Calipers de Freno
4. 🧴 Líquido de Frenos
5. 🔗 Otros componentes de freno

Por favor selecciona un número (1-5) o describe lo que necesitas."""
        
        # Store vehicle info in context (simplified for now)
        context_updates = {
            "vehicle_info_raw": user_message,
            "vehicle_info_timestamp": datetime.utcnow().isoformat()
        }
        
        response = MessageFormatter.format_for_chat(content)
        return response, ConversationState.PART_TYPE_SELECTION, context_updates

class ErrorState(BaseState):
    """State for handling errors"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.ERROR
    
    def get_entry_message(self, language: str = "es") -> str:
        """Get error message"""
        from src.core.conversation.utils.message_formatter import MessageFormatter
        
        if language == "en":
            content = """Sorry, an unexpected error has occurred. 😔

Please try again or contact our support team if the problem persists.

Would you like to return to the main menu?"""
        else:  # Spanish
            content = """Lo siento, ha ocurrido un error inesperado. 😔

Por favor intenta de nuevo o contacta a nuestro equipo de soporte si el problema persiste.

¿Te gustaría volver al menú principal?"""
        
        return MessageFormatter.format_for_chat(content)
    
    async def process_message(self, session, user_message: str):
        """Handle error state recovery"""
        # Reset to intent menu
        return self.get_entry_message(session.context.language), ConversationState.INTENT_MENU, None

# State factory
STATE_REGISTRY: Dict[ConversationState, Type[BaseState]] = {
    ConversationState.INTENT_MENU: IntentMenuState,
    ConversationState.PRODUCT_SEARCH_INIT: ProductSearchInitState,
    ConversationState.ERROR: ErrorState,
}

def get_state_handler(state: ConversationState) -> BaseState:
    """Get state handler instance for a given state"""
    state_class = STATE_REGISTRY.get(state)
    if not state_class:
        logger.warning(f"No handler found for state {state}, using error state")
        return ErrorState()
    
    return state_class()
