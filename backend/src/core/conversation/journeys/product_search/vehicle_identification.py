"""Vehicle Identification State for Product Search Journey"""

from typing import Dict, Any, Optional, Tuple
import json
from src.core.conversation.models import ConversationSession, ConversationState
from src.core.conversation.journeys.base import BaseState
from src.core.services.tecdoc_service import TecDocService
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Default TecDoc constants (using values from task requirements)
TECDOC_DEFAULT_LANGUAGE_ID = 4  # Language ID (4 for English/Spanish)
TECDOC_DEFAULT_COUNTRY_ID = 62  # Country ID (62 for Spain)

class VehicleIdentificationState(BaseState):
    """State for vehicle identification through TecDoc integration"""
    
    def __init__(self, templates: Dict[str, Any]):
        super().__init__(templates)
        self.tecdoc_service = TecDocService()
    
    async def process(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process vehicle identification"""
        
        language = session.context.language
        
        # Check if this is a vehicle selection callback from frontend
        if user_message.startswith("VEHICLE_SELECTED:"):
            return await self._handle_vehicle_selection(session, user_message, language)
        
        # Check if this is a TecDoc data request from frontend
        if user_message.startswith("GET_MANUFACTURERS:"):
            return await self._handle_manufacturers_request(session, user_message, language)
        
        if user_message.startswith("GET_MODELS:"):
            return await self._handle_models_request(session, user_message, language)
        
        if user_message.startswith("GET_VEHICLES:"):
            return await self._handle_vehicles_request(session, user_message, language)
        
        # Check if user selected VIN/License plate option (not implemented)
        if user_message == "VIN_LICENSE_OPTION":
            response = self.get_template("vin_not_implemented", language)
            return response, None, None
        
        # Check if user selected make/model option
        if user_message == "MAKE_MODEL_OPTION":
            # Get vehicle types from TecDoc service
            try:
                vehicle_types_result = await self.tecdoc_service.list_vehicle_types()
                vehicle_types = [
                    {"id": vt.id, "vehicleType": vt.vehicleType} 
                    for vt in vehicle_types_result.root
                ]
                
                # Return signal to frontend to open vehicle selection modal with vehicle types
                response = json.dumps({
                    "type": "OPEN_VEHICLE_MODAL",
                    "message": self.get_template("opening_vehicle_selector", language),
                    "vehicleTypes": vehicle_types
                })
                return response, None, None
            except Exception as e:
                logger.error(f"Error fetching vehicle types: {e}")
                response = self.get_template("vehicle_selection_error", language)
                return response, None, None
        
        # Initial entry to this state - show vehicle identification options
        # This includes empty messages from auto-processing
        response = json.dumps({
            "type": "VEHICLE_ID_OPTIONS",
            "message": self.get_template("vehicle_identification_prompt", language),
            "buttons": [
                {
                    "id": "VIN_LICENSE_OPTION",
                    "text": self.get_template("vin_license_button", language),
                    "disabled": True,
                    "note": self.get_template("not_implemented_note", language)
                },
                {
                    "id": "MAKE_MODEL_OPTION", 
                    "text": self.get_template("make_model_button", language),
                    "disabled": False
                }
            ]
        })
        
        return response, None, None
    
    async def _handle_vehicle_selection(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle vehicle selection from frontend"""
        
        try:
            # Parse vehicle data from message
            vehicle_data = json.loads(user_message.replace("VEHICLE_SELECTED:", ""))
            
            # Update context with vehicle information
            context_updates = {
                "vehicle_type_id": vehicle_data.get("vehicle_type_id"),
                "manufacturer_id": vehicle_data.get("manufacturer_id"),
                "model_id": vehicle_data.get("model_id"),
                "vehicle_id": vehicle_data.get("vehicle_id"),
                "vehicle_make": vehicle_data.get("manufacturer_name"),
                "vehicle_model": vehicle_data.get("model_name"),
                "vehicle_year": vehicle_data.get("year"),
                "vehicle_details": vehicle_data
            }
            
            # Format response with vehicle details
            response = self.get_template("vehicle_selected", language).format(
                make=vehicle_data.get("manufacturer_name", "Unknown"),
                model=vehicle_data.get("model_name", "Unknown"),
                engine=vehicle_data.get("engine_name", ""),
                year=vehicle_data.get("year", "Unknown")
            )
            
            # Add prompt for next step
            response += "\n\n" + self.get_template("proceed_to_parts", language)
            
            # Transition to part type selection
            return response, ConversationState.PART_TYPE_SELECTION, context_updates
            
        except Exception as e:
            logger.error(f"Error handling vehicle selection: {e}")
            response = self.get_template("vehicle_selection_error", language)
            return response, None, None
    
    async def _handle_manufacturers_request(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle manufacturers data request from frontend"""
        
        try:
            # Parse type_id from message
            type_id = int(user_message.replace("GET_MANUFACTURERS:", ""))
            
            # Get manufacturers from TecDoc service
            manufacturers_result = await self.tecdoc_service.list_manufacturers(
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=type_id
            )
            
            # Format response for frontend
            manufacturers_data = [
                {
                    "manufacturerId": manufacturer.manufacturerId,
                    "brand": manufacturer.brand
                }
                for manufacturer in manufacturers_result.manufacturers
            ]
            
            response = json.dumps({
                "type": "MANUFACTURERS_DATA",
                "data": manufacturers_data
            })
            
            return response, None, None
            
        except Exception as e:
            logger.error(f"Error fetching manufacturers: {e}")
            response = json.dumps({
                "type": "ERROR",
                "message": "Error loading manufacturers"
            })
            return response, None, None
    
    async def _handle_models_request(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle models data request from frontend"""
        
        try:
            # Parse manufacturer_id and type_id from message
            parts = user_message.replace("GET_MODELS:", "").split(":")
            manufacturer_id = int(parts[0])
            type_id = int(parts[1])
            
            # Get models from TecDoc service
            models_result = await self.tecdoc_service.list_models(
                manufacturer_id=manufacturer_id,
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=type_id
            )
            
            # Format response for frontend
            models_data = [
                {
                    "modelId": model.modelId,
                    "modelName": model.modelName,
                    "modelYearFrom": model.modelYearFrom,
                    "modelYearTo": model.modelYearTo
                }
                for model in models_result.models
            ]
            
            response = json.dumps({
                "type": "MODELS_DATA",
                "data": models_data
            })
            
            return response, None, None
            
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            response = json.dumps({
                "type": "ERROR",
                "message": "Error loading models"
            })
            return response, None, None
    
    async def _handle_vehicles_request(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle vehicles data request from frontend"""
        
        try:
            # Parse model_id, manufacturer_id, and type_id from message
            parts = user_message.replace("GET_VEHICLES:", "").split(":")
            model_id = int(parts[0])
            manufacturer_id = int(parts[1])
            type_id = int(parts[2])
            
            # Get vehicles from TecDoc service
            vehicles_result = await self.tecdoc_service.list_vehicle_engine_types(
                model_id=model_id,
                manufacturer_id=manufacturer_id,
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=type_id
            )
            
            # Format response for frontend
            vehicles_data = [
                {
                    "vehicleId": vehicle.vehicleId,
                    "manufacturerName": vehicle.manufacturerName,
                    "modelName": vehicle.modelName,
                    "typeEngineName": vehicle.typeEngineName,
                    "constructionIntervalStart": vehicle.constructionIntervalStart,
                    "constructionIntervalEnd": vehicle.constructionIntervalEnd,
                    "powerKw": vehicle.powerKw,
                    "powerPs": vehicle.powerPs,
                    "fuelType": vehicle.fuelType,
                    "bodyType": vehicle.bodyType,
                    "numberOfCylinders": vehicle.numberOfCylinders,
                    "capacityLt": vehicle.capacityLt
                }
                for vehicle in vehicles_result.modelTypes
            ]
            
            response = json.dumps({
                "type": "VEHICLES_DATA",
                "data": vehicles_data
            })
            
            return response, None, None
            
        except Exception as e:
            logger.error(f"Error fetching vehicles: {e}")
            response = json.dumps({
                "type": "ERROR",
                "message": "Error loading vehicles"
            })
            return response, None, None
