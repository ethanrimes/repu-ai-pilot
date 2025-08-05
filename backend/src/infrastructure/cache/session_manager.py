# backend/src/infrastructure/cache/session_manager.py

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession

from src.infrastructure.cache.cache_manager import get_cache_manager
from src.infrastructure.database.repositories.company_repo import SessionRepository
from src.core.models.company import Session, SessionCreate, SessionUpdate, Channel
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class SessionManager:
    """Manage user sessions in Redis and PostgreSQL"""
    
    def __init__(self, db: Optional[DBSession] = None):
        self.cache = get_cache_manager()
        self.session_ttl = 86400  # 24 hours
        self.refresh_threshold = 3600  # Refresh if less than 1 hour left
        self.db = db
        self._session_repo = None
    
    @property
    def session_repo(self) -> Optional[SessionRepository]:
        """Lazy load session repository"""
        if self._session_repo is None and self.db is not None:
            self._session_repo = SessionRepository(self.db)
        return self._session_repo
    
    async def create_session(
        self,
        user_id: int,
        firebase_uid: str,
        channel: str = "web",
        meta_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new session in both Redis and PostgreSQL"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "firebase_uid": firebase_uid,
            "channel": channel,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "meta_data": meta_data or {}
        }
        
        # Store in Redis for active session management
        session_key = self.cache.session_key(session_id)
        await self.cache.set(session_key, session_data, self.session_ttl)
        
        # Store user -> sessions mapping
        user_sessions_key = f"user_sessions:{user_id}"
        await self.cache.hset(user_sessions_key, session_id, datetime.utcnow().isoformat())
        await self.cache.expire(user_sessions_key, self.session_ttl)
        
        # Store in PostgreSQL for audit/history if repository is available
        if self.session_repo:
            try:
                # Convert channel string to Channel enum
                channel_enum = Channel(channel) if channel in [e.value for e in Channel] else Channel.WEB
                
                session_create = SessionCreate(
                    session_id=session_id,
                    customer_id=user_id,
                    channel=channel_enum,
                    current_state="active",
                    context={"firebase_uid": firebase_uid, **(meta_data or {})}
                )
                await self.session_repo.create(session_create)
                logger.info(f"Session {session_id} created in PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to create session in PostgreSQL: {e}")
                # Don't fail the session creation if DB write fails
        else:
            logger.debug("No session repository available, skipping PostgreSQL storage")
        
        logger.info(f"Created session {session_id} for user {user_id}")
        
        return {
            "session_id": session_id,
            "expires_in": self.session_ttl,
            "user_id": user_id
        }
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        session_key = self.cache.session_key(session_id)
        session_data = await self.cache.get(session_key)
        
        if session_data:
            # Update last activity
            session_data["last_activity"] = datetime.utcnow().isoformat()
            await self.cache.set(session_key, session_data, self.session_ttl)
            
            # Check if we should refresh TTL
            ttl = self.cache.redis.ttl(session_key)
            if ttl < self.refresh_threshold:
                await self.cache.expire(session_key, self.session_ttl)
                logger.debug(f"Refreshed TTL for session {session_id}")
            
            # Also update in PostgreSQL if available
            if self.session_repo:
                try:
                    await self.session_repo.update(
                        session_id,
                        SessionUpdate(current_state="active")
                    )
                except Exception as e:
                    logger.error(f"Failed to update session in PostgreSQL: {e}")
        
        return session_data
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and return session data"""
        session_data = await self.get_session(session_id)
        
        if not session_data:
            logger.warning(f"Session {session_id} not found or expired")
            return None
        
        # Additional validation checks can be added here
        return session_data
    
    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        # Merge updates
        session_data.update(updates)
        session_data["last_activity"] = datetime.utcnow().isoformat()
        
        # Save back to Redis
        session_key = self.cache.session_key(session_id)
        success = await self.cache.set(session_key, session_data, self.session_ttl)
        
        # Update in PostgreSQL if available
        if success and self.session_repo:
            try:
                session_update = SessionUpdate(
                    current_state=updates.get("current_state"),
                    intent=updates.get("intent"),
                    context=updates.get("context")
                )
                await self.session_repo.update(session_id, session_update)
            except Exception as e:
                logger.error(f"Failed to update session in PostgreSQL: {e}")
        
        return success
    
    async def end_session(self, session_id: str) -> bool:
        """End a session in both Redis and PostgreSQL"""
        session_data = await self.get_session(session_id)
        
        if not session_data:
            return False
        
        # Remove from Redis
        session_key = self.cache.session_key(session_id)
        await self.cache.delete(session_key)
        
        # Remove from user sessions
        if "user_id" in session_data:
            user_sessions_key = f"user_sessions:{session_data['user_id']}"
            self.cache.redis.hdel(user_sessions_key, session_id)
        
        # Mark as ended in PostgreSQL
        if self.session_repo:
            try:
                await self.session_repo.end_session(session_id)
                logger.info(f"Session {session_id} ended in PostgreSQL")
            except Exception as e:
                logger.error(f"Failed to end session in PostgreSQL: {e}")
        
        logger.info(f"Ended session {session_id}")
        return True
    
    async def get_user_sessions(self, user_id: int) -> Dict[str, str]:
        """Get all sessions for a user from Redis"""
        user_sessions_key = f"user_sessions:{user_id}"
        return await self.cache.hgetall(user_sessions_key)
    
    async def end_all_user_sessions(self, user_id: int) -> int:
        """End all sessions for a user"""
        sessions = await self.get_user_sessions(user_id)
        count = 0
        
        for session_id in sessions.keys():
            if await self.end_session(session_id):
                count += 1
        
        # Clean up user sessions mapping
        user_sessions_key = f"user_sessions:{user_id}"
        await self.cache.delete(user_sessions_key)
        
        logger.info(f"Ended {count} sessions for user {user_id}")
        return count
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions from PostgreSQL"""
        if not self.session_repo:
            logger.warning("No session repository available for cleanup")
            return 0
        
        try:
            # Get all active sessions from PostgreSQL
            active_sessions = await self.session_repo.get_active_sessions()
            cleaned_count = 0
            
            for session in active_sessions:
                # Check if session exists in Redis
                session_key = self.cache.session_key(session.session_id)
                exists = await self.cache.exists(session_key)
                
                if not exists:
                    # Session expired in Redis, mark as ended in PostgreSQL
                    await self.session_repo.end_session(session.session_id)
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
            return 0

# Singleton instance management
_session_managers: Dict[int, SessionManager] = {}

def get_session_manager(db: Optional[DBSession] = None) -> SessionManager:
    """Get session manager instance, optionally with database session"""
    # If no db provided, return a manager without PostgreSQL support
    if db is None:
        return SessionManager(None)
    
    # Create a new manager with the provided db session
    # We don't cache these because each request might have a different db session
    return SessionManager(db)