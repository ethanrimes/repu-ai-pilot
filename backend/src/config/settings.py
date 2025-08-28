# backend/api/config/settings.py
# Path: backend/api/config/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from .env_loader import load_environment  # This will auto-load env vars
from typing import Optional, Literal
from functools import lru_cache

class Settings(BaseSettings):
    """Central configuration using Pydantic Settings"""
    
    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    
    # API
    api_version: str = "v1"
    api_title: str = "Colombian Aftermarket RAG API"
    
    # Database (Supabase)
    supabase_url: str
    supabase_service_key: str
    database_url: str
    
    # Authentication (Firebase)
    firebase_api_key: str
    firebase_auth_domain: str
    firebase_project_id: str
    firebase_storage_bucket: str
    firebase_messaging_sender_id: str
    firebase_app_id: str
    firebase_admin_sdk_path: Optional[str] = None
    
    # Cache (Upstash Redis)
    upstash_redis_rest_url: str
    upstash_redis_rest_token: str
    upstash_redis_max_retries: int = 3
    upstash_redis_retry_delay: int = 100
    
    # LLM Provider
    llm_provider: Literal["openai", "azure"] = "openai"
    openai_api_key: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_deployment_name: Optional[str] = None
    
    # Model Configuration
    chat_model: str = "gpt-4-turbo-preview"
    embedding_model: str = "text-embedding-3-small"
    
    # WhatsApp Business API
    whatsapp_business_id: str
    whatsapp_access_token: str
    whatsapp_verify_token: str
    whatsapp_phone_number_id: str
    whatsapp_webhook_url: Optional[str] = None
    
    # TecDoc API (RapidAPI)
    rapidapi_key: str
    rapidapi_host: str = "tecdoc-catalog.p.rapidapi.com"
    tecdoc_api_url: str = "https://tecdoc-catalog.p.rapidapi.com"
    
    # Infosys RAI
    infosys_rai_enabled: bool = True
    infosys_rai_moderation_url: str = "http://localhost:8001"
    infosys_rai_api_key: Optional[str] = None
    infosys_rai_timeout: int = 30
    infosys_rai_max_retries: int = 2
    
    # Rate Limiting
    rate_limit_anonymous_per_min: int = 10
    rate_limit_free_per_min: int = 30
    rate_limit_premium_per_min: int = 100
    rate_limit_whatsapp_per_min: int = 60
    rate_limit_daily: int = 200  # NEW daily request cap per identifier
    rate_limit_weekly: int = 1000  # NEW weekly request cap per identifier
    
    # Language Settings
    default_language: str = "es"
    supported_languages: list[str] = ["es", "en"]
    auto_detect_language: bool = True
    
    # URLs
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Monitoring
    sentry_dsn: Optional[str] = None
    prometheus_enabled: bool = False
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Add this to ignore extra env vars
    )

    # Product Search Configuration
    category_dropdown_levels: int = 3  # Number of category levels to show (1-4)
    max_articles_per_page: int = 20  # Max articles to show per page

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()