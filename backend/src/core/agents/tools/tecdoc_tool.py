# backend/src/core/agents/tools/tecdoc_tool.py
from __future__ import annotations

from typing import Optional, List
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from src.infrastructure.integrations.tecdoc.client import get_tecdoc_client, TecDocClient
from src.infrastructure.integrations.tecdoc.client import TecDocError

# ------------------------- Argument Schemas ------------------------- #
class ArticleSearchArgs(BaseModel):
    article_no: str = Field(..., description="Article/part number, e.g., 113-1306X")
    supplier_id: Optional[int] = Field(None, description="Optional supplier ID to narrow search")
    lang_id: int = Field(4, description="Language ID (default 4 = English)")
    country_id: int = Field(120, description="Country ID (default 120 = Germany)")

class ListManufacturersArgs(BaseModel):
    country_id: int = Field(..., description="Country ID, e.g., 120")
    vehicle_type: int = Field(..., description="Vehicle type numeric code (e.g., 1=PC)")

class ListModelsArgs(BaseModel):
    manufacturer_id: int = Field(..., description="Manufacturer ID returned from list_manufacturers")
    country_id: int = Field(..., description="Country ID")
    vehicle_type: int = Field(..., description="Vehicle type code")
    year: Optional[int] = Field(None, description="Filter by model year (start range)")
    fuel: Optional[str] = Field(None, description="Fuel type filter (e.g., Diesel, Petrol)")
    body: Optional[str] = Field(None, description="Body type filter")

class ListVehicleTypesArgs(BaseModel):
    model_id: int = Field(..., description="Model ID from list_models")
    country_id: int = Field(..., description="Country ID")
    vehicle_type: int = Field(..., description="Vehicle type code used previously")

class ListCategoriesArgs(BaseModel):
    vehicle_id: int = Field(..., description="Vehicle type ID from list_vehicle_types")
    country_id: int = Field(..., description="Country ID")
    lang_id: int = Field(4, description="Language ID for category names")
    version: int = Field(3, description="Category API version (1,2,3) default 3")

class ListArticlesArgs(BaseModel):
    vehicle_id: int = Field(..., description="Vehicle ID")
    product_group_id: int = Field(..., description="Category/product group ID from list_categories")
    country_id: int = Field(..., description="Country ID")
    lang_id: int = Field(4, description="Language ID")

class ArticleDetailsArgs(BaseModel):
    article_id: int = Field(..., description="Article ID from search or list_articles")
    country_id: int = Field(..., description="Country ID")
    lang_id: int = Field(4, description="Language ID")

class ArticleMediaArgs(BaseModel):
    article_id: int = Field(..., description="Article ID to fetch media for")

# ------------------------- Helper ------------------------- #

def _client() -> TecDocClient:
    return get_tecdoc_client()

# ------------------------- Tool Functions ------------------------- #
async def _search_article_number(args: ArticleSearchArgs):
    return (await _client().search_article_number(
        article_no=args.article_no,
        supplier_id=args.supplier_id,
        lang_id=args.lang_id,
        country_id=args.country_id,
    )).model_dump()

async def _list_manufacturers(args: ListManufacturersArgs):
    return (await _client().list_manufacturers(country_id=args.country_id, vehicle_type=args.vehicle_type)).model_dump()

async def _list_models(args: ListModelsArgs):
    return (await _client().list_models(
        manufacturer_id=args.manufacturer_id,
        country_id=args.country_id,
        vehicle_type=args.vehicle_type,
        year=args.year,
        fuel=args.fuel,
        body=args.body,
    )).model_dump()

async def _list_vehicle_types(args: ListVehicleTypesArgs):
    return (await _client().list_vehicle_types(model_id=args.model_id, country_id=args.country_id, vehicle_type=args.vehicle_type)).model_dump()

async def _list_categories(args: ListCategoriesArgs):
    return (await _client().list_categories(vehicle_id=args.vehicle_id, country_id=args.country_id, lang_id=args.lang_id, version=args.version)).model_dump()

async def _list_articles(args: ListArticlesArgs):
    return (await _client().list_articles(vehicle_id=args.vehicle_id, product_group_id=args.product_group_id, country_id=args.country_id, lang_id=args.lang_id)).model_dump()

async def _get_article_details(args: ArticleDetailsArgs):
    return (await _client().get_article_details(article_id=args.article_id, country_id=args.country_id, lang_id=args.lang_id)).model_dump()

async def _get_article_media(args: ArticleMediaArgs):
    return (await _client().get_article_media(article_id=args.article_id)).model_dump()

# ------------------------- StructuredTool Instances ------------------------- #
search_article_number_tool = StructuredTool.from_function(
    coroutine=_search_article_number,
    name="search_article_number",
    description=(
        "Search TecDoc by article/part number. Optionally narrow by supplier. "
        "Returns list of matching articles with IDs and basic info."
    ),
    args_schema=ArticleSearchArgs,
)

list_manufacturers_tool = StructuredTool.from_function(
    coroutine=_list_manufacturers,
    name="list_manufacturers",
    description="List manufacturers (brand ids + names) for a given country and vehicle type.",
    args_schema=ListManufacturersArgs,
)

list_models_tool = StructuredTool.from_function(
    coroutine=_list_models,
    name="list_models",
    description="List models for a manufacturer (optionally filter by year, fuel, body).",
    args_schema=ListModelsArgs,
)

list_vehicle_types_tool = StructuredTool.from_function(
    coroutine=_list_vehicle_types,
    name="list_vehicle_types",
    description="List vehicle type IDs for a specific model.",
    args_schema=ListVehicleTypesArgs,
)

list_categories_tool = StructuredTool.from_function(
    coroutine=_list_categories,
    name="list_categories",
    description="Fetch category tree (hierarchical product groups) for a vehicle.",
    args_schema=ListCategoriesArgs,
)

list_articles_tool = StructuredTool.from_function(
    coroutine=_list_articles,
    name="list_articles",
    description="List articles (SKUs) for a vehicle within a product/category group.",
    args_schema=ListArticlesArgs,
)

get_article_details_tool = StructuredTool.from_function(
    coroutine=_get_article_details,
    name="get_article_details",
    description="Get comprehensive details (specs, compatibility) for one article ID.",
    args_schema=ArticleDetailsArgs,
)

get_article_media_tool = StructuredTool.from_function(
    coroutine=_get_article_media,
    name="get_article_media",
    description="Get media (image metadata) for one article ID.",
    args_schema=ArticleMediaArgs,
)

# Toolkit export
TECDOC_TOOLS: List[StructuredTool] = [
    search_article_number_tool,
    list_manufacturers_tool,
    list_models_tool,
    list_vehicle_types_tool,
    list_categories_tool,
    list_articles_tool,
    get_article_details_tool,
    get_article_media_tool,
]

__all__ = ["TECDOC_TOOLS"]
