# backend/src/core/models/document.py
# Path: backend/src/core/models/document.py

from pydantic import BaseModel, Field, field_validator, BeforeValidator, PlainSerializer, ConfigDict
from typing import List, Optional, Dict, Any, Annotated
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

# Better UUID serialization for frontend compatibility
BetterUUID = Annotated[
    UUID,
    BeforeValidator(lambda x: UUID(x) if isinstance(x, str) else x),
    PlainSerializer(lambda x: str(x)),
    Field(description="UUID serialized as string"),
]

class DocumentType(str, Enum):
    """Document type enumeration"""
    MANUAL = "manual"
    POLICY = "policy"
    FAQ = "faq"
    DIAGNOSTIC = "diagnostic"
    INSTALLATION = "installation"
    CATALOG = "catalog"
    SPECIFICATION = "specification"
    SERVICE = "service"
    
class DocumentCategory(str, Enum):
    """Main document categories"""
    FAQS = "faqs"
    LEGAL = "legal"
    POLICIES = "policies"
    SHIPPING_INFO = "shipping_info"
    STORE_INFO = "store_info"
    TECH_DOCS = "tech_docs"

class ChunkStrategy(str, Enum):
    """Chunking strategies"""
    RECURSIVE = "recursive"
    FIXED = "fixed"
    SEMANTIC = "semantic"

# Base Models
class DocumentBase(BaseModel):
    """Base document model with common fields"""
    title: str = Field(..., min_length=1, max_length=255)
    filename: str = Field(..., min_length=1, max_length=255)
    file_path: str = Field(..., min_length=1, max_length=500)
    document_type: Optional[DocumentType] = None
    category: Optional[DocumentCategory] = None
    subcategory: Optional[str] = Field(None, max_length=100)
    language: str = Field(default="es", pattern="^[a-z]{2}$")
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    hierarchy: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('meta_data', 'hierarchy', mode='before')
    @classmethod
    def validate_json_fields(cls, v):
        """Ensure JSON fields are dictionaries"""
        if v is None:
            return {}
        return v

class ChunkBase(BaseModel):
    """Base chunk model"""
    content: str = Field(..., min_length=1)
    chunk_index: int = Field(..., ge=0)
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    tokens: Optional[int] = Field(None, ge=0)
    chunk_strategy: ChunkStrategy = Field(default=ChunkStrategy.RECURSIVE)

# Create Models (for insertion)
class DocumentCreate(DocumentBase):
    """Model for creating a new document"""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Manual de Frenos Mazda CX-30",
                "filename": "manual_brake_disc_100032_advics_6716338.md",
                "file_path": "/tech_docs/manuals/manual_brake_disc_100032_advics_6716338.md",
                "document_type": "manual",
                "category": "tech_docs",
                "subcategory": "manuals",
                "content": "# Manual de instalación...",
                "language": "es",
                "meta_data": {"brand": "ADVICS", "part_type": "brake_disc"},
                "hierarchy": {"root": "tech_docs", "level1": "manuals"}
            }
        }
    )
    
    content: str = Field(..., min_length=1)

class ChunkCreate(ChunkBase):
    """Model for creating a new chunk"""
    document_id: int = Field(..., gt=0)
    embedding: Optional[List[float]] = Field(None, min_items=1536, max_items=1536)

class DocumentArticleLink(BaseModel):
    """Link between document and article"""
    document_id: int = Field(..., gt=0)
    article_id: int = Field(..., gt=0)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)

class DocumentVehicleLink(BaseModel):
    """Link between document and vehicle"""
    document_id: int = Field(..., gt=0)
    vehicle_id: int = Field(..., gt=0)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)

# Response Models (with IDs and timestamps)
class Document(DocumentBase):
    """Complete document model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    content: str
    content_hash: str
    is_processed: bool = False
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    chunks: List['Chunk'] = Field(default_factory=list)
    article_links: List[DocumentArticleLink] = Field(default_factory=list)
    vehicle_links: List[DocumentVehicleLink] = Field(default_factory=list)

class Chunk(ChunkBase):
    """Complete chunk model with all fields"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    document_id: int
    embedding: Optional[List[float]] = None
    created_at: datetime
    
    # Relationship
    document: Optional['Document'] = None

# Update Models
class DocumentUpdate(BaseModel):
    """Model for updating document fields"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    document_type: Optional[DocumentType] = None
    meta_data: Optional[Dict[str, Any]] = None
    is_processed: Optional[bool] = None

# Search Models
class DocumentSearch(BaseModel):
    """Document search parameters"""
    query: Optional[str] = None
    document_type: Optional[DocumentType] = None
    category: Optional[DocumentCategory] = None
    subcategory: Optional[str] = None
    language: Optional[str] = None
    article_ids: Optional[List[int]] = None
    vehicle_ids: Optional[List[int]] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class VectorSearchParams(BaseModel):
    """Vector search parameters"""
    query: str = Field(..., min_length=1)
    embedding: Optional[List[float]] = None
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    limit: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResult(BaseModel):
    """Search result with similarity score"""
    chunk: Chunk
    document: Document
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    highlights: Optional[List[str]] = None

# Bulk Operations
class BulkDocumentCreate(BaseModel):
    """Model for bulk document creation"""
    documents: List[DocumentCreate]
    auto_chunk: bool = Field(default=True)
    chunk_config: Optional[Dict[str, Any]] = None

# Update forward references
Document.model_rebuild()
Chunk.model_rebuild()