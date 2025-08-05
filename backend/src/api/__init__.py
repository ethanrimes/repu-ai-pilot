# backend/src/api/middleware/__init__.py
"""
Middleware Stack (in order):
1. error_handler.py - Catches all exceptions and returns consistent error responses
2. logging_middleware.py - Logs all requests/responses for debugging
3. rate_limiter.py - Prevents abuse by limiting requests per user/IP
4. firebase_auth.py - Validates Firebase tokens for protected endpoints
5. language_detector.py - Detects user language from headers/preferences
"""