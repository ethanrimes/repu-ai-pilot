# backend/src/infrastructure/integrations/whatsapp/whatsapp_config.py
from typing import Dict, Any
import httpx
from src.config.settings import get_settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

class WhatsAppClient:
    """WhatsApp Business API Client"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/v22.0/{settings.whatsapp_phone_number_id}"
        self.headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }
        self.verify_token = settings.whatsapp_verify_token

        # ✅ Add logs to verify tokens/IDs are loaded
        logger.info(f"Initialized WhatsAppClient")
        logger.info(f"Phone Number ID: {settings.whatsapp_phone_number_id}")
        logger.info(f"Verify Token: {self.verify_token}")
        
        # Mask the access token except first/last 4 chars
        token_preview = (
            settings.whatsapp_access_token[:4] + "..." + settings.whatsapp_access_token[-4:]
            if settings.whatsapp_access_token else "MISSING"
        )
        logger.info(f"Access Token (masked): {token_preview}")
    
    async def send_message(self, to: str, text: str) -> Dict[str, Any]:
        """Send text message to WhatsApp user"""
        
        url = f"{self.base_url}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": "17037276762",
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"}
            }
        }

        # logger.info(f"url {url} Message: {payload} headers {self.headers}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Message sent to {to}: {result.get('messages', [{}])[0].get('id')}")
                return result
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise
    
    async def send_interactive_message(self, to: str, body: str, buttons: list) -> Dict[str, Any]:
        """Send interactive button message"""
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": body
                },
                "action": {
                    "buttons": buttons
                }
            }
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error sending interactive message: {e}")
            raise
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        
        url = f"{self.base_url}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Error marking message as read: {e}")
            # Don't raise, just log
            return {}