# backend/api/config/upstash_config.py
# Path: backend/api/config/upstash_config.py

from upstash_redis import Redis
from functools import lru_cache
from .settings import get_settings

settings = get_settings()

@lru_cache()
def get_redis_client() -> Redis:
    """Get Upstash Redis client"""
    return Redis(
        url=settings.upstash_redis_rest_url,
        token=settings.upstash_redis_rest_token,
        rest_retries=settings.upstash_redis_max_retries,
        rest_retry_interval=settings.upstash_redis_retry_delay / 1000  # Convert to seconds
    )

def test_redis():
    """Test Redis connection"""
    try:
        client = get_redis_client()
        client.set("test_key", "test_value", ex=10)
        value = client.get("test_key")
        print(f"✅ Redis connection successful: {value}")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False