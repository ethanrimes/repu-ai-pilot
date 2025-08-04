from backend.src.config.settings import get_settings
from backend.src.api.routers import auth, chat, documents, health
from backend.src.api.middleware.error_handler import error_handler_middleware

