# backend/src/api/download.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.core.download_mgr import DownloadManager

router = APIRouter()
_manager = DownloadManager()


class DownloadRequest(BaseModel):
    url: str
    video_id: str
    title: str
    format_id: str


@router.post("/download")
async def start_download(req: DownloadRequest):
    task = _manager.add_task(
        url=req.url,
        video_id=req.video_id,
        title=req.title,
        format_id=req.format_id,
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
