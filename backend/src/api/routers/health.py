# backend/src/api/routers/health.py

from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "repu-ai-backend"}

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Colombian Aftermarket RAG API", "version": "1.0.0"}
