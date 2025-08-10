# backend/src/infrastructure/integrations/tecdoc/tecdoc_config.py
from __future__ import annotations
import httpx
from functools import lru_cache
from src.config.settings import get_settings

# Get settings instance
settings = get_settings()

@lru_cache()
def get_tecdoc_headers() -> dict:
    """Get headers for TecDoc API requests"""
    return {
        "X-RapidAPI-Key": settings.rapidapi_key,
        "X-RapidAPI-Host": settings.rapidapi_host
    }

@lru_cache()
def get_tecdoc_client() -> httpx.AsyncClient:
    """Get async HTTP client for TecDoc API"""
    return httpx.AsyncClient(
        base_url=settings.tecdoc_api_url,
        headers=get_tecdoc_headers(),
        timeout=30.0
    )

async def test_tecdoc():
    """Test TecDoc API connection"""
    try:
        async with get_tecdoc_client() as client:
            response = await client.get("/vehicletypes")
            if response.status_code == 200:
                print("✅ TecDoc API connection successful")
                return True
            else:
                print(f"❌ TecDoc API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ TecDoc API connection failed: {e}")
        return False