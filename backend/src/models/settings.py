import os
from pydantic import BaseModel, Field


class AppSettings(BaseModel):
    download_dir: str = Field(
        default_factory=lambda: os.path.join(os.path.expanduser("~"), "Downloads", "Youtuber")
    )
    default_quality: str = "best"
    proxy: str | None = None
    max_concurrent_downloads: int = Field(default=3, ge=1, le=10)
    language: str = "zh"
