# backend/src/infrastructure/integrations/whatsapp/message_processor.py
from fastapi import APIRouter, Request, Query, BackgroundTasks, Response
from typing import Optional
from src.infrastructure.integrations.whatsapp.message_processor import WhatsAppMessageProcessor
from src.infrastructure.integrations.whatsapp.whatsapp_config import WhatsAppClient
from src.shared.utils.logger import get_logger
from typing import Dict
import json

logger = get_logger(__name__)

class WhatsAppWebhookHandler:
    """Handle WhatsApp webhook verification and messages"""
    
    def __init__(self):
        self.processor = WhatsAppMessageProcessor()
        self.client = WhatsAppClient()
    
    async def verify_webhook(
        self,
        mode: Optional[str] = Query(None, alias="hub.mode"),
        token: Optional[str] = Query(None, alias="hub.verify_token"),
        challenge: Optional[str] = Query(None, alias="hub.challenge")
    ) -> str:
        """Verify webhook for WhatsApp Business API"""
        
        # Log the raw query parameters received
        logger.info(f"Webhook verification request received.")
        logger.info(f"  hub.mode: {mode}")
        logger.info(f"  hub.verify_token: {token}")
        logger.info(f"  hub.challenge: {challenge}")
        logger.info(f"  Expected verify_token from config: {self.client.verify_token}")
        
        if mode == "subscribe" and token == self.client.verify_token:
            logger.info("✅ Webhook verified successfully. Returning challenge.")
            return challenge or ""
        else:
            logger.warning("❌ Webhook verification failed. Check mode or token.")
            raise HTTPException(status_code=403, detail="Verification failed")
    
    async def handle_webhook(self, request: Request) -> Dict[str, str]:
        """Handle incoming webhook from WhatsApp"""
        
        try:
            data = await request.json()
            
            logger.info(f"Received webhook data: {json.dumps(data)[:500]}")
            
            # Process message asynchronously
            # In production, you might want to use a task queue
            await self.processor.process_message(data)
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error handling webhook: {e}", exc_info=True)
            # Return success to prevent WhatsApp from retrying
            return {"status": "success"}