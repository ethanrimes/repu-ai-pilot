# backend/src/api/middleware/error_handler.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "type": "http_error"}
            )
        except Exception as e:
            traceback.print_exc()
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "type": "server_error"}
            )