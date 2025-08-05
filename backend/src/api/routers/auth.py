# backend/src/api/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from pydantic import BaseModel

from backend.src.infrastructure.cache.session_manager import get_session_manager
from backend.src.infrastructure.integrations.firebase.firebase_config import verify_token
from backend.src.infrastructure.database.repositories.company_repo import CustomerRepository
from backend.src.core.models.company import CustomerCreate
from backend.src.api.dependencies import get_db
from backend.src.shared.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response models
class LoginRequest(BaseModel):
    firebase_token: str
    channel: str = "web"

class LoginResponse(BaseModel):
    session_id: str
    user_id: int
    email: str
    name: str
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
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Validate session from Bearer token"""
    session_manager = get_session_manager()
    session_data = await session_manager.validate_session(credentials.credentials)
    
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session"
        )
    
    return session_data

async def get_current_user(
    session: Dict[str, Any] = Depends(get_current_session),
    db = Depends(get_db)
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
    db = Depends(get_db)
):
    """Login with Firebase token and create session"""
    try:
        # Verify Firebase token
        decoded_token = verify_token(request.firebase_token)
        firebase_uid = decoded_token["uid"]
        email = decoded_token.get("email", "")
        name = decoded_token.get("name", "")
        
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    
    # Get or create user
    customer_repo = CustomerRepository(db)
    user = await customer_repo.get_by_firebase_uid(firebase_uid)
    
    if not user:
        # Create new user
        user_create = CustomerCreate(
            firebase_uid=firebase_uid,
            email=email,
            name=name
        )
        user = await customer_repo.create(user_create)
        logger.info(f"Created new user: {user.id}")
    
    # Create session
    session_manager = get_session_manager()
    session_info = await session_manager.create_session(
        user_id=user.id,
        firebase_uid=firebase_uid,
        channel=request.channel
    )
    
    return LoginResponse(
        session_id=session_info["session_id"],
        user_id=user.id,
        email=user.email,
        name=user.name,
        expires_in=session_info["expires_in"]
    )

@router.post("/logout")
async def logout(
    session: Dict[str, Any] = Depends(get_current_session)
):
    """Logout and end session"""
    session_manager = get_session_manager()
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
    session: Dict[str, Any] = Depends(get_current_session)
):
    """Refresh session TTL"""
    session_manager = get_session_manager()
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