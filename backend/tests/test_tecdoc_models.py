from __future__ import annotations
import asyncio
import inspect
from typing import List, Type
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'backend' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT) + "/backend")

import pytest
from pydantic import BaseModel

# 1) Models module must import and expose BaseModel subclasses


def test_tecdoc_models_are_importable_and_well_formed():
    import src.core.models.tecdoc as tecdoc_models  # type: ignore

    model_types: List[Type[BaseModel]] = [
        m
        for _, m in inspect.getmembers(tecdoc_models, inspect.isclass)
        if issubclass(m, BaseModel) and m is not BaseModel
    ]

    # The file should define at least one response model.
    assert model_types, "No Pydantic models found in core.models.tecdoc"

    # Every model should be able to produce a JSON schema.
    for cls in model_types:
        schema = cls.model_json_schema()
        assert isinstance(schema, dict) and "title" in schema


# 2) Endpoints builders must match the bash script paths exactly for the provided IDs

from src.infrastructure.integrations.tecdoc import endpoints as ep


@pytest.mark.parametrize(
    "got,expected",
    [
        (ep.languages_list(), "/languages/list"),
        (ep.get_language(4), "/languages/get-language/lang-id/4"),
        (ep.countries_list(), "/countries/list"),
        (
            ep.get_country(4, 120),
            "/countries/get-country/lang-id/4/country-filter-id/120",
        ),
        (ep.list_countries_by_lang(4), "/countries/list-countries-by-lang-id/4"),
        (ep.list_vehicle_types(), "/types/list-vehicles-type"),
        (ep.suppliers_list(), "/suppliers/list"),
        (
            ep.manufacturers_list(4, 120, 1),
            "/manufacturers/list/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (ep.manufacturer_by_id(72), "/manufacturers/find-by-id/72"),
        (
            ep.models_list(72, 4, 120, 1),
            "/models/list/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.model_by_id(39795, 4, 120, 1),
            "/models/find-by/39795/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.model_details_by_vehicle_id(138817, 4, 120, 1),
            "/models/get-model-details-by-vehicle-id/138817/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.vehicle_type_details(138817, 72, 4, 120, 1),
            "/types/vehicle-type-details/138817/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.list_vehicle_engine_types(39795, 72, 4, 120, 1),
            "/types/list-vehicles-types/39795/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.category_variant_1(138817, 72, 4, 120, 1),
            "/category/category-products-groups-variant-1/138817/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.category_variant_2(138817, 72, 4, 120, 1),
            "/category/category-products-groups-variant-2/138817/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.category_variant_3(138817, 72, 4, 120, 1),
            "/category/category-products-groups-variant-3/138817/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.articles_list(138817, 100806, 72, 4, 120, 1),
            "/articles/list/vehicle-id/138817/product-group-id/100806/manufacturer-id/72/lang-id/4/country-filter-id/120/type-id/1",
        ),
        (
            ep.article_id_complete_details(1043331, 4, 120),
            "/articles/article-id-details/1043331/lang-id/4/country-filter-id/120",
        ),
        (
            ep.article_id_spec_details(1043331, 4, 120),
            "/articles/details/1043331/lang-id/4/country-filter-id/120",
        ),
        (
            ep.article_number_complete_details(4, 120, "113-1306X"),
            "/articles/article-number-details/lang-id/4/country-filter-id/120/article-no/113-1306X",
        ),
        (
            ep.article_all_media(1043331, 4),
            "/articles/article-all-media-info/1043331/lang-id/4",
        ),
        (
            ep.article_search(4, "113-1306X"),
            "/articles/search/lang-id/4/article-search/113-1306X",
        ),
        (
            ep.article_search_with_supplier(4, 6304, "113-1306X"),
            "/articles/search/lang-id/4/supplier-id/6304/article-search/113-1306X",
        ),
    ],
)
def test_endpoint_builders_match_bash_script(got, expected):
    assert got == expected


# 3) Client headers should include RapidAPI requirements
from src.infrastructure.integrations.tecdoc.client import AsyncTecDocClient
from src.infrastructure.integrations.tecdoc.tecdoc_config import TecDocSettings


def test_client_headers_configuration():
    cfg = TecDocSettings(
        rapidapi_key="KEY",
        rapidapi_host="tecdoc-catalog.p.rapidapi.com",
    )

    client = AsyncTecDocClient(cfg)

    async def _peek_headers():
        async with client as c:
            return c._client.headers  # type: ignore[attr-defined]

    headers = asyncio.run(_peek_headers())
    assert headers.get("x-rapidapi-host") == cfg.rapidapi_host
    assert headers.get("x-rapidapi-key") == cfg.rapidapi_key


# 4) Service caching prevents duplicate GETs (we monkeypatch the client)
from src.core.services.tecdoc_service import TecDocService


class _DummyClient(AsyncTecDocClient):
    def __init__(self):
        super().__init__()
        self.calls = 0

    async def get(self, path: str, params=None):  # type: ignore[override]
        self.calls += 1
        return {"ok": True, "path": path}


# @pytest.mark.asyncio
# async def test_service_caches_identical_requests():
#     dummy = _DummyClient()
#     svc = TecDocService(client=dummy, cache_ttl=60)

#     p = ep.languages_list()
#     a = await svc._fetch(p)
#     b = await svc._fetch(p)

#     assert a == b == {"ok": True, "path": "/languages/list"}
#     assert dummy.calls == 1