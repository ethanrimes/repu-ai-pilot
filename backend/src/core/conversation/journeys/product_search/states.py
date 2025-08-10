# ============================================
# journeys/product_search/states.py - Product search states
# ============================================

from typing import Dict, Any, Optional, Tuple
from src.core.conversation.models import ConversationSession, ConversationState
from src.core.conversation.journeys.base import BaseState
from src.core.conversation.journeys.product_search.vehicle_identification import VehicleIdentificationState
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
        """Process initial product search request - redirect to vehicle identification"""
        
        language = session.context.language
        
        # Import here to avoid circular imports
        import json
        from src.core.services.tecdoc_service import TecDocService
        
        # Initialize TecDoc service
        tecdoc_service = TecDocService()
        
        try:
            # Get vehicle types from TecDoc service
            vehicle_types_result = await tecdoc_service.list_vehicle_types()
            vehicle_types = [
                {"id": vt.id, "vehicleType": vt.vehicleType} 
                for vt in vehicle_types_result.root
            ]
            
            # Get templates from the same template structure used by this journey
            lang_templates = self.templates.get(language, self.templates.get("es", {}))
            
            # Directly return vehicle identification options with vehicle types
            response = json.dumps({
                "type": "VEHICLE_ID_OPTIONS",
                "message": lang_templates.get("vehicle_identification_prompt", "Para identificar tu vehículo, puedes elegir una de estas opciones:"),
                "buttons": [
                    {
                        "id": "VIN_LICENSE_OPTION",
                        "text": lang_templates.get("vin_license_button", "🔍 Proceder con VIN o matrícula"),
                        "disabled": True,
                        "note": lang_templates.get("not_implemented_note", "(No implementado)")
                    },
                    {
                        "id": "MAKE_MODEL_OPTION", 
                        "text": lang_templates.get("make_model_button", "🚗 Buscar por marca y modelo"),
                        "disabled": False
                    }
                ],
                "vehicleTypes": vehicle_types
            })
            
            return response, ConversationState.VEHICLE_IDENTIFICATION, None
            
        except Exception as e:
            logger.error(f"Error in ProductSearchInitState: {e}")
            # Fallback to simple transition
            response = ""
            return response, ConversationState.VEHICLE_IDENTIFICATION, None
