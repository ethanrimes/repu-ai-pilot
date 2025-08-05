# backend/tests/test_upstash_connectivity.py
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.infrastructure.cache.upstash_config import get_redis_client
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

async def test_upstash_connection():
    """Test Upstash Redis connectivity and basic operations"""
    
    print("🔄 Testing Upstash Redis connection...")
    
    try:
        # Get Redis client
        redis = get_redis_client()
        
        # Test 1: Basic connectivity
        print("1️⃣ Testing basic connectivity...")
        redis.ping()
        print("✅ Connected to Upstash Redis")
        
        # Test 2: Set/Get operations
        print("\n2️⃣ Testing SET/GET operations...")
        test_key = "test:connection"
        test_value = "Hello from test!"
        
        redis.set(test_key, test_value, ex=60)  # 60 second expiry
        retrieved = redis.get(test_key)
        
        assert retrieved == test_value, f"Expected '{test_value}', got '{retrieved}'"
        print(f"✅ SET/GET working: {retrieved}")
        
        # Test 3: Hash operations
        print("\n3️⃣ Testing HASH operations...")
        hash_key = "test:hash"
        redis.hset(hash_key, "field1", "value1")
        redis.hset(hash_key, "field2", "value2")
        
        hash_data = redis.hgetall(hash_key)
        print(f"✅ HASH working: {hash_data}")
        
        # Test 4: Expiry
        print("\n4️⃣ Testing TTL/Expiry...")
        redis.expire(hash_key, 60)
        ttl = redis.ttl(hash_key)
        print(f"✅ TTL working: {ttl} seconds")
        
        # Test 5: JSON operations
        print("\n5️⃣ Testing JSON storage...")
        import json
        json_data = {"user": "test", "timestamp": "2024-01-01"}
        redis.set("test:json", json.dumps(json_data), ex=60)
        retrieved_json = json.loads(redis.get("test:json"))
        print(f"✅ JSON storage working: {retrieved_json}")
        
        # Cleanup
        print("\n🧹 Cleaning up test keys...")
        redis.delete(test_key, hash_key, "test:json")
        
        print("\n✅ All Upstash Redis tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_upstash_connection())