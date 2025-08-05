# backend/src/infrastructure/cache/cache_manager.py

import json
from typing import Optional, Any, Dict
from datetime import timedelta
from upstash_redis import Redis
from backend.src.infrastructure.cache.upstash_config import get_redis_client
from backend.src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Centralized cache management with Upstash Redis"""
    
    def __init__(self):
        self.redis = get_redis_client()
        self.default_ttl = 3600  # 1 hour default
    
    # Key generators
    @staticmethod
    def session_key(session_id: str) -> str:
        return f"session:{session_id}"
    
    @staticmethod
    def user_key(user_id: int) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def rate_limit_key(identifier: str, endpoint: str) -> str:
        return f"rate_limit:{identifier}:{endpoint}"
    
    @staticmethod
    def cache_key(namespace: str, identifier: str) -> str:
        return f"cache:{namespace}:{identifier}"
    
    # Generic operations
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value and isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                self.redis.setex(key, ttl, value)
            else:
                self.redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key"""
        try:
            self.redis.expire(key, ttl)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    # Hash operations for complex data
    async def hset(self, key: str, field: str, value: Any) -> bool:
        """Set hash field"""
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            self.redis.hset(key, field, value)
            return True
        except Exception as e:
            logger.error(f"Redis HSET error for key {key}: {e}")
            return False
    
    async def hget(self, key: str, field: str) -> Optional[Any]:
        """Get hash field"""
        try:
            value = self.redis.hget(key, field)
            if value and isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        except Exception as e:
            logger.error(f"Redis HGET error for key {key}: {e}")
            return None
    
    async def hgetall(self, key: str) -> Dict[str, Any]:
        """Get all hash fields"""
        try:
            data = self.redis.hgetall(key)
            result = {}
            for field, value in data.items():
                if isinstance(value, str):
                    try:
                        result[field] = json.loads(value)
                    except json.JSONDecodeError:
                        result[field] = value
                else:
                    result[field] = value
            return result
        except Exception as e:
            logger.error(f"Redis HGETALL error for key {key}: {e}")
            return {}

# Singleton instance
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Get singleton cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager