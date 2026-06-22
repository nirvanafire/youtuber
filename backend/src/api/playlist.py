# backend/src/api/playlist.py
import logging
import os
import tempfile
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.config import SettingsManager
from src.core.url_detector import detect_url_type, UrlType
from src.core.ytdl_wrapper import YtdlWrapper

logger = logging.getLogger("youtuber.playlist")
router = APIRouter()

_settings_path = os.path.join(tempfile.gettempdir(), "youtuber_settings.json")
_settings_mgr = SettingsManager(_settings_path)


def _get_wrapper() -> YtdlWrapper:
    settings = _settings_mgr.load()
    proxy = settings.proxy
    if proxy:
        logger.info(f"using proxy from settings: {proxy}")
    return YtdlWrapper(proxy=proxy)


class PlaylistInfoRequest(BaseModel):
    url: str
    page: int = 1
    page_size: int = 50


@router.post("/playlist/info")
async def playlist_info(req: PlaylistInfoRequest):
    logger.info(f"playlist_info called, url={req.url}, page={req.page}")
    try:
        result = detect_url_type(req.url)
        logger.info(f"url_type={result}")
    except ValueError as e:
        logger.warning(f"url validation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    if result.type not in (UrlType.PLAYLIST, UrlType.VIDEO):
        raise HTTPException(status_code=400, detail="URL 不是播放列表或频道")
    wrapper = _get_wrapper()
    try:
        info = wrapper.extract_playlist(req.url, page=req.page, page_size=req.page_size)
        logger.info(f"extract_playlist success, title={info.title}, video_count={info.video_count}")
    except Exception as e:
        logger.error(f"extract_playlist failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    return info.model_dump()
