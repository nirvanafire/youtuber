# backend/src/api/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.models.download import DownloadProgress

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Register this WebSocket as a progress listener
    tracker = websocket.app.state.progress_tracker

    async def send_progress(task_id: str, progress: DownloadProgress):
        try:
            await websocket.send_json({
                "task_id": task_id,
                "progress": progress.model_dump(),
            })
        except Exception:
            pass

    tracker.register(send_progress)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        tracker.unregister(send_progress)
