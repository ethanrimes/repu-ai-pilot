"""TecDoc API Pydantic Schemas - Comprehensive models for all API responses"""

from typing import Any, Dict, List, Optional, Union
from datetime import date
from pydantic import BaseModel, Field, RootModel


# Base models for common structures
class ArticleMediaInfo(BaseModel):
    articleMediaType: int
    articleMediaFileName: str
    articleMediaSupplierId: Optional[int] = None
    mediaInformation: Optional[str] = None


class ArticleSpecification(BaseModel):
    criteriaName: str
    criteriaValue: str


class EanNumbers(BaseModel):
    eanNumbers: str


class OemNumber(BaseModel):
    oemBrand: str
    oemDisplayNo: str


class CompatibleCar(BaseModel):
    vehicleId: int
    modelId: int
    manufacturerName: str
    modelName: str
    typeEngineName: str
    constructionIntervalStart: str
    constructionIntervalEnd: Optional[str] = None


class ArticleInfo(BaseModel):
    articleId: int
    articleNo: str
    supplierId: int
    supplierName: str
    isAccessory: int
    articleProductName: str


class ArticleBase(BaseModel):
    articleId: int
    articleNo: str
    articleProductName: str
    supplierName: str
    supplierId: int
    articleMediaType: int
    articleMediaFileName: str
    imageLink: str
    imageMedia: str
    s3ImageLink: str


class ArticleExtended(ArticleBase):
    articleInfo: ArticleInfo
    allSpecifications: List[ArticleSpecification]
    eanNo: Optional[EanNumbers] = None
    oemNo: Optional[List[OemNumber]] = None
    compatibleCars: Optional[List[CompatibleCar]] = None


# Article search responses
class ArticleSearchResult(BaseModel):
    articleId: int
    articleNo: str
    articleProductName: str
    supplierName: str
    supplierId: int
    articleMediaType: int
    articleMediaFileName: str
    imageLink: str
    imageMedia: str
    s3ImageLink: str


class ArticleSearch(BaseModel):
    articleSearchNr: str
    countArticles: int
    articles: List[ArticleSearchResult]


class ArticleSearchWithSupplier(ArticleSearch):
    pass  # Same structure as ArticleSearch


# Article media info response (root is array)
class ArticleMediaInfoList(RootModel[List[ArticleMediaInfo]]):
    root: List[ArticleMediaInfo]


# Article number details response
class ArticleNumberDetailsArticle(ArticleExtended):
    pass


class ArticleNumberDetails(BaseModel):
    articleNo: str
    countArticles: int
    articles: List[ArticleNumberDetailsArticle]


# Article specification details response
class ArticleSpecificationDetails(BaseModel):
    articleId: str
    article: ArticleInfo
    articleAllSpecifications: List[ArticleSpecification]
    articleEanNo: Optional[EanNumbers] = None
    articleOemNo: Optional[List[OemNumber]] = None


# Article complete details response
class ArticleCompleteDetailsArticle(ArticleExtended):
    pass


class ArticleCompleteDetails(BaseModel):
    article: ArticleCompleteDetailsArticle


# Articles list response
class ArticleListItem(BaseModel):
    articleId: int
    articleNo: str
    supplierName: str
    supplierId: int
    articleProductName: str
    productId: int
    articleMediaType: int
    articleMediaFileName: str
    imageLink: str
    imageMedia: str
    s3ImageLink: str


class ArticlesList(BaseModel):
    vehicleId: int
    productGroupId: int
    countArticles: int
    articles: List[ArticleListItem]


# Category V1 response
class CategoryV1Item(BaseModel):
    level: int
    levelText_1: str
    levelId_1: str
    levelText_2: Optional[str] = None
    levelId_2: Optional[str] = None
    levelText_3: Optional[str] = None
    levelId_3: Optional[str] = None
    levelText_4: Optional[str] = None
    levelId_4: Optional[str] = None


class CategoryV1(BaseModel):
    categories: List[CategoryV1Item]


# Category V2 response - dynamic nested structure
class CategoryV2Node(BaseModel):
    categoryId: int
    categoryName: str
    level: int
    children: Dict[str, 'CategoryV2Node'] = Field(default_factory=dict)


class CategoryV2(BaseModel):
    categories: Dict[str, CategoryV2Node]


# Category V3 response - dynamic nested structure with different format
class CategoryV3Children(BaseModel):
    text: str
    children: Union[Dict[str, 'CategoryV3Children'], List[Any]] = Field(default_factory=list)


class CategoryV3(BaseModel):
    categories: Dict[str, CategoryV3Children]


# Update forward references for recursive models
CategoryV2Node.model_rebuild()
CategoryV3Children.model_rebuild()


# Vehicle engine types response
class VehicleEngineType(BaseModel):
    vehicleId: int
    manufacturerName: str
    modelName: str
    typeEngineName: str
    constructionIntervalStart: str
    constructionIntervalEnd: Optional[str] = None
    powerKw: str
    powerPs: str
    capacityTax: Optional[str] = None
    fuelType: str
    bodyType: str
    numberOfCylinders: int
    capacityLt: str
    capacityTech: str
    engineCodes: str


class VehicleEngineTypes(BaseModel):
    modelType: str
    countModelTypes: int
    modelTypes: List[VehicleEngineType]


# Vehicle type details response
class VehicleTypeDetailsInfo(BaseModel):
    brand: str
    modelType: str
    typeEngine: str
    constructionIntervalStart: str
    constructionIntervalEnd: Optional[str] = None
    powerKw: str
    powerPs: str
    capacityTax: Optional[str] = None
    capacityLt: str
    capacityTech: str
    abs: Optional[str] = None
    asr: Optional[str] = None
    numberOfCylinders: int
    numberOfValves: int
    bodyType: str
    engineType: str
    gearType: Optional[str] = None
    driveType: str
    brakeSystem: Optional[str] = None
    brakeType: Optional[str] = None
    fuelType: str
    catalysatorType: str
    fuelMixture: str
    engCodes: str


class VehicleTypeDetails(BaseModel):
    vehicleTypeDetails: VehicleTypeDetailsInfo


# Model details responses
class ModelDetails(BaseModel):
    modelId: int
    modelName: str


class ModelDetailsByVehicle(ModelDetails):
    pass  # Same structure


# Models list response
class ModelListItem(BaseModel):
    modelId: int
    modelName: str
    modelYearFrom: str
    modelYearTo: Optional[str] = None


class ModelsList(BaseModel):
    countModels: int
    models: List[ModelListItem]


# Manufacturer details response
class ManufacturerDetails(BaseModel):
    mfaId: int
    mfaBrand: str
    mfaCv: bool
    mfaDc: bool
    mfaEng: bool
    mfaMtb: bool
    mfaPc: bool
    mfaVgl: bool
    mfaAxl: bool
    mfaMatchCode: str
    mfaModelsCount: int
    mfaPcCtm: int
    mfaCvCtm: int


# Manufacturers list response
class ManufacturerListItem(BaseModel):
    manufacturerId: int
    brand: str


class ManufacturersList(BaseModel):
    countManufactures: int
    manufacturers: List[ManufacturerListItem]


# Suppliers list response (root is array)
class Supplier(BaseModel):
    supId: str
    supBrand: str
    supMatchCode: str
    supLogoName: str


class SuppliersList(RootModel[List[Supplier]]):
    root: List[Supplier]


# Vehicle types list response (root is array)
class VehicleType(BaseModel):
    id: int
    vehicleType: str


class VehicleTypesList(RootModel[List[VehicleType]]):
    root: List[VehicleType]


# Language models (inferred from API structure)
class Language(BaseModel):
    langId: int
    langName: str
    langCode: str


class LanguagesList(BaseModel):
    languages: List[Language]


class LanguageDetails(BaseModel):
    language: Language


# Country models (inferred from API structure)
class Country(BaseModel):
    countryId: int
    countryName: str
    countryCode: str


class CountriesList(BaseModel):
    countries: List[Country]


class CountryDetails(BaseModel):
    country: Country


class CountriesByLanguage(BaseModel):
    langId: int
    countries: List[Country]


# Update forward references for recursive models
ProductCategory.model_rebuild()

# Export all models for easy import
__all__ = [
    # Article models
    'ArticleSearch',
    'ArticleSearchWithSupplier',
    'ArticleMediaInfoList',
    'ArticleNumberDetails',
    'ArticleSpecificationDetails',
    'ArticleCompleteDetails',
    'ArticlesList',
    
    # Category models
    'CategoryV1',
    'CategoryV2',
    'CategoryV3',
    
    # Vehicle models
    'VehicleEngineTypes',
    'VehicleTypeDetails',
    'ModelDetails',
    'ModelDetailsByVehicle',
    'ModelsList',
    
    # Manufacturer models
    'ManufacturerDetails',
    'ManufacturersList',
    
    # Supplier models
    'SuppliersList',
    
    # Vehicle type models
    'VehicleTypesList',
    
    # Language models
    'LanguagesList',
    'LanguageDetails',
    
    # Country models
    'CountriesList',
    'CountryDetails',
    'CountriesByLanguage',
    
    # Base models (for type hints)
    'ArticleInfo',
    'ArticleSpecification',
    'CompatibleCar',
    'OemNumber',
    'EanNumbers',
]

