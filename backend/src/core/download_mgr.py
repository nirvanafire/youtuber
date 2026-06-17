import uuid
import asyncio
from src.models.download import DownloadTask, DownloadStatus
from src.core.ytdl_wrapper import YtdlWrapper
from src.core.progress import ProgressTracker


class DownloadManager:
    def __init__(self, max_concurrent: int = 3):
        self._tasks: dict[str, DownloadTask] = {}
        self._max_concurrent = max_concurrent
        self._active_tasks: set[str] = set()
        self._tracker = None

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    @max_concurrent.setter
    def max_concurrent(self, value: int) -> None:
        self._max_concurrent = value

    def add_task(self, url: str, video_id: str, title: str, format_id: str) -> DownloadTask:
        task = DownloadTask(
            id=str(uuid.uuid4()),
            video_id=video_id,
            title=title,
            url=url,
            format_id=format_id,
            status=DownloadStatus.WAITING,
        )
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> DownloadTask | None:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[DownloadTask]:
        return list(self._tasks.values())

    def remove_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            if task_id in self._active_tasks:
                self.cancel_task(task_id)
            del self._tasks[task_id]
            return True
        return False

    def cancel_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False
        task.status = DownloadStatus.CANCELLED
        self._active_tasks.discard(task_id)
        return True

    def pause_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status not in (
            DownloadStatus.DOWNLOADING,
            DownloadStatus.WAITING,
        ):
            return False
        task.status = DownloadStatus.PAUSED
        self._active_tasks.discard(task_id)
        return True

    def resume_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != DownloadStatus.PAUSED:
            return False
        task.status = DownloadStatus.WAITING
        return True

    def set_progress_tracker(self, tracker: ProgressTracker) -> None:
        self._tracker = tracker

    async def execute_task(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if not task or task.status != DownloadStatus.WAITING:
            return
        task.status = DownloadStatus.DOWNLOADING
        self._active_tasks.add(task_id)
        try:
            wrapper = YtdlWrapper()
            hook = self._tracker.create_hook(task_id) if self._tracker else None
            filepath = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: wrapper.download(task.url, task.format_id, "/tmp/youtuber_downloads", hook),
            )
            task.status = DownloadStatus.COMPLETED
            task.filepath = filepath
        except Exception as e:
            task.status = DownloadStatus.FAILED
            task.error = str(e)
        finally:
            self._active_tasks.discard(task_id)
