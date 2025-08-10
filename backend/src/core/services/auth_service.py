# backend/src/core/services/auth_service.py

# backend/src/core/services/auth_service.py

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session as DBSession
from fastapi import HTTPException, status

from src.infrastructure.integrations.firebase.firebase_config import verify_token
from src.infrastructure.database.repositories.company_repo import CustomerRepository
from src.core.models.company import CustomerCreate
from src.infrastructure.cache.session_manager import get_session_manager
from src.infrastructure.database.repositories.invite_repo import InviteRepository
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication + session orchestration (no HTTP objects)."""

    @staticmethod
    async def login(
        *,
        db: DBSession,
        firebase_token: str,
        channel: str = "web",
        invite_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify Firebase token, require invite code for first-time users,
        create (or reuse) user, and create a session.
        Returns: dict with session_id, user_id, email, name, expires_in
        """
        # 1) Verify Firebase token
        try:
            decoded = verify_token(firebase_token)
            firebase_uid = decoded["uid"]
            email = decoded.get("email", "") or ""
            name = (decoded.get("name") or None) or None
            if isinstance(name, str) and name.strip() == "":
                name = None
        except Exception as e:
            logger.error(f"Firebase token verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token",
            )

        # 2) Find or create user (with invite on first seen)
        customer_repo = CustomerRepository(db)
        user = await customer_repo.get_by_firebase_uid(firebase_uid)

        if not user:
            # Require a valid invite code for first-time creation
            if not invite_code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invite code required",
                )

            invite_repo = InviteRepository(db)
            code_row = await invite_repo.get_valid_code(invite_code)
            if not code_row:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid or expired invite code",
                )

            # Create the user
            user = await customer_repo.create(
                CustomerCreate(firebase_uid=firebase_uid, email=email, name=name)
            )
            logger.info(f"Created new user: {user.id}")

            # Redeem invite (increment uses, optionally log redeemer)
            await invite_repo.redeem(code_id=code_row.id, user_id=user.id)

        # 3) Create session
        session_manager = get_session_manager(db)
        session_info = await session_manager.create_session(
            user_id=user.id, firebase_uid=firebase_uid, channel=channel
        )

        return {
            "session_id": session_info["session_id"],
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "expires_in": session_info["expires_in"],
        }

    @staticmethod
    async def validate_session(
        *, db: DBSession, bearer_token: str
    ) -> Optional[Dict[str, Any]]:
        """Return session dict or None."""
        session_manager = get_session_manager(db)
        return await session_manager.validate_session(bearer_token)

    @staticmethod
    async def logout(*, db: DBSession, session_id: str) -> bool:
        session_manager = get_session_manager(db)
        return await session_manager.end_session(session_id)

    @staticmethod
    async def refresh_session(*, db: DBSession, session_id: str) -> Dict[str, Any]:
        session_manager = get_session_manager(db)
        session_key = session_manager.cache.session_key(session_id)
        await session_manager.cache.expire(session_key, session_manager.session_ttl)
        return {"session_id": session_id, "expires_in": session_manager.session_ttl}

    @staticmethod
    async def get_user_from_session(*, db: DBSession, session: Dict[str, Any]) -> Dict[str, Any]:
        customer_repo = CustomerRepository(db)
        user = await customer_repo.get_by_id(session["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return {"id": user.id, "email": user.email, "name": user.name, "firebase_uid": user.firebase_uid}

    @staticmethod
    async def cleanup_expired_sessions(*, db: DBSession) -> int:
        session_manager = get_session_manager(db)
        return await session_manager.cleanup_expired_sessions()
