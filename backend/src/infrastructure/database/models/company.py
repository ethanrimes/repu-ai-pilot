# backend/src/infrastructure/database/models/company.py
# Path: backend/src/infrastructure/database/models/company.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, JSON, Date, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stock'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False, index=True)  # TecDoc article ID
    supplier_id = Column(Integer, index=True)  # TecDoc supplier ID
    quantity_available = Column(Integer, default=0, index=True)
    warehouse_location = Column(String(50), index=True)
    min_stock_level = Column(Integer, default=5)
    max_stock_level = Column(Integer, default=100)
    last_restocked = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Price(Base):
    __tablename__ = 'prices'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, nullable=False, index=True)
    price_cop = Column(Numeric(12, 2), nullable=False)
    cost_cop = Column(Numeric(12, 2))  # Internal cost
    currency = Column(String(3), default='COP')
    price_type = Column(String(20), default='retail', index=True)  # retail, wholesale, promotional
    discount_percentage = Column(Numeric(5, 2), default=0)
    valid_from = Column(Date)
    valid_to = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_prices_validity', 'valid_from', 'valid_to'),
    )

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    firebase_uid = Column(String(128), unique=True, index=True)  # Firebase Auth UID
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    whatsapp_number = Column(String(20))
    name = Column(String(255), nullable=True)
    company_name = Column(String(255))
    customer_type = Column(String(20), default='retail', index=True)  # retail, wholesale, mechanic
    tax_id = Column(String(50))  # NIT/CC
    address = Column(Text)
    city = Column(String(100), default='Bogotá', index=True)
    preferred_language = Column(String(2), default='es')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime)
    
    orders = relationship("Order", back_populates="customer")
    sessions = relationship("Session", back_populates="customer")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    channel = Column(String(20))  # web, whatsapp
    status = Column(String(20), default='pending', index=True)  # pending, confirmed, paid, shipped, delivered, cancelled
    payment_method = Column(String(30))  # cash, transfer, card
    subtotal_cop = Column(Numeric(12, 2))
    tax_cop = Column(Numeric(12, 2))
    shipping_cop = Column(Numeric(12, 2))
    total_cop = Column(Numeric(12, 2))
    notes = Column(Text)
    shipping_address = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), index=True)
    article_id = Column(Integer, nullable=False, index=True)
    article_number = Column(String(100))  # Store TecDoc article number
    supplier_name = Column(String(100))
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_cop = Column(Numeric(12, 2))
    discount_cop = Column(Numeric(12, 2), default=0)
    total_price_cop = Column(Numeric(12, 2))
    
    order = relationship("Order", back_populates="items")

class ChatbotResponse(Base):
    __tablename__ = 'chatbot_responses'
    
    id = Column(Integer, primary_key=True)
    intent = Column(String(50), nullable=False, index=True)  # product_search, price_quote, etc.
    question_pattern = Column(Text)
    response_text_es = Column(Text)
    response_text_en = Column(Text)
    meta_data = Column(JSON)  # Additional context
    source = Column(String(100))  # FAQ, manual, policy, generated
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), index=True)
    channel = Column(String(20), index=True)  # web, whatsapp
    current_state = Column(String(50), index=True)  # FSM state
    intent = Column(String(50))
    context = Column(JSON)  # Session context data
    language = Column(String(2), default='es')
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    customer = relationship("Customer", back_populates="sessions")