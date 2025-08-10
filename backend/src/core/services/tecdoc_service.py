from __future__ import annotations
import asyncio
import time
from typing import Any, Dict, Generic, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel, ValidationError

from ...infrastructure.integrations.tecdoc.client import AsyncTecDocClient
from ...infrastructure.integrations.tecdoc import endpoints as ep

T = TypeVar("T", bound=BaseModel)


class _TTLCache:
    def __init__(self, ttl_seconds: float = 300.0) -> None:
        self.ttl = ttl_seconds
        self._store: Dict[Tuple[str, Tuple[Tuple[str, Any], ...]], Tuple[float, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: Tuple[str, Tuple[Tuple[str, Any], ...]]):
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            ts, val = entry
            if time.time() - ts > self.ttl:
                self._store.pop(key, None)
                return None
            return val

    async def set(self, key: Tuple[str, Tuple[Tuple[str, Any], ...]], value: Any):
        async with self._lock:
            self._store[key] = (time.time(), value)


class TecDocService:
    """High-level ops: path building, fetching, validation (Pydantic), and caching."""

    def __init__(self, client: Optional[AsyncTecDocClient] = None, cache_ttl: float = 300.0) -> None:
        self.client = client or AsyncTecDocClient()
        self.cache = _TTLCache(ttl_seconds=cache_ttl)

    async def _fetch(self, path: str) -> Dict[str, Any]:
        key = (path, tuple())
        cached = await self.cache.get(key)
        if cached is not None:
            return cached
        data = await self.client.get(path)
        await self.cache.set(key, data)
        return data

    async def fetch_and_validate(self, path: str, model: Type[T]) -> T:
        payload = await self._fetch(path)
        try:
            return model.model_validate(payload)
        except ValidationError as e:
            # Re-raise with a cleaner message that includes the path for debugging
            raise ValidationError.from_exception_data(
                message=f"TecDoc payload validation failed for path={path}",
                line_errors=e.errors(),
            )

    # Convenience wrappers matching your bash test file ----------------------
    async def languages_list(self, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.languages_list(), model)

    async def language(self, lang_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.get_language(lang_id), model)

    async def countries_list(self, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.countries_list(), model)

    async def country(self, lang_id: int, country_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.get_country(lang_id, country_id), model)

    async def list_countries_by_lang(self, lang_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.list_countries_by_lang(lang_id), model)

    async def vehicle_types(self, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.list_vehicle_types(), model)

    async def suppliers(self, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.suppliers_list(), model)

    async def manufacturers(self, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.manufacturers_list(lang_id, country_id, type_id), model)

    async def manufacturer_by_id(self, manufacturer_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.manufacturer_by_id(manufacturer_id), model)

    async def models(self, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.models_list(manufacturer_id, lang_id, country_id, type_id), model)

    async def model(self, model_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.model_by_id(model_id, lang_id, country_id, type_id), model)

    async def model_details_by_vehicle(self, vehicle_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.model_details_by_vehicle_id(vehicle_id, lang_id, country_id, type_id), model)

    async def vehicle_type_details(self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.vehicle_type_details(vehicle_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def vehicle_engine_types(self, model_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.list_vehicle_engine_types(model_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def category_v1(self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.category_variant_1(vehicle_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def category_v2(self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.category_variant_2(vehicle_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def category_v3(self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.category_variant_3(vehicle_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def articles_list(self, vehicle_id: int, product_group_id: int, manufacturer_id: int, lang_id: int, country_id: int, type_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.articles_list(vehicle_id, product_group_id, manufacturer_id, lang_id, country_id, type_id), model)

    async def article_complete_details(self, article_id: int, lang_id: int, country_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_id_complete_details(article_id, lang_id, country_id), model)

    async def article_spec_details(self, article_id: int, lang_id: int, country_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_id_spec_details(article_id, lang_id, country_id), model)

    async def article_number_complete_details(self, lang_id: int, country_id: int, article_no: str, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_number_complete_details(lang_id, country_id, article_no), model)

    async def article_all_media(self, article_id: int, lang_id: int, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_all_media(article_id, lang_id), model)

    async def search_articles(self, lang_id: int, article_no: str, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_search(lang_id, article_no), model)

    async def search_articles_with_supplier(self, lang_id: int, supplier_id: int, article_no: str, model: Type[T]) -> T:
        return await self.fetch_and_validate(ep.article_search_with_supplier(lang_id, supplier_id, article_no), model)