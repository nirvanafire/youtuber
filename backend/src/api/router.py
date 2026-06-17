# backend/src/api/router.py
from fastapi import APIRouter
from src.api.health import router as health_router
from src.api.video import router as video_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(video_router, prefix="/api/v1")
# Additional routers will be added in later tasks:
# api_router.include_router(playlist_router, prefix="/api/v1")
# api_router.include_router(download_router, prefix="/api/v1")
# api_router.include_router(settings_router, prefix="/api/v1")
