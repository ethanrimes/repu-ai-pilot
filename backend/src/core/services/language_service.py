"""
Language configuration module for handling language-specific system prompts.
Path: backend/src/core/services/language_service.py
"""

from typing import Dict, Optional
from pathlib import Path
import yaml
from src.config.settings import get_settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

class LanguageService:
    """Service for managing language-specific configurations and prompts"""
    
    def __init__(self):
        self._system_prompts: Dict[str, Dict[str, str]] = {}
        self._load_system_prompts()
    
    def _load_system_prompts(self) -> None:
        """Load system prompts from YAML files"""
        try:
            # Get project root directory
            project_root = Path(__file__).parent.parent.parent.parent.parent
            config_path = project_root / "config" / "prompts"
            
            # Load prompts for each supported language
            for language in settings.supported_languages:
                prompt_file = config_path / f"system_prompts_{language}.yaml"
                
                if prompt_file.exists():
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        prompts = yaml.safe_load(f) or {}
                        self._system_prompts[language] = prompts
                        logger.info(f"Loaded system prompts for language: {language}")
                else:
                    logger.warning(f"System prompt file not found: {prompt_file}")
                    self._system_prompts[language] = self._get_default_prompts(language)
                    
        except Exception as e:
            logger.error(f"Error loading system prompts: {e}")
            # Load default prompts for all supported languages
            for language in settings.supported_languages:
                self._system_prompts[language] = self._get_default_prompts(language)
    
    def _get_default_prompts(self, language: str) -> Dict[str, str]:
        """Get default system prompts for a language"""
        if language == 'es':
            return {
                "base_system": """Eres un asistente especializado en repuestos automotrices para el mercado colombiano. 
Tu nombre es RepuAI y trabajas para una empresa de autopartes que se especializa en componentes de frenos.

Responsabilidades principales:
- Ayudar a identificar los repuestos correctos para vehículos específicos
- Proporcionar especificaciones técnicas e información de compatibilidad
- Responder preguntas sobre instalación y mantenimiento
- Asistir con consultas de pedidos y precios
- Ofrecer recomendaciones de productos basadas en el vehículo del cliente

Contexto del mercado:
- Mercado colombiano de autopartes
- Enfoque en componentes de frenos (pastillas, discos, calipers, etc.)
- Precios en pesos colombianos (COP)
- Métodos de pago locales (Nequi, Daviplata, PSE)
- Ciudades principales: Bogotá, Medellín, Cali, Barranquilla

Tono y estilo:
- Profesional pero amigable
- Claro y conciso
- Técnicamente preciso
- Culturalmente apropiado para Colombia

Siempre sé útil, profesional y preciso. Si no estás seguro sobre la compatibilidad específica de una pieza, recomienda verificar con el equipo técnico.""",
                
                "greeting": "¡Hola! Soy RepuAI, tu asistente especializado en repuestos automotrices. ¿En qué puedo ayudarte hoy?",
                
                "error_fallback": "Lo siento, no tengo información específica sobre eso. Te recomiendo contactar a nuestro equipo técnico para obtener asistencia personalizada."
            }
        else:  # English
            return {
                "base_system": """You are a specialized assistant for automotive parts in the Colombian market.
Your name is RepuAI and you work for an auto parts company that specializes in brake components.

Main responsibilities:
- Help identify the correct parts for specific vehicles
- Provide technical specifications and compatibility information
- Answer questions about installation and maintenance
- Assist with order inquiries and pricing
- Offer product recommendations based on customer's vehicle

Market context:
- Colombian automotive parts market
- Focus on brake components (pads, discs, calipers, etc.)
- Prices in Colombian pesos (COP)
- Local payment methods (Nequi, Daviplata, PSE)
- Main cities: Bogotá, Medellín, Cali, Barranquilla

Tone and style:
- Professional but friendly
- Clear and concise
- Technically accurate
- Culturally appropriate for Colombia

Always be helpful, professional, and accurate. If you're unsure about specific part compatibility, recommend verifying with the technical team.""",
                
                "greeting": "Hello! I'm RepuAI, your specialized automotive parts assistant. How can I help you today?",
                
                "error_fallback": "I'm sorry, I don't have specific information about that. I recommend contacting our technical team for personalized assistance."
            }
    
    def get_system_prompt(self, language: str, prompt_type: str = "base_system") -> str:
        """Get system prompt for specific language and type"""
        language = language.lower()
        
        # Fallback to default language if requested language not supported
        if language not in settings.supported_languages:
            logger.warning(f"Unsupported language '{language}', falling back to '{settings.default_language}'")
            language = settings.default_language
        
        # Get prompts for the language
        language_prompts = self._system_prompts.get(language, {})
        
        # Get specific prompt type
        prompt = language_prompts.get(prompt_type)
        
        if not prompt:
            logger.warning(f"Prompt type '{prompt_type}' not found for language '{language}'")
            # Fallback to base_system or default
            prompt = language_prompts.get("base_system") or self._get_default_prompts(language)["base_system"]
        
        return prompt
    
    def get_greeting(self, language: str) -> str:
        """Get greeting message for specific language"""
        return self.get_system_prompt(language, "greeting")
    
    def get_error_fallback(self, language: str) -> str:
        """Get error fallback message for specific language"""
        return self.get_system_prompt(language, "error_fallback")
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported"""
        return language.lower() in settings.supported_languages
    
    def get_supported_languages(self) -> list[str]:
        """Get list of supported languages"""
        return settings.supported_languages
    
    def reload_prompts(self) -> None:
        """Reload system prompts from files"""
        logger.info("Reloading system prompts...")
        self._system_prompts.clear()
        self._load_system_prompts()

# Global instance
_language_service = None

def get_language_service() -> LanguageService:
    """Get global language service instance"""
    global _language_service
    if _language_service is None:
        _language_service = LanguageService()
    return _language_service
