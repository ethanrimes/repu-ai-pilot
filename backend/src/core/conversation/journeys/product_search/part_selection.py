# backend/src/core/conversation/journeys/product_search/part_selection.py

"""Part/Category Selection State for Product Search Journey"""

from typing import Dict, Any, Optional, Tuple
import json
from src.core.conversation.models import ConversationSession, ConversationState
from src.core.conversation.journeys.base import BaseState
from src.core.services.tecdoc_service import TecDocService
from src.core.services.inventory_service import InventoryService
from src.api.dependencies import get_db
from src.config.settings import get_settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Default TecDoc constants
TECDOC_DEFAULT_LANGUAGE_ID = 4
TECDOC_DEFAULT_COUNTRY_ID = 62

class PartSelectionState(BaseState):
    """State for part/category selection through TecDoc integration"""
    
    def __init__(self, templates: Dict[str, Any]):
        super().__init__(templates)
        self.tecdoc_service = TecDocService()
        self.category_levels = settings.category_dropdown_levels
        logger.info(f"Part selection state initialized...")
    
    async def process(
        self,
        session: ConversationSession,
        user_message: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Process part/category selection"""
        
        language = session.context.language
        logger.info(f"[PART_SELECTION_DEBUG] Part selection state processing: {user_message[:100]}...")
        logger.info(f"[PART_SELECTION_DEBUG] Current session state: {session.current_state}")
        
        # Handle specific frontend requests
        if user_message.startswith("GET_CATEGORIES:"):
            logger.info(f"[PART_SELECTION_DEBUG] Handling GET_CATEGORIES request")
            return await self._handle_categories_request(session, user_message, language)
        
        if user_message.startswith("GET_ARTICLES:"):
            return await self._handle_articles_request(session, user_message, language)
        
        if user_message.startswith("CATEGORY_SELECTED:"):
            return await self._handle_category_selection(session, user_message, language)
        
        # Check if we have vehicle context
        vehicle_id = getattr(session.context, 'vehicle_id', None)
        manufacturer_id = getattr(session.context, 'manufacturer_id', None)
        vehicle_type_id = getattr(session.context, 'vehicle_type_id', None)
        
        logger.info(f"[PART_SELECTION_DEBUG] Vehicle context - vehicle_id: {vehicle_id}, manufacturer_id: {manufacturer_id}, vehicle_type_id: {vehicle_type_id}")
        
        if not vehicle_id or not manufacturer_id:
            logger.warning(f"[PART_SELECTION_DEBUG] Missing vehicle info - vehicle_id: {vehicle_id}, manufacturer_id: {manufacturer_id}")
            response = self.get_template("missing_vehicle_info", language)
            return response, ConversationState.VEHICLE_IDENTIFICATION, None
        
        # NEW: Fetch Category V3 data from TecDoc when entering this state
        try:
            logger.info(f"Fetching Category V3 data for vehicle_id: {vehicle_id}")
            
            categories_result = await self.tecdoc_service.category_v3(
                vehicle_id=vehicle_id,
                manufacturer_id=manufacturer_id,
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=vehicle_type_id or 1
            )
            
            # Store categories in session context for later use
            # context_updates = {
            #     "available_categories": categories_result.model_dump() if categories_result else None
            # }
            
            # Build hierarchical category structure for frontend
            category_tree = self._build_category_tree(categories_result)
            
            response = json.dumps({
                "type": "OPEN_CATEGORY_MODAL",
                "message": self.get_template("opening_category_selector", language),
                "vehicleId": vehicle_id,
                "manufacturerId": manufacturer_id,
                "categoryLevels": self.category_levels,
                "categories": category_tree
            })
            
            return response, None, context_updates
            
        except Exception as e:
            logger.error(f"Error fetching categories for vehicle {vehicle_id}: {e}")
            response = self.get_template("category_selection_error", language)
            return response, None, None
    
    def _build_category_tree(self, categories_result) -> Dict[str, Any]:
        """Build hierarchical category structure from TecDoc Category V3 response"""
        if not categories_result or not hasattr(categories_result, 'categories'):
            return {}
        
        # The CategoryV3 response already has the correct hierarchical structure
        # We just need to transform it to match the frontend expectations
        return self._transform_categories_for_frontend(categories_result.categories)
    
    def _transform_categories_for_frontend(self, categories_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Transform TecDoc CategoryV3 structure to match frontend CategorySelectionModal expectations"""
        transformed = {}
        
        for key, category in categories_dict.items():
            # Handle both Pydantic model objects and plain dictionaries
            if hasattr(category, 'text'):
                # Pydantic model object
                text = category.text
                children = category.children
            else:
                # Plain dictionary
                text = category.get('text', '')
                children = category.get('children', {})
            
            # Transform each category node
            transformed_node = {
                'categoryId': int(key),  # Use the key as categoryId
                'categoryName': text,
                'text': text,
                'level': 1,  # Will be updated based on depth
                'children': {}
            }
            
            # Handle children recursively
            if isinstance(children, dict) and children:
                transformed_node['children'] = self._transform_categories_for_frontend(children)
            elif isinstance(children, list) and len(children) == 0:
                # Empty list means leaf node
                transformed_node['children'] = {}
            
            transformed[key] = transformed_node
        
        return transformed
    
    async def _handle_categories_request(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle categories data request from frontend"""
        
        try:
            # Parse vehicle info from request
            parts = user_message.replace("GET_CATEGORIES:", "").split(":")
            vehicle_id = int(parts[0])
            manufacturer_id = int(parts[1])
            
            logger.info(f"[PART_SELECTION_DEBUG] Fetching categories for vehicle_id: {vehicle_id}, manufacturer_id: {manufacturer_id}")
            
            # Get vehicle type from session context
            vehicle_type_id = getattr(session.context, 'vehicle_type_id', 1)
            logger.info(f"[PART_SELECTION_DEBUG] Using vehicle_type_id: {vehicle_type_id}")
            
            # Fetch categories from TecDoc
            logger.info(f"[PART_SELECTION_DEBUG] Calling TecDoc category_v3 API...")
            categories_result = await self.tecdoc_service.category_v3(
                vehicle_id=vehicle_id,
                manufacturer_id=manufacturer_id,
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=vehicle_type_id
            )
            
            logger.info(f"[PART_SELECTION_DEBUG] TecDoc API result: {categories_result is not None}")
            if categories_result:
                logger.info(f"[PART_SELECTION_DEBUG] Categories result has categories: {hasattr(categories_result, 'categories')}")
                if hasattr(categories_result, 'categories'):
                    logger.info(f"[PART_SELECTION_DEBUG] Categories dict length: {len(categories_result.categories) if categories_result.categories else 0}")
                    logger.info(f"[PART_SELECTION_DEBUG] Sample category keys: {list(categories_result.categories.keys())[:5] if categories_result.categories else []}")
            
            if not categories_result or not hasattr(categories_result, 'categories') or not categories_result.categories:
                logger.warning(f"No categories found for vehicle {vehicle_id}")
                response = json.dumps({
                    "type": "ERROR",
                    "message": "No categories available for this vehicle"
                })
                return response, None, None
            
            # Build hierarchical category tree
            category_tree = self._build_category_tree(categories_result)
            
            logger.info(f"[PART_SELECTION_DEBUG] Built category tree with {len(category_tree)} top-level categories")
            if category_tree:
                logger.info(f"[PART_SELECTION_DEBUG] Sample category keys: {list(category_tree.keys())[:3]}")
            
            response_data = {
                "type": "CATEGORIES_DATA",
                "data": {
                    "categories": category_tree
                }
            }
            
            logger.info(f"[PART_SELECTION_DEBUG] Sending response: {json.dumps(response_data)[:200]}...")
            response = json.dumps(response_data)
            
            return response, None, None
            
        except Exception as e:
            logger.error(f"Error handling categories request: {e}")
            response = json.dumps({
                "type": "ERROR",
                "message": "Error loading categories"
            })
            return response, None, None
    
    async def _handle_articles_request(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle articles data request from frontend with inventory lookup"""
        
        try:
            # Parse request from message
            parts = user_message.replace("GET_ARTICLES:", "").split(":")
            vehicle_id = int(parts[0])
            product_group_id = int(parts[1])
            manufacturer_id = int(parts[2])
            
            logger.info(f"Fetching articles for vehicle_id: {vehicle_id}, product_group_id: {product_group_id}")
            
            # Get articles from TecDoc service
            articles_result = await self.tecdoc_service.list_articles(
                vehicle_id=vehicle_id,
                product_group_id=product_group_id,
                manufacturer_id=manufacturer_id,
                lang_id=TECDOC_DEFAULT_LANGUAGE_ID,
                country_filter_id=TECDOC_DEFAULT_COUNTRY_ID,
                type_id=getattr(session.context, 'vehicle_type_id', 1)
            )
            
            # Check if any articles were found
            if not articles_result.articles or articles_result.countArticles == 0:
                response = json.dumps({
                    "type": "NO_ARTICLES",
                    "message": self.get_template("no_articles_found", language)
                })
                return response, None, None
            
            # Get article IDs for inventory lookup
            article_ids = [article.articleId for article in articles_result.articles]
            
            # NEW: Get inventory information for these articles
            try:
                # Get database session (this needs to be properly injected in production)
                db_gen = get_db()
                db = next(db_gen)
                
                inventory_service = InventoryService(db)
                
                # Fetch inventory data
                inventory_data = await inventory_service.get_articles_with_inventory(
                    article_ids[:settings.max_articles_per_page]
                )
                
                # Create lookup dict for inventory by article_id
                inventory_lookup = {item['article_id']: item for item in inventory_data}
                
                # Combine TecDoc articles with inventory data
                enriched_articles = []
                for article in articles_result.articles[:settings.max_articles_per_page]:
                    article_dict = article.model_dump()
                    
                    # Add inventory information
                    inventory_info = inventory_lookup.get(article.articleId, {})
                    article_dict['inventory'] = {
                        'in_stock': inventory_info.get('in_stock', False),
                        'quantity_available': inventory_info.get('quantity_available', 0),
                        'price_cop': inventory_info.get('price_cop'),
                        'currency': inventory_info.get('currency', 'COP'),
                        'has_inventory': inventory_info.get('has_inventory', False),
                        'warehouse_location': inventory_info.get('warehouse_location')
                    }
                    
                    enriched_articles.append(article_dict)
                
                # Check if we have any inventory
                has_any_inventory = any(item.get('has_inventory', False) for item in inventory_data)
                
                if not has_any_inventory:
                    logger.warning(f"No inventory found for any articles in product group {product_group_id}")
                    response = json.dumps({
                        "type": "NO_INVENTORY",
                        "message": self.get_template("no_stock_available", language),
                        "articles": enriched_articles  # Still show articles for reference
                    })
                    return response, None, None
                
                logger.info(f"Found {len(enriched_articles)} articles with inventory data")
                
            except Exception as inventory_error:
                logger.error(f"Error fetching inventory data: {inventory_error}")
                # Fallback to articles without inventory
                enriched_articles = [article.model_dump() for article in articles_result.articles[:settings.max_articles_per_page]]
                
                response = json.dumps({
                    "type": "INVENTORY_ERROR", 
                    "message": self.get_template("inventory_check_error", language),
                    "articles": enriched_articles
                })
                return response, None, None
            
            # Store in context for potential future use
            context_updates = {
                "selected_category_id": product_group_id,
                "filtered_article_ids": article_ids[:settings.max_articles_per_page],
                "enriched_articles": enriched_articles
            }
            
            # Format successful response
            response = json.dumps({
                "type": "ARTICLES_DATA",
                "data": {
                    "articles": enriched_articles,
                    "totalCount": articles_result.countArticles,
                    "vehicleId": articles_result.vehicleId,
                    "productGroupId": articles_result.productGroupId,
                    "hasInventory": has_any_inventory
                }
            })
            
            return response, None, context_updates
            
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            response = json.dumps({
                "type": "ERROR",
                "message": "Error loading articles"
            })
            return response, None, None
    
    async def _handle_category_selection(
        self,
        session: ConversationSession,
        user_message: str,
        language: str
    ) -> Tuple[str, Optional[ConversationState], Optional[Dict[str, Any]]]:
        """Handle final category selection"""
        
        try:
            # Parse selection data
            selection_data = json.loads(user_message.replace("CATEGORY_SELECTED:", ""))
            
            # Update context with selection
            context_updates = {
                "selected_category_path": selection_data.get("path"),
                "selected_category_id": selection_data.get("category_id"),
                "selected_articles": selection_data.get("articles", [])
            }
            
            # Format response
            response = self.get_template("category_selected", language).format(
                category=selection_data.get("category_name", "Unknown")
            )
            
            # Add prompt for next step
            response += "\n\n" + self.get_template("proceed_to_inventory", language)
            
            # Transition to product presentation
            return response, ConversationState.PRODUCT_PRESENTATION, context_updates
            
        except Exception as e:
            logger.error(f"Error handling category selection: {e}")
            response = self.get_template("category_selection_error", language)
            return response, None, None
    
