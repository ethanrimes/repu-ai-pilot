# backend/src/core/conversation/message_templates.py

from typing import Dict, Any, Optional
from src.core.conversation.state_manager import ConversationState, CustomerIntent

class MessageTemplates:
    """Message templates for different conversation states and languages"""
    
    def __init__(self):
        # Initial greeting messages
        self.greetings = {
            "es": """¡Hola! Soy RepuAI, tu asistente especializado en repuestos automotrices para el mercado colombiano. 🚗

Me especializo en componentes de frenos y estoy aquí para ayudarte a encontrar las piezas exactas que necesitas para tu vehículo.

Por favor selecciona la opción que mejor describe lo que necesitas:

1. 🛒 **Búsqueda de Productos** - Buscar repuestos automotrices [implementado]
2. 🧑‍🔧 **Información Técnica** [no implementado]
3. 🚚 **Estado de Pedido / Entrega** [no implementado]
4. 🔁 **Devoluciones / Garantía** [no implementado]
5. 🤖 **Información General/Tienda** [no implementado]
6. 📝 **Otro** [no implementado]

Por favor responde con el número de tu elección (1-6).""",
            
            "en": """Hello! I'm RepuAI, your specialized assistant for automotive parts in the Colombian market. 🚗

I specialize in brake components and I'm here to help you find the exact parts you need for your vehicle.

Please select the option that best describes what you need:

1. 🛒 **Product Search** - Search for automotive parts [implemented]
2. 🧑‍🔧 **Technical Information** [not implemented]
3. 🚚 **Order Status / Delivery** [not implemented]
4. 🔁 **Returns / Warranty** [not implemented]
5. 🤖 **General/Store Information** [not implemented]
6. 📝 **Other** [not implemented]

Please respond with the number of your choice (1-6)."""
        }
        
        # Product search initialization messages
        self.product_search_init = {
            "es": """¡Perfecto! Vamos a buscar los repuestos que necesitas. 🔍

Para ayudarte mejor, necesito información sobre tu vehículo. Por favor proporcióname:

🚗 **Marca del vehículo** (ej: Toyota, Chevrolet, Renault)
📅 **Año** (ej: 2020, 2018)
🏷️ **Modelo** (ej: Corolla, Spark, Logan)

Puedes escribir algo como: "Toyota Corolla 2020" o dar los detalles paso a paso.

¿Cuál es la información de tu vehículo?""",
            
            "en": """Perfect! Let's search for the parts you need. 🔍

To help you better, I need information about your vehicle. Please provide me with:

🚗 **Vehicle brand** (e.g: Toyota, Chevrolet, Renault)
📅 **Year** (e.g: 2020, 2018)
🏷️ **Model** (e.g: Corolla, Spark, Logan)

You can write something like: "Toyota Corolla 2020" or give the details step by step.

What's your vehicle information?"""
        }
        
        # Language change messages
        self.language_changed = {
            "es": """El idioma ha sido cambiado a español. 🇪🇸

Empecemos de nuevo. ¿En qué puedo ayudarte hoy?""",
            
            "en": """Language has been changed to English. 🇺🇸

Let's start over. How can I help you today?"""
        }
        
        # Error messages
        self.error_messages = {
            "es": """Lo siento, ha ocurrido un error inesperado. 😔

Por favor intenta de nuevo o contacta a nuestro equipo de soporte si el problema persiste.

¿Te gustaría volver al menú principal?""",
            
            "en": """Sorry, an unexpected error has occurred. 😔

Please try again or contact our support team if the problem persists.

Would you like to return to the main menu?"""
        }
    
    def get_greeting_message(self, language: str = "es") -> str:
        """Get initial greeting message"""
        return self.greetings.get(language, self.greetings["es"])
    
    def get_product_search_init_message(self, language: str = "es") -> str:
        """Get product search initialization message"""
        return self.product_search_init.get(language, self.product_search_init["es"])
    
    def get_language_changed_message(self, language: str = "es") -> str:
        """Get language change confirmation message"""
        return self.language_changed.get(language, self.language_changed["es"])
    
    def get_error_message(self, language: str = "es") -> str:
        """Get error message"""
        return self.error_messages.get(language, self.error_messages["es"])
    
    def get_confirmation_message(self, intent: CustomerIntent, language: str = "es") -> str:
        """Get confirmation message for selected intent"""
        confirmations = {
            CustomerIntent.PRODUCT_SEARCH: {
                "es": "¡Excelente! Has seleccionado Búsqueda de Productos. Te ayudo a encontrar los repuestos que necesitas.",
                "en": "Excellent! You've selected Product Search. I'll help you find the parts you need."
            }
        }
        
        return confirmations.get(intent, {}).get(language, "")
    
    def get_state_message(self, state: ConversationState, language: str = "es", **kwargs) -> str:
        """Get message for a specific conversation state"""
        if state == ConversationState.INTENT_SELECTION:
            return self.get_greeting_message(language)
        elif state == ConversationState.PRODUCT_SEARCH_INIT:
            return self.get_product_search_init_message(language)
        elif state == ConversationState.ERROR:
            return self.get_error_message(language)
        else:
            # For future states, return a placeholder
            if language == "en":
                return f"This functionality ({state.value}) is under development. Please return to the main menu."
            else:
                return f"Esta funcionalidad ({state.value}) está en desarrollo. Por favor regresa al menú principal."
