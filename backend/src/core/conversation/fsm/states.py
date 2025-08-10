# backend/src/core/conversation/fsm/states.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate

from src.core.conversation.fsm.state_manager import ConversationState, ConversationSession, CustomerIntent
from src.core.conversation.intents.parser import IntentParser, ParsedIntent
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

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

class IntentMenuState(BaseState):
    """State for showing and handling the intent selection menu"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.INTENT_MENU
        self.intent_parser = IntentParser()
    
    def get_entry_message(self, language: str = "es") -> str:
        """Get the intent menu message"""
        if language == "en":
            return """Hello! I'm RepuAI, your specialized assistant for automotive parts in the Colombian market. 🚗

I specialize in brake components and I'm here to help you find the exact parts you need for your vehicle.

Please select the option that best describes what you need:

1. 🛒 **Product Search** - Search for automotive parts  
   [✅ implemented]

2. 🧑‍🔧 **Technical Information**  
   [❌ not implemented]

3. 🚚 **Order Status / Delivery**  
   [❌ not implemented]

4. 🔁 **Returns / Warranty**  
   [❌ not implemented]

5. 🤖 **General/Store Information**  
   [❌ not implemented]

6. 📝 **Other**  
   [❌ not implemented]

Please respond with the number of your choice (1-6)."""
        else:  # Spanish
            return """¡Hola! Soy RepuAI, tu asistente especializado en repuestos automotrices para el mercado colombiano. 🚗

Me especializo en componentes de frenos y estoy aquí para ayudarte a encontrar las piezas exactas que necesitas para tu vehículo.

Por favor selecciona la opción que mejor describe lo que necesitas:

1. 🛒 **Búsqueda de Productos** - Buscar repuestos automotrices  
   [✅ implementado]

2. 🧑‍🔧 **Información Técnica**  
   [❌ no implementado]

3. 🚚 **Estado de Pedido / Entrega**  
   [❌ no implementado]

4. 🔁 **Devoluciones / Garantía**  
   [❌ no implementado]

5. 🤖 **Información General/Tienda**  
   [❌ no implementado]

6. 📝 **Otro**  
   [❌ no implementado]

Por favor responde con el número de tu elección (1-6)."""
    
    async def process_message(self, session: ConversationSession, user_message: str) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle intent selection from the main menu"""
        language = session.context.language
        parsed_intent = self.intent_parser.parse_intent(user_message)
        
        if not parsed_intent.intent:
            # Invalid selection
            response = self._get_invalid_selection_message(user_message, language)
            return response, None, None
        
        if parsed_intent.intent == CustomerIntent.PRODUCT_SEARCH:
            # Start product search journey
            response = self._get_product_search_init_message(language)
            new_state = ConversationState.PRODUCT_SEARCH_INIT
            context_updates = {"selected_intent": parsed_intent.intent.name}
            return response, new_state, context_updates
        
        else:
            # Not implemented functionality
            response = self._get_not_implemented_message(parsed_intent.intent, language)
            return response, None, None
    
    def _get_invalid_selection_message(self, user_input: str, language: str = "es") -> str:
        """Get message for invalid menu selection"""
        if language == "en":
            return f"""I didn't understand your selection "{user_input}". 

Please choose a number from 1 to 6:

1. 🛒 **Product Search**  
   [✅ implemented]

2. 🧑‍🔧 **Technical Information**  
   [❌ not implemented]

3. 🚚 **Order Status / Delivery**  
   [❌ not implemented]

4. 🔁 **Returns / Warranty**  
   [❌ not implemented]

5. 🤖 **General/Store Information**  
   [❌ not implemented]

6. 📝 **Other**  
   [❌ not implemented]

Just type the number (like "1") to make your selection."""
        else:  # Spanish
            return f"""No entendí tu selección "{user_input}".

Por favor elige un número del 1 al 6:

1. 🛒 **Búsqueda de Productos**  
   [✅ implementado]

2. 🧑‍🔧 **Información Técnica**  
   [❌ no implementado]

3. 🚚 **Estado de Pedido / Entrega**  
   [❌ no implementado]

4. 🔁 **Devoluciones / Garantía**  
   [❌ no implementado]

5. 🤖 **Información General/Tienda**  
   [❌ no implementado]

6. 📝 **Otro**  
   [❌ no implementado]

Simplemente escribe el número (como "1") para hacer tu selección."""
    
    def _get_not_implemented_message(self, intent: CustomerIntent, language: str = "es") -> str:
        """Get message for not implemented functionality"""
        intent_names = {
            CustomerIntent.TECHNICAL_INFO: {
                "es": "Información Técnica",
                "en": "Technical Information"
            },
            CustomerIntent.ORDER_STATUS: {
                "es": "Estado de Pedido / Entrega", 
                "en": "Order Status / Delivery"
            },
            CustomerIntent.RETURNS_WARRANTY: {
                "es": "Devoluciones / Garantía",
                "en": "Returns / Warranty"
            },
            CustomerIntent.GENERAL_INFO: {
                "es": "Información General/Tienda",
                "en": "General/Store Information"
            },
            CustomerIntent.OTHER: {
                "es": "Otro",
                "en": "Other"
            }
        }
        
        intent_name = intent_names.get(intent, {}).get(language, "Unknown")
        
        if language == "en":
            return f"""Sorry, the "{intent_name}" functionality is not yet implemented. 

Currently, only **Product Search** is available. Would you like to search for automotive parts instead?

Please select option 1 to start a product search, or let me know how else I can help you!"""
        else:  # Spanish
            return f"""Lo siento, la funcionalidad "{intent_name}" aún no está implementada.

Actualmente, solo está disponible la **Búsqueda de Productos**. ¿Te gustaría buscar repuestos automotrices en su lugar?

Por favor selecciona la opción 1 para iniciar una búsqueda de productos, ¡o déjame saber cómo más puedo ayudarte!"""
    
    def _get_product_search_init_message(self, language: str = "es") -> str:
        """Get product search initialization message"""
        if language == "en":
            return """Perfect! Let's search for the parts you need. 🔍

To help you better, I need information about your vehicle. Please provide me with:

🚗 **Vehicle brand** (e.g: Toyota, Chevrolet, Renault)
📅 **Year** (e.g: 2020, 2018)
🏷️ **Model** (e.g: Corolla, Spark, Logan)

You can write something like: "Toyota Corolla 2020" or give the details step by step.

What's your vehicle information?"""
        else:  # Spanish
            return """¡Perfecto! Vamos a buscar los repuestos que necesitas. 🔍

Para ayudarte mejor, necesito información sobre tu vehículo. Por favor proporcióname:

🚗 **Marca del vehículo** (ej: Toyota, Chevrolet, Renault)
📅 **Año** (ej: 2020, 2018)
🏷️ **Modelo** (ej: Corolla, Spark, Logan)

Puedes escribir algo como: "Toyota Corolla 2020" o dar los detalles paso a paso.

¿Cuál es la información de tu vehículo?"""

class ProductSearchInitState(BaseState):
    """State for initializing product search and collecting vehicle info"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.PRODUCT_SEARCH_INIT
    
    def get_entry_message(self, language: str = "es") -> str:
        """This state doesn't show an entry message as it's handled by the previous state"""
        return ""
    
    async def process_message(self, session: ConversationSession, user_message: str) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle vehicle information collection"""
        language = session.context.language
        
        # For now, we'll transition to a more advanced state handling
        # This is where we would extract vehicle information from the message
        
        if language == "en":
            response = """Great! I received your vehicle information. Let me help you find the right brake parts.

What type of brake component are you looking for?

1. 🛠️ Brake Pads
2. 💿 Brake Discs/Rotors  
3. 🔧 Brake Calipers
4. 🧴 Brake Fluid
5. 🔗 Other brake components

Please select a number (1-5) or describe what you need."""
        else:
            response = """¡Excelente! Recibí la información de tu vehículo. Te ayudo a encontrar las piezas de freno correctas.

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
        
        return response, ConversationState.PART_TYPE_SELECTION, context_updates

class ErrorState(BaseState):
    """State for handling errors"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.ERROR
    
    def get_entry_message(self, language: str = "es") -> str:
        """Get error message"""
        if language == "en":
            return """Sorry, an unexpected error has occurred. 😔

Please try again or contact our support team if the problem persists.

Would you like to return to the main menu?"""
        else:  # Spanish
            return """Lo siento, ha ocurrido un error inesperado. 😔

Por favor intenta de nuevo o contacta a nuestro equipo de soporte si el problema persiste.

¿Te gustaría volver al menú principal?"""
    
    async def process_message(self, session: ConversationSession, user_message: str) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle error state recovery"""
        # Reset to intent menu
        return self.get_entry_message(session.context.language), ConversationState.INTENT_MENU, None

# State factory
STATE_REGISTRY = {
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
