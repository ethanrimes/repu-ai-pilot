# backend/src/api/routers/admin.py - Add cleanup endpoint
@router.post("/cleanup-sessions")
async def cleanup_expired_sessions(
    db: Session = Depends(get_db),
    current_user: Dict = Depends(require_admin)
):
    """Manual session cleanup (or run as cron job)"""
    session_manager = SessionManager(db)
    count = await session_manager.cleanup_expired_sessions()
    return {"cleaned_up": count}