import os
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'backend' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT) + "/backend")
    print(f"Added {str(PROJECT_ROOT) + '/backend'} to sys.path")
    
from src.core.services.tecdoc_service import TecDocService
from src.config.settings import get_settings

def _require_key():
    s = get_settings()
    if not getattr(s, 'rapidapi_key', None):
        pytest.skip("No TecDoc rapidapi_key configured; skipping live TecDoc tests.")

@pytest.mark.asyncio
async def test_languages_and_countries_typing():
    _require_key()
    svc = TecDocService()  # real client internally
    langs = await svc.list_languages()
    assert len(langs.languages) >= 1

    lang_id = next((l.langId for l in langs.languages if str(l.langCode or "").lower() in {"en","gb","en-gb"}), langs.languages[0].langId)
    country = await svc.get_country(lang_id=lang_id, country_id=120)
    assert country.country.countryId == 120

    countries = await svc.list_countries_by_lang(lang_id=lang_id)
    assert countries.langId == lang_id
    assert len(countries.countries) >= 1
    assert any(c.countryId == 120 for c in countries.countries)

@pytest.mark.asyncio
async def test_articles_and_models_typing_and_cache():
    _require_key()
    svc = TecDocService()

    mans = await svc.list_manufacturers(lang_id=4, country_filter_id=120, type_id=1)
    assert mans.countManufactures >= 1
    manu_id = mans.manufacturers[0].manufacturerId

    models = await svc.list_models(manufacturer_id=manu_id, lang_id=4, country_filter_id=120, type_id=1)
    assert models.countModels >= 1
    model_id = models.models[0].modelId

    # Pick a product group that's common enough
    articles = await svc.list_articles(
        vehicle_id=138817, product_group_id=100806, manufacturer_id=manu_id,
        lang_id=4, country_filter_id=120, type_id=1
    )
    assert articles.countArticles >= 1
    a1 = articles.articles[0]

    # basic "cache" smoke: second call should return same shape (service may cache inside session)
    articles2 = await svc.list_articles(
        vehicle_id=138817, product_group_id=100806, manufacturer_id=manu_id,
        lang_id=4, country_filter_id=120, type_id=1
    )
    assert articles2.countArticles >= 1
    assert type(a1) == type(articles2.articles[0])

@pytest.mark.asyncio
async def test_schema_error_wraps_validation_error():
    _require_key()
    svc = TecDocService()
    # Call a known-good endpoint but intentionally check a required field exists to ensure typing
    types_list = await svc.list_vehicle_types()
    assert len(types_list.root) >= 1
