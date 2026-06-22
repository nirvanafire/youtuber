# backend/src/api/video.py
import logging
import os
import shutil
import tempfile
import yt_dlp
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from src.config import SettingsManager
from src.core.url_detector import detect_url_type
from src.core.ytdl_wrapper import YtdlWrapper

logger = logging.getLogger("youtuber.video")
router = APIRouter()

_settings_path = os.path.join(tempfile.gettempdir(), "youtuber_settings.json")
_settings_mgr = SettingsManager(_settings_path)


def _get_wrapper() -> YtdlWrapper:
    settings = _settings_mgr.load()
    proxy = settings.proxy
    if proxy:
        logger.info(f"using proxy from settings: {proxy}")
    return YtdlWrapper(proxy=proxy)


class VideoInfoRequest(BaseModel):
    url: str


@router.get("/video/diagnose")
async def diagnose():
    """Diagnostic endpoint to check yt-dlp and environment status."""
    settings = _settings_mgr.load()
    has_ffmpeg = shutil.which("ffmpeg") is not None
    has_deno = shutil.which("deno") is not None
    has_node = shutil.which("node") is not None

    # Check available JS runtimes
    js_runtimes = []
    if has_deno:
        js_runtimes.append("deno")
    if has_node:
        js_runtimes.append("node")

    return {
        "yt_dlp_version": yt_dlp.version.__version__,
        "proxy": settings.proxy,
        "download_dir": settings.download_dir,
        "ffmpeg_available": has_ffmpeg,
        "js_runtimes_available": js_runtimes,
        "deno_available": has_deno,
        "node_available": has_node,
    }


@router.post("/video/info")
async def video_info(req: VideoInfoRequest):
    logger.info(f"video_info called, url={req.url}")
    try:
        result = detect_url_type(req.url)
        logger.info(f"url_type={result}")
    except ValueError as e:
        logger.warning(f"url validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    wrapper = _get_wrapper()
    try:
        info = wrapper.extract_info(req.url)
        logger.info(f"extract_info success, title={info.title}")
    except Exception as e:
        logger.error(f"extract_info failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    return info.model_dump()
