# backend/src/api/routers/inventory.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel

from src.api.dependencies import get_db, require_session
from src.core.services.inventory_service import InventoryService
from src.core.models.company import PriceType
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/inventory", tags=["inventory"])

class ArticleInventoryRequest(BaseModel):
    article_ids: List[int]
    price_type: Optional[PriceType] = PriceType.RETAIL

class ArticleInventoryResponse(BaseModel):
    articles: List[Dict[str, Any]]
    total_count: int

@router.post("/articles", response_model=ArticleInventoryResponse)
async def get_articles_inventory(
    request: ArticleInventoryRequest,
    db: DBSession = Depends(get_db),
    session: Dict[str, Any] = Depends(require_session)
):
    """Get inventory information for multiple articles"""
    
    if not request.article_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No article IDs provided"
        )
    
    if len(request.article_ids) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 articles per request"
        )
    
    try:
        inventory_service = InventoryService(db)
        articles_data = await inventory_service.get_articles_with_inventory(
            article_ids=request.article_ids,
            price_type=request.price_type
        )
        
        return ArticleInventoryResponse(
            articles=articles_data,
            total_count=len(articles_data)
        )
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch inventory information"
        )

@router.get("/article/{article_id}/availability")
async def check_article_availability(
    article_id: int,
    quantity: int = Query(1, gt=0),
    db: DBSession = Depends(get_db),
    session: Dict[str, Any] = Depends(require_session)
):
    """Check availability for a specific article"""
    
    try:
        inventory_service = InventoryService(db)
        availability = await inventory_service.check_availability(
            article_id=article_id,
            quantity_requested=quantity
        )
        return availability
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check availability"
        )