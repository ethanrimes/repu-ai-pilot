from src.config.settings import get_settings
from src.api.routers import auth, chat, documents, health
from src.api.middleware.error_handler import error_handler_middleware

