# backend/src/api/middleware/language_detector.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class LanguageDetectorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Detect language from Accept-Language header or query param
        lang = request.headers.get("Accept-Language", "es")
        if "lang" in request.query_params:
            lang = request.query_params["lang"]
        
        # Store in request state for use in endpoints
        request.state.language = lang[:2]  # Just the language code
        
        response = await call_next(request)
        return response