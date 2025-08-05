# backend/src/api/dependencies.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator, Optional, Dict, Any

from src.infrastructure.integrations.supabase.supabase_config import get_db_pool
from src.infrastructure.cache.session_manager import get_session_manager
from src.config.settings import get_settings

settings = get_settings()

# Create SQLAlchemy engine and session factory
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_optional_session(
    authorization: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Get session if provided, but don't require it"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    session_id = authorization[7:]  # Remove "Bearer " prefix
    session_manager = get_session_manager()
    return await session_manager.get_session(session_id)

async def require_session(
    authorization: Optional[str] = None
) -> Dict[str, Any]:
    """Require valid session"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or invalid"
        )
    
    session_id = authorization[7:]  # Remove "Bearer " prefix
    session_manager = get_session_manager()
    session_data = await session_manager.validate_session(session_id)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return session_data