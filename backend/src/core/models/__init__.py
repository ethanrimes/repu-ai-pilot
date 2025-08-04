# backend/src/core/models/__init__.py
# Path: backend/src/core/models/__init__.py

from .chat import *
from .company import *
from .tecdoc import *
from .document import (
    # Enums
    DocumentType, DocumentCategory, ChunkStrategy,
    
    # Base models
    DocumentBase, ChunkBase,
    
    # Create models
    DocumentCreate, ChunkCreate,
    DocumentArticleLink, DocumentVehicleLink,
    
    # Response models
    Document, Chunk,
    
    # Update models
    DocumentUpdate,
    
    # Search models
    DocumentSearch, VectorSearchParams, SearchResult,
    
    # Bulk operations
    BulkDocumentCreate
)

# Export all document models
__all__ = [
    # Document enums
    'DocumentType', 'DocumentCategory', 'ChunkStrategy',
    
    # Document models
    'DocumentBase', 'ChunkBase',
    'DocumentCreate', 'ChunkCreate',
    'DocumentArticleLink', 'DocumentVehicleLink',
    'Document', 'Chunk',
    'DocumentUpdate',
    'DocumentSearch', 'VectorSearchParams', 'SearchResult',
    'BulkDocumentCreate'
]