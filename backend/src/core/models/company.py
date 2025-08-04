# backend/src/core/models/company.py
# Path: backend/src/core/models/company.py

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict, SkipValidation
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

# Enums
class CustomerType(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    MECHANIC = "mechanic"

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CASH = "cash"
    TRANSFER = "transfer"
    CARD = "card"

class PriceType(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    PROMOTIONAL = "promotional"

class Channel(str, Enum):
    WEB = "web"
    WHATSAPP = "whatsapp"

# Stock Models
class StockBase(BaseModel):
    """Base stock model"""
    article_id: int = Field(..., gt=0)
    supplier_id: Optional[int] = Field(None, gt=0)
    quantity_available: int = Field(default=0, ge=0)
    warehouse_location: Optional[str] = Field(None, max_length=50)
    min_stock_level: int = Field(default=5, ge=0)
    max_stock_level: int = Field(default=100, ge=0)
    last_restocked: Optional[datetime] = None

class StockCreate(StockBase):
    """Model for creating stock entry"""
    pass

class StockUpdate(BaseModel):
    """Model for updating stock"""
    quantity_available: Optional[int] = Field(None, ge=0)
    warehouse_location: Optional[str] = Field(None, max_length=50)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)
    last_restocked: Optional[datetime] = None

class Stock(StockBase):
    """Complete stock model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    last_updated: datetime

# Price Models
class PriceBase(BaseModel):
    """Base price model"""
    article_id: int = Field(..., gt=0)
    price_cop: Decimal = Field(..., decimal_places=2, ge=0)
    cost_cop: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    currency: str = Field(default="COP", pattern="^[A-Z]{3}$")
    price_type: PriceType = Field(default=PriceType.RETAIL)
    discount_percentage: Decimal = Field(default=0, ge=0, le=100, decimal_places=2)
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

    @field_validator('valid_to')
    @classmethod
    def validate_date_range(cls, v, info):
        """Ensure valid_to is after valid_from"""
        if v and 'valid_from' in info.data and info.data['valid_from']:
            if v < info.data['valid_from']:
                raise ValueError('valid_to must be after valid_from')
        return v

class PriceCreate(PriceBase):
    """Model for creating price"""
    pass

class PriceUpdate(BaseModel):
    """Model for updating price"""
    price_cop: Optional[Decimal] = Field(None, decimal_places=2, ge=0)
    discount_percentage: Optional[Decimal] = Field(None, ge=0, le=100, decimal_places=2)
    valid_to: Optional[date] = None

class Price(PriceBase):
    """Complete price model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime

# Customer Models
class CustomerBase(BaseModel):
    """Base customer model"""
    email: EmailStr
    phone: Optional[str] = Field(None, pattern="^\\+?[0-9\\s-]+$", max_length=20)
    whatsapp_number: Optional[str] = Field(None, pattern="^\\+?[0-9]+$", max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    customer_type: CustomerType = Field(default=CustomerType.RETAIL)
    tax_id: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: str = Field(default="Bogotá", max_length=100)
    preferred_language: str = Field(default="es", pattern="^[a-z]{2}$")

class CustomerCreate(CustomerBase):
    """Model for creating customer"""
    firebase_uid: Optional[str] = Field(None, max_length=128)

class CustomerUpdate(BaseModel):
    """Model for updating customer"""
    phone: Optional[str] = Field(None, pattern="^\\+?[0-9\\s-]+$", max_length=20)
    whatsapp_number: Optional[str] = Field(None, pattern="^\\+?[0-9]+$", max_length=20)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    preferred_language: Optional[str] = Field(None, pattern="^[a-z]{2}$")

class Customer(CustomerBase):
    """Complete customer model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    firebase_uid: Optional[str] = None
    created_at: datetime
    last_active: Optional[datetime] = None
    
    # Relationships - Skip validation to avoid infinite recursion
    orders: SkipValidation[List['Order']] = Field(default_factory=list)
    sessions: SkipValidation[List['Session']] = Field(default_factory=list)

# Order Item Models
class OrderItemBase(BaseModel):
    """Base order item model"""
    article_id: int = Field(..., gt=0)
    article_number: Optional[str] = Field(None, max_length=100)
    supplier_name: Optional[str] = Field(None, max_length=100)
    product_name: str = Field(..., max_length=255)
    quantity: int = Field(..., gt=0)
    unit_price_cop: Decimal = Field(..., decimal_places=2, ge=0)
    discount_cop: Decimal = Field(default=0, decimal_places=2, ge=0)
    
    @property
    def total_price_cop(self) -> Decimal:
        """Calculate total price"""
        return (self.unit_price_cop * self.quantity) - self.discount_cop

class OrderItemCreate(OrderItemBase):
    """Model for creating order item"""
    pass

class OrderItem(OrderItemBase):
    """Complete order item model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_id: int
    total_price_cop: Decimal = Field(..., decimal_places=2, ge=0)
    
    # Skip validation for order relationship to avoid circular reference
    order: SkipValidation[Optional['Order']] = None

# Order Models
class OrderBase(BaseModel):
    """Base order model"""
    customer_id: int = Field(..., gt=0)
    channel: Channel
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None

class OrderCreate(OrderBase):
    """Model for creating order"""
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    """Model for updating order"""
    status: Optional[OrderStatus] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None

class Order(OrderBase):
    """Complete order model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    order_number: str
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    subtotal_cop: Decimal = Field(..., decimal_places=2, ge=0)
    tax_cop: Decimal = Field(..., decimal_places=2, ge=0)
    shipping_cop: Decimal = Field(..., decimal_places=2, ge=0)
    total_cop: Decimal = Field(..., decimal_places=2, ge=0)
    created_at: datetime
    updated_at: datetime
    
    # Relationships - Skip validation to avoid infinite recursion
    customer: SkipValidation[Optional[Customer]] = None
    items: SkipValidation[List[OrderItem]] = Field(default_factory=list)

# Session Models
class SessionBase(BaseModel):
    """Base session model"""
    session_id: str = Field(..., min_length=1, max_length=128)
    customer_id: Optional[int] = Field(None, gt=0)
    channel: Optional[Channel] = None
    current_state: Optional[str] = Field(None, max_length=50)
    intent: Optional[str] = Field(None, max_length=50)
    context: Dict[str, Any] = Field(default_factory=dict)
    language: str = Field(default="es", pattern="^[a-z]{2}$")

class SessionCreate(SessionBase):
    """Model for creating session"""
    pass

class SessionUpdate(BaseModel):
    """Model for updating session"""
    current_state: Optional[str] = Field(None, max_length=50)
    intent: Optional[str] = Field(None, max_length=50)
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = Field(None, pattern="^[a-z]{2}$")

class Session(SessionBase):
    """Complete session model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime] = None
    
    # Relationship - Skip validation to avoid infinite recursion
    customer: SkipValidation[Optional[Customer]] = None

# Search and Filter Models
class StockSearch(BaseModel):
    """Stock search parameters"""
    article_ids: Optional[List[int]] = None
    warehouse_location: Optional[str] = None
    min_quantity: Optional[int] = None
    low_stock_only: bool = False
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class PriceSearch(BaseModel):
    """Price search parameters"""
    article_ids: Optional[List[int]] = None
    price_type: Optional[PriceType] = None
    active_only: bool = True
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class CustomerSearch(BaseModel):
    """Customer search parameters"""
    query: Optional[str] = None
    customer_type: Optional[CustomerType] = None
    city: Optional[str] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class OrderSearch(BaseModel):
    """Order search parameters"""
    customer_id: Optional[int] = None
    status: Optional[OrderStatus] = None
    channel: Optional[Channel] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

# Update forward references
Customer.model_rebuild()
Order.model_rebuild()
OrderItem.model_rebuild()
Session.model_rebuild()