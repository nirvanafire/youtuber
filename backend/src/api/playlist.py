# backend/src/api/playlist.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.core.url_detector import detect_url_type, UrlType
from src.core.ytdl_wrapper import YtdlWrapper

router = APIRouter()
_wrapper = YtdlWrapper()


class PlaylistInfoRequest(BaseModel):
    url: str
    page: int = 1
    page_size: int = 50


@router.post("/playlist/info")
async def playlist_info(req: PlaylistInfoRequest):
    try:
        result = detect_url_type(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if result.type not in (UrlType.PLAYLIST, UrlType.VIDEO):
        raise HTTPException(status_code=400, detail="URL 不是播放列表或频道")
    try:
        info = _wrapper.extract_playlist(req.url, page=req.page, page_size=req.page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return info.model_dump()
