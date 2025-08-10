from typing import Optional
from src.core.conversation.models import ConversationState
from src.core.conversation.journeys.base import BaseJourney

# Import journey implementations
from src.core.conversation.journeys.product_search.journey import ProductSearchJourney

# Journey registry
_journeys = {
    "product_search": ProductSearchJourney(),
}

def get_journey_handler(state: ConversationState) -> Optional[BaseJourney]:
    """Get journey handler for a given state"""
    for journey in _journeys.values():
        if journey.handles_state(state):
            return journey
    return None