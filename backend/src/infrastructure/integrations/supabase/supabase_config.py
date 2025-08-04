# backend/api/config/supabase_config.py
# Path: backend/api/config/supabase_config.py

from supabase import create_client, Client
from functools import lru_cache
from .settings import get_settings
import psycopg2
from psycopg2.pool import SimpleConnectionPool

settings = get_settings()

@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )

@lru_cache()
def get_db_pool():
    """Get PostgreSQL connection pool"""
    # Parse DATABASE_URL
    import re
    pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
    match = re.match(pattern, settings.database_url)
    
    if not match:
        raise ValueError("Invalid DATABASE_URL format")
    
    return SimpleConnectionPool(
        1, 20,  # min and max connections
        user=match.group(1),
        password=match.group(2),
        host=match.group(3),
        port=match.group(4),
        database=match.group(5)
    )

def test_connection():
    """Test Supabase connection"""
    try:
        client = get_supabase_client()
        # Try a simple query
        response = client.table('customers').select('id').limit(1).execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False