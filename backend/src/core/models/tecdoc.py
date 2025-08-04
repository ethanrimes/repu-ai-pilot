# backend/api/models/schemas/tecdoc.py
"""TecDoc API response schemas using Pydantic
Path: backend/api/models/schemas/tecdoc.py
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import date

class Manufacturer(BaseModel):
    """TecDoc Manufacturer schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    mfaId: int = Field(alias="mfaId")
    brand: str = Field(alias="mfaBrand")
    is_cv: bool = Field(alias="mfaCv")  # Commercial vehicles
    is_dc: bool = Field(alias="mfaDc")
    is_eng: bool = Field(alias="mfaEng")
    is_mtb: bool = Field(alias="mfaMtb")  # Motorbike
    is_pc: bool = Field(alias="mfaPc")  # Passenger cars
    match_code: str = Field(alias="mfaMatchCode")
    models_count: int = Field(alias="mfaModelsCount")
    # Additional fields from response
    is_vgl: Optional[bool] = Field(default=None, alias="mfaVgl")
    is_axl: Optional[bool] = Field(default=None, alias="mfaAxl")
    pc_ctm: Optional[int] = Field(default=None, alias="mfaPcCtm")
    cv_ctm: Optional[int] = Field(default=None, alias="mfaCvCtm")

class VehicleType(BaseModel):
    """TecDoc Vehicle Type schema"""
    id: int
    vehicle_type: str = Field(alias="vehicleType")

class VehicleDetails(BaseModel):
    """TecDoc Vehicle Details schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    brand: str
    model_type: str = Field(alias="modelType")
    type_engine: str = Field(alias="typeEngine")
    construction_start: str = Field(alias="constructionIntervalStart")
    construction_end: str = Field(alias="constructionIntervalEnd")
    power_kw: Optional[float] = Field(alias="powerKw")
    power_ps: Optional[float] = Field(alias="powerPs")
    capacity_tax: Optional[float] = Field(default=None, alias="capacityTax")
    capacity_lt: Optional[float] = Field(alias="capacityLt")
    capacity_tech: Optional[float] = Field(alias="capacityTech")
    cylinders: Optional[int] = Field(alias="numberOfCylinders")
    valves: Optional[int] = Field(alias="numberOfValves")
    body_type: Optional[str] = Field(alias="bodyType")
    engine_type: Optional[str] = Field(alias="engineType")
    gear_type: Optional[str] = Field(default=None, alias="gearType")
    drive_type: Optional[str] = Field(alias="driveType")
    brake_system: Optional[str] = Field(default=None, alias="brakeSystem")
    brake_type: Optional[str] = Field(default=None, alias="brakeType")
    fuel_type: Optional[str] = Field(alias="fuelType")
    catalysator_type: Optional[str] = Field(default=None, alias="catalysatorType")
    fuel_mixture: Optional[str] = Field(default=None, alias="fuelMixture")
    engine_codes: Optional[str] = Field(alias="engCodes")
    abs: Optional[Any] = Field(default=None)
    asr: Optional[Any] = Field(default=None)

class Vehicle(BaseModel):
    """TecDoc Vehicle schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    vehicle_type_details: VehicleDetails = Field(alias="vehicleTypeDetails")

class Model(BaseModel):
    """TecDoc Model schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    model_id: int = Field(alias="modelId")
    model_name: str = Field(alias="modelName")

class ProductCategory(BaseModel):
    """TecDoc Product Category schema - single category"""
    text: str
    children: Optional[Dict[str, 'ProductCategory']] = Field(default_factory=dict)

class ProductCategoriesResponse(BaseModel):
    """Response containing all product categories"""
    categories: Dict[str, ProductCategory]

class Supplier(BaseModel):
    """TecDoc Supplier schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    sup_id: str = Field(alias="supId")
    brand: str = Field(alias="supBrand")
    match_code: str = Field(alias="supMatchCode")
    logo_name: Optional[str] = Field(alias="supLogoName")

class ArticleSpecification(BaseModel):
    """Article specification details"""
    model_config = ConfigDict(populate_by_name=True)
    
    criteria_name: str = Field(alias="criteriaName")
    criteria_value: Optional[str] = Field(alias="criteriaValue")

class OEMNumber(BaseModel):
    """OEM Number mapping"""
    model_config = ConfigDict(populate_by_name=True)
    
    oem_brand: str = Field(alias="oemBrand")
    oem_display_no: str = Field(alias="oemDisplayNo")

class CompatibleCar(BaseModel):
    """Compatible vehicle for an article"""
    model_config = ConfigDict(populate_by_name=True)
    
    vehicle_id: int = Field(alias="vehicleId")
    model_id: int = Field(alias="modelId")
    manufacturer_name: str = Field(alias="manufacturerName")
    model_name: str = Field(alias="modelName")
    type_engine_name: str = Field(alias="typeEngineName")
    construction_start: str = Field(alias="constructionIntervalStart")
    construction_end: str = Field(alias="constructionIntervalEnd")

class ArticleInfo(BaseModel):
    """Article info nested object"""
    model_config = ConfigDict(populate_by_name=True)
    
    article_id: int = Field(alias="articleId")
    article_no: str = Field(alias="articleNo")
    supplier_id: int = Field(alias="supplierId")
    supplier_name: str = Field(alias="supplierName")
    is_accessory: Optional[bool] = Field(alias="isAccessory")
    article_product_name: str = Field(alias="articleProductName")

class EANNumbers(BaseModel):
    """EAN numbers wrapper"""
    model_config = ConfigDict(populate_by_name=True)
    
    ean_numbers: str = Field(alias="eanNumbers")

class Article(BaseModel):
    """TecDoc Article schema"""
    model_config = ConfigDict(populate_by_name=True)
    
    article_id: int = Field(alias="articleId")
    article_no: str = Field(alias="articleNo")
    supplier_name: str = Field(alias="supplierName")
    supplier_id: int = Field(alias="supplierId")
    article_product_name: str = Field(alias="articleProductName")
    product_id: Optional[int] = Field(default=None, alias="productId")
    
    # Media fields
    article_media_type: Optional[int] = Field(default=None, alias="articleMediaType")
    article_media_file_name: Optional[str] = Field(default=None, alias="articleMediaFileName")
    
    # Nested objects
    article_info: Optional[ArticleInfo] = Field(default=None, alias="articleInfo")
    all_specifications: Optional[List[ArticleSpecification]] = Field(default_factory=list, alias="allSpecifications")
    ean_no: Optional[EANNumbers] = Field(default=None, alias="eanNo")
    oem_no: Optional[List[OEMNumber]] = Field(default_factory=list, alias="oemNo")
    
    # Image links
    image_link: Optional[str] = Field(default=None, alias="imageLink")
    image_media: Optional[str] = Field(default=None, alias="imageMedia")
    s3_image_link: Optional[str] = Field(default=None, alias="s3ImageLink")
    
    # Compatible vehicles
    compatible_cars: Optional[List[CompatibleCar]] = Field(default_factory=list, alias="compatibleCars")

class ArticleResponse(BaseModel):
    """Wrapper for single article response"""
    article: Article

class ArticleSearchResponse(BaseModel):
    """Response for article search by vehicle and product group"""
    model_config = ConfigDict(populate_by_name=True)
    
    vehicle_id: int = Field(alias="vehicleId")
    product_group_id: int = Field(alias="productGroupId")
    count_articles: int = Field(alias="countArticles")
    articles: List[Article]

# Update forward references for recursive models
ProductCategory.model_rebuild()