from __future__ import annotations
from typing import Optional, Type, TypeVar

from cachetools import TTLCache
from pydantic import BaseModel, ValidationError

from src.infrastructure.integrations.tecdoc.client import AsyncTecDocClient
from src.infrastructure.integrations.tecdoc import endpoints as ep
from src.core.models import tecdoc as M

T = TypeVar("T", bound=BaseModel)


class TecDocSchemaError(RuntimeError):
    """Raised when an API response fails validation against the expected schema."""

    def __init__(self, path: str, model: type[BaseModel], raw: object, err: Exception):
        super().__init__(f"Validation failed for {path} -> {model.__name__}: {err}")
        self.path = path
        self.model = model
        self.raw = raw
        self.err = err


class TecDocService:
    """High-level TecDoc service with strongly-typed methods.

    Every public method returns a specific Pydantic model defined in
    `backend/src/core/models/tecdoc.py` and validates the HTTP response
    accordingly. Responses are cached by request path for `cache_ttl` seconds.
    """

    def __init__(self, client: Optional[AsyncTecDocClient] = None, cache_ttl: int = 60) -> None:
        self._client: AsyncTecDocClient = client or AsyncTecDocClient()
        self._cache: TTLCache[str, BaseModel] = TTLCache(maxsize=512, ttl=cache_ttl)

    # ------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------
    async def _get(self, path: str, model: Type[T]) -> T:
        from src.shared.utils.logger import get_logger
        logger = get_logger(__name__)
        
        logger.info(f"[TECDOC_DEBUG] Requesting path: {path}")
        
        if path in self._cache:
            logger.info(f"[TECDOC_DEBUG] Cache hit for path: {path}")
            return self._cache[path]  # type: ignore[return-value]

        logger.info(f"[TECDOC_DEBUG] Cache miss, making API call to: {path}")
        async with self._client as c:
            raw = await c.get(path)

        logger.info(f"[TECDOC_DEBUG] Got response, validating against {model.__name__}")
        try:
            parsed: T = model.model_validate(raw)
            logger.info(f"[TECDOC_DEBUG] Successfully parsed {model.__name__}")
        except ValidationError as e:
            logger.error(f"[TECDOC_DEBUG] Validation error for {model.__name__}: {e}")
            raise TecDocSchemaError(path, model, raw, e) from e

        self._cache[path] = parsed
        return parsed

    async def _fetch(self, path: str) -> dict:
        """Back-compat raw fetch used by the older TecDocTool. Prefer `_get` above."""
        async with self._client as c:
            return await c.get(path)

    # ------------------------------------------------------------
    # Languages
    # ------------------------------------------------------------
    async def list_languages(self) -> M.LanguagesList:
        return await self._get(ep.languages_list(), M.LanguagesList)

    async def get_language(self, lang_id: int) -> M.LanguageDetails:
        return await self._get(ep.get_language(lang_id), M.LanguageDetails)

    # ------------------------------------------------------------
    # Countries
    # ------------------------------------------------------------
    async def list_countries(self) -> M.CountriesList:
        return await self._get(ep.countries_list(), M.CountriesList)

    async def get_country(self, lang_id: int, country_id: int) -> M.CountryDetails:
        return await self._get(
            ep.get_country(lang_id, country_id),
            M.CountryDetails,
        )

    async def list_countries_by_lang(self, lang_id: int) -> M.CountriesByLanguage:
        return await self._get(ep.list_countries_by_lang(lang_id), M.CountriesByLanguage)

    # ------------------------------------------------------------
    # Vehicle types (high-level lists/details)
    # ------------------------------------------------------------
    async def list_vehicle_types(self) -> M.VehicleTypesList:
        return await self._get(ep.list_vehicle_types(), M.VehicleTypesList)

    async def vehicle_type_details(
        self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.VehicleTypeDetails:
        return await self._get(
            ep.vehicle_type_details(vehicle_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.VehicleTypeDetails,
        )

    async def list_vehicle_engine_types(
        self, model_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.VehicleEngineTypes:
        return await self._get(
            ep.list_vehicle_engine_types(model_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.VehicleEngineTypes,
        )

    # ------------------------------------------------------------
    # Suppliers
    # ------------------------------------------------------------
    async def list_suppliers(self) -> M.SuppliersList:
        return await self._get(ep.suppliers_list(), M.SuppliersList)

    # ------------------------------------------------------------
    # Manufacturers
    # ------------------------------------------------------------
    async def list_manufacturers(self, lang_id: int, country_filter_id: int, type_id: int) -> M.ManufacturersList:
        return await self._get(ep.manufacturers_list(lang_id, country_filter_id, type_id), M.ManufacturersList)

    async def manufacturer_details(self, manufacturer_id: int) -> M.ManufacturerDetails:
        return await self._get(ep.manufacturer_by_id(manufacturer_id), M.ManufacturerDetails)

    # ------------------------------------------------------------
    # Models
    # ------------------------------------------------------------
    async def list_models(
        self, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.ModelsList:
        return await self._get(
            ep.models_list(manufacturer_id, lang_id, country_filter_id, type_id),
            M.ModelsList,
        )

    async def model_details(
        self, model_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.ModelDetails:
        return await self._get(
            ep.model_by_id(model_id, lang_id, country_filter_id, type_id),
            M.ModelDetails,
        )

    async def model_details_by_vehicle(
        self, vehicle_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.ModelDetailsByVehicle:
        return await self._get(
            ep.model_details_by_vehicle_id(vehicle_id, lang_id, country_filter_id, type_id),
            M.ModelDetailsByVehicle,
        )

    # ------------------------------------------------------------
    # Categories (three variants)
    # ------------------------------------------------------------
    async def category_v1(
        self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.CategoryV1:
        return await self._get(
            ep.category_variant_1(vehicle_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.CategoryV1,
        )

    async def category_v2(
        self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.CategoryV2:
        return await self._get(
            ep.category_variant_2(vehicle_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.CategoryV2,
        )

    async def category_v3(
        self, vehicle_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.CategoryV3:
        from src.shared.utils.logger import get_logger
        logger = get_logger(__name__)
        
        logger.info(f"[TECDOC_DEBUG] category_v3 called with vehicle_id={vehicle_id}, manufacturer_id={manufacturer_id}, lang_id={lang_id}, country_filter_id={country_filter_id}, type_id={type_id}")
        
        result = await self._get(
            ep.category_variant_3(vehicle_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.CategoryV3,
        )
        
        if hasattr(result, 'categories'):
            logger.info(f"[TECDOC_DEBUG] category_v3 returned {len(result.categories) if result.categories else 0} categories")
            if result.categories:
                logger.info(f"[TECDOC_DEBUG] Sample category keys: {list(result.categories.keys())[:5]}")
        else:
            logger.warning(f"[TECDOC_DEBUG] category_v3 result has no categories attribute")
        
        return result

    # ------------------------------------------------------------
    # Articles
    # ------------------------------------------------------------
    async def list_articles(
        self, vehicle_id: int, product_group_id: int, manufacturer_id: int, lang_id: int, country_filter_id: int, type_id: int
    ) -> M.ArticlesList:
        return await self._get(
            ep.articles_list(vehicle_id, product_group_id, manufacturer_id, lang_id, country_filter_id, type_id),
            M.ArticlesList,
        )

    async def article_complete_details(self, article_id: int, lang_id: int, country_filter_id: int) -> M.ArticleCompleteDetails:
        return await self._get(ep.article_id_complete_details(article_id, lang_id, country_filter_id), M.ArticleCompleteDetails)

    async def article_specification_details(self, article_id: int, lang_id: int, country_filter_id: int) -> M.ArticleSpecificationDetails:
        return await self._get(ep.article_id_spec_details(article_id, lang_id, country_filter_id), M.ArticleSpecificationDetails)

    async def article_number_details(self, lang_id: int, country_filter_id: int, article_no: str) -> M.ArticleNumberDetails:
        return await self._get(ep.article_number_complete_details(lang_id, country_filter_id, article_no), M.ArticleNumberDetails)

    async def article_all_media_info(self, article_id: int, lang_id: int) -> M.ArticleMediaInfoList:
        return await self._get(ep.article_all_media(article_id, lang_id), M.ArticleMediaInfoList)

    async def article_search(self, lang_id: int, article_search: str) -> M.ArticleSearch:
        return await self._get(ep.article_search(lang_id, article_search), M.ArticleSearch)

    async def article_search_with_supplier(self, lang_id: int, supplier_id: int, article_search: str) -> M.ArticleSearchWithSupplier:
        return await self._get(ep.article_search_with_supplier(lang_id, supplier_id, article_search), M.ArticleSearchWithSupplier)


__all__ = [
    "TecDocService",
    "TecDocSchemaError",
]