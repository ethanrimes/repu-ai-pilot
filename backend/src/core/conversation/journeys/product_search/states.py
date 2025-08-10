# ============================================
# journeys/product_search/states.py - Product search states
# ============================================

from typing import Dict, Any, Optional, Tuple
from src.core.conversation.models import ConversationSession, ConversationState
from src.core.conversation.journeys.base import BaseState
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class ProductSearchInitState(BaseState):
    """Initial state for product search journey"""
    
    def __init__(self, templates: Dict[str, Any]):
        super().__init__(templates)
    
    async def process(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process vehicle information"""
        
        language = session.context.language
        
        # Parse vehicle info
        vehicle_info = self.vehicle_parser.parse(user_message)
        
        if vehicle_info.confidence < 0.5:
            # Need more info
            response = self.get_template("need_vehicle_info", language)
            return response, ConversationState.VEHICLE_INFO_COLLECTION, None
        
        # Store vehicle info and move to part selection
        context_updates = {
            "vehicle_make": vehicle_info.make,
            "vehicle_model": vehicle_info.model,
            "vehicle_year": vehicle_info.year
        }
        
        response = self.get_template("vehicle_received", language).format(
            make=vehicle_info.make or "Unknown",
            model=vehicle_info.model or "Unknown",
            year=vehicle_info.year or "Unknown"
        )
        response += "\n\n" + self.get_template("ask_part_type", language)
        
        return response, ConversationState.PART_TYPE_SELECTION, context_updates