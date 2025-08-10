# backend/src/core/conversation/intents/parser.py

import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from src.core.conversation.fsm.state_manager import CustomerIntent
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
