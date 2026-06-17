# backend/src/api/router.py
from fastapi import APIRouter
from src.api.health import router as health_router
from src.api.video import router as video_router
from src.api.playlist import router as playlist_router
from src.api.download import router as download_router
from src.api.settings import router as settings_router
from src.api.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(video_router, prefix="/api/v1")
api_router.include_router(playlist_router, prefix="/api/v1")
api_router.include_router(download_router, prefix="/api/v1")
api_router.include_router(settings_router, prefix="/api/v1")
api_router.include_router(ws_router)
