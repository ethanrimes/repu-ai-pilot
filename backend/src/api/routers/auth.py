# backend/src/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session as DBSession
from typing import Optional, Dict, Any
from pydantic import BaseModel

from src.infrastructure.cache.session_manager import get_session_manager, SessionManager
from src.infrastructure.integrations.firebase.firebase_config import verify_token
from src.infrastructure.database.repositories.company_repo import CustomerRepository
from src.core.models.company import CustomerCreate
from src.api.dependencies import get_db
from src.shared.utils.logger import get_logger
from src.core.services.auth_service import AuthService  # NEW IMPORT

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    firebase_token: str
    channel: str = "web"
    invite_code: Optional[str] = None  # NEW

class LoginResponse(BaseModel):
    session_id: str
    user_id: int
    email: str
    name: Optional[str]
    expires_in: int

class SessionResponse(BaseModel):
    session_id: str
    user_id: int
    firebase_uid: str
    channel: str
    created_at: str
    last_activity: str

# Dependencies
async def get_current_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: DBSession = Depends(get_db)
) -> Dict[str, Any]:
    """Validate session from Bearer token"""
    session_manager = get_session_manager(db)
    session_data = await session_manager.validate_session(credentials.credentials)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return session_data

async def get_current_user(
    session: Dict[str, Any] = Depends(get_current_session),
    db: DBSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user from session"""
    customer_repo = CustomerRepository(db)
    user = await customer_repo.get_by_id(session["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "firebase_uid": user.firebase_uid
    }

# Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: DBSession = Depends(get_db)
):
    """Login with Firebase token and create session (invite enforced for new users)."""
    auth_result = await AuthService.login(
        db=db,
        firebase_token=request.firebase_token,
        channel=request.channel,
        invite_code=request.invite_code,
    )
    return LoginResponse(**auth_result)

@router.post("/logout")
async def logout(
    session: Dict[str, Any] = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """Logout and end session"""
    session_manager = get_session_manager(db)
    success = await session_manager.end_session(session["session_id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to end session"
        )
    
    return {"message": "Logged out successfully"}

@router.get("/session", response_model=SessionResponse)
async def get_session(
    session: Dict[str, Any] = Depends(get_current_session)
):
    """Get current session info"""
    return SessionResponse(**session)

@router.post("/refresh")
async def refresh_session(
    session: Dict[str, Any] = Depends(get_current_session),
    db: DBSession = Depends(get_db)
):
    """Refresh session TTL"""
    session_manager = get_session_manager(db)
    session_key = session_manager.cache.session_key(session["session_id"])
    
    # Refresh TTL
    await session_manager.cache.expire(session_key, session_manager.session_ttl)
    
    return {
        "session_id": session["session_id"],
        "expires_in": session_manager.session_ttl
    }

@router.get("/me")
async def get_current_user_info(
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information"""
    return user

# Admin endpoint for manual session cleanup
@router.post("/cleanup-sessions", include_in_schema=False)
async def cleanup_expired_sessions(
    db: DBSession = Depends(get_db),
    # Add admin authentication here if needed
):
    """Manual session cleanup (for admin use or cron job)"""
    session_manager = get_session_manager(db)
    count = await session_manager.cleanup_expired_sessions()
    return {"cleaned_up": count, "message": f"Cleaned up {count} expired sessions"}