# backend/api/models/schemas/tecdoc.py
"""TecDoc API response schemas using Pydantic
Path: backend/api/models/schemas/tecdoc.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

class Manufacturer(BaseModel):
    """TecDoc Manufacturer schema"""
    mfaId: int = Field(alias="mfaId")
    brand: str = Field(alias="mfaBrand")
    is_cv: bool = Field(alias="mfaCv")  # Commercial vehicles
    is_dc: bool = Field(alias="mfaDc")
    is_eng: bool = Field(alias="mfaEng")
    is_mtb: bool = Field(alias="mfaMtb")  # Motorbike
    is_pc: bool = Field(alias="mfaPc")  # Passenger cars
    match_code: str = Field(alias="mfaMatchCode")
    models_count: int = Field(alias="mfaModelsCount")
    
    class Config:
        populate_by_name = True

class VehicleType(BaseModel):
    """TecDoc Vehicle Type schema"""
    id: int
    vehicle_type: str = Field(alias="vehicleType")

class VehicleDetails(BaseModel):
    """TecDoc Vehicle Details schema"""
    brand: str
    model_type: str = Field(alias="modelType")
    type_engine: str = Field(alias="typeEngine")
    construction_start: str = Field(alias="constructionIntervalStart")
    construction_end: str = Field(alias="constructionIntervalEnd")
    power_kw: Optional[float] = Field(alias="powerKw")
    power_ps: Optional[float] = Field(alias="powerPs")
    capacity_lt: Optional[float] = Field(alias="capacityLt")
    capacity_tech: Optional[float] = Field(alias="capacityTech")
    cylinders: Optional[int] = Field(alias="numberOfCylinders")
    valves: Optional[int] = Field(alias="numberOfValves")
    body_type: Optional[str] = Field(alias="bodyType")
    engine_type: Optional[str] = Field(alias="engineType")
    drive_type: Optional[str] = Field(alias="driveType")
    fuel_type: Optional[str] = Field(alias="fuelType")
    engine_codes: Optional[str] = Field(alias="engCodes")

class Vehicle(BaseModel):
    """TecDoc Vehicle schema"""
    vehicle_type_details: VehicleDetails = Field(alias="vehicleTypeDetails")

class Model(BaseModel):
    """TecDoc Model schema"""
    model_id: int = Field(alias="modelId")
    model_name: str = Field(alias="modelName")

class ProductCategory(BaseModel):
    """TecDoc Product Category schema"""
    text: str
    children: Optional[Dict[str, 'ProductCategory']] = {}

class Supplier(BaseModel):
    """TecDoc Supplier schema"""
    sup_id: str = Field(alias="supId")
    brand: str = Field(alias="supBrand")
    match_code: str = Field(alias="supMatchCode")
    logo_name: Optional[str] = Field(alias="supLogoName")

class ArticleSpecification(BaseModel):
    """Article specification details"""
    criteria_name: str = Field(alias="criteriaName")
    criteria_value: Optional[str] = Field(alias="criteriaValue")

class OEMNumber(BaseModel):
    """OEM Number mapping"""
    oem_brand: str = Field(alias="oemBrand")
    oem_display_no: str = Field(alias="oemDisplayNo")

class CompatibleCar(BaseModel):
    """Compatible vehicle for an article"""
    vehicle_id: int = Field(alias="vehicleId")
    model_id: int = Field(alias="modelId")
    manufacturer_name: str = Field(alias="manufacturerName")
    model_name: str = Field(alias="modelName")
    type_engine_name: str = Field(alias="typeEngineName")
    construction_start: str = Field(alias="constructionIntervalStart")
    construction_end: str = Field(alias="constructionIntervalEnd")

class Article(BaseModel):
    """TecDoc Article schema"""
    article_id: int = Field(alias="articleId")
    article_no: str = Field(alias="articleNo")
    supplier_name: str = Field(alias="supplierName")
    supplier_id: int = Field(alias="supplierId")
    article_product_name: str = Field(alias="articleProductName")
    product_id: Optional[int] = Field(alias="productId")
    specifications: Optional[List[ArticleSpecification]] = Field(default_factory=list, alias="allSpecifications")
    ean_numbers: Optional[str] = Field(alias="eanNo")
    oem_numbers: Optional[List[OEMNumber]] = Field(default_factory=list, alias="oemNo")
    image_link: Optional[str] = Field(alias="imageLink")
    s3_image_link: Optional[str] = Field(alias="s3ImageLink")
    compatible_cars: Optional[List[CompatibleCar]] = Field(default_factory=list, alias="compatibleCars")

class ArticleSearchResponse(BaseModel):
    """Response for article search by vehicle and product group"""
    vehicle_id: int = Field(alias="vehicleId")
    product_group_id: int = Field(alias="productGroupId")
    count_articles: int = Field(alias="countArticles")
    articles: List[Article]