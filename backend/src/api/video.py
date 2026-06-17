# backend/src/api/video.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.core.url_detector import detect_url_type
from src.core.ytdl_wrapper import YtdlWrapper

router = APIRouter()
_wrapper = YtdlWrapper()


class VideoInfoRequest(BaseModel):
    url: str


@router.post("/video/info")
async def video_info(req: VideoInfoRequest):
    try:
        result = detect_url_type(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    try:
        info = _wrapper.extract_info(req.url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return info.model_dump()
