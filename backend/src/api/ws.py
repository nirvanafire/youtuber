# backend/src/api/ws.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.models.download import DownloadProgress

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    tracker = websocket.app.state.progress_tracker

    async def send_update(task_id: str, data, extra: dict | None = None):
        try:
            if isinstance(data, DownloadProgress):
                await websocket.send_json({
                    "task_id": task_id,
                    "progress": data.model_dump(),
                })
            else:
                msg = {"task_id": task_id, "status": data}
                if extra:
                    msg.update(extra)
                await websocket.send_json(msg)
        except Exception:
            pass

    tracker.register(send_update)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        tracker.unregister(send_update)
