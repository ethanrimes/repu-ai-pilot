"""TecDoc API Async Client Wrapper

Provides typed, retriable access to a curated subset of TecDoc endpoints the
LLM agent is allowed to call. Each public method returns a Pydantic model
(or dict) defined in `src.core.models.tecdoc`.
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Type, TypeVar
import httpx
from tenacity import (
    retry, retry_if_exception, stop_after_attempt, wait_exponential,
)
from pydantic import BaseModel

from src.config.settings import get_settings
from src.core.models import tecdoc as models

settings = get_settings()

__all__ = ["TecDocClient", "TecDocError", "TecDocRateLimitError"]

T = TypeVar("T", bound=BaseModel)


class TecDocError(Exception):
    """Base exception for TecDoc client errors."""


class TecDocRateLimitError(TecDocError):
    """Raised when the API returns 429 (rate limited)."""


class TecDocResponseError(TecDocError):
    """Raised for non-success responses that are not retriable."""

    def __init__(self, status_code: int, message: str, payload: Any | None = None):
        super().__init__(f"TecDoc API error {status_code}: {message}")
        self.status_code = status_code
        self.payload = payload


def _is_retriable_exception(exc: BaseException) -> bool:
    if isinstance(exc, TecDocRateLimitError):
        return True
    if isinstance(exc, TecDocResponseError) and 500 <= exc.status_code < 600:
        return True
    if isinstance(exc, httpx.HTTPError):
        return True
    return False


class TecDocClient:
    """Async HTTP client wrapper for TecDoc.

    Notes
    -----
    * Uses RapidAPI headers loaded from settings.
    * Retries automatically on 429 and 5xx with exponential backoff.
    * Converts JSON responses into strongly typed Pydantic models.
    * Only exposes a whitelisted set of safe read-only endpoints.
    """

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        api_host: str | None = None,
        timeout: float = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = (base_url or settings.tecdoc_api_url).rstrip("/")
        self._headers = {
            "X-RapidAPI-Key": api_key or settings.rapidapi_key,
            "X-RapidAPI-Host": api_host or settings.rapidapi_host,
            "Accept": "application/json",
            "User-Agent": "repu-ai-tecdoc-client/1.0",
        }
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(base_url=self._base_url, headers=self._headers, timeout=timeout)

    async def aclose(self):  # pragma: no cover - simple resource closer
        if not self._external_client:
            await self._client.aclose()

    # ------------------------- internal helpers ------------------------- #
    @retry(
        retry=retry_if_exception(_is_retriable_exception),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Dict[str, Any] | None = None,
        model: Type[T] | None = None,
    ) -> T | Dict[str, Any] | Any:
        url = path if path.startswith("/") else f"/{path}"
        try:
            resp = await self._client.request(method.upper(), url, params=params)
        except httpx.HTTPError as e:  # network / protocol errors (retriable)
            raise TecDocError(str(e)) from e

        if resp.status_code == 429:
            raise TecDocRateLimitError("Rate limit hit (429)")
        if 500 <= resp.status_code < 600:
            raise TecDocResponseError(resp.status_code, "Server error", resp.text)
        if not resp.is_success:
            # Non-retriable client error
            try:
                data = resp.json()
                message = data.get("message") or data.get("error") or resp.text
            except Exception:
                data = None
                message = resp.text
            raise TecDocResponseError(resp.status_code, message, data)

        data = resp.json()
        if model:
            try:
                return model.model_validate(data)
            except Exception as e:
                raise TecDocError(f"Failed to parse response for {path}: {e}") from e
        return data

    # ------------------------- public API methods ----------------------- #
    async def list_languages(self) -> models.LanguagesList:
        return await self._request("GET", "/languages", model=models.LanguagesList)

    async def list_countries(self, *, lang_id: int | None = None) -> models.CountriesList:
        params = {"langId": lang_id} if lang_id else None
        return await self._request("GET", "/countries", params=params, model=models.CountriesList)

    async def list_manufacturers(self, *, country_id: int, vehicle_type: int) -> models.ManufacturersList:
        params = {"countryId": country_id, "vehicleType": vehicle_type}
        return await self._request("GET", "/manufacturers", params=params, model=models.ManufacturersList)

    async def list_models(
        self,
        *,
        manufacturer_id: int,
        country_id: int,
        vehicle_type: int,
        year: Optional[int] = None,
        fuel: Optional[str] = None,
        body: Optional[str] = None,
    ) -> models.ModelsList:
        params: Dict[str, Any] = {
            "manufacturerId": manufacturer_id,
            "countryId": country_id,
            "vehicleType": vehicle_type,
        }
        if year:
            params["year"] = year
        if fuel:
            params["fuelType"] = fuel
        if body:
            params["bodyType"] = body
        return await self._request("GET", "/models", params=params, model=models.ModelsList)

    async def list_vehicle_types(self, *, model_id: int, country_id: int, vehicle_type: int) -> models.VehicleTypesList:
        params = {"modelId": model_id, "countryId": country_id, "vehicleType": vehicle_type}
        return await self._request("GET", "/vehicletypes", params=params, model=models.VehicleTypesList)

    async def list_categories(self, *, vehicle_id: int, country_id: int, lang_id: int, version: int = 3) -> models.CategoryV3 | models.CategoryV2 | models.CategoryV1:
        """Return category tree for a vehicle.

        version: choose between 1,2,3 – default 3 (most structured).
        """
        if version not in (1, 2, 3):
            raise ValueError("version must be 1, 2, or 3")
        params = {"vehicleId": vehicle_id, "countryId": country_id, "langId": lang_id}
        model_map: Dict[int, Type[BaseModel]] = {1: models.CategoryV1, 2: models.CategoryV2, 3: models.CategoryV3}
        return await self._request("GET", f"/categories/v{version}", params=params, model=model_map[version])  # type: ignore

    async def list_articles(self, *, vehicle_id: int, product_group_id: int, country_id: int, lang_id: int) -> models.ArticlesList:
        params = {"vehicleId": vehicle_id, "productGroupId": product_group_id, "countryId": country_id, "langId": lang_id}
        return await self._request("GET", "/articles", params=params, model=models.ArticlesList)

    async def get_article_details(self, *, article_id: int, country_id: int, lang_id: int) -> models.ArticleCompleteDetails:
        params = {"articleId": article_id, "countryId": country_id, "langId": lang_id}
        return await self._request("GET", "/article/details", params=params, model=models.ArticleCompleteDetails)

    async def get_article_media(self, *, article_id: int) -> models.ArticleMediaInfoList:
        params = {"articleId": article_id}
        return await self._request("GET", "/article/media", params=params, model=models.ArticleMediaInfoList)

    async def search_article_number(
        self,
        *,
        article_no: str,
        country_id: int,
        lang_id: int,
        supplier_id: Optional[int] = None,
    ) -> models.ArticleSearch:
        params: Dict[str, Any] = {"articleNo": article_no, "countryId": country_id, "langId": lang_id}
        if supplier_id:
            params["supplierId"] = supplier_id
        return await self._request("GET", "/article/search", params=params, model=models.ArticleSearch)


# Singleton helper (lazy)
_client_instance: TecDocClient | None = None


def get_tecdoc_client() -> TecDocClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = TecDocClient()
    return _client_instance
