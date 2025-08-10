import os
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'backend' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT) + "/backend")
    print(f"Added {str(PROJECT_ROOT) + '/backend'} to sys.path")
    
from src.core.services.tecdoc_service import TecDocService, TecDocSchemaError
from src.infrastructure.integrations.tecdoc import endpoints as ep
from src.config.settings import get_settings

def _require_key():
    s = get_settings()
    if not getattr(s, 'rapidapi_key', None):
        pytest.skip("No TecDoc rapidapi_key configured; skipping live TecDoc tests.")

@pytest.mark.asyncio
async def test_languages_typing():
    """Test that language endpoints return correct schema"""
    _require_key()
    svc = TecDocService()
    
    # Test list languages
    langs = await svc.list_languages()
    assert len(langs.root) >= 1
    
    # Verify language structure
    first_lang = langs.root[0]
    assert hasattr(first_lang, 'lngId')
    assert hasattr(first_lang, 'lngIso2')
    assert hasattr(first_lang, 'lngDescription')
    
    # Test get specific language
    lang_details = await svc.get_language(lang_id=4)  # English GB
    assert lang_details.lngId == "4"
    assert lang_details.lngDescription == "English (GB)"

@pytest.mark.asyncio
async def test_countries_typing():
    """Test that country endpoints return correct schema"""
    _require_key()
    svc = TecDocService()
    
    # Test list countries
    countries = await svc.list_countries()
    assert len(countries.countries) >= 1
    
    # Verify country structure
    first_country = countries.countries[0]
    assert hasattr(first_country, 'id')
    assert hasattr(first_country, 'couCode')
    assert hasattr(first_country, 'countryName')
    
    # Test get specific country
    country = await svc.get_country(lang_id=4, country_id=120)
    assert country.id == 120
    assert country.couCode == "IO"
    assert country.country_name == "British Indian Ocean Territory"
    
    # Test countries by language
    countries_by_lang = await svc.list_countries_by_lang(lang_id=4)
    assert len(countries_by_lang.countries) >= 1
    # Find the British Indian Ocean Territory
    io_country = next((c for c in countries_by_lang.countries if c.id == 120), None)
    assert io_country is not None
    assert io_country.couCode == "IO"

@pytest.mark.asyncio
async def test_manufacturers_and_models_typing():
    """Test manufacturer and model endpoints"""
    _require_key()
    svc = TecDocService()
    
    # Test list manufacturers
    manufacturers = await svc.list_manufacturers(lang_id=4, country_filter_id=120, type_id=1)
    assert manufacturers.countManufactures >= 1
    assert len(manufacturers.manufacturers) >= 1
    
    # Get MAZDA manufacturer (ID: 72)
    mazda = next((m for m in manufacturers.manufacturers if m.manufacturerId == 72), None)
    if mazda:
        # Test manufacturer details
        manu_details = await svc.manufacturer_details(manufacturer_id=72)
        assert manu_details.mfaId == 72
        assert manu_details.mfaBrand == "MAZDA"
        
        # Test list models for MAZDA
        models = await svc.list_models(
            manufacturer_id=72, 
            lang_id=4, 
            country_filter_id=120, 
            type_id=1
        )
        assert models.countModels >= 1
        
        # Test model details if CX-30 exists
        cx30 = next((m for m in models.models if m.modelId == 39795), None)
        if cx30:
            model_details = await svc.model_details(
                model_id=39795,
                lang_id=4,
                country_filter_id=120,
                type_id=1
            )
            assert model_details.modelId == 39795
            assert "CX-30" in model_details.modelName

@pytest.mark.asyncio
async def test_vehicle_types_typing():
    """Test vehicle type endpoints"""
    _require_key()
    svc = TecDocService()
    
    # Test list vehicle types
    vehicle_types = await svc.list_vehicle_types()
    assert len(vehicle_types.root) >= 1
    
    # Check structure
    first_type = vehicle_types.root[0]
    assert hasattr(first_type, 'id')
    assert hasattr(first_type, 'vehicleType')
    
    # Check for automobile type
    automobile = next((vt for vt in vehicle_types.root if vt.id == 1), None)
    assert automobile is not None
    assert automobile.vehicleType == "Automobile"

@pytest.mark.asyncio
async def test_articles_typing():
    """Test article endpoints"""
    _require_key()
    svc = TecDocService()
    
    # Test article search
    article_search = await svc.article_search(lang_id=4, article_search="113-1306X")
    assert article_search.articleSearchNr == "113-1306X"
    assert article_search.countArticles >= 1
    assert len(article_search.articles) >= 1
    
    # Verify article structure
    first_article = article_search.articles[0]
    assert hasattr(first_article, 'articleId')
    assert hasattr(first_article, 'articleNo')
    assert hasattr(first_article, 'supplierName')
    assert hasattr(first_article, 'imageLink')
    
    # Test article with supplier
    if article_search.articles:
        supplier_id = article_search.articles[0].supplierId
        article_with_supplier = await svc.article_search_with_supplier(
            lang_id=4,
            supplier_id=supplier_id,
            article_search="113-1306X"
        )
        assert article_with_supplier.articleSearchNr == "113-1306X"
        assert article_with_supplier.countArticles >= 0
    
    # Test article complete details
    article_details = await svc.article_complete_details(
        article_id=1043331,
        lang_id=4,
        country_filter_id=120
    )
    assert article_details.article.articleId == 1043331
    assert article_details.article.articleNo == "113-1306X"
    assert hasattr(article_details.article, 'articleInfo')
    assert hasattr(article_details.article, 'allSpecifications')
    
    # Test article media info
    media_info = await svc.article_all_media_info(article_id=1043331, lang_id=4)
    assert len(media_info.root) >= 1
    first_media = media_info.root[0]
    assert hasattr(first_media, 'articleMediaType')
    assert hasattr(first_media, 'articleMediaFileName')

@pytest.mark.asyncio
async def test_categories_typing():
    """Test category endpoints with different variants"""
    _require_key()
    svc = TecDocService()
    
    # Test Category V1
    cat_v1 = await svc.category_v1(
        vehicle_id=138817,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert len(cat_v1.categories) >= 1
    first_cat = cat_v1.categories[0]
    assert hasattr(first_cat, 'level')
    assert hasattr(first_cat, 'levelText_1')
    assert hasattr(first_cat, 'levelId_1')
    
    # Test Category V2
    cat_v2 = await svc.category_v2(
        vehicle_id=138817,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert isinstance(cat_v2.categories, dict)
    if cat_v2.categories:
        first_key = next(iter(cat_v2.categories))
        first_node = cat_v2.categories[first_key]
        assert hasattr(first_node, 'categoryId')
        assert hasattr(first_node, 'categoryName')
        assert hasattr(first_node, 'level')
        assert hasattr(first_node, 'children')
    
    # Test Category V3
    cat_v3 = await svc.category_v3(
        vehicle_id=138817,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert isinstance(cat_v3.categories, dict)
    if cat_v3.categories:
        first_key = next(iter(cat_v3.categories))
        first_node = cat_v3.categories[first_key]
        assert hasattr(first_node, 'text')
        assert hasattr(first_node, 'children')

@pytest.mark.asyncio
async def test_schema_error_handling():
    """Test that schema validation errors are properly raised"""
    _require_key()
    svc = TecDocService()
    
    # Mock a bad response by trying to parse wrong model
    # This should raise TecDocSchemaError
    try:
        # Force a schema error by using wrong model for the endpoint
        from src.core.models.tecdoc import ArticlesList
        # Manually call _get with wrong model
        await svc._get(ep.languages_list(), ArticlesList)
        assert False, "Should have raised TecDocSchemaError"
    except TecDocSchemaError as e:
        assert e.path == "/languages/list"
        assert e.model == ArticlesList
        assert e.raw is not None
        assert e.err is not None

@pytest.mark.asyncio
async def test_cache_functionality():
    """Test that caching works correctly"""
    _require_key()
    svc = TecDocService()
    
    # First call - should hit API
    langs1 = await svc.list_languages()
    
    # Second call - should hit cache
    langs2 = await svc.list_languages()
    
    # Both should return same data
    assert len(langs1.root) == len(langs2.root)
    assert langs1.root[0].lngId == langs2.root[0].lngId
    
    # Verify cache has the entry
    cache_key = "/languages/list"
    assert cache_key in svc._cache
    
    # Clear cache and call again
    svc._cache.clear()
    langs3 = await svc.list_languages()
    
    # Should still work and return same data
    assert len(langs1.root) == len(langs3.root)