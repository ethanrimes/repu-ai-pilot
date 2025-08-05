from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Import dependencies
from src.api.dependencies import get_db

# Import session manager
from src.infrastructure.cache.session_manager import SessionManager

# Import routers
from src.api.routers import auth, chat, documents, health

# Import middleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.rate_limiter import RateLimitMiddleware
from src.api.middleware.language_detector import LanguageDetectorMiddleware

# Import settings
from src.config.settings import get_settings

# Create FastAPI app
app = FastAPI(
    title="Colombian Aftermarket RAG API",
    version="1.0.0",
    description="AI-powered automotive parts assistant"
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LanguageDetectorMiddleware)

# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
# app.include_router(chat.router, prefix="/api/v1")
# app.include_router(documents.router, prefix="/api/v1")

# Initialize scheduler
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=6)
async def cleanup_sessions_job():
    """Run session cleanup every 6 hours"""
    async with get_db() as db:
        session_manager = SessionManager(db)
        await session_manager.cleanup_expired_sessions()

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    print("✅ Scheduler started - session cleanup every 6 hours")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    print("🛑 Scheduler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)