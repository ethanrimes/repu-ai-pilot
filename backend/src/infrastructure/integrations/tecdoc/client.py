# backend/src/infrastructure/integrations/tecdoc/client.py
from __future__ import annotations
import asyncio
import random
from typing import Any, Dict, Optional

import httpx

from .tecdoc_config import TecDocSettings

RETRY_STATUS = {408, 429, 500, 502, 503, 504}


def _backoff_seconds(attempt: int) -> float:
    """Exponential backoff with jitter; caps near ~9s."""
    base = min(2 ** (attempt - 1), 8)
    return base + random.random()


class AsyncTecDocClient:
    """
    Thin async HTTP client with retries for TecDoc endpoints.

    This client builds settings from the environment by default via `TecDocSettings()`.
    Ensure your `backend/.env` (or process environment) defines:

        TECDOC_RAPIDAPI_KEY=<your key>
        TECDOC_RAPIDAPI_HOST=tecdoc-catalog.p.rapidapi.com  (optional)
        TECDOC_BASE_URL=https://tecdoc-catalog.p.rapidapi.com (optional)

    Usage:
        async with AsyncTecDocClient() as c:
            data = await c.get("/languages/list")
    """

    def __init__(self, settings: Optional[TecDocSettings] = None) -> None:
        # IMPORTANT: construct from env so the API key comes from settings/.env.
        # We intentionally avoid importing any module-level default with hardcoded keys.
        self.settings = settings or TecDocSettings()
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncTecDocClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=str(self.settings.base_url),
                timeout=self.settings.timeout_seconds,
                headers={
                    "x-rapidapi-host": self.settings.rapidapi_host,
                    "x-rapidapi-key": self.settings.rapidapi_key,
                },
            )
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self._client is None:
            # allow usage without async-with
            await self.__aenter__()
            close_after = True
        else:
            close_after = False

        try:
            attempt = 0
            while True:
                attempt += 1
                try:
                    resp = await self._client.get(path, params=params)
                except httpx.TimeoutException:
                    if attempt <= self.settings.max_retries:
                        await asyncio.sleep(_backoff_seconds(attempt))
                        continue
                    raise

                if resp.status_code in RETRY_STATUS and attempt <= self.settings.max_retries:
                    await asyncio.sleep(_backoff_seconds(attempt))
                    continue

                resp.raise_for_status()
                return resp.json()
        finally:
            if close_after:
                await self.__aexit__(None, None, None)
