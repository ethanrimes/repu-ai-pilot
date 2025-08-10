# backend/api/config/tecdoc_config.py
# Path: backend/api/config/tecdoc_config.py

import httpx
from functools import lru_cache
from src.config.settings import get_settings

from __future__ import annotations
from pydantic import BaseSettings, Field, HttpUrl

class TecDocSettings(BaseSettings):
    """Configuration for the TecDoc integration.

    Values are read from env if present, with the shown defaults used for local/dev.
    """

    base_url: HttpUrl = Field(
        default="https://tecdoc-catalog.p.rapidapi.com", description="TecDoc base URL"
    )
    rapidapi_key: str = Field(..., description="RapidAPI key for TecDoc")
    rapidapi_host: str = Field(
        default="tecdoc-catalog.p.rapidapi.com", description="RapidAPI host header"
    )
    timeout_seconds: float = Field(15.0, description="HTTP timeout for TecDoc calls")
    max_retries: int = Field(3, ge=0, le=8, description="Max retry attempts on 5xx/timeout")

    class Config:
        env_prefix = "TECDOC_"
        case_sensitive = False

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