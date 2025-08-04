# backend/src/infrastructure/database/repositories/company_repo.py
# Path: backend/src/infrastructure/database/repositories/company_repo.py

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from backend.src.infrastructure.database.models.company import (
    Customer as CustomerDB,
    Order as OrderDB,
    OrderItem as OrderItemDB,
    Stock as StockDB,
    Price as PriceDB,
    Session as SessionDB
)
from backend.src.core.models.company import (
    Customer, CustomerCreate, CustomerUpdate, CustomerSearch,
    Order, OrderCreate, OrderUpdate, OrderSearch, OrderItem, OrderItemCreate,
    Stock, StockCreate, StockUpdate, StockSearch,
    Price, PriceCreate, PriceUpdate, PriceSearch,
    Session as SessionModel, SessionCreate, SessionUpdate,
    OrderStatus, CustomerType, PriceType
)

class CustomerRepository:
    """Repository for customer-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, customer: CustomerCreate) -> Customer:
        """Create a new customer"""
        db_customer = CustomerDB(**customer.model_dump())
        
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        
        return Customer.model_validate(db_customer)
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        db_customer = self.db.query(CustomerDB).filter(
            CustomerDB.id == customer_id
        ).first()
        
        if db_customer:
            return Customer.model_validate(db_customer)
        return None
    
    async def get_by_email(self, email: str) -> Optional[Customer]:
        """Get customer by email"""
        db_customer = self.db.query(CustomerDB).filter(
            CustomerDB.email == email
        ).first()
        
        if db_customer:
            return Customer.model_validate(db_customer)
        return None
    
    async def get_by_firebase_uid(self, firebase_uid: str) -> Optional[Customer]:
        """Get customer by Firebase UID"""
        db_customer = self.db.query(CustomerDB).filter(
            CustomerDB.firebase_uid == firebase_uid
        ).first()
        
        if db_customer:
            return Customer.model_validate(db_customer)
        return None
    
    async def update(self, customer_id: int, update: CustomerUpdate) -> Optional[Customer]:
        """Update customer"""
        db_customer = self.db.query(CustomerDB).filter(
            CustomerDB.id == customer_id
        ).first()
        
        if not db_customer:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        
        db_customer.last_active = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_customer)
        
        return Customer.model_validate(db_customer)
    
    async def search(self, params: CustomerSearch) -> Tuple[List[Customer], int]:
        """Search customers"""
        query = self.db.query(CustomerDB)
        
        if params.query:
            search_filter = or_(
                CustomerDB.name.ilike(f"%{params.query}%"),
                CustomerDB.email.ilike(f"%{params.query}%"),
                CustomerDB.company_name.ilike(f"%{params.query}%")
            )
            query = query.filter(search_filter)
        
        if params.customer_type:
            query = query.filter(CustomerDB.customer_type == params.customer_type)
        
        if params.city:
            query = query.filter(CustomerDB.city == params.city)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        customers = query.offset(params.offset).limit(params.limit).all()
        
        return [Customer.model_validate(c) for c in customers], total_count

class OrderRepository:
    """Repository for order-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, order: OrderCreate) -> Order:
        """Create a new order with items"""
        # Generate order number
        order_number = self._generate_order_number()
        
        # Calculate totals
        subtotal = sum(
            item.unit_price_cop * item.quantity - item.discount_cop 
            for item in order.items
        )
        tax = subtotal * 0.19  # 19% IVA in Colombia
        shipping = 10000  # Fixed shipping for now
        total = subtotal + tax + shipping
        
        # Create order
        db_order = OrderDB(
            customer_id=order.customer_id,
            order_number=order_number,
            channel=order.channel,
            payment_method=order.payment_method,
            notes=order.notes,
            shipping_address=order.shipping_address,
            subtotal_cop=subtotal,
            tax_cop=tax,
            shipping_cop=shipping,
            total_cop=total
        )
        
        self.db.add(db_order)
        self.db.flush()  # Get the order ID
        
        # Create order items
        for item_data in order.items:
            db_item = OrderItemDB(
                order_id=db_order.id,
                **item_data.model_dump(),
                total_price_cop=item_data.unit_price_cop * item_data.quantity - item_data.discount_cop
            )
            self.db.add(db_item)
        
        self.db.commit()
        self.db.refresh(db_order)
        
        # Load with relationships
        db_order = self.db.query(OrderDB).options(
            joinedload(OrderDB.items),
            joinedload(OrderDB.customer)
        ).filter(OrderDB.id == db_order.id).first()
        
        return Order.model_validate(db_order)
    
    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items"""
        db_order = self.db.query(OrderDB).options(
            joinedload(OrderDB.items),
            joinedload(OrderDB.customer)
        ).filter(OrderDB.id == order_id).first()
        
        if db_order:
            return Order.model_validate(db_order)
        return None
    
    async def get_by_number(self, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        db_order = self.db.query(OrderDB).options(
            joinedload(OrderDB.items),
            joinedload(OrderDB.customer)
        ).filter(OrderDB.order_number == order_number).first()
        
        if db_order:
            return Order.model_validate(db_order)
        return None
    
    async def update(self, order_id: int, update: OrderUpdate) -> Optional[Order]:
        """Update order"""
        db_order = self.db.query(OrderDB).filter(OrderDB.id == order_id).first()
        
        if not db_order:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        
        self.db.commit()
        self.db.refresh(db_order)
        
        return await self.get_by_id(order_id)
    
    async def search(self, params: OrderSearch) -> Tuple[List[Order], int]:
        """Search orders"""
        query = self.db.query(OrderDB).options(
            joinedload(OrderDB.customer),
            joinedload(OrderDB.items)
        )
        
        if params.customer_id:
            query = query.filter(OrderDB.customer_id == params.customer_id)
        
        if params.status:
            query = query.filter(OrderDB.status == params.status)
        
        if params.channel:
            query = query.filter(OrderDB.channel == params.channel)
        
        if params.date_from:
            query = query.filter(OrderDB.created_at >= params.date_from)
        
        if params.date_to:
            query = query.filter(OrderDB.created_at <= params.date_to)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        orders = query.order_by(OrderDB.created_at.desc()).offset(
            params.offset
        ).limit(params.limit).all()
        
        return [Order.model_validate(o) for o in orders], total_count
    
    def _generate_order_number(self) -> str:
        """Generate unique order number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        count = self.db.query(OrderDB).count()
        return f"ORD-{timestamp}-{count + 1:04d}"

class StockRepository:
    """Repository for stock-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, stock: StockCreate) -> Stock:
        """Create stock entry"""
        db_stock = StockDB(**stock.model_dump())
        
        self.db.add(db_stock)
        self.db.commit()
        self.db.refresh(db_stock)
        
        return Stock.model_validate(db_stock)
    
    async def get_by_article(self, article_id: int) -> Optional[Stock]:
        """Get stock by article ID"""
        db_stock = self.db.query(StockDB).filter(
            StockDB.article_id == article_id
        ).first()
        
        if db_stock:
            return Stock.model_validate(db_stock)
        return None
    
    async def update(self, stock_id: int, update: StockUpdate) -> Optional[Stock]:
        """Update stock"""
        db_stock = self.db.query(StockDB).filter(StockDB.id == stock_id).first()
        
        if not db_stock:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_stock, field, value)
        
        self.db.commit()
        self.db.refresh(db_stock)
        
        return Stock.model_validate(db_stock)
    
    async def update_quantity(self, article_id: int, quantity_change: int) -> Optional[Stock]:
        """Update stock quantity (positive to add, negative to subtract)"""
        db_stock = self.db.query(StockDB).filter(
            StockDB.article_id == article_id
        ).first()
        
        if not db_stock:
            return None
        
        new_quantity = db_stock.quantity_available + quantity_change
        if new_quantity < 0:
            raise ValueError("Insufficient stock")
        
        db_stock.quantity_available = new_quantity
        
        self.db.commit()
        self.db.refresh(db_stock)
        
        return Stock.model_validate(db_stock)
    
    async def search(self, params: StockSearch) -> Tuple[List[Stock], int]:
        """Search stock"""
        query = self.db.query(StockDB)
        
        if params.article_ids:
            query = query.filter(StockDB.article_id.in_(params.article_ids))
        
        if params.warehouse_location:
            query = query.filter(StockDB.warehouse_location == params.warehouse_location)
        
        if params.min_quantity is not None:
            query = query.filter(StockDB.quantity_available >= params.min_quantity)
        
        if params.low_stock_only:
            query = query.filter(StockDB.quantity_available <= StockDB.min_stock_level)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        stocks = query.offset(params.offset).limit(params.limit).all()
        
        return [Stock.model_validate(s) for s in stocks], total_count

class PriceRepository:
    """Repository for price-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, price: PriceCreate) -> Price:
        """Create price entry"""
        db_price = PriceDB(**price.model_dump())
        
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        
        return Price.model_validate(db_price)
    
    async def get_current_price(self, article_id: int, price_type: PriceType = PriceType.RETAIL) -> Optional[Price]:
        """Get current active price for article"""
        today = date.today()
        
        db_price = self.db.query(PriceDB).filter(
            and_(
                PriceDB.article_id == article_id,
                PriceDB.price_type == price_type,
                or_(PriceDB.valid_from == None, PriceDB.valid_from <= today),
                or_(PriceDB.valid_to == None, PriceDB.valid_to >= today)
            )
        ).order_by(PriceDB.created_at.desc()).first()
        
        if db_price:
            return Price.model_validate(db_price)
        return None
    
    async def update(self, price_id: int, update: PriceUpdate) -> Optional[Price]:
        """Update price"""
        db_price = self.db.query(PriceDB).filter(PriceDB.id == price_id).first()
        
        if not db_price:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_price, field, value)
        
        self.db.commit()
        self.db.refresh(db_price)
        
        return Price.model_validate(db_price)
    
    async def search(self, params: PriceSearch) -> Tuple[List[Price], int]:
        """Search prices"""
        query = self.db.query(PriceDB)
        
        if params.article_ids:
            query = query.filter(PriceDB.article_id.in_(params.article_ids))
        
        if params.price_type:
            query = query.filter(PriceDB.price_type == params.price_type)
        
        if params.active_only:
            today = date.today()
            query = query.filter(
                and_(
                    or_(PriceDB.valid_from == None, PriceDB.valid_from <= today),
                    or_(PriceDB.valid_to == None, PriceDB.valid_to >= today)
                )
            )
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        prices = query.offset(params.offset).limit(params.limit).all()
        
        return [Price.model_validate(p) for p in prices], total_count

class SessionRepository:
    """Repository for session-related database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, session: SessionCreate) -> SessionModel:
        """Create session"""
        db_session = SessionDB(**session.model_dump())
        
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        
        return SessionModel.model_validate(db_session)
    
    async def get_by_session_id(self, session_id: str) -> Optional[SessionModel]:
        """Get session by session ID"""
        db_session = self.db.query(SessionDB).filter(
            SessionDB.session_id == session_id
        ).first()
        
        if db_session:
            return SessionModel.model_validate(db_session)
        return None
    
    async def update(self, session_id: str, update: SessionUpdate) -> Optional[SessionModel]:
        """Update session"""
        db_session = self.db.query(SessionDB).filter(
            SessionDB.session_id == session_id
        ).first()
        
        if not db_session:
            return None
        
        update_data = update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_session, field, value)
        
        db_session.last_activity = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_session)
        
        return SessionModel.model_validate(db_session)
    
    async def end_session(self, session_id: str) -> bool:
        """End a session"""
        db_session = self.db.query(SessionDB).filter(
            SessionDB.session_id == session_id
        ).first()
        
        if not db_session:
            return False
        
        db_session.ended_at = datetime.utcnow()
        
        self.db.commit()
        return True
    
    async def get_active_sessions(self, customer_id: Optional[int] = None) -> List[SessionModel]:
        """Get active sessions"""
        query = self.db.query(SessionDB).filter(SessionDB.ended_at == None)
        
        if customer_id:
            query = query.filter(SessionDB.customer_id == customer_id)
        
        sessions = query.all()
        return [SessionModel.model_validate(s) for s in sessions]