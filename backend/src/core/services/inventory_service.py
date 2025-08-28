# backend/src/core/services/inventory_service.py

from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session as DBSession
from decimal import Decimal

from src.infrastructure.database.repositories.company_repo import (
    StockRepository, PriceRepository
)
from src.core.models.company import Stock, Price, PriceType
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

class InventoryService:
    """Service for managing inventory (stock and prices)"""
    
    def __init__(self, db: DBSession):
        self.db = db
        self.stock_repo = StockRepository(db)
        self.price_repo = PriceRepository(db)
    
    async def get_articles_with_inventory(
        self, 
        article_ids: List[int],
        price_type: PriceType = PriceType.RETAIL
    ) -> List[Dict[str, Any]]:
        """Get articles with their stock and price information"""
        
        articles_data = []
        
        for article_id in article_ids:
            try:
                # Get stock info
                stock = await self.stock_repo.get_by_article(article_id)
                
                # Get current price
                price = await self.price_repo.get_current_price(article_id, price_type)
                
                article_info = {
                    'article_id': article_id,
                    'in_stock': stock.quantity_available > 0 if stock else False,
                    'quantity_available': stock.quantity_available if stock else 0,
                    'warehouse_location': stock.warehouse_location if stock else None,
                    'price_cop': float(price.price_cop) if price else None,
                    'discount_percentage': float(price.discount_percentage) if price else 0,
                    'currency': price.currency if price else 'COP',
                    'has_inventory': stock is not None or price is not None
                }
                
                articles_data.append(article_info)
                
            except Exception as e:
                logger.error(f"Error getting inventory for article {article_id}: {e}")
                articles_data.append({
                    'article_id': article_id,
                    'in_stock': False,
                    'quantity_available': 0,
                    'price_cop': None,
                    'has_inventory': False,
                    'error': str(e)
                })
        
        return articles_data
    
    async def check_availability(
        self,
        article_id: int,
        quantity_requested: int
    ) -> Dict[str, Any]:
        """Check if requested quantity is available"""
        
        stock = await self.stock_repo.get_by_article(article_id)
        
        if not stock:
            return {
                'available': False,
                'current_stock': 0,
                'message': 'Product not in stock'
            }
        
        is_available = stock.quantity_available >= quantity_requested
        
        return {
            'available': is_available,
            'current_stock': stock.quantity_available,
            'warehouse_location': stock.warehouse_location,
            'message': 'Available' if is_available else f'Only {stock.quantity_available} units available'
        }