# backend/src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import session manager
from src.infrastructure.cache.session_manager import SessionManager

# Import routers
from src.api.routers import auth, chat, documents, health, inventory  # Add inventory


# Import middleware
from src.api.middleware.error_handler import ErrorHandlerMiddleware
from src.api.middleware.rate_limiter import RateLimitMiddleware
from src.api.middleware.language_detector import LanguageDetectorMiddleware

# Import settings
from src.config.settings import get_settings
from src.shared.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Colombian Aftermarket RAG API",
    version="1.0.0",
    description="AI-powered automotive parts assistant"
)

# Get settings
settings = get_settings()

# Create database engine for background tasks
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
app.include_router(chat.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")  # Add this line
# app.include_router(documents.router, prefix="/api/v1")

# Initialize scheduler
scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=6)
async def cleanup_sessions_job():
    """Run session cleanup every 6 hours"""
    logger.info("Starting scheduled session cleanup...")
    
    # Create a new database session for the background task
    db = SessionLocal()
    try:
        session_manager = SessionManager(db)
        count = await session_manager.cleanup_expired_sessions()
        logger.info(f"Session cleanup completed: {count} sessions cleaned")
    except Exception as e:
        logger.error(f"Error in session cleanup job: {e}")
    finally:
        db.close()

# Start scheduler on app startup
@app.on_event("startup")
async def startup_event():
    scheduler.start()
    logger.info("✅ Application started")
    logger.info("✅ Scheduler started - session cleanup every 6 hours")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("🛑 Scheduler stopped")
    logger.info("🛑 Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
