# ============================================
# utils/parser.py - Consolidated parser utilities
# ============================================

import re
from typing import Optional, Dict, Any
from dataclasses import dataclass
from src.core.conversation.models import CustomerIntent
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
    """Parses user input to extract customer intent"""
    
    def __init__(self):
        # Map of number strings to CustomerIntent
        self.intent_mapping = {
            "1": CustomerIntent.PRODUCT_SEARCH,
            "2": CustomerIntent.TECHNICAL_INFO,
            "3": CustomerIntent.ORDER_STATUS,
            "4": CustomerIntent.RETURNS_WARRANTY,
            "5": CustomerIntent.GENERAL_INFO,
            "6": CustomerIntent.OTHER,
        }
    
    def parse_intent(self, user_input: str) -> ParsedIntent:
        """Parse user input to extract intent"""
        if not user_input:
            return ParsedIntent(
                intent=None,
                confidence=0.0,
                raw_input=user_input
            )
        
        # Clean and normalize input
        cleaned_input = user_input.strip()
        
        # Try to extract number from input
        number_match = re.search(r'\d+', cleaned_input)
        extracted_number = None
        
        if number_match:
            extracted_number = int(number_match.group())
            number_str = str(extracted_number)
            
            # Check if it's a valid intent option
            if number_str in self.intent_mapping:
                return ParsedIntent(
                    intent=self.intent_mapping[number_str],
                    confidence=1.0,
                    raw_input=user_input,
                    extracted_number=extracted_number
                )
        
        # If no valid number found, return no intent
        return ParsedIntent(
            intent=None,
            confidence=0.0,
            raw_input=user_input,
            extracted_number=extracted_number
        )