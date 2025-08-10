# backend/src/core/models/common.py
"""Common type definitions and utilities for all models"""

from typing import Annotated
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BeforeValidator, PlainSerializer, Field

# UUID type that serializes to string for frontend compatibility
BetterUUID = Annotated[
    UUID,
    BeforeValidator(lambda x: UUID(x) if isinstance(x, str) else x),
    PlainSerializer(lambda x: str(x)),
    Field(default_factory=uuid4, description="UUID serialized as string"),
]

# Optional datetime that serializes to ISO string
BetterDateTime = Annotated[
    datetime,
    PlainSerializer(lambda x: x.isoformat() if x else None),
    Field(default_factory=datetime.utcnow, description="DateTime serialized as ISO string"),
]

# Export for easy importing
__all__ = ['BetterUUID', 'BetterDateTime']