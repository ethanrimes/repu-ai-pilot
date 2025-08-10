# backend/src/core/conversation/journeys/product_search/journey.py
from typing import Dict, Any, Optional, Tuple
import yaml
from pathlib import Path

from ...models import ConversationSession, ConversationState
from ..base import BaseJourney
from .states import ProductSearchInitState
from .vehicle_identification import VehicleIdentificationState

class ProductSearchJourney(BaseJourney):
    """Product search customer journey"""
    
    def __init__(self):
        # Load templates
        template_path = Path(__file__).parent / "templates.yaml"
        with open(template_path, 'r', encoding='utf-8') as f:
            self.templates = yaml.safe_load(f)
        
        # Initialize states
        self.states = {
            ConversationState.PRODUCT_SEARCH_INIT: ProductSearchInitState(self.templates),
            ConversationState.VEHICLE_IDENTIFICATION: VehicleIdentificationState(self.templates),
            # ConversationState.VEHICLE_INFO_COLLECTION: VehicleInfoCollectionState(self.templates),
            # ConversationState.PART_TYPE_SELECTION: PartTypeSelectionState(self.templates),
            # ConversationState.PRODUCT_PRESENTATION: ProductPresentationState(self.templates),
        }
    
    def handles_state(self, state: ConversationState) -> bool:
        """Check if this journey handles the given state"""
        return state in self.states
    
    async def process_state(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process message for current state"""
        
        state_handler = self.states.get(session.current_state)
        if not state_handler:
            return "State not implemented", ConversationState.INTENT_MENU, None
        
        return await state_handler.process(session, user_message)
