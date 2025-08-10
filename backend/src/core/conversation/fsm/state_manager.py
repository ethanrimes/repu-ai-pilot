# backend/src/core/conversation/fsm/state_manager.py

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import json

from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class ConversationState(Enum):
    """States in the customer journey FSM"""
    INITIAL = "initial"
    INTENT_MENU = "intent_menu"  # Changed from INTENT_SELECTION to be more descriptive
    
    # Product Search Journey States
    PRODUCT_SEARCH_INIT = "product_search_init"
    VEHICLE_INFO_COLLECTION = "vehicle_info_collection"
    PART_TYPE_SELECTION = "part_type_selection"
    PRODUCT_PRESENTATION = "product_presentation"
    PRICE_NEGOTIATION = "price_negotiation"
    ORDER_CONFIRMATION = "order_confirmation"
    
    # Future Journey States (not implemented yet)
    TECHNICAL_INFO = "technical_info"
    ORDER_STATUS = "order_status"
    RETURNS_WARRANTY = "returns_warranty"
    GENERAL_INFO = "general_info"
    OTHER = "other"
    
    # Special States
    ERROR = "error"
    END = "end"

class CustomerIntent(Enum):
    """Customer intent options from the menu"""
    PRODUCT_SEARCH = 1
    TECHNICAL_INFO = 2
    ORDER_STATUS = 3
    RETURNS_WARRANTY = 4
    GENERAL_INFO = 5
    OTHER = 6

@dataclass
class ConversationContext:
    """Context data carried through the conversation"""
    # Vehicle information
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_year: Optional[str] = None
    
    # Part information
    part_type: Optional[str] = None
    part_specifications: Optional[Dict[str, Any]] = None
    
    # Search results
    search_results: Optional[List[Dict[str, Any]]] = None
    selected_products: Optional[List[Dict[str, Any]]] = None
    
    # Order information
    quoted_price: Optional[float] = None
    negotiated_price: Optional[float] = None
    order_details: Optional[Dict[str, Any]] = None
    
    # Intent tracking
    selected_intent: Optional[str] = None
    
    # Metadata
    language: str = "es"
    channel: str = "web"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_year": self.vehicle_year,
            "part_type": self.part_type,
            "part_specifications": self.part_specifications,
            "search_results": self.search_results,
            "selected_products": self.selected_products,
            "quoted_price": self.quoted_price,
            "negotiated_price": self.negotiated_price,
            "order_details": self.order_details,
            "selected_intent": self.selected_intent,
            "language": self.language,
            "channel": self.channel
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """Create from dictionary"""
        return cls(**data)

@dataclass
class ConversationSession:
    """Complete conversation session state"""
    session_id: str
    current_state: ConversationState
    context: ConversationContext
    message_count: int = 0
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
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
        """Create from dictionary"""
        return cls(
            session_id=data["session_id"],
            current_state=ConversationState(data["current_state"]),
            context=ConversationContext.from_dict(data["context"]),
            message_count=data.get("message_count", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            updated_at=datetime.fromisoformat(data.get("updated_at", datetime.utcnow().isoformat()))
        )

class ConversationStateManager:
    """Manages conversation state transitions and context"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.state_ttl = 86400  # 24 hours
    
    def _get_conversation_key(self, session_id: str) -> str:
        """Generate Redis key for conversation state"""
        return f"conversation:{session_id}"
    
    async def get_conversation_session(self, session_id: str) -> ConversationSession:
        """Get or create conversation session"""
        conv_key = self._get_conversation_key(session_id)
        session_data = await self.cache.get(conv_key)
        
        if not session_data:
            # Create new session starting with intent menu
            session = ConversationSession(
                session_id=session_id,
                current_state=ConversationState.INTENT_MENU,  # Start with menu
                context=ConversationContext()
            )
            await self.save_conversation_session(session)
            logger.info(f"Created new conversation session {session_id} in state {session.current_state}")
            return session
        
        return ConversationSession.from_dict(session_data)
    
    async def save_conversation_session(self, session: ConversationSession) -> None:
        """Save conversation session to cache"""
        session.updated_at = datetime.utcnow()
        conv_key = self._get_conversation_key(session.session_id)
        await self.cache.set(conv_key, session.to_dict(), ttl=self.state_ttl)
        logger.debug(f"Saved conversation session {session.session_id} in state {session.current_state}")
    
    async def transition_to_state(self, session_id: str, new_state: ConversationState, 
                                 context_updates: Optional[Dict[str, Any]] = None) -> ConversationSession:
        """Transition conversation to a new state"""
        session = await self.get_conversation_session(session_id)
        
        logger.info(f"Transitioning session {session_id} from {session.current_state} to {new_state}")
        
        # Update state
        session.current_state = new_state
        
        # Update context if provided
        if context_updates:
            for key, value in context_updates.items():
                if hasattr(session.context, key):
                    setattr(session.context, key, value)
                else:
                    logger.warning(f"Unknown context key: {key}")
        
        await self.save_conversation_session(session)
        return session
    
    async def reset_conversation(self, session_id: str, language: str = "es") -> ConversationSession:
        """Reset conversation to initial state (used when language changes)"""
        logger.info(f"Resetting conversation for session {session_id} to language {language}")
        
        session = ConversationSession(
            session_id=session_id,
            current_state=ConversationState.INTENT_MENU,  # Start with menu
            context=ConversationContext(language=language)
        )
        await self.save_conversation_session(session)
        return session
    
    async def increment_message_count(self, session_id: str) -> int:
        """Increment message count for session"""
        session = await self.get_conversation_session(session_id)
        session.message_count += 1
        await self.save_conversation_session(session)
        return session.message_count
    
    async def clear_conversation(self, session_id: str) -> bool:
        """Clear conversation state"""
        conv_key = self._get_conversation_key(session_id)
        success = await self.cache.delete(conv_key)
        if success:
            logger.info(f"Cleared conversation state for session {session_id}")
        return success

# State transition validation rules
VALID_TRANSITIONS = {
    ConversationState.INITIAL: [ConversationState.INTENT_MENU],
    ConversationState.INTENT_MENU: [
        ConversationState.PRODUCT_SEARCH_INIT,
        ConversationState.TECHNICAL_INFO,
        ConversationState.ORDER_STATUS,
        ConversationState.RETURNS_WARRANTY,
        ConversationState.GENERAL_INFO,
        ConversationState.OTHER,
        ConversationState.ERROR
    ],
    ConversationState.PRODUCT_SEARCH_INIT: [
        ConversationState.VEHICLE_INFO_COLLECTION,
        ConversationState.INTENT_MENU,  # Allow going back
        ConversationState.ERROR
    ],
    ConversationState.VEHICLE_INFO_COLLECTION: [
        ConversationState.PART_TYPE_SELECTION,
        ConversationState.PRODUCT_SEARCH_INIT,  # Allow going back
        ConversationState.ERROR
    ],
    ConversationState.PART_TYPE_SELECTION: [
        ConversationState.PRODUCT_PRESENTATION,
        ConversationState.VEHICLE_INFO_COLLECTION,  # Allow going back
        ConversationState.ERROR
    ],
    ConversationState.PRODUCT_PRESENTATION: [
        ConversationState.PRICE_NEGOTIATION,
        ConversationState.ORDER_CONFIRMATION,
        ConversationState.PART_TYPE_SELECTION,  # Allow going back
        ConversationState.INTENT_MENU,  # Start new search
        ConversationState.ERROR
    ],
    ConversationState.PRICE_NEGOTIATION: [
        ConversationState.ORDER_CONFIRMATION,
        ConversationState.PRODUCT_PRESENTATION,  # Allow going back
        ConversationState.ERROR
    ],
    ConversationState.ORDER_CONFIRMATION: [
        ConversationState.END,
        ConversationState.INTENT_MENU,  # Start new conversation
        ConversationState.ERROR
    ],
    # Error state can transition anywhere
    ConversationState.ERROR: list(ConversationState),
    # End state can restart
    ConversationState.END: [ConversationState.INTENT_MENU]
}

def is_valid_transition(from_state: ConversationState, to_state: ConversationState) -> bool:
    """Check if state transition is valid"""
    return to_state in VALID_TRANSITIONS.get(from_state, [])
