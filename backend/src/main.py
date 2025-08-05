from backend.src.config.settings import get_settings
from backend.src.api.routers import auth, chat, documents, health
from backend.src.api.middleware.error_handler import error_handler_middleware

# For automatic cleanup, add to main.py:
from apscheduler.schedulers.asyncio import AsyncIOScheduler

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