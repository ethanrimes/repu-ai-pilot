# backend/api/models/database/company.py
"""Company-specific database models
Path: backend/api/models/database/company.py
"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stock'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False)  # TecDoc article ID
    supplier_id = Column(Integer)  # TecDoc supplier ID
    quantity_available = Column(Integer, default=0)
    warehouse_location = Column(String(50))
    min_stock_level = Column(Integer, default=5)
    max_stock_level = Column(Integer, default=100)
    last_restocked = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Price(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False)
    price_cop = Column(Numeric(12, 2), nullable=False)
    cost_cop = Column(Numeric(12, 2))  # Internal cost
    currency = Column(String(3), default='COP')
    price_type = Column(String(20), default='retail')  # retail, wholesale, promotional
    discount_percentage = Column(Numeric(5, 2), default=0)
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    firebase_uid = Column(String(128), unique=True)  # Firebase Auth UID
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    whatsapp_number = Column(String(20))
    name = Column(String(255))
    company_name = Column(String(255))
    customer_type = Column(String(20), default='retail')  # retail, wholesale, mechanic
    tax_id = Column(String(50))  # NIT/CC
    address = Column(Text)
    city = Column(String(100), default='Bogotá')
    preferred_language = Column(String(2), default='es')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    order_number = Column(String(50), unique=True)
    channel = Column(String(20))  # web, whatsapp
    status = Column(String(20), default='pending')  # pending, confirmed, paid, shipped, delivered, cancelled
    payment_method = Column(String(30))  # cash, transfer, card
    subtotal_cop = Column(Numeric(12, 2))
    tax_cop = Column(Numeric(12, 2))
    shipping_cop = Column(Numeric(12, 2))
    total_cop = Column(Numeric(12, 2))
    notes = Column(Text)
    shipping_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    article_id = Column(Integer, nullable=False)
    article_number = Column(String(100))  # Store TecDoc article number
    supplier_name = Column(String(100))
    product_name = Column(String(255))
    quantity = Column(Integer, nullable=False)
    unit_price_cop = Column(Numeric(12, 2))
    discount_cop = Column(Numeric(12, 2), default=0)
    total_price_cop = Column(Numeric(12, 2))
    
    order = relationship("Order", back_populates="items")

class ChatbotResponse(Base):
    __tablename__ = 'chatbot_responses'
    
    id = Column(Integer, primary_key=True)
    intent = Column(String(50), nullable=False)  # product_search, price_quote, etc.
    question_pattern = Column(Text)
    response_text_es = Column(Text)
    response_text_en = Column(Text)
    metadata = Column(JSON)  # Additional context
    source = Column(String(100))  # FAQ, manual, policy, generated
    priority = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50))  # manual, policy, faq, catalog
    file_path = Column(String(500))
    content_hash = Column(String(64))  # SHA256 hash for deduplication
    language = Column(String(2), default='es')
    metadata = Column(JSON)
    is_processed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    chunks = relationship("DocumentChunk", back_populates="document")

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding_vector = Column(JSON)  # Store as JSON, or use pgvector
    metadata = Column(JSON)
    tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    channel = Column(String(20))  # web, whatsapp
    current_state = Column(String(50))  # FSM state
    intent = Column(String(50))
    context = Column(JSON)  # Session context data
    language = Column(String(2), default='es')
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)