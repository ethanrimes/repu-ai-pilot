# backend/src/core/conversation/intent_parser.py

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.core.conversation.state_manager import CustomerIntent
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class ParsedIntent:
    """Result of intent parsing"""
    intent: Optional[CustomerIntent]
    confidence: float
    raw_input: str
    extracted_number: Optional[int] = None
    
class IntentParser:
    """Parser for extracting customer intent from user input"""
    
    def __init__(self):
        # Patterns for number extraction (support various formats)
        self.number_patterns = [
            r'^(\d+)\.?\s*$',  # Just a number: "1", "1.", "1 "
            r'^\s*(\d+)\s*$',  # Number with spaces: " 1 "
            r'opci[oó]n\s+(\d+)',  # Spanish: "opción 1"
            r'option\s+(\d+)',  # English: "option 1"
            r'n[uú]mero\s+(\d+)',  # Spanish: "número 1"
            r'number\s+(\d+)',  # English: "number 1"
            r'^\s*(\d+)\s*[.,-]',  # Number with punctuation
        ]
        
        # Text-based intent mapping (fallback)
        self.text_intent_mapping = {
            # Spanish keywords
            "búsqueda": CustomerIntent.PRODUCT_SEARCH,
            "buscar": CustomerIntent.PRODUCT_SEARCH,
            "producto": CustomerIntent.PRODUCT_SEARCH,
            "repuesto": CustomerIntent.PRODUCT_SEARCH,
            "parte": CustomerIntent.PRODUCT_SEARCH,
            "freno": CustomerIntent.PRODUCT_SEARCH,
            
            "técnico": CustomerIntent.TECHNICAL_INFO,
            "técnica": CustomerIntent.TECHNICAL_INFO,
            "información": CustomerIntent.TECHNICAL_INFO,
            "especificación": CustomerIntent.TECHNICAL_INFO,
            
            "pedido": CustomerIntent.ORDER_STATUS,
            "orden": CustomerIntent.ORDER_STATUS,
            "entrega": CustomerIntent.ORDER_STATUS,
            "estado": CustomerIntent.ORDER_STATUS,
            
            "devolución": CustomerIntent.RETURNS_WARRANTY,
            "garantía": CustomerIntent.RETURNS_WARRANTY,
            "retorno": CustomerIntent.RETURNS_WARRANTY,
            
            "general": CustomerIntent.GENERAL_INFO,
            "tienda": CustomerIntent.GENERAL_INFO,
            "empresa": CustomerIntent.GENERAL_INFO,
            
            "otro": CustomerIntent.OTHER,
            "otra": CustomerIntent.OTHER,
            
            # English keywords
            "search": CustomerIntent.PRODUCT_SEARCH,
            "product": CustomerIntent.PRODUCT_SEARCH,
            "part": CustomerIntent.PRODUCT_SEARCH,
            "brake": CustomerIntent.PRODUCT_SEARCH,
            
            "technical": CustomerIntent.TECHNICAL_INFO,
            "specification": CustomerIntent.TECHNICAL_INFO,
            "info": CustomerIntent.TECHNICAL_INFO,
            
            "order": CustomerIntent.ORDER_STATUS,
            "delivery": CustomerIntent.ORDER_STATUS,
            "status": CustomerIntent.ORDER_STATUS,
            
            "return": CustomerIntent.RETURNS_WARRANTY,
            "warranty": CustomerIntent.RETURNS_WARRANTY,
            
            "store": CustomerIntent.GENERAL_INFO,
            "company": CustomerIntent.GENERAL_INFO,
            
            "other": CustomerIntent.OTHER,
        }
    
    def parse_intent(self, user_input: str) -> ParsedIntent:
        """Parse user input to extract intent"""
        if not user_input or not user_input.strip():
            return ParsedIntent(
                intent=None,
                confidence=0.0,
                raw_input=user_input
            )
        
        user_input_clean = user_input.strip().lower()
        
        # First, try to extract a number
        extracted_number = self._extract_number(user_input_clean)
        
        if extracted_number is not None:
            # Map number to intent
            intent = self._number_to_intent(extracted_number)
            confidence = 0.9 if intent else 0.1
            
            return ParsedIntent(
                intent=intent,
                confidence=confidence,
                raw_input=user_input,
                extracted_number=extracted_number
            )
        
        # Fallback: try text-based intent detection
        intent, confidence = self._detect_text_intent(user_input_clean)
        
        return ParsedIntent(
            intent=intent,
            confidence=confidence,
            raw_input=user_input
        )
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract number from text using various patterns"""
        for pattern in self.number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    number = int(match.group(1))
                    logger.debug(f"Extracted number {number} from text: {text}")
                    return number
                except ValueError:
                    continue
        return None
    
    def _number_to_intent(self, number: int) -> Optional[CustomerIntent]:
        """Map number selection to customer intent"""
        try:
            # Direct mapping to enum values
            if 1 <= number <= 6:
                return CustomerIntent(number)
            else:
                logger.warning(f"Number {number} is out of valid range (1-6)")
                return None
        except ValueError:
            logger.warning(f"Invalid intent number: {number}")
            return None
    
    def _detect_text_intent(self, text: str) -> tuple[Optional[CustomerIntent], float]:
        """Detect intent from text keywords (fallback method)"""
        # Look for keywords in the text
        found_intents = []
        
        for keyword, intent in self.text_intent_mapping.items():
            if keyword in text:
                found_intents.append(intent)
        
        if not found_intents:
            return None, 0.0
        
        # If multiple intents found, pick the most common one
        # For now, just return the first one with medium confidence
        return found_intents[0], 0.6
    
    def get_intent_menu_text(self, language: str = "es") -> str:
        """Get the intent selection menu text"""
        if language == "en":
            return """Please select the option that best describes what you need:

1. 🛒 **Product Search** - Search for automotive parts [implemented]
2. 🧑‍🔧 **Technical Information** [not implemented]
3. 🚚 **Order Status / Delivery** [not implemented]  
4. 🔁 **Returns / Warranty** [not implemented]
5. 🤖 **General/Store Information** [not implemented]
6. 📝 **Other** [not implemented]

Please respond with the number of your choice (1-6)."""
        else:  # Spanish
            return """Por favor selecciona la opción que mejor describe lo que necesitas:

1. 🛒 **Búsqueda de Productos** - Buscar repuestos automotrices [implementado]
2. 🧑‍🔧 **Información Técnica** [no implementado]
3. 🚚 **Estado de Pedido / Entrega** [no implementado]
4. 🔁 **Devoluciones / Garantía** [no implementado]
5. 🤖 **Información General/Tienda** [no implementado]
6. 📝 **Otro** [no implementado]

Por favor responde con el número de tu elección (1-6)."""
    
    def get_not_implemented_message(self, intent: CustomerIntent, language: str = "es") -> str:
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

    def get_invalid_selection_message(self, user_input: str, language: str = "es") -> str:
        """Get message for invalid menu selection"""
        if language == "en":
            return f"""I didn't understand your selection "{user_input}". 

Please choose a number from 1 to 6:

1. 🛒 Product Search [implemented]
2. 🧑‍🔧 Technical Information [not implemented]
3. 🚚 Order Status / Delivery [not implemented]
4. 🔁 Returns / Warranty [not implemented]
5. 🤖 General/Store Information [not implemented]
6. 📝 Other [not implemented]

Just type the number (like "1") to make your selection."""
        else:  # Spanish
            return f"""No entendí tu selección "{user_input}".

Por favor elige un número del 1 al 6:

1. 🛒 Búsqueda de Productos [implementado]
2. 🧑‍🔧 Información Técnica [no implementado]
3. 🚚 Estado de Pedido / Entrega [no implementado]
4. 🔁 Devoluciones / Garantía [no implementado]
5. 🤖 Información General/Tienda [no implementado]
6. 📝 Otro [no implementado]

Solo escribe el número (como "1") para hacer tu selección."""
