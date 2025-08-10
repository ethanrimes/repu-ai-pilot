#!/usr/bin/env python3
"""
TecDoc API Pydantic Schema Generator
Fetches responses from TecDoc API endpoints and generates Pydantic models using datamodel-code-generator
"""

import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import sys

# Configuration
BASE_URL = "https://tecdoc-catalog.p.rapidapi.com"
API_KEY = ""
API_HOST = "tecdoc-catalog.p.rapidapi.com"

# Test data (same as in bash script)
LANG_ID = 4
COUNTRY_ID = 120
TYPE_ID = 1
MANUFACTURER_ID = 72
MODEL_ID = 39795
VEHICLE_ID = 138817
PRODUCT_GROUP_ID = 100806
ARTICLE_ID = 1043331
SUPPLIER_ID = 6304
ARTICLE_NO = "113-1306X"

# Headers for API requests
HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY
}

# Define all endpoints with their descriptions and parameter substitutions
ENDPOINTS = [
    # Language endpoints
    ("/languages/list", "LanguagesList", {}),
    (f"/languages/get-language/lang-id/{LANG_ID}", "LanguageDetails", {}),
    
    # Country endpoints
    ("/countries/list", "CountriesList", {}),
    (f"/countries/get-country/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}", "CountryDetails", {}),
    (f"/countries/list-countries-by-lang-id/{LANG_ID}", "CountriesByLanguage", {}),
    
    # Vehicle type endpoints
    ("/types/list-vehicles-type", "VehicleTypesList", {}),
    
    # Supplier endpoints
    ("/suppliers/list", "SuppliersList", {}),
    
    # Manufacturer endpoints
    (f"/manufacturers/list/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "ManufacturersList", {}),
    (f"/manufacturers/find-by-id/{MANUFACTURER_ID}", "ManufacturerDetails", {}),
    
    # Model endpoints
    (f"/models/list/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "ModelsList", {}),
    (f"/models/find-by/{MODEL_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "ModelDetails", {}),
    (f"/models/get-model-details-by-vehicle-id/{VEHICLE_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "ModelDetailsByVehicle", {}),
    
    # Vehicle type detailed information
    (f"/types/vehicle-type-details/{VEHICLE_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "VehicleTypeDetails", {}),
    
    # Vehicle engine types
    (f"/types/list-vehicles-types/{MODEL_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "VehicleEngineTypes", {}),
    
    # Category endpoints (3 variants)
    (f"/category/category-products-groups-variant-1/{VEHICLE_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "CategoryV1", {}),
    (f"/category/category-products-groups-variant-2/{VEHICLE_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "CategoryV2", {}),
    (f"/category/category-products-groups-variant-3/{VEHICLE_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "CategoryV3", {}),
    
    # Article endpoints
    (f"/articles/list/vehicle-id/{VEHICLE_ID}/product-group-id/{PRODUCT_GROUP_ID}/manufacturer-id/{MANUFACTURER_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/type-id/{TYPE_ID}", "ArticlesList", {}),
    (f"/articles/article-id-details/{ARTICLE_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}", "ArticleCompleteDetails", {}),
    (f"/articles/details/{ARTICLE_ID}/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}", "ArticleSpecificationDetails", {}),
    (f"/articles/article-number-details/lang-id/{LANG_ID}/country-filter-id/{COUNTRY_ID}/article-no/{ARTICLE_NO}", "ArticleNumberDetails", {}),
    (f"/articles/article-all-media-info/{ARTICLE_ID}/lang-id/{LANG_ID}", "ArticleMediaInfo", {}),
    (f"/articles/search/lang-id/{LANG_ID}/article-search/{ARTICLE_NO}", "ArticleSearch", {}),
    (f"/articles/search/lang-id/{LANG_ID}/supplier-id/{SUPPLIER_ID}/article-search/{ARTICLE_NO}", "ArticleSearchWithSupplier", {}),
]


def fetch_endpoint(endpoint: str) -> Tuple[bool, Dict]:
    """Fetch data from an endpoint and return success status and JSON response"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=HEADERS, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            print(f"  ✗ Failed with status {response.status_code}: {response.text[:200]}")
            return False, {}
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return False, {}


def save_response(endpoint: str, model_name: str, data: Dict, output_dir: Path):
    """Save API response to JSON file"""
    # Clean endpoint for filename
    filename = model_name.lower() + "_response.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filepath


def generate_pydantic_model(json_file: Path, model_name: str, output_dir: Path):
    """Generate Pydantic model from JSON file using datamodel-code-generator"""
    output_file = output_dir / f"{model_name.lower()}_model.py"
    
    cmd = [
        "datamodel-codegen",
        "--input", str(json_file),
        "--input-file-type", "json",
        "--output", str(output_file),
        "--class-name", model_name,
        "--use-schema-description",
        "--field-constraints",
        "--use-default",
        "--reuse-model",
        "--enum-field-as-literal", "all",
        "--target-python-version", "3.13"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Generated model: {output_file.name}")
            return True
        else:
            print(f"  ✗ Failed to generate model: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ Error generating model: {str(e)}")
        return False


def create_combined_models_file(models_dir: Path):
    """Combine all individual model files into a single file"""
    combined_file = models_dir.parent / "tecdoc_models.py"
    
    with open(combined_file, 'w', encoding='utf-8') as outfile:
        outfile.write('"""TecDoc API Pydantic Models - Auto-generated"""\n\n')
        outfile.write('from typing import Any, Dict, List, Optional, Union\n')
        outfile.write('from pydantic import BaseModel, Field\n')
        outfile.write('from enum import Enum\n\n')
        
        # Collect all model files
        model_files = sorted(models_dir.glob("*_model.py"))
        
        # Extract and combine unique imports and models
        all_content = []
        for model_file in model_files:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Skip the import statements (we already have them)
                lines = content.split('\n')
                model_content = []
                skip_imports = True
                for line in lines:
                    if skip_imports and (line.strip() == '' or line.startswith('from ') or line.startswith('import ')):
                        continue
                    else:
                        skip_imports = False
                        model_content.append(line)
                
                all_content.append('\n'.join(model_content))
        
        # Write all models
        outfile.write('\n\n'.join(all_content))
    
    print(f"\n✓ Created combined models file: {combined_file}")
    return combined_file


def main():
    """Main function to orchestrate the schema generation process"""
    print("=== TecDoc API Pydantic Schema Generator ===\n")
    
    # Create output directories
    output_dir = Path("tecdoc_schemas")
    responses_dir = output_dir / "responses"
    models_dir = output_dir / "models"
    
    responses_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Output directory: {output_dir.absolute()}\n")
    
    successful_models = []
    failed_endpoints = []
    
    # Process each endpoint
    for endpoint, model_name, params in ENDPOINTS:
        print(f"\nProcessing: {model_name}")
        print(f"  Endpoint: {endpoint}")
        
        # Fetch data
        print("  Fetching data...")
        success, data = fetch_endpoint(endpoint)
        
        if success and data:
            # Save response
            json_file = save_response(endpoint, model_name, data, responses_dir)
            print(f"  ✓ Saved response: {json_file.name}")
            
            # Generate Pydantic model
            print("  Generating Pydantic model...")
            if generate_pydantic_model(json_file, model_name, models_dir):
                successful_models.append(model_name)
            else:
                failed_endpoints.append((endpoint, model_name, "Model generation failed"))
        else:
            failed_endpoints.append((endpoint, model_name, "API request failed"))
    
    # Create combined models file
    if successful_models:
        create_combined_models_file(models_dir)
    
    # Summary
    print("\n=== Summary ===")
    print(f"Total endpoints: {len(ENDPOINTS)}")
    print(f"Successful models: {len(successful_models)}")
    print(f"Failed: {len(failed_endpoints)}")
    
    if failed_endpoints:
        print("\nFailed endpoints:")
        for endpoint, model_name, reason in failed_endpoints:
            print(f"  - {model_name}: {reason}")
    
    print(f"\n✓ Schema generation complete!")
    print(f"  Response JSONs: {responses_dir}")
    print(f"  Individual models: {models_dir}")
    print(f"  Combined models: {output_dir / 'tecdoc_models.py'}")


if __name__ == "__main__":
    main()