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