import logging
import os
import tempfile
import uuid
import asyncio
from src.config import SettingsManager
from src.models.download import DownloadTask, DownloadStatus
from src.core.ytdl_wrapper import YtdlWrapper, DownloadInterrupted
from src.core.progress import ProgressTracker

logger = logging.getLogger("youtuber.download_mgr")

_settings_path = os.path.join(tempfile.gettempdir(), "youtuber_settings.json")
_settings_mgr = SettingsManager(_settings_path)


class DownloadManager:
    def __init__(self, max_concurrent: int = 3, auto_schedule: bool = True):
        self._tasks: dict[str, DownloadTask] = {}
        self._max_concurrent = max_concurrent
        self._active_tasks: set[str] = set()
        self._interrupt_tasks: set[str] = set()
        self._tracker: ProgressTracker | None = None
        self._auto_schedule = auto_schedule

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
        logger.info(f"[add_task] task created: id={task.id}, url={url}, format_id={format_id}, status={task.status}")
        self._schedule_next()
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
        if task.status == DownloadStatus.DOWNLOADING:
            self._interrupt_tasks.add(task_id)
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
        if task.status == DownloadStatus.DOWNLOADING:
            self._interrupt_tasks.add(task_id)
        task.status = DownloadStatus.PAUSED
        self._active_tasks.discard(task_id)
        return True

    def resume_task(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != DownloadStatus.PAUSED:
            return False
        task.status = DownloadStatus.WAITING
        self._schedule_next()
        return True

    def set_progress_tracker(self, tracker: ProgressTracker) -> None:
        self._tracker = tracker

    def _schedule_next(self) -> None:
        if not self._auto_schedule:
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        while len(self._active_tasks) < self._max_concurrent:
            waiting = [
                t for t in self._tasks.values()
                if t.status == DownloadStatus.WAITING and t.id not in self._active_tasks
            ]
            if not waiting:
                break
            task = waiting[0]
            # Mark as active immediately to prevent re-scheduling in this loop
            self._active_tasks.add(task.id)
            logger.info(f"[_schedule_next] scheduling task {task.id} ({task.title})")
            loop.create_task(self.execute_task(task.id))

    def _should_abort(self, task_id: str) -> bool:
        return task_id in self._interrupt_tasks

    async def execute_task(self, task_id: str) -> None:
        task = self._tasks.get(task_id)
        if not task or task.status != DownloadStatus.WAITING:
            return
        task.status = DownloadStatus.DOWNLOADING
        self._active_tasks.add(task_id)
        try:
            settings = _settings_mgr.load()
            proxy = settings.proxy
            download_dir = settings.download_dir
            os.makedirs(download_dir, exist_ok=True)
            logger.info(f"execute_task: task_id={task_id}, url={task.url}, proxy={proxy}, download_dir={download_dir}")
            wrapper = YtdlWrapper(proxy=proxy)
            hook = self._tracker.create_hook(task_id) if self._tracker else None
            subtitle_lang = None
            if task.format_id.startswith("subtitle:"):
                subtitle_lang = task.format_id.split(":", 1)[1]

            filepath = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: wrapper.download(
                    task.url, task.format_id, download_dir, hook,
                    should_abort=lambda: self._should_abort(task_id),
                    subtitle_lang=subtitle_lang,
                ),
            )
            task.status = DownloadStatus.COMPLETED
            task.filepath = filepath
            if self._tracker:
                await self._tracker.broadcast_status(task_id, "completed", filepath=filepath)
        except DownloadInterrupted:
            logger.info(f"execute_task: task_id={task_id} interrupted, status={task.status}")
            if task.status == DownloadStatus.CANCELLED:
                if self._tracker:
                    await self._tracker.broadcast_status(task_id, "cancelled")
            elif task.status == DownloadStatus.PAUSED:
                if self._tracker:
                    await self._tracker.broadcast_status(task_id, "paused")
        except Exception as e:
            logger.error(f"execute_task: task_id={task_id} failed: {type(e).__name__}: {e}", exc_info=True)
            task.status = DownloadStatus.FAILED
            task.error = str(e)
            if self._tracker:
                await self._tracker.broadcast_status(task_id, "failed", error=str(e))
        finally:
            self._active_tasks.discard(task_id)
            self._interrupt_tasks.discard(task_id)
            self._schedule_next()
