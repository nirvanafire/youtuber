# backend/src/core/progress.py
import asyncio
from collections.abc import Callable, Awaitable
from src.models.download import DownloadProgress

ProgressCallback = Callable[[str, DownloadProgress], Awaitable[None]]


class ProgressTracker:
    def __init__(self):
        self._listeners: list[ProgressCallback] = []
        self._loop: asyncio.AbstractEventLoop | None = None

    def register(self, callback: ProgressCallback) -> None:
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        self._listeners.append(callback)

    def unregister(self, callback: ProgressCallback) -> None:
        self._listeners = [cb for cb in self._listeners if cb is not callback]

    async def broadcast(self, task_id: str, progress: DownloadProgress) -> None:
        for cb in self._listeners[:]:
            try:
                await cb(task_id, progress)
            except Exception:
                pass

    def broadcast_sync(self, task_id: str, progress: DownloadProgress) -> None:
        """Thread-safe synchronous broadcast for use from sync test clients."""
        if self._loop and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self.broadcast(task_id, progress), self._loop
            )
            future.result(timeout=5)
        else:
            asyncio.run(self.broadcast(task_id, progress))

    def create_hook(self, task_id: str) -> Callable:
        def hook(d: dict):
            if d.get("status") != "downloading":
                return
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            percent = (downloaded / total * 100) if total else 0.0
            progress = DownloadProgress(
                percent=round(percent, 1),
                speed=d.get("speed", 0) or 0,
                downloaded_bytes=downloaded,
                total_bytes=total,
                eta=d.get("eta"),
            )
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.broadcast(task_id, progress))
            except RuntimeError:
                # No running loop (called from sync context without an event loop).
                # This can happen in tests or when yt-dlp runs outside async.
                pass
        return hook
