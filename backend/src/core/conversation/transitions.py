# ============================================
# transitions.py - State transition rules
# ============================================

from src.core.conversation.models import ConversationState

# State transition validation rules
VALID_TRANSITIONS = {
    ConversationState.INTENT_MENU: [
        ConversationState.PRODUCT_SEARCH_INIT,
        ConversationState.TECHNICAL_INFO,
        ConversationState.ORDER_STATUS,
        ConversationState.RETURNS_WARRANTY,
        ConversationState.GENERAL_INFO,
        ConversationState.ERROR
    ],
    ConversationState.PRODUCT_SEARCH_INIT: [
        ConversationState.VEHICLE_IDENTIFICATION,  # Now goes to vehicle identification
        ConversationState.INTENT_MENU,
        ConversationState.ERROR
    ],
    ConversationState.VEHICLE_IDENTIFICATION: [
        ConversationState.PART_TYPE_SELECTION,  # After vehicle is identified
        ConversationState.PRODUCT_SEARCH_INIT,  # Go back if needed
        ConversationState.INTENT_MENU,
        ConversationState.ERROR
    ],
    ConversationState.VEHICLE_INFO_COLLECTION: [
        ConversationState.PART_TYPE_SELECTION,
        ConversationState.PRODUCT_SEARCH_INIT,
        ConversationState.ERROR
    ],
    ConversationState.PART_TYPE_SELECTION: [
        ConversationState.PRODUCT_PRESENTATION,
        ConversationState.VEHICLE_INFO_COLLECTION,
        ConversationState.ERROR
    ],
    ConversationState.PRODUCT_PRESENTATION: [
        ConversationState.PRICE_NEGOTIATION,
        ConversationState.ORDER_CONFIRMATION,
        ConversationState.PART_TYPE_SELECTION,
        ConversationState.INTENT_MENU,
        ConversationState.ERROR
    ],
    ConversationState.PRICE_NEGOTIATION: [
        ConversationState.ORDER_CONFIRMATION,
        ConversationState.PRODUCT_PRESENTATION,
        ConversationState.ERROR
    ],
    ConversationState.ORDER_CONFIRMATION: [
        ConversationState.END,
        ConversationState.INTENT_MENU,
        ConversationState.ERROR
    ],
    ConversationState.ERROR: list(ConversationState),
    ConversationState.END: [ConversationState.INTENT_MENU]
}

def is_valid_transition(from_state: ConversationState, to_state: ConversationState) -> bool:
    """Check if state transition is valid"""
    return to_state in VALID_TRANSITIONS.get(from_state, [])
