# backend/src/infrastructure/integrations/whatsapp/message_processor.py
from typing import Dict, Any, Optional
from src.infrastructure.integrations.whatsapp.whatsapp_config import WhatsAppClient
from src.core.conversation.manager import ConversationManager
from src.infrastructure.cache.cache_manager import get_cache_manager
from src.shared.utils.logger import get_logger
import re

logger = get_logger(__name__)

class WhatsAppMessageProcessor:
    """Process incoming WhatsApp messages and generate responses"""
    
    def __init__(self):
        self.client = WhatsAppClient()
        self.cache_manager = get_cache_manager()
        self.conversation_manager = ConversationManager(self.cache_manager)
    
    async def process_message(self, webhook_data: Dict[str, Any]) -> None:
        """Process incoming webhook data from WhatsApp"""
        
        try:
            # Extract message data
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                logger.debug("No messages in webhook data")
                return
            
            message = messages[0]
            from_number = message.get("from")
            message_id = message.get("id")
            message_type = message.get("type")
            
            # Mark message as read
            await self.client.mark_as_read(message_id)
            
            # Extract message content based on type
            user_message = ""
            
            if message_type == "text":
                user_message = message.get("text", {}).get("body", "")
            elif message_type == "interactive":
                # Handle button replies
                interactive = message.get("interactive", {})
                if interactive.get("type") == "button_reply":
                    user_message = interactive.get("button_reply", {}).get("id", "")
            else:
                # Send unsupported message type response
                await self.client.send_message(
                    from_number,
                    "Lo siento, solo puedo procesar mensajes de texto. Por favor, envía tu consulta como texto."
                )
                return
            
            # Create session ID from phone number
            session_id = f"whatsapp_{from_number}"
            
            # Detect language preference (default to Spanish for WhatsApp)
            language = "es"
            
            # Process through conversation manager
            response_text, metadata = await self.conversation_manager.process_message(
                session_id=session_id,
                user_message=user_message,
                language=language
            )
            
            # Format and send response
            await self._send_formatted_response(from_number, response_text, metadata)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}", exc_info=True)
            
            # Send error message to user
            if from_number:
                await self.client.send_message(
                    from_number,
                    "Lo siento, ocurrió un error procesando tu mensaje. Por favor, intenta nuevamente."
                )
    
    async def _send_formatted_response(self, to: str, response: str, metadata: Dict[str, Any]) -> None:
        """Format and send response based on content"""
        
        # Check if response contains JSON (for special formatting)
        if "{" in response and "}" in response:
            try:
                import json
                # Extract JSON from response
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end]
                json_data = json.loads(json_str)
                
                # Handle different response types
                if json_data.get("type") == "VEHICLE_ID_OPTIONS":
                    # Send as interactive buttons
                    await self._send_vehicle_options(to, json_data)
                    return
                elif json_data.get("type") in ["OPEN_VEHICLE_MODAL", "OPEN_CATEGORY_MODAL"]:
                    # These are web-specific, send simplified message
                    await self.client.send_message(
                        to,
                        json_data.get("message", "Por favor, proporciona la información solicitada.")
                    )
                    return
                    
            except json.JSONDecodeError:
                pass
        
        # Split long messages
        messages = self._split_message(response)
        
        # Send each part
        for msg in messages:
            await self.client.send_message(to, msg)
    
    def _split_message(self, text: str, max_length: int = 4096) -> list:
        """Split long messages for WhatsApp"""
        
        if len(text) <= max_length:
            return [text]
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        messages = []
        current_msg = ""
        
        for para in paragraphs:
            if len(current_msg) + len(para) + 2 <= max_length:
                if current_msg:
                    current_msg += "\n\n"
                current_msg += para
            else:
                if current_msg:
                    messages.append(current_msg)
                current_msg = para
        
        if current_msg:
            messages.append(current_msg)
        
        return messages
    
    async def _send_vehicle_options(self, to: str, data: Dict[str, Any]) -> None:
        """Send vehicle identification options as buttons"""
        
        buttons = []
        for button in data.get("buttons", []):
            if not button.get("disabled", True):
                buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": button.get("id"),
                        "title": button.get("text", "")[:20]  # WhatsApp limit
                    }
                })
        
        if buttons:
            await self.client.send_interactive_message(
                to,
                data.get("message", "Selecciona una opción:"),
                buttons
            )
        else:
            await self.client.send_message(to, data.get("message", ""))