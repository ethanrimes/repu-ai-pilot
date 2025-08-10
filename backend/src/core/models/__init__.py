# backend/src/core/models/__init__.py

# Import common types first
from .common import BetterUUID, BetterDateTime

# Import all model modules
from .chat import *
from .company import *
from .tecdoc import *
from .document import *

# Export common types at package level
__all__ = [
    # Common types
    'BetterUUID', 'BetterDateTime',
    
    # Chat models
    'MessageRole', 'ChatMessage', 'ChatRequest', 'ChatResponse',
    'ChatHistory', 'ChatStatusResponse',
    
    # Document models  
    'DocumentType', 'DocumentCategory', 'ChunkStrategy',
    'DocumentBase', 'ChunkBase',
    'DocumentCreate', 'ChunkCreate',
    'DocumentArticleLink', 'DocumentVehicleLink',
    'Document', 'Chunk',
    'DocumentUpdate',
    'DocumentSearch', 'VectorSearchParams', 'SearchResult',
    'BulkDocumentCreate',
    
    # Company models
    'CustomerType', 'OrderStatus', 'PaymentMethod', 'PriceType', 'Channel',
    'Stock', 'StockCreate', 'StockUpdate', 'StockSearch',
    'Price', 'PriceCreate', 'PriceUpdate', 'PriceSearch',
    'Customer', 'CustomerCreate', 'CustomerUpdate', 'CustomerSearch',
    'Order', 'OrderCreate', 'OrderUpdate', 'OrderSearch',
    'OrderItem', 'OrderItemCreate',
    'Session', 'SessionCreate', 'SessionUpdate',
    
    # TecDoc models (add as needed)
]