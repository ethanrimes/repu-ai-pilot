# backend/test_env.py
from src.config.settings import get_settings

settings = get_settings()
print(f"WhatsApp Access Token: {settings.whatsapp_access_token[:20]}..." if settings.whatsapp_access_token else "NOT LOADED")
print(f"WhatsApp Phone ID: {settings.whatsapp_phone_number_id}")
print(f"WhatsApp Business ID: {settings.whatsapp_business_id}")