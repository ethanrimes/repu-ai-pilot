# backend/src/api/routers/webhooks/whatsapp.py

from fastapi import APIRouter, Request, Query, BackgroundTasks, Response
from typing import Optional, Dict, Any
from src.infrastructure.integrations.whatsapp.webhook_handler import WhatsAppWebhookHandler
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/webhooks/whatsapp", tags=["webhooks"])

webhook_handler = WhatsAppWebhookHandler()

@router.get("")
async def verify_webhook(
    mode: Optional[str] = Query(None, alias="hub.mode"),
    token: Optional[str] = Query(None, alias="hub.verify_token"),
    challenge: Optional[str] = Query(None, alias="hub.challenge")
) -> Response:
    """Webhook verification endpoint for WhatsApp"""
    challenge_value = await webhook_handler.verify_webhook(mode, token, challenge)
    
    # Return plain text response, not JSON
    resp = Response(content=challenge_value, media_type="text/plain")
    logger.info(f"Responding to webhook verification with: {resp}")
    return resp

@router.post("")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks
) -> Dict[str, str]:
    """Receive webhook from WhatsApp"""
    
    # Process in background to return quickly
    data = await request.json()
    background_tasks.add_task(webhook_handler.processor.process_message, data)
    
    return {"status": "success"}