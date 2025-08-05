# backend/src/api/middleware/rate_limiter.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from backend.src.infrastructure.cache.cache_manager import get_cache_manager
from backend.src.shared.utils.logger import get_logger
from typing import Optional
import time
import uuid

logger = get_logger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.cache = get_cache_manager()
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get identifier (IP address or session ID)
        identifier = self._get_identifier(request)
        
        # Check rate limit
        if not await self._check_rate_limit(identifier, request.url.path):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get identifier for rate limiting"""
        # Try to get session ID from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return f"session:{auth_header[7:]}"
        
        # Fall back to IP address
        client_ip = request.client.host
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, identifier: str, endpoint: str) -> bool:
        """
        Sliding window rate limiting:
        1. Each request creates a key with timestamp
        2. Count requests in the last 60 seconds
        3. Remove old entries outside the window
        """
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Use sorted set for sliding window
        key = f"rate_limit:{identifier}:{endpoint}"
        
        # Remove old entries
        await self.cache.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in window
        request_count = await self.cache.redis.zcard(key)
        
        if request_count >= self.requests_per_minute:
            return False
        
        # Add current request
        await self.cache.redis.zadd(key, {str(uuid.uuid4()): current_time})
        await self.cache.redis.expire(key, self.window_seconds)
        
        return True