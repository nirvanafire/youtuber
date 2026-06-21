from enum import Enum

from pydantic import BaseModel


class DownloadStatus(str, Enum):
    WAITING = "waiting"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadProgress(BaseModel):
    percent: float
    speed: float
    downloaded_bytes: float
    total_bytes: float | None
    eta: float | None


class DownloadTask(BaseModel):
    id: str
    video_id: str
    title: str
    url: str
    format_id: str
    status: DownloadStatus
    progress: DownloadProgress | None = None
    filepath: str | None = None
    error: str | None = None
