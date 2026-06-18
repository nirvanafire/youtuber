# backend/src/api/download.py
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from src.core.download_mgr import DownloadManager

router = APIRouter()
_manager = DownloadManager()
_tracker_initialized = False


class DownloadRequest(BaseModel):
    url: str
    video_id: str
    title: str
    format_id: str


class DownloadSubtitleRequest(BaseModel):
    url: str
    video_id: str
    title: str
    language: str
    ext: str


def _ensure_tracker(request: Request) -> None:
    global _tracker_initialized
    if not _tracker_initialized:
        tracker = request.app.state.progress_tracker
        _manager.set_progress_tracker(tracker)
        _tracker_initialized = True


@router.post("/download")
async def start_download(req: DownloadRequest, request: Request):
    _ensure_tracker(request)
    task = _manager.add_task(
        url=req.url,
        video_id=req.video_id,
        title=req.title,
        format_id=req.format_id,
    )
    return task.model_dump()


@router.post("/download/subtitle")
async def start_subtitle_download(req: DownloadSubtitleRequest, request: Request):
    _ensure_tracker(request)
    task = _manager.add_task(
        url=req.url,
        video_id=req.video_id,
        title=f"{req.title} [{req.language}]",
        format_id=f"subtitle:{req.language}",
    )
    return task.model_dump()


@router.get("/download/queue")
async def get_queue():
    return [t.model_dump() for t in _manager.list_tasks()]


@router.post("/download/{task_id}/pause")
async def pause_download(task_id: str):
    task = _manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    _manager.pause_task(task_id)
    return _manager.get_task(task_id).model_dump()


@router.post("/download/{task_id}/resume")
async def resume_download(task_id: str):
    task = _manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    _manager.resume_task(task_id)
    return _manager.get_task(task_id).model_dump()


@router.post("/download/{task_id}/cancel")
async def cancel_download(task_id: str):
    task = _manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    _manager.cancel_task(task_id)
    return _manager.get_task(task_id).model_dump()
