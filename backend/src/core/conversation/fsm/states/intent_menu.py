# backend/src/core/conversation/fsm/states/intent_menu.py

from typing import Dict, Any, Optional, Tuple
from src.core.conversation.fsm.state_manager import ConversationState, ConversationSession, CustomerIntent
from src.core.conversation.intents.parser import IntentParser
from src.core.conversation.utils.message_formatter import MessageFormatter
from src.core.conversation.fsm.states.base import BaseState
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class IntentMenuState(BaseState):
    """State for showing and handling the intent selection menu"""
    
    def __init__(self):
        super().__init__()
        self.state_name = ConversationState.INTENT_MENU
        self.intent_parser = IntentParser()
    
    def get_entry_message(self, language: str = "es") -> str:
        """Get the intent menu message with proper formatting"""
        if language == "en":
            greeting = "Hello! I'm RepuAI, your specialized assistant for automotive parts in the Colombian market. 🚗"
            intro = "I specialize in brake components and I'm here to help you find the exact parts you need for your vehicle."
            instruction = "Please select the option that best describes what you need:"
            
            options = [
                "1. 🛒 **Product Search** - Search for automotive parts",
                "   ✅ implemented",
                "",
                "2. 🧑‍🔧 **Technical Information**",
                "   ❌ not implemented",
                "",
                "3. 🚚 **Order Status / Delivery**",
                "   ❌ not implemented", 
                "",
                "4. 🔁 **Returns / Warranty**",
                "   ❌ not implemented",
                "",
                "5. 🤖 **General/Store Information**",
                "   ❌ not implemented",
                "",
                "6. 📝 **Other**",
                "   ❌ not implemented"
            ]
            
            footer = "Please respond with the number of your choice (1-6)."
            
        else:  # Spanish
            greeting = "¡Hola! Soy RepuAI, tu asistente especializado en repuestos automotrices para el mercado colombiano. 🚗"
            intro = "Me especializo en componentes de frenos y estoy aquí para ayudarte a encontrar las piezas exactas que necesitas para tu vehículo."
            instruction = "Por favor selecciona la opción que mejor describe lo que necesitas:"
            
            options = [
                "1. 🛒 **Búsqueda de Productos** - Buscar repuestos automotrices",
                "   ✅ implementado",
                "",
                "2. 🧑‍🔧 **Información Técnica**",
                "   ❌ no implementado",
                "",
                "3. 🚚 **Estado de Pedido / Entrega**",
                "   ❌ no implementado",
                "",
                "4. 🔁 **Devoluciones / Garantía**",
                "   ❌ no implementado",
                "",
                "5. 🤖 **Información General/Tienda**",
                "   ❌ no implementado",
                "",
                "6. 📝 **Otro**",
                "   ❌ no implementado"
            ]
            
            footer = "Por favor responde con el número de tu elección (1-6)."
        
        # Combine all parts
        content_parts = [greeting, "", intro, "", instruction, ""] + options + ["", footer]
        content = "\n".join(content_parts)
        
        # Apply formatting
        return MessageFormatter.format_for_chat(content)
    
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
            error_msg = f'I didn\'t understand your selection "{user_input}".'
            instruction = "Please choose a number from 1 to 6:"
            
            options = [
                "1. 🛒 **Product Search**",
                "   ✅ implemented",
                "",
                "2. 🧑‍🔧 **Technical Information**",
                "   ❌ not implemented",
                "",
                "3. 🚚 **Order Status / Delivery**",
                "   ❌ not implemented",
                "",
                "4. 🔁 **Returns / Warranty**", 
                "   ❌ not implemented",
                "",
                "5. 🤖 **General/Store Information**",
                "   ❌ not implemented",
                "",
                "6. 📝 **Other**",
                "   ❌ not implemented"
            ]
            
            footer = 'Just type the number (like "1") to make your selection.'
            
        else:  # Spanish
            error_msg = f'No entendí tu selección "{user_input}".'
            instruction = "Por favor elige un número del 1 al 6:"
            
            options = [
                "1. 🛒 **Búsqueda de Productos**",
                "   ✅ implementado",
                "",
                "2. 🧑‍🔧 **Información Técnica**",
                "   ❌ no implementado",
                "",
                "3. 🚚 **Estado de Pedido / Entrega**",
                "   ❌ no implementado",
                "",
                "4. 🔁 **Devoluciones / Garantía**",
                "   ❌ no implementado",
                "",
                "5. 🤖 **Información General/Tienda**",
                "   ❌ no implementado",
                "",
                "6. 📝 **Otro**",
                "   ❌ no implementado"
            ]
            
            footer = 'Simplemente escribe el número (como "1") para hacer tu selección.'
        
        # Combine all parts
        content_parts = [error_msg, "", instruction, ""] + options + ["", footer]
        content = "\n".join(content_parts)
        
        return MessageFormatter.format_for_chat(content)
    
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
            content = f"""Sorry, the "{intent_name}" functionality is not yet implemented.

Currently, only **Product Search** is available. Would you like to search for automotive parts instead?

Please select option 1 to start a product search, or let me know how else I can help you!"""
        else:  # Spanish
            content = f"""Lo siento, la funcionalidad "{intent_name}" aún no está implementada.

Actualmente, solo está disponible la **Búsqueda de Productos**. ¿Te gustaría buscar repuestos automotrices en su lugar?

Por favor selecciona la opción 1 para iniciar una búsqueda de productos, ¡o déjame saber cómo más puedo ayudarte!"""
        
        return MessageFormatter.format_for_chat(content)
    
    def _get_product_search_init_message(self, language: str = "es") -> str:
        """Get product search initialization message"""
        if language == "en":
            content = """Perfect! Let's search for the parts you need. 🔍

To help you better, I need information about your vehicle. Please provide me with:

🚗 **Vehicle brand** (e.g: Toyota, Chevrolet, Renault)
📅 **Year** (e.g: 2020, 2018)
🏷️ **Model** (e.g: Corolla, Spark, Logan)

You can write something like: "Toyota Corolla 2020" or give the details step by step.

What's your vehicle information?"""
        else:  # Spanish
            content = """¡Perfecto! Vamos a buscar los repuestos que necesitas. 🔍

Para ayudarte mejor, necesito información sobre tu vehículo. Por favor proporcióname:

🚗 **Marca del vehículo** (ej: Toyota, Chevrolet, Renault)
📅 **Año** (ej: 2020, 2018)
🏷️ **Modelo** (ej: Corolla, Spark, Logan)

Puedes escribir algo como: "Toyota Corolla 2020" o dar los detalles paso a paso.

¿Cuál es la información de tu vehículo?"""
        
        return MessageFormatter.format_for_chat(content)
