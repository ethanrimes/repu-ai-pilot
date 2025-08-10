# backend/src/core/models/chat.py

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import uuid4

# Import common types
from src.core.models.common import BetterUUID, BetterDateTime

class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    """Individual chat message"""
    id: BetterUUID = Field(default_factory=uuid4)  # use uuid4 directly
    role: MessageRole
    content: str
    timestamp: BetterDateTime = Field(default_factory=BetterDateTime)
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str = Field(..., min_length=1, max_length=4000)
    context: Optional[Dict[str, Any]] = None
    language: Optional[Literal['es','en']] = Field(default='es', description="Optional language code, defaults to 'es'")

class ChatResponse(BaseModel):
    """Response from chat"""
    message_id: BetterUUID = Field(default_factory=uuid4)  # use uuid4 directly
    message: str
    timestamp: BetterDateTime = Field(default_factory=BetterDateTime)
    usage: Optional[Dict[str, Any]] = None

class ChatHistory(BaseModel):
    """Chat history for a session"""
    session_id: str  # Keep as string since it comes from session
    messages: List[ChatMessage]
    total_messages: int
    last_activity: Optional[BetterDateTime] = None

class ChatStatusResponse(BaseModel):
    """Chat session status"""
    session_id: str  # Keep as string since it comes from session
    message_count: int
    last_activity: Optional[BetterDateTime] = None