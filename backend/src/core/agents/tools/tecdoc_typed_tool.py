from __future__ import annotations
from enum import Enum
from typing import Any, Dict, Optional, TypeAlias
from typing import ClassVar, Type as _Type


from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from src.core.services.tecdoc_service import TecDocService

JSONable: TypeAlias = Dict[str, Any]


class TecEndpoint(str, Enum):
    # Languages
    LANGUAGES_LIST = "languages_list"
    GET_LANGUAGE = "get_language"
    # Countries
    COUNTRIES_LIST = "countries_list"
    GET_COUNTRY = "get_country"
    COUNTRIES_BY_LANG = "list_countries_by_lang"
    # Vehicle types
    VEHICLE_TYPES = "list_vehicle_types"
    VEHICLE_TYPE_DETAILS = "vehicle_type_details"
    VEHICLE_ENGINE_TYPES = "list_vehicle_engine_types"
    # Suppliers
    SUPPLIERS_LIST = "suppliers_list"
    # Manufacturers & models
    MANUFACTURERS_LIST = "manufacturers_list"
    MANUFACTURER_DETAILS = "manufacturer_details"
    MODELS_LIST = "models_list"
    MODEL_DETAILS = "model_details"
    MODEL_DETAILS_BY_VEHICLE = "model_details_by_vehicle"
    # Categories
    CATEGORY_V1 = "category_v1"
    CATEGORY_V2 = "category_v2"
    CATEGORY_V3 = "category_v3"
    # Articles
    ARTICLES_LIST = "articles_list"
    ARTICLE_COMPLETE_DETAILS = "article_complete_details"
    ARTICLE_SPEC_DETAILS = "article_specification_details"
    ARTICLE_NUMBER_DETAILS = "article_number_details"
    ARTICLE_MEDIA_INFO = "article_all_media_info"
    ARTICLE_SEARCH = "article_search"
    ARTICLE_SEARCH_WITH_SUPPLIER = "article_search_with_supplier"


class TecDocTypedInput(BaseModel):
    endpoint: TecEndpoint = Field(..., description="Which typed TecDoc call to make")
    # Common params (unused ones can be omitted)
    lang_id: Optional[int] = None
    country_filter_id: Optional[int] = None
    type_id: Optional[int] = None
    manufacturer_id: Optional[int] = None
    model_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    product_group_id: Optional[int] = None
    article_id: Optional[int] = None
    supplier_id: Optional[int] = None
    article_no: Optional[str] = None
    article_search: Optional[str] = None


class TecDocTypedTool(BaseTool):
    name: str = "tecdoc_typed_api"
    description: str = "TecDoc API with strictly typed responses, returning JSON serialized from Pydantic models."
    args_schema: ClassVar[_Type[BaseModel]] = TecDocTypedInput
    
    # Define service as a private attribute
    def __init__(self, service: Optional[TecDocService] = None, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic's validation
        object.__setattr__(self, 'service', service or TecDocService())

    async def _arun(self, **kwargs) -> JSONable:
        args = TecDocTypedInput(**kwargs)
        s = self.service
        e = args.endpoint

        # Dispatch based on endpoint enum; return Pydantic model_dump()
        if e is TecEndpoint.LANGUAGES_LIST:
            return (await s.list_languages()).model_dump()
        if e is TecEndpoint.GET_LANGUAGE:
            return (await s.get_language(args.lang_id)).model_dump()  # type: ignore[arg-type]

        if e is TecEndpoint.COUNTRIES_LIST:
            return (await s.list_countries()).model_dump()
        if e is TecEndpoint.GET_COUNTRY:
            return (await s.get_country(args.lang_id, args.country_filter_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.COUNTRIES_BY_LANG:
            return (await s.list_countries_by_lang(args.lang_id)).model_dump()  # type: ignore[arg-type]

        if e is TecEndpoint.VEHICLE_TYPES:
            return (await s.list_vehicle_types()).model_dump()
        if e is TecEndpoint.VEHICLE_TYPE_DETAILS:
            return (
                await s.vehicle_type_details(
                    args.vehicle_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id
                )
            ).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.VEHICLE_ENGINE_TYPES:
            return (
                await s.list_vehicle_engine_types(
                    args.model_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id
                )
            ).model_dump()  # type: ignore[arg-type]

        if e is TecEndpoint.SUPPLIERS_LIST:
            return (await s.list_suppliers()).model_dump()

        if e is TecEndpoint.MANUFACTURERS_LIST:
            return (await s.list_manufacturers(args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.MANUFACTURER_DETAILS:
            return (await s.manufacturer_details(args.manufacturer_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.MODELS_LIST:
            return (await s.list_models(args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.MODEL_DETAILS:
            return (await s.model_details(args.model_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.MODEL_DETAILS_BY_VEHICLE:
            return (await s.model_details_by_vehicle(args.vehicle_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]

        if e is TecEndpoint.CATEGORY_V1:
            return (await s.category_v1(args.vehicle_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.CATEGORY_V2:
            return (await s.category_v2(args.vehicle_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.CATEGORY_V3:
            return (await s.category_v3(args.vehicle_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id)).model_dump()  # type: ignore[arg-type]

        if e is TecEndpoint.ARTICLES_LIST:
            return (
                await s.list_articles(
                    args.vehicle_id, args.product_group_id, args.manufacturer_id, args.lang_id, args.country_filter_id, args.type_id
                )
            ).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_COMPLETE_DETAILS:
            return (await s.article_complete_details(args.article_id, args.lang_id, args.country_filter_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_SPEC_DETAILS:
            return (await s.article_specification_details(args.article_id, args.lang_id, args.country_filter_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_NUMBER_DETAILS:
            return (await s.article_number_details(args.lang_id, args.country_filter_id, args.article_no)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_MEDIA_INFO:
            return (await s.article_all_media_info(args.article_id, args.lang_id)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_SEARCH:
            return (await s.article_search(args.lang_id, args.article_search)).model_dump()  # type: ignore[arg-type]
        if e is TecEndpoint.ARTICLE_SEARCH_WITH_SUPPLIER:
            return (await s.article_search_with_supplier(args.lang_id, args.supplier_id, args.article_search)).model_dump()  # type: ignore[arg-type]

        raise ValueError(f"Unsupported endpoint: {e}")

    def _run(self, *args, **kwargs):  # pragma: no cover - async only
        raise NotImplementedError
