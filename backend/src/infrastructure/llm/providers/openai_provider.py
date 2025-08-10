# backend/src/infrastructure/llm/providers/openai_provider.py

from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.core.models.chat import ChatMessage, MessageRole
from src.core.services.language_service import get_language_service
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

class OpenAIChatProvider:
    """OpenAI chat completion provider with language support"""
    
    def __init__(self, model: str = None, language: str = None):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = model or settings.chat_model or "gpt-4-turbo-preview"
        self.max_tokens = 2000
        self.temperature = 0.7
        self.language = language or settings.default_language
        self.language_service = get_language_service()
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the assistant based on language"""
        return self.language_service.get_system_prompt(self.language, "base_system")
    
    def set_language(self, language: str) -> None:
        """Update the language and reload system prompt"""
        if self.language_service.is_language_supported(language):
            self.language = language
            self.system_prompt = self._get_system_prompt()
            logger.info(f"Language set to: {language}")
        else:
            logger.warning(f"Unsupported language '{language}', keeping current: {self.language}")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_response(
        self, 
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        language: Optional[str] = None
    ) -> tuple[str, Dict[str, Any]]:
        """Generate a chat response using OpenAI with language support"""
        
        # Update language if provided
        if language and language != self.language:
            self.set_language(language)
        
        # Convert messages to OpenAI format
        openai_messages = []
        
        # Always include system prompt in the current language
        openai_messages.append({
            "role": "system",
            "content": self.system_prompt
        })
        
        # Add conversation history
        for msg in messages:
            openai_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        try:
            logger.debug(f"Sending {len(openai_messages)} messages to OpenAI (language: {self.language})")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract response
            message_content = response.choices[0].message.content
            
            # Extract usage info
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": self.model,
                "language": self.language
            }
            
            logger.info(f"Generated response with {usage_info['total_tokens']} tokens (language: {self.language})")
            
            return message_content, usage_info
            
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise
    
    async def generate_streaming_response(
        self,
        messages: List[ChatMessage],
        temperature: Optional[float] = None,
        language: Optional[str] = None
    ):
        """Generate streaming chat response (for future use) with language support"""
        
        # Update language if provided
        if language and language != self.language:
            self.set_language(language)
        
        # Convert messages to OpenAI format
        openai_messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        for msg in messages:
            openai_messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Create streaming response
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=temperature or self.temperature,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content