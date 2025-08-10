# backend/src/infrastructure/integrations/tecdoc/client.py
from __future__ import annotations
import asyncio
import random
from typing import Any, Dict, Optional

import httpx

from src.config.settings import get_settings

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

    def __init__(self, settings=None) -> None:
        # Use the global settings from src.config.settings
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AsyncTecDocClient":
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=str(self.settings.tecdoc_api_url),
                timeout=30.0,  # Use a reasonable default timeout
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
                    if attempt <= 3:  # Use hardcoded max retries
                        await asyncio.sleep(_backoff_seconds(attempt))
                        continue
                    raise

                if resp.status_code in RETRY_STATUS and attempt <= 3:  # Use hardcoded max retries
                    await asyncio.sleep(_backoff_seconds(attempt))
                    continue

                resp.raise_for_status()
                return resp.json()
        finally:
            if close_after:
                await self.__aexit__(None, None, None)

# ---- Typed, higher-level TecDocClient for agent tools (non-path style) ---- #
from typing import Type, TypeVar
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from pydantic import BaseModel
from src.config.settings import get_settings
from src.core.models import tecdoc as tec_models

T = TypeVar("T", bound=BaseModel)

class TecDocError(Exception):
    pass

class TecDocRateLimitError(TecDocError):
    pass

class TecDocResponseError(TecDocError):
    def __init__(self, status_code: int, message: str, payload: Any | None = None):
        super().__init__(f"TecDoc API error {status_code}: {message}")
        self.status_code = status_code
        self.payload = payload

def _is_retriable(exc: BaseException) -> bool:
    if isinstance(exc, (TecDocRateLimitError,)):
        return True
    if isinstance(exc, TecDocResponseError) and 500 <= exc.status_code < 600:
        return True
    if isinstance(exc, httpx.HTTPError):
        return True
    return False

class TecDocClient:
    """High-level typed client exposing curated endpoints for the LLM tools."""
    def __init__(self, *, settings_obj=None, timeout: float = 30.0, client: httpx.AsyncClient | None = None):
        s = settings_obj or get_settings()
        self._base_url = s.tecdoc_api_url.rstrip("/")
        self._headers = {
            "X-RapidAPI-Key": s.rapidapi_key,
            "X-RapidAPI-Host": s.rapidapi_host,
            "Accept": "application/json",
            "User-Agent": "repu-ai-tecdoc-client/1.0",
        }
        self._external = client is not None
        self._client = client or httpx.AsyncClient(base_url=self._base_url, headers=self._headers, timeout=timeout)

    async def aclose(self):
        if not self._external:
            await self._client.aclose()

    @retry(
        retry=retry_if_exception(_is_retriable),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _request(self, path: str, *, params: Dict[str, Any] | None = None, model: Type[T] | None = None) -> T | Dict[str, Any]:
        try:
            resp = await self._client.get(path, params=params)
        except httpx.HTTPError as e:
            raise TecDocError(str(e)) from e
        if resp.status_code == 429:
            raise TecDocRateLimitError("Rate limited (429)")
        if 500 <= resp.status_code < 600:
            raise TecDocResponseError(resp.status_code, "Server error", resp.text)
        if not resp.is_success:
            msg = None
            try:
                j = resp.json()
                msg = j.get("message") or j.get("error") or resp.text
            except Exception:
                j = None
                msg = resp.text
            raise TecDocResponseError(resp.status_code, msg, j)
        data = resp.json()
        if model:
            return model.model_validate(data)
        return data

    # Endpoint wrappers (using simplified query variant names) -----------------
    async def list_languages(self) -> tec_models.LanguagesList:
        return await self._request("/languages", model=tec_models.LanguagesList)  # type: ignore

    async def list_countries(self, *, lang_id: int | None = None) -> tec_models.CountriesList:
        params = {"langId": lang_id} if lang_id else None
        return await self._request("/countries", params=params, model=tec_models.CountriesList)  # type: ignore

    async def list_manufacturers(self, *, country_id: int, vehicle_type: int) -> tec_models.ManufacturersList:
        params = {"countryId": country_id, "vehicleType": vehicle_type}
        return await self._request("/manufacturers", params=params, model=tec_models.ManufacturersList)  # type: ignore

    async def list_models(self, *, manufacturer_id: int, country_id: int, vehicle_type: int, year: int | None = None, fuel: str | None = None, body: str | None = None) -> tec_models.ModelsList:
        params: Dict[str, Any] = {"manufacturerId": manufacturer_id, "countryId": country_id, "vehicleType": vehicle_type}
        if year:
            params["year"] = year
        if fuel:
            params["fuelType"] = fuel
        if body:
            params["bodyType"] = body
        return await self._request("/models", params=params, model=tec_models.ModelsList)  # type: ignore

    async def list_vehicle_types(self, *, model_id: int, country_id: int, vehicle_type: int) -> tec_models.VehicleTypesList:
        params = {"modelId": model_id, "countryId": country_id, "vehicleType": vehicle_type}
        return await self._request("/vehicletypes", params=params, model=tec_models.VehicleTypesList)  # type: ignore

    async def list_categories(self, *, vehicle_id: int, country_id: int, lang_id: int, version: int = 3):
        if version not in (1, 2, 3):
            raise ValueError("version must be 1, 2, or 3")
        params = {"vehicleId": vehicle_id, "countryId": country_id, "langId": lang_id}
        model_map: Dict[int, Type[BaseModel]] = {1: tec_models.CategoryV1, 2: tec_models.CategoryV2, 3: tec_models.CategoryV3}
        return await self._request(f"/categories/v{version}", params=params, model=model_map[version])  # type: ignore

    async def list_articles(self, *, vehicle_id: int, product_group_id: int, country_id: int, lang_id: int) -> tec_models.ArticlesList:
        params = {"vehicleId": vehicle_id, "productGroupId": product_group_id, "countryId": country_id, "langId": lang_id}
        return await self._request("/articles", params=params, model=tec_models.ArticlesList)  # type: ignore

    async def get_article_details(self, *, article_id: int, country_id: int, lang_id: int) -> tec_models.ArticleCompleteDetails:
        params = {"articleId": article_id, "countryId": country_id, "langId": lang_id}
        return await self._request("/article/details", params=params, model=tec_models.ArticleCompleteDetails)  # type: ignore

    async def get_article_media(self, *, article_id: int) -> tec_models.ArticleMediaInfoList:
        params = {"articleId": article_id}
        return await self._request("/article/media", params=params, model=tec_models.ArticleMediaInfoList)  # type: ignore

    async def search_article_number(self, *, article_no: str, country_id: int, lang_id: int, supplier_id: int | None = None) -> tec_models.ArticleSearch:
        params: Dict[str, Any] = {"articleNo": article_no, "countryId": country_id, "langId": lang_id}
        if supplier_id:
            params["supplierId"] = supplier_id
        return await self._request("/article/search", params=params, model=tec_models.ArticleSearch)  # type: ignore

_client_singleton: TecDocClient | None = None

def get_tecdoc_client() -> TecDocClient:
    global _client_singleton
    if _client_singleton is None:
        _client_singleton = TecDocClient()
    return _client_singleton

__all__ = [
    "AsyncTecDocClient",
    "TecDocClient",
    "get_tecdoc_client",
    "TecDocError",
    "TecDocRateLimitError",
    "TecDocResponseError",
]