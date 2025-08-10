# backend/src/infrastructure/database/models/__init__.py
# Path: backend/src/infrastructure/database/models/__init__.py
"""
Models = The toys themselves 🧸.
They describe what your data looks like: a “Customer” toy has a name, 
an email, and a unique number. In code, these are SQLAlchemy ORM classes that map to tables in the database.
"""


from .company import (
    Stock, Price, Customer, Order, OrderItem,
    ChatbotResponse, Session
)

from .document import (
    Document, Chunk, DocumentArticleLink, DocumentVehicleLink
)

# Export all models
__all__ = [
    # Company models
    'Stock', 'Price', 'Customer', 'Order', 'OrderItem',
    'ChatbotResponse', 'Session',
    
    # Document models
    'Document', 'Chunk', 'DocumentArticleLink', 'DocumentVehicleLink'
]