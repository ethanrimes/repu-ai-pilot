# backend/src/api/routers/chat.py

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Dict, Any, Optional

from src.core.models.chat import (
    ChatRequest, ChatResponse, ChatHistory, ChatStatusResponse
)
from src.core.services.chat_service import ChatService
from src.infrastructure.cache.cache_manager import get_cache_manager
from src.api.dependencies import require_session  # Changed from get_current_session
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

def get_chat_service() -> ChatService:
    """Get chat service instance"""
    cache_manager = get_cache_manager()
    return ChatService(cache_manager)

@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    authorization: Optional[str] = Header(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a chat message and get AI response
    
    - Requires valid session
    - Message is stored in Redis tied to session
    - Returns AI-generated response
    """
    # Get session using the require_session dependency
    session = await require_session(authorization)
    
    try:
        session_id = session["session_id"]
        logger.info(f"Processing chat message for session {session_id}")
        
        response = await chat_service.process_chat_message(
            session_id=session_id,
            request=request
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/history", response_model=ChatHistory)
async def get_chat_history(
    authorization: Optional[str] = Header(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat history for current session
    
    - Returns all messages in the current session
    - Messages are ordered chronologically
    """
    session = await require_session(authorization)
    session_id = session["session_id"]
    
    history = await chat_service.get_chat_history(session_id)
    
    return history

@router.delete("/history")
async def clear_chat_history(
    authorization: Optional[str] = Header(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Clear chat history for current session
    
    - Removes all messages from Redis
    - Useful for starting a new conversation
    """
    session = await require_session(authorization)
    session_id = session["session_id"]
    
    success = await chat_service.clear_chat_history(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )
    
    return {"message": "Chat history cleared successfully"}

@router.get("/status", response_model=ChatStatusResponse)
async def get_chat_status(
    authorization: Optional[str] = Header(None),
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get chat session status
    
    - Returns message count and last activity
    - Useful for UI indicators
    """
    session = await require_session(authorization)
    session_id = session["session_id"]
    
    status = await chat_service.get_chat_status(session_id)
    
    return status