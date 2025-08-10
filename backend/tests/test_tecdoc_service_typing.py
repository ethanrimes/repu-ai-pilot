import os
import pytest
import sys
from pathlib import Path

# Ensure repository root is on sys.path so 'backend' package is importable
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))
    print(f"Added {BACKEND_PATH} to sys.path")
    
from src.core.services.tecdoc_service import TecDocService, TecDocSchemaError
from src.infrastructure.integrations.tecdoc import endpoints as ep
from src.config.settings import get_settings

def _require_key():
    s = get_settings()
    if not getattr(s, 'rapidapi_key', None):
        pytest.skip("No TecDoc rapidapi_key configured; skipping live TecDoc tests.")

@pytest.mark.asyncio
async def test_suppliers_typing():
    """Test supplier endpoints"""
    _require_key()
    svc = TecDocService()
    
    # Test list suppliers
    suppliers = await svc.list_suppliers()
    assert len(suppliers.root) >= 1
    
    # Verify supplier structure
    first_supplier = suppliers.root[0]
    assert hasattr(first_supplier, 'supId')
    assert hasattr(first_supplier, 'supBrand')
    assert hasattr(first_supplier, 'supMatchCode')
    assert hasattr(first_supplier, 'supLogoName')


@pytest.mark.asyncio
async def test_vehicle_detailed_typing():
    """Test vehicle type detailed information and engine types"""
    _require_key()
    svc = TecDocService()
    
    # Test vehicle type details
    vehicle_details = await svc.vehicle_type_details(
        vehicle_id=138817,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert hasattr(vehicle_details, 'vehicleTypeDetails')
    details = vehicle_details.vehicleTypeDetails
    assert hasattr(details, 'brand')
    assert hasattr(details, 'modelType')
    assert hasattr(details, 'typeEngine')
    assert hasattr(details, 'powerKw')
    assert hasattr(details, 'powerPs')
    
    # Test vehicle engine types
    engine_types = await svc.list_vehicle_engine_types(
        model_id=39795,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert hasattr(engine_types, 'modelType')
    assert hasattr(engine_types, 'countModelTypes')
    assert hasattr(engine_types, 'modelTypes')
    assert len(engine_types.modelTypes) >= 1
    
    # Verify engine type structure
    if engine_types.modelTypes:
        first_engine = engine_types.modelTypes[0]
        assert hasattr(first_engine, 'vehicleId')
        assert hasattr(first_engine, 'manufacturerName')
        assert hasattr(first_engine, 'modelName')
        assert hasattr(first_engine, 'typeEngineName')
        assert hasattr(first_engine, 'powerKw')
        assert hasattr(first_engine, 'fuelType')


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
            
        # Test model details by vehicle ID
        model_by_vehicle = await svc.model_details_by_vehicle(
            vehicle_id=138817,
            lang_id=4,
            country_filter_id=120,
            type_id=1
        )
        assert hasattr(model_by_vehicle, 'modelId')
        assert hasattr(model_by_vehicle, 'modelName')

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
    
    # Test articles list
    articles_list = await svc.list_articles(
        vehicle_id=138817,
        product_group_id=100806,
        manufacturer_id=72,
        lang_id=4,
        country_filter_id=120,
        type_id=1
    )
    assert hasattr(articles_list, 'vehicleId')
    assert hasattr(articles_list, 'productGroupId')
    assert hasattr(articles_list, 'countArticles')
    assert hasattr(articles_list, 'articles')
    
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
    
    # Test article specification details
    article_spec = await svc.article_specification_details(
        article_id=1043331,
        lang_id=4,
        country_filter_id=120
    )
    assert article_spec.articleId == "1043331"  # Note: This is a string in the response
    assert hasattr(article_spec, 'article')
    assert hasattr(article_spec, 'articleAllSpecifications')
    
    # Test article number details
    article_num_details = await svc.article_number_details(
        lang_id=4,
        country_filter_id=120,
        article_no="113-1306X"
    )
    assert article_num_details.articleNo == "113-1306X"
    assert hasattr(article_num_details, 'countArticles')
    assert hasattr(article_num_details, 'articles')
    assert len(article_num_details.articles) >= 1
    
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
        # Children can be either dict (has children) or list (empty/leaf node)
        assert isinstance(first_node.children, (dict, list))
    
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
        # Children can be either dict (has children) or list (empty/leaf node)
        assert isinstance(first_node.children, (dict, list))

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

# @pytest.mark.asyncio
# async def test_cache_functionality():
#     """Test that caching works correctly"""
#     _require_key()
#     svc = TecDocService()
    
#     # First call - should hit API
#     langs1 = await svc.list_languages()
    
#     # Second call - should hit cache
#     langs2 = await svc.list_languages()
    
#     # Both should return same data
#     assert len(langs1.root) == len(langs2.root)
#     assert langs1.root[0].lngId == langs2.root[0].lngId
    
#     # Verify cache has the entry
#     cache_key = "/languages/list"
#     assert cache_key in svc._cache
    
#     # Clear cache and call again
#     svc._cache.clear()
#     langs3 = await svc.list_languages()
    
#     # Should still work and return same data
#     assert len(langs1.root) == len(langs3.root)


@pytest.mark.asyncio
async def test_all_endpoints_coverage():
    """Summary test to ensure all 24 endpoints are covered"""
    _require_key()
    svc = TecDocService()
    
    # This test verifies we have methods for all endpoints
    endpoints_tested = [
        # Language endpoints (2)
        ('list_languages', '/languages/list'),
        ('get_language', '/languages/get-language/lang-id/{lang_id}'),
        
        # Country endpoints (3)
        ('list_countries', '/countries/list'),
        ('get_country', '/countries/get-country/lang-id/{lang_id}/country-filter-id/{country_id}'),
        ('list_countries_by_lang', '/countries/list-countries-by-lang-id/{lang_id}'),
        
        # Vehicle type endpoints (1)
        ('list_vehicle_types', '/types/list-vehicles-type'),
        
        # Supplier endpoints (1)
        ('list_suppliers', '/suppliers/list'),
        
        # Manufacturer endpoints (2)
        ('list_manufacturers', '/manufacturers/list/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('manufacturer_details', '/manufacturers/find-by-id/{manufacturer_id}'),
        
        # Model endpoints (3)
        ('list_models', '/models/list/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('model_details', '/models/find-by/{model_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('model_details_by_vehicle', '/models/get-model-details-by-vehicle-id/{vehicle_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        
        # Vehicle type detailed information (1)
        ('vehicle_type_details', '/types/vehicle-type-details/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        
        # Vehicle engine types (1)
        ('list_vehicle_engine_types', '/types/list-vehicles-types/{model_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        
        # Category endpoints (3)
        ('category_v1', '/category/category-products-groups-variant-1/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('category_v2', '/category/category-products-groups-variant-2/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('category_v3', '/category/category-products-groups-variant-3/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        
        # Article endpoints (7)
        ('list_articles', '/articles/list/vehicle-id/{vehicle_id}/product-group-id/{product_group_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}'),
        ('article_complete_details', '/articles/article-id-details/{article_id}/lang-id/{lang_id}/country-filter-id/{country_id}'),
        ('article_specification_details', '/articles/details/{article_id}/lang-id/{lang_id}/country-filter-id/{country_id}'),
        ('article_number_details', '/articles/article-number-details/lang-id/{lang_id}/country-filter-id/{country_id}/article-no/{article_no}'),
        ('article_all_media_info', '/articles/article-all-media-info/{article_id}/lang-id/{lang_id}'),
        ('article_search', '/articles/search/lang-id/{lang_id}/article-search/{article_no}'),
        ('article_search_with_supplier', '/articles/search/lang-id/{lang_id}/supplier-id/{supplier_id}/article-search/{article_no}'),
    ]
    
    # Verify all methods exist
    for method_name, endpoint_path in endpoints_tested:
        assert hasattr(svc, method_name), f"Service missing method: {method_name} for endpoint: {endpoint_path}"
    
    # Total: 24 endpoints
    assert len(endpoints_tested) == 24, f"Expected 24 endpoints, got {len(endpoints_tested)}"
    print(f"✓ All 24 endpoints have corresponding service methods")