#!/bin/bash

# Configuration
BASE_URL="https://tecdoc-catalog.p.rapidapi.com"
API_KEY=""
API_HOST="tecdoc-catalog.p.rapidapi.com"

# Define your test data combinations here
# These IDs should be valid and correspond to each other in the hierarchy
LANG_ID=4
COUNTRY_ID=120
TYPE_ID=1
MANUFACTURER_ID=72
MODEL_ID=39795  # Replace with actual model ID
VEHICLE_ID=138817
PRODUCT_GROUP_ID=100806  # Replace with actual product group ID
ARTICLE_ID=1043331  # Replace with actual article ID
SUPPLIER_ID=6304  # Replace with actual supplier ID
ARTICLE_NO="113-1306X"  # Replace with actual article number

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to make API call and display result
make_request() {
    local endpoint=$1
    local description=$2
    
    echo -e "\n${YELLOW}Testing: ${description}${NC}"
    echo "Endpoint: ${endpoint}"
    
    response=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}${endpoint}" \
        -H "x-rapidapi-host: ${API_HOST}" \
        -H "x-rapidapi-key: ${API_KEY}")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Success (HTTP ${http_code})${NC}"
        echo "Response preview: $(echo "$body" | head -c 200)..."
    else
        echo -e "${RED}✗ Failed (HTTP ${http_code})${NC}"
        echo "Response: $body"
    fi
}

echo "=== TecDoc API Endpoint Testing ==="
echo "Configuration:"
echo "  Language ID: $LANG_ID"
echo "  Country ID: $COUNTRY_ID"
echo "  Type ID: $TYPE_ID"
echo "  Manufacturer ID: $MANUFACTURER_ID"
echo "  Model ID: $MODEL_ID"
echo "  Vehicle ID: $VEHICLE_ID"
echo "  Product Group ID: $PRODUCT_GROUP_ID"
echo "  Article ID: $ARTICLE_ID"

# Test all endpoints

# 1. Language endpoints
make_request "/languages/list" "Get all languages"
make_request "/languages/get-language/lang-id/${LANG_ID}" "Get language details by ID"

# 2. Country endpoints
make_request "/countries/list" "Get all countries"
make_request "/countries/get-country/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}" "Get country details by ID"
make_request "/countries/list-countries-by-lang-id/${LANG_ID}" "Get countries by language ID"

# 3. Vehicle type endpoints
make_request "/types/list-vehicles-type" "Get all vehicle types"

# 4. Supplier endpoints
make_request "/suppliers/list" "Get all suppliers"

# 5. Manufacturer endpoints
make_request "/manufacturers/list/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get manufacturers"
make_request "/manufacturers/find-by-id/${MANUFACTURER_ID}" "Get manufacturer details by ID"

# 6. Model endpoints
make_request "/models/list/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get models"
make_request "/models/find-by/${MODEL_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get model details by ID"
make_request "/models/get-model-details-by-vehicle-id/${VEHICLE_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get model details by vehicle ID"

# 7. Vehicle type detailed information
make_request "/types/vehicle-type-details/${VEHICLE_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get vehicle type detailed information"

# 8. Vehicle engine types
make_request "/types/list-vehicles-types/${MODEL_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get all vehicle engine types"

# 9. Category endpoints (3 variants)
make_request "/category/category-products-groups-variant-1/${VEHICLE_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get category V1"
make_request "/category/category-products-groups-variant-2/${VEHICLE_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get category V2"
make_request "/category/category-products-groups-variant-3/${VEHICLE_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get category V3"

# 10. Article endpoints
make_request "/articles/list/vehicle-id/${VEHICLE_ID}/product-group-id/${PRODUCT_GROUP_ID}/manufacturer-id/${MANUFACTURER_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/type-id/${TYPE_ID}" "Get articles list"
make_request "/articles/article-id-details/${ARTICLE_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}" "Get article complete details by ID"
make_request "/articles/details/${ARTICLE_ID}/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}" "Get article specification details by ID"
make_request "/articles/article-number-details/lang-id/${LANG_ID}/country-filter-id/${COUNTRY_ID}/article-no/${ARTICLE_NO}" "Get complete details for article number"
make_request "/articles/article-all-media-info/${ARTICLE_ID}/lang-id/${LANG_ID}" "Get article all media"
make_request "/articles/search/lang-id/${LANG_ID}/article-search/${ARTICLE_NO}" "Search articles by article number"
make_request "/articles/search/lang-id/${LANG_ID}/supplier-id/${SUPPLIER_ID}/article-search/${ARTICLE_NO}" "Search articles by article number and supplier ID"

echo -e "\n=== Testing Complete ==="