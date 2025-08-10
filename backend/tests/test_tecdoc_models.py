"""
Test script to validate TecDoc Pydantic models against actual API responses.
Run from backend directory: python -m pytest tests/test_tecdoc_models.py -v
"""
import asyncio
import json
from typing import Any, Dict, List, Optional
import pytest
import httpx
from pydantic import ValidationError
import sys
from pathlib import Path

# Add backend project root (so 'backend' package is discoverable)
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # repu-ai-pilot/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT) + "/backend")

    print(f"Added {PROJECT_ROOT / 'backend'} to sys.path")

# Import the models and client
from src.core.models import tecdoc as models
from src.infrastructure.integrations.tecdoc.client import TecDocClient
from src.config.settings import get_settings

# Test data from the shell script
TEST_DATA = {
    "lang_id": 4,
    "country_id": 120,
    "type_id": 1,
    "manufacturer_id": 72,
    "model_id": 39795,
    "vehicle_id": 138817,
    "product_group_id": 100806,
    "article_id": 1043331,
    "supplier_id": 6304,
    "article_no": "113-1306X"
}

class TecDocModelTester:
    """Test harness for validating TecDoc models against real API responses."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = TecDocClient()
        self.results: List[Dict[str, Any]] = []
        
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
        
    def log_result(self, endpoint: str, model_name: str, success: bool, error: Optional[str] = None):
        """Log test result for reporting."""
        result = {
            "endpoint": endpoint,
            "model": model_name,
            "success": success,
            "error": error
        }
        self.results.append(result)
        
        # Print immediate feedback
        status = "✅" if success else "❌"
        print(f"{status} {endpoint} -> {model_name}")
        if error:
            print(f"   Error: {error[:200]}...")
            
    async def test_languages(self):
        """Test language endpoints."""
        try:
            # Test list languages
            result = await self.client.list_languages()
            assert isinstance(result, models.LanguagesList)
            assert hasattr(result, 'languages')
            self.log_result("/languages", "LanguagesList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/languages", "LanguagesList", False, str(e))
            
    async def test_countries(self):
        """Test country endpoints."""
        try:
            # Test list all countries
            result = await self.client.list_countries()
            assert isinstance(result, models.CountriesList)
            assert hasattr(result, 'countries')
            self.log_result("/countries", "CountriesList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/countries", "CountriesList", False, str(e))
            
        try:
            # Test list countries by language
            result = await self.client.list_countries(lang_id=TEST_DATA["lang_id"])
            assert isinstance(result, models.CountriesList)
            self.log_result("/countries?langId", "CountriesList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/countries?langId", "CountriesList", False, str(e))
            
    async def test_manufacturers(self):
        """Test manufacturer endpoints."""
        try:
            result = await self.client.list_manufacturers(
                country_id=TEST_DATA["country_id"],
                vehicle_type=TEST_DATA["type_id"]
            )
            assert isinstance(result, models.ManufacturersList)
            assert hasattr(result, 'manufacturers')
            assert hasattr(result, 'countManufactures')
            self.log_result("/manufacturers", "ManufacturersList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/manufacturers", "ManufacturersList", False, str(e))
            
    async def test_models(self):
        """Test model endpoints."""
        try:
            result = await self.client.list_models(
                manufacturer_id=TEST_DATA["manufacturer_id"],
                country_id=TEST_DATA["country_id"],
                vehicle_type=TEST_DATA["type_id"]
            )
            assert isinstance(result, models.ModelsList)
            assert hasattr(result, 'models')
            assert hasattr(result, 'countModels')
            self.log_result("/models", "ModelsList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/models", "ModelsList", False, str(e))
            
    async def test_vehicle_types(self):
        """Test vehicle type endpoints."""
        try:
            result = await self.client.list_vehicle_types(
                model_id=TEST_DATA["model_id"],
                country_id=TEST_DATA["country_id"],
                vehicle_type=TEST_DATA["type_id"]
            )
            assert isinstance(result, models.VehicleTypesList)
            assert hasattr(result, 'root')  # RootModel structure
            self.log_result("/vehicletypes", "VehicleTypesList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/vehicletypes", "VehicleTypesList", False, str(e))
            
    async def test_categories(self):
        """Test category endpoints (all 3 versions)."""
        # Test Category V1
        try:
            result = await self.client.list_categories(
                vehicle_id=TEST_DATA["vehicle_id"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"],
                version=1
            )
            assert isinstance(result, models.CategoryV1)
            assert hasattr(result, 'categories')
            self.log_result("/categories/v1", "CategoryV1", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/categories/v1", "CategoryV1", False, str(e))
            
        # Test Category V2
        try:
            result = await self.client.list_categories(
                vehicle_id=TEST_DATA["vehicle_id"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"],
                version=2
            )
            assert isinstance(result, models.CategoryV2)
            assert hasattr(result, 'categories')
            self.log_result("/categories/v2", "CategoryV2", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/categories/v2", "CategoryV2", False, str(e))
            
        # Test Category V3
        try:
            result = await self.client.list_categories(
                vehicle_id=TEST_DATA["vehicle_id"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"],
                version=3
            )
            assert isinstance(result, models.CategoryV3)
            assert hasattr(result, 'categories')
            self.log_result("/categories/v3", "CategoryV3", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/categories/v3", "CategoryV3", False, str(e))
            
    async def test_articles(self):
        """Test article endpoints."""
        # Test list articles
        try:
            result = await self.client.list_articles(
                vehicle_id=TEST_DATA["vehicle_id"],
                product_group_id=TEST_DATA["product_group_id"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"]
            )
            assert isinstance(result, models.ArticlesList)
            assert hasattr(result, 'articles')
            assert hasattr(result, 'countArticles')
            self.log_result("/articles", "ArticlesList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/articles", "ArticlesList", False, str(e))
            
        # Test article details
        try:
            result = await self.client.get_article_details(
                article_id=TEST_DATA["article_id"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"]
            )
            assert isinstance(result, models.ArticleCompleteDetails)
            assert hasattr(result, 'article')
            self.log_result("/article/details", "ArticleCompleteDetails", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/article/details", "ArticleCompleteDetails", False, str(e))
            
        # Test article media
        try:
            result = await self.client.get_article_media(
                article_id=TEST_DATA["article_id"]
            )
            assert isinstance(result, models.ArticleMediaInfoList)
            assert hasattr(result, 'root')  # RootModel structure
            self.log_result("/article/media", "ArticleMediaInfoList", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/article/media", "ArticleMediaInfoList", False, str(e))
            
        # Test article search
        try:
            result = await self.client.search_article_number(
                article_no=TEST_DATA["article_no"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"]
            )
            assert isinstance(result, models.ArticleSearch)
            assert hasattr(result, 'articles')
            assert hasattr(result, 'countArticles')
            self.log_result("/article/search", "ArticleSearch", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/article/search", "ArticleSearch", False, str(e))
            
        # Test article search with supplier
        try:
            result = await self.client.search_article_number(
                article_no=TEST_DATA["article_no"],
                country_id=TEST_DATA["country_id"],
                lang_id=TEST_DATA["lang_id"],
                supplier_id=TEST_DATA["supplier_id"]
            )
            assert isinstance(result, models.ArticleSearch)
            self.log_result("/article/search?supplierId", "ArticleSearch", True)
        except (ValidationError, AssertionError) as e:
            self.log_result("/article/search?supplierId", "ArticleSearch", False, str(e))
            
    async def run_all_tests(self):
        """Run all model validation tests."""
        print("\n" + "="*60)
        print("TecDoc Model Schema Validation Tests")
        print("="*60 + "\n")
        
        # Run all test groups
        await self.test_languages()
        await self.test_countries()
        await self.test_manufacturers()
        await self.test_models()
        await self.test_vehicle_types()
        await self.test_categories()
        await self.test_articles()
        
        # Print summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)
        
        success_count = sum(1 for r in self.results if r["success"])
        failure_count = len(self.results) - success_count
        
        print(f"\nTotal Tests: {len(self.results)}")
        print(f"✅ Passed: {success_count}")
        print(f"❌ Failed: {failure_count}")
        
        if failure_count > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['endpoint']} ({result['model']})")
                    if result["error"]:
                        # Print first line of error
                        error_lines = result["error"].split('\n')
                        print(f"    {error_lines[0][:100]}")
        
        print("\n" + "="*60)
        
        # Close the client
        await self.close()
        
        return success_count, failure_count


# Pytest fixtures and tests
@pytest.fixture
async def tester():
    """Create a tester instance."""
    tester = TecDocModelTester()
    yield tester
    await tester.close()


@pytest.mark.asyncio
async def test_language_models(tester):
    """Test language-related models."""
    await tester.test_languages()
    # Check that at least one test passed
    assert any(r["success"] for r in tester.results if "language" in r["endpoint"].lower())


@pytest.mark.asyncio
async def test_country_models(tester):
    """Test country-related models."""
    await tester.test_countries()
    assert any(r["success"] for r in tester.results if "countries" in r["endpoint"])


@pytest.mark.asyncio
async def test_manufacturer_models(tester):
    """Test manufacturer-related models."""
    await tester.test_manufacturers()
    assert any(r["success"] for r in tester.results if "manufacturers" in r["endpoint"])


@pytest.mark.asyncio
async def test_model_models(tester):
    """Test model-related models."""
    await tester.test_models()
    assert any(r["success"] for r in tester.results if "models" in r["endpoint"])


@pytest.mark.asyncio
async def test_vehicle_type_models(tester):
    """Test vehicle type models."""
    await tester.test_vehicle_types()
    assert any(r["success"] for r in tester.results if "vehicletypes" in r["endpoint"])


@pytest.mark.asyncio
async def test_category_models(tester):
    """Test all category model versions."""
    await tester.test_categories()
    # Should have results for v1, v2, and v3
    category_results = [r for r in tester.results if "categories" in r["endpoint"]]
    assert len(category_results) >= 3


@pytest.mark.asyncio
async def test_article_models(tester):
    """Test article-related models."""
    await tester.test_articles()
    article_results = [r for r in tester.results if "article" in r["endpoint"]]
    assert len(article_results) >= 4  # Should have multiple article endpoints tested


@pytest.mark.asyncio
async def test_all_models(tester):
    """Run all model tests and verify overall success."""
    await tester.run_all_tests()
    success_count = sum(1 for r in tester.results if r["success"])
    total_count = len(tester.results)
    
    # We expect at least 80% success rate for a passing test suite
    success_rate = success_count / total_count if total_count > 0 else 0
    assert success_rate >= 0.8, f"Only {success_count}/{total_count} tests passed ({success_rate:.1%})"


# Standalone script execution
async def main():
    """Run tests as a standalone script."""
    tester = TecDocModelTester()
    try:
        success, failures = await tester.run_all_tests()
        
        # Exit with appropriate code
        exit_code = 0 if failures == 0 else 1
        exit(exit_code)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    # Check if we have necessary environment variables
    settings = get_settings()
    if not settings.rapidapi_key or not settings.rapidapi_host:
        print("⚠️  Warning: RAPIDAPI_KEY or RAPIDAPI_HOST not set in environment")
        print("   Please set these in your .env file or environment")
        exit(1)
        
    # Run the tests
    asyncio.run(main())