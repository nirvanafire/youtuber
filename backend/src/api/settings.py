# backend/src/api/settings.py
import os
import tempfile
from fastapi import APIRouter
from pydantic import BaseModel
from src.config import SettingsManager

router = APIRouter()

_settings_path = os.path.join(tempfile.gettempdir(), "youtuber_settings.json")
_mgr = SettingsManager(_settings_path)


class SettingsUpdateRequest(BaseModel):
    download_dir: str | None = None
    default_quality: str | None = None
    proxy: str | None = None
    max_concurrent_downloads: int | None = None
    language: str | None = None


@router.get("/settings")
async def get_settings():
    return _mgr.load().model_dump()


@router.put("/settings")
async def update_settings(req: SettingsUpdateRequest):
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = _mgr.update(data)
    return updated.model_dump()
