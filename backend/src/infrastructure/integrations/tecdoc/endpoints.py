from __future__ import annotations
from typing import Any

BASE = ""

# These functions mirror backend/scripts/test_tecdoc_endpoints.sh one-to-one.
# They build *path-only* strings that are joined to the configured base_url by the client.

# 1. Language endpoints
languages_list = lambda: f"/languages/list"
get_language = lambda lang_id: f"/languages/get-language/lang-id/{lang_id}"

# 2. Country endpoints
countries_list = lambda: f"/countries/list"
get_country = (
    lambda lang_id, country_id: f"/countries/get-country/lang-id/{lang_id}/country-filter-id/{country_id}"
)
list_countries_by_lang = lambda lang_id: f"/countries/list-countries-by-lang-id/{lang_id}"

# 3. Vehicle type endpoints
list_vehicle_types = lambda: f"/types/list-vehicles-type"

# 4. Supplier endpoints
suppliers_list = lambda: f"/suppliers/list"

# 5. Manufacturer endpoints
manufacturers_list = (
    lambda lang_id, country_id, type_id: f"/manufacturers/list/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
manufacturer_by_id = lambda manufacturer_id: f"/manufacturers/find-by-id/{manufacturer_id}"

# 6. Model endpoints
models_list = (
    lambda manufacturer_id, lang_id, country_id, type_id: f"/models/list/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
model_by_id = (
    lambda model_id, lang_id, country_id, type_id: f"/models/find-by/{model_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
model_details_by_vehicle_id = (
    lambda vehicle_id, lang_id, country_id, type_id: f"/models/get-model-details-by-vehicle-id/{vehicle_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)

# 7. Vehicle type detailed information
vehicle_type_details = (
    lambda vehicle_id, manufacturer_id, lang_id, country_id, type_id: f"/types/vehicle-type-details/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)

# 8. Vehicle engine types
list_vehicle_engine_types = (
    lambda model_id, manufacturer_id, lang_id, country_id, type_id: f"/types/list-vehicles-types/{model_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)

# 9. Category endpoints (3 variants)
category_variant_1 = (
    lambda vehicle_id, manufacturer_id, lang_id, country_id, type_id: f"/category/category-products-groups-variant-1/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
category_variant_2 = (
    lambda vehicle_id, manufacturer_id, lang_id, country_id, type_id: f"/category/category-products-groups-variant-2/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
category_variant_3 = (
    lambda vehicle_id, manufacturer_id, lang_id, country_id, type_id: f"/category/category-products-groups-variant-3/{vehicle_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)

# 10. Article endpoints
articles_list = (
    lambda vehicle_id, product_group_id, manufacturer_id, lang_id, country_id, type_id: f"/articles/list/vehicle-id/{vehicle_id}/product-group-id/{product_group_id}/manufacturer-id/{manufacturer_id}/lang-id/{lang_id}/country-filter-id/{country_id}/type-id/{type_id}"
)
article_id_complete_details = (
    lambda article_id, lang_id, country_id: f"/articles/article-id-details/{article_id}/lang-id/{lang_id}/country-filter-id/{country_id}"
)
article_id_spec_details = (
    lambda article_id, lang_id, country_id: f"/articles/details/{article_id}/lang-id/{lang_id}/country-filter-id/{country_id}"
)
article_number_complete_details = (
    lambda lang_id, country_id, article_no: f"/articles/article-number-details/lang-id/{lang_id}/country-filter-id/{country_id}/article-no/{article_no}"
)
article_all_media = lambda article_id, lang_id: f"/articles/article-all-media-info/{article_id}/lang-id/{lang_id}"
article_search = lambda lang_id, article_no: f"/articles/search/lang-id/{lang_id}/article-search/{article_no}"
article_search_with_supplier = (
    lambda lang_id, supplier_id, article_no: f"/articles/search/lang-id/{lang_id}/supplier-id/{supplier_id}/article-search/{article_no}"
)