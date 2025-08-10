# backend/src/core/conversation/models.py
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

class ConversationState(Enum):
    """All conversation states"""
    # Menu
    INTENT_MENU = "intent_menu"
    
    # Product Search Journey
    PRODUCT_SEARCH_INIT = "product_search_init"
    VEHICLE_INFO_COLLECTION = "vehicle_info_collection"
    PART_TYPE_SELECTION = "part_type_selection"
    PRODUCT_PRESENTATION = "product_presentation"
    PRICE_NEGOTIATION = "price_negotiation"
    ORDER_CONFIRMATION = "order_confirmation"
    
    # Other Journeys (future)
    ORDER_STATUS = "order_status"
    TECHNICAL_INFO = "technical_info"
    RETURNS_WARRANTY = "returns_warranty"
    GENERAL_INFO = "general_info"
    
    # Special
    ERROR = "error"
    END = "end"

class CustomerIntent(Enum):
    """Customer intent options"""
    PRODUCT_SEARCH = 1
    TECHNICAL_INFO = 2
    ORDER_STATUS = 3
    RETURNS_WARRANTY = 4
    GENERAL_INFO = 5
    OTHER = 6

@dataclass
class ConversationContext:
    """Context carried through conversation"""
    # Current journey
    current_journey: Optional[str] = None
    selected_intent: Optional[CustomerIntent] = None
    
    # Vehicle info
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None
    
    # Part info
    part_type: Optional[str] = None
    part_specifications: Optional[Dict[str, Any]] = None
    
    # Search results
    search_results: Optional[List[Dict[str, Any]]] = None
    selected_products: Optional[List[Dict[str, Any]]] = None
    
    # Metadata
    language: str = "es"
    channel: str = "web"
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        return cls(**data)

@dataclass
class ConversationSession:
    """Session state"""
    session_id: str
    current_state: ConversationState
    context: ConversationContext
    message_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "context": self.context.to_dict(),
            "message_count": self.message_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSession":
        return cls(
            session_id=data["session_id"],
            current_state=ConversationState(data["current_state"]),
            context=ConversationContext.from_dict(data["context"]),
            message_count=data.get("message_count", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )