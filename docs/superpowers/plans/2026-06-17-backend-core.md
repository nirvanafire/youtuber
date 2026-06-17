# Backend Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Python FastAPI backend that wraps yt-dlp, providing REST API + WebSocket for video info extraction, format selection, subtitle management, playlist browsing, download queue management, and settings persistence.

**Architecture:** FastAPI app with yt-dlp library-mode integration. REST endpoints for request-response operations, WebSocket for real-time download progress push. Download manager controls concurrent downloads with pause/resume/cancel. Settings persisted to JSON file.

**Tech Stack:** Python 3.10+, FastAPI, uvicorn, yt-dlp, Pydantic v2, pytest, httpx (for testing), websockets

---

## File Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app, uvicorn entry, PORT= output
│   ├── config.py                   # Settings file paths, defaults
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py                # VideoInfo, FormatInfo, SubtitleInfo
│   │   ├── playlist.py             # PlaylistInfo, PlaylistVideoItem
│   │   ├── download.py             # DownloadTask, DownloadProgress, DownloadStatus enum
│   │   └── settings.py             # AppSettings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py               # APIRouter aggregation
│   │   ├── health.py               # GET /health
│   │   ├── video.py                # POST /api/v1/video/info
│   │   ├── playlist.py             # POST /api/v1/playlist/info
│   │   ├── download.py             # POST /api/v1/download, GET /api/v1/download/queue, pause/resume/cancel
│   │   ├── settings.py             # GET/PUT /api/v1/settings
│   │   └── ws.py                   # WebSocket /ws endpoint
│   └── core/
│       ├── __init__.py
│       ├── ytdl_wrapper.py         # yt-dlp library wrapper
│       ├── download_mgr.py         # Download queue, concurrency control
│       ├── progress.py             # Progress tracking, WebSocket broadcast
│       └── url_detector.py         # URL type detection
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared fixtures (test client, mock yt-dlp)
│   ├── test_models/
│   │   ├── __init__.py
│   │   ├── test_video.py
│   │   ├── test_playlist.py
│   │   ├── test_download.py
│   │   └── test_settings.py
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_ytdl_wrapper.py
│   │   ├── test_download_mgr.py
│   │   ├── test_progress.py
│   │   └── test_url_detector.py
│   └── test_api/
│       ├── __init__.py
│       ├── test_health.py
│       ├── test_video.py
│       ├── test_playlist.py
│       ├── test_download.py
│       ├── test_settings.py
│       └── test_ws.py
├── requirements.txt
├── pyproject.toml
└── pytest.ini
```

---

## Task 1: Project Scaffolding

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.txt`
- Create: `backend/pytest.ini`
- Create: `backend/src/__init__.py`
- Create: `backend/src/models/__init__.py`
- Create: `backend/src/api/__init__.py`
- Create: `backend/src/core/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/test_models/__init__.py`
- Create: `backend/tests/test_core/__init__.py`
- Create: `backend/tests/test_api/__init__.py`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "youtuber-backend"
version = "0.1.0"
description = "YouTube video downloader backend"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "yt-dlp>=2026.01.01",
    "pydantic>=2.0.0",
    "aiofiles>=24.0.0",
    "websockets>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "pytest-cov>=5.0.0",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["src*"]
```

- [ ] **Step 2: Create requirements.txt**

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
yt-dlp>=2026.01.01
pydantic>=2.0.0
aiofiles>=24.0.0
websockets>=13.0.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
httpx>=0.27.0
pytest-cov>=5.0.0
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
pythonpath = src
```

- [ ] **Step 4: Create all __init__.py files and conftest.py**

```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    from src.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

- [ ] **Step 5: Verify project structure**

Run: `cd backend && python -c "import src; print('OK')"`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "chore: scaffold backend project with FastAPI, yt-dlp, pytest"
```

---

## Task 2: Pydantic Models — VideoInfo, FormatInfo, SubtitleInfo

**Files:**
- Create: `backend/src/models/video.py`
- Create: `backend/tests/test_models/test_video.py`

- [ ] **Step 1: Write failing tests for video models**

```python
# backend/tests/test_models/test_video.py
from src.models.video import VideoInfo, FormatInfo, SubtitleInfo


class TestFormatInfo:
    def test_create_format_with_all_fields(self):
        fmt = FormatInfo(
            format_id="137",
            ext="mp4",
            resolution="1920x1080",
            fps=30,
            vcodec="avc1",
            acodec="none",
            filesize=50_000_000,
            format_note="1080p",
            is_video_only=True,
            is_audio_only=False,
        )
        assert fmt.format_id == "137"
        assert fmt.resolution == "1920x1080"
        assert fmt.is_video_only is True
        assert fmt.is_audio_only is False

    def test_format_without_filesize(self):
        fmt = FormatInfo(
            format_id="22",
            ext="mp4",
            resolution="1280x720",
            fps=30,
            vcodec="avc1",
            acodec="mp4a",
            filesize=None,
            format_note="720p",
            is_video_only=False,
            is_audio_only=False,
        )
        assert fmt.filesize is None

    def test_audio_only_format(self):
        fmt = FormatInfo(
            format_id="140",
            ext="m4a",
            resolution="audio only",
            fps=None,
            vcodec="none",
            acodec="mp4a",
            filesize=5_000_000,
            format_note="audio",
            is_video_only=False,
            is_audio_only=True,
        )
        assert fmt.is_audio_only is True
        assert fmt.is_video_only is False


class TestSubtitleInfo:
    def test_manual_subtitle(self):
        sub = SubtitleInfo(
            language="en",
            language_name="English",
            ext="srt",
            is_auto_generated=False,
        )
        assert sub.is_auto_generated is False

    def test_auto_subtitle(self):
        sub = SubtitleInfo(
            language="zh-Hans",
            language_name="Chinese (Simplified)",
            ext="vtt",
            is_auto_generated=True,
        )
        assert sub.is_auto_generated is True


class TestVideoInfo:
    def test_create_video_info(self):
        video = VideoInfo(
            id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            duration=212,
            uploader="Rick Astley",
            thumbnail="https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            webpage_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            formats=[
                FormatInfo(
                    format_id="22",
                    ext="mp4",
                    resolution="1280x720",
                    fps=30,
                    vcodec="avc1",
                    acodec="mp4a",
                    filesize=20_000_000,
                    format_note="720p",
                    is_video_only=False,
                    is_audio_only=False,
                )
            ],
            subtitles=[
                SubtitleInfo(
                    language="en",
                    language_name="English",
                    ext="srt",
                    is_auto_generated=False,
                )
            ],
        )
        assert video.id == "dQw4w9WgXcQ"
        assert video.title == "Never Gonna Give You Up"
        assert video.duration == 212
        assert len(video.formats) == 1
        assert len(video.subtitles) == 1

    def test_video_info_serializes_to_dict(self):
        video = VideoInfo(
            id="test",
            title="Test",
            duration=60,
            uploader="TestUser",
            thumbnail="https://example.com/thumb.jpg",
            webpage_url="https://youtube.com/watch?v=test",
            formats=[],
            subtitles=[],
        )
        d = video.model_dump()
        assert d["id"] == "test"
        assert d["formats"] == []
        assert d["subtitles"] == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_models/test_video.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.models.video'`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/models/video.py
from pydantic import BaseModel


class FormatInfo(BaseModel):
    format_id: str
    ext: str
    resolution: str
    fps: int | None
    vcodec: str
    acodec: str
    filesize: int | None
    format_note: str
    is_video_only: bool
    is_audio_only: bool


class SubtitleInfo(BaseModel):
    language: str
    language_name: str
    ext: str
    is_auto_generated: bool


class VideoInfo(BaseModel):
    id: str
    title: str
    duration: int
    uploader: str
    thumbnail: str
    webpage_url: str
    formats: list[FormatInfo]
    subtitles: list[SubtitleInfo]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models/test_video.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/models/video.py backend/tests/test_models/test_video.py
git commit -m "feat(models): add VideoInfo, FormatInfo, SubtitleInfo Pydantic models"
```

---

## Task 3: Pydantic Models — PlaylistInfo

**Files:**
- Create: `backend/src/models/playlist.py`
- Create: `backend/tests/test_models/test_playlist.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_models/test_playlist.py
from src.models.playlist import PlaylistInfo, PlaylistVideoItem


class TestPlaylistVideoItem:
    def test_create_item(self):
        item = PlaylistVideoItem(
            id="abc123",
            title="Video 1",
            duration=120,
            thumbnail="https://example.com/thumb.jpg",
            url="https://www.youtube.com/watch?v=abc123",
        )
        assert item.id == "abc123"
        assert item.duration == 120

    def test_item_without_duration(self):
        item = PlaylistVideoItem(
            id="abc123",
            title="Live Stream",
            duration=None,
            thumbnail="https://example.com/thumb.jpg",
            url="https://www.youtube.com/watch?v=abc123",
        )
        assert item.duration is None


class TestPlaylistInfo:
    def test_create_playlist(self):
        playlist = PlaylistInfo(
            id="PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf",
            title="My Playlist",
            uploader="TestUser",
            video_count=3,
            videos=[
                PlaylistVideoItem(
                    id="vid1",
                    title="First",
                    duration=60,
                    thumbnail="https://example.com/1.jpg",
                    url="https://youtube.com/watch?v=vid1",
                ),
                PlaylistVideoItem(
                    id="vid2",
                    title="Second",
                    duration=90,
                    thumbnail="https://example.com/2.jpg",
                    url="https://youtube.com/watch?v=vid2",
                ),
                PlaylistVideoItem(
                    id="vid3",
                    title="Third",
                    duration=120,
                    thumbnail="https://example.com/3.jpg",
                    url="https://youtube.com/watch?v=vid3",
                ),
            ],
            page=1,
            total_pages=1,
        )
        assert playlist.video_count == 3
        assert len(playlist.videos) == 3
        assert playlist.page == 1

    def test_playlist_pagination(self):
        videos = [
            PlaylistVideoItem(
                id=f"vid{i}",
                title=f"Video {i}",
                duration=60,
                thumbnail=f"https://example.com/{i}.jpg",
                url=f"https://youtube.com/watch?v=vid{i}",
            )
            for i in range(50)
        ]
        playlist = PlaylistInfo(
            id="PLtest",
            title="Big Playlist",
            uploader="TestUser",
            video_count=200,
            videos=videos,
            page=1,
            total_pages=4,
        )
        assert playlist.total_pages == 4
        assert len(playlist.videos) == 50
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_models/test_playlist.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/models/playlist.py
from pydantic import BaseModel


class PlaylistVideoItem(BaseModel):
    id: str
    title: str
    duration: int | None
    thumbnail: str
    url: str


class PlaylistInfo(BaseModel):
    id: str
    title: str
    uploader: str
    video_count: int
    videos: list[PlaylistVideoItem]
    page: int
    total_pages: int
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models/test_playlist.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/models/playlist.py backend/tests/test_models/test_playlist.py
git commit -m "feat(models): add PlaylistInfo and PlaylistVideoItem models"
```

---

## Task 4: Pydantic Models — DownloadTask, DownloadProgress

**Files:**
- Create: `backend/src/models/download.py`
- Create: `backend/tests/test_models/test_download.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_models/test_download.py
from src.models.download import DownloadTask, DownloadProgress, DownloadStatus


class TestDownloadStatus:
    def test_all_statuses_exist(self):
        assert DownloadStatus.WAITING == "waiting"
        assert DownloadStatus.DOWNLOADING == "downloading"
        assert DownloadStatus.PAUSED == "paused"
        assert DownloadStatus.COMPLETED == "completed"
        assert DownloadStatus.FAILED == "failed"
        assert DownloadStatus.CANCELLED == "cancelled"


class TestDownloadTask:
    def test_create_task(self):
        task = DownloadTask(
            id="task-001",
            video_id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            format_id="22",
            status=DownloadStatus.WAITING,
        )
        assert task.id == "task-001"
        assert task.status == DownloadStatus.WAITING
        assert task.progress is None

    def test_task_defaults(self):
        task = DownloadTask(
            id="task-002",
            video_id="test",
            title="Test",
            url="https://youtube.com/watch?v=test",
            format_id="best",
            status=DownloadStatus.WAITING,
        )
        assert task.progress is None
        assert task.filepath is None
        assert task.error is None


class TestDownloadProgress:
    def test_create_progress(self):
        progress = DownloadProgress(
            percent=45.2,
            speed=1_500_000,
            downloaded_bytes=45_000_000,
            total_bytes=100_000_000,
            eta=37,
        )
        assert progress.percent == 45.2
        assert progress.speed == 1_500_000
        assert progress.eta == 37

    def test_progress_unknown_total(self):
        progress = DownloadProgress(
            percent=50.0,
            speed=1_000_000,
            downloaded_bytes=50_000_000,
            total_bytes=None,
            eta=None,
        )
        assert progress.total_bytes is None
        assert progress.eta is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_models/test_download.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/models/download.py
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
    speed: int
    downloaded_bytes: int
    total_bytes: int | None
    eta: int | None


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models/test_download.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/models/download.py backend/tests/test_models/test_download.py
git commit -m "feat(models): add DownloadTask, DownloadProgress, DownloadStatus models"
```

---

## Task 5: Pydantic Models — AppSettings

**Files:**
- Create: `backend/src/models/settings.py`
- Create: `backend/tests/test_models/test_settings.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_models/test_settings.py
from src.models.settings import AppSettings


class TestAppSettings:
    def test_default_settings(self):
        settings = AppSettings()
        assert settings.download_dir is not None
        assert settings.default_quality == "best"
        assert settings.proxy is None
        assert settings.max_concurrent_downloads == 3
        assert settings.language == "zh"

    def test_custom_settings(self):
        settings = AppSettings(
            download_dir="/tmp/downloads",
            default_quality="1080p",
            proxy="http://127.0.0.1:7890",
            max_concurrent_downloads=5,
            language="en",
        )
        assert settings.download_dir == "/tmp/downloads"
        assert settings.default_quality == "1080p"
        assert settings.proxy == "http://127.0.0.1:7890"
        assert settings.max_concurrent_downloads == 5
        assert settings.language == "en"

    def test_settings_serialization_roundtrip(self):
        original = AppSettings(
            download_dir="/tmp/test",
            default_quality="720p",
            proxy="socks5://127.0.0.1:1080",
            max_concurrent_downloads=2,
            language="en",
        )
        data = original.model_dump()
        restored = AppSettings(**data)
        assert restored == original

    def test_concurrent_downloads_bounds(self):
        settings = AppSettings(max_concurrent_downloads=1)
        assert settings.max_concurrent_downloads == 1
        settings = AppSettings(max_concurrent_downloads=10)
        assert settings.max_concurrent_downloads == 10
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_models/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/models/settings.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models/test_settings.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/models/settings.py backend/tests/test_models/test_settings.py
git commit -m "feat(models): add AppSettings model with defaults and validation"
```

---

## Task 6: URL Detector

**Files:**
- Create: `backend/src/core/url_detector.py`
- Create: `backend/tests/test_core/test_url_detector.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_core/test_url_detector.py
import pytest
from src.core.url_detector import detect_url_type, UrlType


class TestDetectUrlType:
    def test_single_video(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.playlist_id is None

    def test_shorts_url(self):
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"

    def test_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = detect_url_type(url)
        assert result.type == UrlType.PLAYLIST
        assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_video_with_playlist(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
        assert result.playlist_id == "PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"

    def test_channel_at_url(self):
        url = "https://www.youtube.com/@RickAstleyYT"
        result = detect_url_type(url)
        assert result.type == UrlType.CHANNEL

    def test_channel_id_url(self):
        url = "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
        result = detect_url_type(url)
        assert result.type == UrlType.CHANNEL

    def test_invalid_url(self):
        with pytest.raises(ValueError, match="无法识别"):
            detect_url_type("https://example.com/not-youtube")

    def test_empty_url(self):
        with pytest.raises(ValueError):
            detect_url_type("")

    def test_youtu_be_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        result = detect_url_type(url)
        assert result.type == UrlType.VIDEO
        assert result.video_id == "dQw4w9WgXcQ"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_url_detector.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/core/url_detector.py
import re
from enum import Enum
from pydantic import BaseModel


class UrlType(str, Enum):
    VIDEO = "video"
    PLAYLIST = "playlist"
    CHANNEL = "channel"


class UrlDetectionResult(BaseModel):
    type: UrlType
    video_id: str | None = None
    playlist_id: str | None = None
    channel_id: str | None = None
    raw_url: str


_PATTERNS = {
    "video": [
        re.compile(r"(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/shorts/)([\w-]{11})"),
    ],
    "playlist": [
        re.compile(r"youtube\.com/playlist\?.*list=([\w-]+)"),
    ],
    "channel": [
        re.compile(r"youtube\.com/@([\w.-]+)"),
        re.compile(r"youtube\.com/channel/([\w-]+)"),
    ],
}


def detect_url_type(url: str) -> UrlDetectionResult:
    if not url or not url.strip():
        raise ValueError("URL 不能为空")

    url = url.strip()

    # Check playlist first (may also have video)
    for pattern in _PATTERNS["playlist"]:
        m = pattern.search(url)
        if m:
            playlist_id = m.group(1)
            # Check if also has video
            video_id = None
            for vp in _PATTERNS["video"]:
                vm = vp.search(url)
                if vm:
                    video_id = vm.group(1)
                    break
            if video_id:
                return UrlDetectionResult(
                    type=UrlType.VIDEO,
                    video_id=video_id,
                    playlist_id=playlist_id,
                    raw_url=url,
                )
            return UrlDetectionResult(
                type=UrlType.PLAYLIST,
                playlist_id=playlist_id,
                raw_url=url,
            )

    # Check video
    for pattern in _PATTERNS["video"]:
        m = pattern.search(url)
        if m:
            return UrlDetectionResult(
                type=UrlType.VIDEO,
                video_id=m.group(1),
                raw_url=url,
            )

    # Check channel
    for pattern in _PATTERNS["channel"]:
        m = pattern.search(url)
        if m:
            return UrlDetectionResult(
                type=UrlType.CHANNEL,
                channel_id=m.group(1),
                raw_url=url,
            )

    raise ValueError(f"无法识别的 YouTube URL: {url}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_url_detector.py -v`
Expected: PASS (9 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/url_detector.py backend/tests/test_core/test_url_detector.py
git commit -m "feat(core): add URL type detector for video/playlist/channel detection"
```

---

## Task 7: yt-dlp Wrapper — extract_info

**Files:**
- Create: `backend/src/core/ytdl_wrapper.py`
- Create: `backend/tests/test_core/test_ytdl_wrapper.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_core/test_ytdl_wrapper.py
import pytest
from unittest.mock import MagicMock, patch
from src.core.ytdl_wrapper import YtdlWrapper
from src.models.video import VideoInfo


class TestYtdlWrapperExtractInfo:
    @pytest.fixture
    def wrapper(self):
        return YtdlWrapper()

    @pytest.fixture
    def mock_ytdl_info(self):
        """Simulated yt-dlp extract_info result."""
        return {
            "id": "dQw4w9WgXcQ",
            "title": "Never Gonna Give You Up",
            "duration": 212,
            "uploader": "Rick Astley",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "formats": [
                {
                    "format_id": "22",
                    "ext": "mp4",
                    "resolution": "1280x720",
                    "fps": 30,
                    "vcodec": "avc1",
                    "acodec": "mp4a",
                    "filesize": 20_000_000,
                    "format_note": "720p",
                },
                {
                    "format_id": "137",
                    "ext": "mp4",
                    "resolution": "1920x1080",
                    "fps": 30,
                    "vcodec": "avc1",
                    "acodec": "none",
                    "filesize": 50_000_000,
                    "format_note": "1080p",
                },
                {
                    "format_id": "140",
                    "ext": "m4a",
                    "resolution": "audio only",
                    "fps": None,
                    "vcodec": "none",
                    "acodec": "mp4a",
                    "filesize": 5_000_000,
                    "format_note": "audio",
                },
            ],
            "subtitles": {
                "en": [
                    {"ext": "srt", "url": "https://example.com/en.srt"},
                ],
            },
            "automatic_captions": {
                "zh-Hans": [
                    {"ext": "vtt", "url": "https://example.com/zh.vtt"},
                ],
            },
        }

    def test_extract_video_info(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert isinstance(info, VideoInfo)
        assert info.id == "dQw4w9WgXcQ"
        assert info.title == "Never Gonna Give You Up"
        assert info.duration == 212
        assert info.uploader == "Rick Astley"

    def test_extract_info_parses_formats(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert len(info.formats) == 3
        video_only = [f for f in info.formats if f.is_video_only]
        audio_only = [f for f in info.formats if f.is_audio_only]
        assert len(video_only) == 1
        assert len(audio_only) == 1
        assert video_only[0].format_id == "137"
        assert audio_only[0].format_id == "140"

    def test_extract_info_parses_subtitles(self, wrapper, mock_ytdl_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_ytdl_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

        assert len(info.subtitles) == 2
        manual = [s for s in info.subtitles if not s.is_auto_generated]
        auto = [s for s in info.subtitles if s.is_auto_generated]
        assert len(manual) == 1
        assert manual[0].language == "en"
        assert len(auto) == 1
        assert auto[0].language == "zh-Hans"

    def test_extract_info_no_formats(self, wrapper):
        raw = {
            "id": "test",
            "title": "Test",
            "duration": 60,
            "uploader": "User",
            "thumbnail": "https://example.com/t.jpg",
            "webpage_url": "https://youtube.com/watch?v=test",
            "formats": None,
            "subtitles": {},
            "automatic_captions": {},
        }
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = raw
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_info("https://youtube.com/watch?v=test")

        assert info.formats == []
        assert info.subtitles == []

    def test_extract_info_ytdl_error(self, wrapper):
        import yt_dlp

        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.side_effect = yt_dlp.utils.DownloadError("Video unavailable")
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(Exception, match="Video unavailable"):
                wrapper.extract_info("https://youtube.com/watch?v=private")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/core/ytdl_wrapper.py
import yt_dlp
from src.models.video import VideoInfo, FormatInfo, SubtitleInfo


class YtdlWrapper:
    def __init__(self, proxy: str | None = None):
        self._proxy = proxy

    def _base_opts(self) -> dict:
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        if self._proxy:
            opts["proxy"] = self._proxy
        return opts

    def _classify_format(self, fmt: dict) -> tuple[bool, bool]:
        vcodec = fmt.get("vcodec", "none")
        acodec = fmt.get("acodec", "none")
        is_video_only = vcodec != "none" and acodec == "none"
        is_audio_only = vcodec == "none" and acodec != "none"
        return is_video_only, is_audio_only

    def _parse_formats(self, raw_formats: list[dict] | None) -> list[FormatInfo]:
        if not raw_formats:
            return []
        result = []
        for fmt in raw_formats:
            is_video_only, is_audio_only = self._classify_format(fmt)
            result.append(FormatInfo(
                format_id=fmt.get("format_id", ""),
                ext=fmt.get("ext", ""),
                resolution=fmt.get("resolution", "N/A"),
                fps=fmt.get("fps"),
                vcodec=fmt.get("vcodec", "none"),
                acodec=fmt.get("acodec", "none"),
                filesize=fmt.get("filesize"),
                format_note=fmt.get("format_note", ""),
                is_video_only=is_video_only,
                is_audio_only=is_audio_only,
            ))
        return result

    def _parse_subtitles(self, subs: dict | None, auto_subs: dict | None) -> list[SubtitleInfo]:
        result = []
        if subs:
            for lang, entries in subs.items():
                ext = entries[0]["ext"] if entries else "srt"
                result.append(SubtitleInfo(
                    language=lang,
                    language_name=lang,
                    ext=ext,
                    is_auto_generated=False,
                ))
        if auto_subs:
            for lang, entries in auto_subs.items():
                ext = entries[0]["ext"] if entries else "vtt"
                result.append(SubtitleInfo(
                    language=lang,
                    language_name=lang,
                    ext=ext,
                    is_auto_generated=True,
                ))
        return result

    def extract_info(self, url: str) -> VideoInfo:
        opts = self._base_opts()
        with yt_dlp.YoutubeDL(opts) as ydl:
            raw = ydl.extract_info(url, download=False)

        return VideoInfo(
            id=raw.get("id", ""),
            title=raw.get("title", ""),
            duration=raw.get("duration", 0),
            uploader=raw.get("uploader", ""),
            thumbnail=raw.get("thumbnail", ""),
            webpage_url=raw.get("webpage_url", url),
            formats=self._parse_formats(raw.get("formats")),
            subtitles=self._parse_subtitles(
                raw.get("subtitles"),
                raw.get("automatic_captions"),
            ),
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/ytdl_wrapper.py backend/tests/test_core/test_ytdl_wrapper.py
git commit -m "feat(core): add yt-dlp wrapper with info extraction and format/subtitle parsing"
```

---

## Task 8: yt-dlp Wrapper — Playlist Extraction

**Files:**
- Modify: `backend/src/core/ytdl_wrapper.py`
- Modify: `backend/tests/test_core/test_ytdl_wrapper.py`

- [ ] **Step 1: Write failing tests**

Append to `backend/tests/test_core/test_ytdl_wrapper.py`:

```python
from src.models.playlist import PlaylistInfo


class TestYtdlWrapperExtractPlaylist:
    @pytest.fixture
    def wrapper(self):
        return YtdlWrapper()

    @pytest.fixture
    def mock_playlist_info(self):
        return {
            "id": "PLtest123",
            "title": "My Playlist",
            "uploader": "TestUser",
            "entries": [
                {
                    "id": "vid1",
                    "title": "First Video",
                    "duration": 60,
                    "thumbnail": "https://example.com/1.jpg",
                    "webpage_url": "https://youtube.com/watch?v=vid1",
                },
                {
                    "id": "vid2",
                    "title": "Second Video",
                    "duration": 90,
                    "thumbnail": "https://example.com/2.jpg",
                    "webpage_url": "https://youtube.com/watch?v=vid2",
                },
            ],
        }

    def test_extract_playlist(self, wrapper, mock_playlist_info):
        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = mock_playlist_info
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            info = wrapper.extract_playlist(
                "https://www.youtube.com/playlist?list=PLtest123",
                page=1,
                page_size=50,
            )

        assert isinstance(info, PlaylistInfo)
        assert info.id == "PLtest123"
        assert info.title == "My Playlist"
        assert info.video_count == 2
        assert len(info.videos) == 2
        assert info.page == 1

    def test_extract_playlist_pagination(self, wrapper):
        entries = [
            {"id": f"vid{i}", "title": f"V{i}", "duration": 60,
             "thumbnail": f"https://example.com/{i}.jpg",
             "webpage_url": f"https://youtube.com/watch?v=vid{i}"}
            for i in range(100)
        ]
        raw = {"id": "PLbig", "title": "Big", "uploader": "User", "entries": entries}

        with patch("src.core.ytdl_wrapper.yt_dlp.YoutubeDL") as mock_cls:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = raw
            mock_cls.return_value.__enter__ = MagicMock(return_value=mock_instance)
            mock_cls.return_value.__exit__ = MagicMock(return_value=False)

            page1 = wrapper.extract_playlist("https://youtube.com/playlist?list=PLbig", page=1, page_size=50)

        assert page1.total_pages == 2
        assert len(page1.videos) == 50
        assert page1.page == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py::TestYtdlWrapperExtractPlaylist -v`
Expected: FAIL — `AttributeError: 'YtdlWrapper' object has no attribute 'extract_playlist'`

- [ ] **Step 3: Write minimal implementation**

Add to `backend/src/core/ytdl_wrapper.py`:

```python
import math
from src.models.playlist import PlaylistInfo, PlaylistVideoItem


# Add method to YtdlWrapper class:
    def extract_playlist(self, url: str, page: int = 1, page_size: int = 50) -> PlaylistInfo:
        opts = self._base_opts()
        opts["extract_flat"] = True
        with yt_dlp.YoutubeDL(opts) as ydl:
            raw = ydl.extract_info(url, download=False)

        entries = list(raw.get("entries", []))
        total = len(entries)
        total_pages = max(1, math.ceil(total / page_size))
        start = (page - 1) * page_size
        end = start + page_size
        page_entries = entries[start:end]

        videos = [
            PlaylistVideoItem(
                id=e.get("id", ""),
                title=e.get("title", ""),
                duration=e.get("duration"),
                thumbnail=e.get("thumbnail", ""),
                url=e.get("webpage_url", e.get("url", "")),
            )
            for e in page_entries
        ]

        return PlaylistInfo(
            id=raw.get("id", ""),
            title=raw.get("title", ""),
            uploader=raw.get("uploader", ""),
            video_count=total,
            videos=videos,
            page=page,
            total_pages=total_pages,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_ytdl_wrapper.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/ytdl_wrapper.py backend/tests/test_core/test_ytdl_wrapper.py
git commit -m "feat(core): add playlist extraction with pagination support"
```

---

## Task 9: Download Manager — Queue and Concurrency

**Files:**
- Create: `backend/src/core/download_mgr.py`
- Create: `backend/tests/test_core/test_download_mgr.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_core/test_download_mgr.py
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from src.core.download_mgr import DownloadManager
from src.models.download import DownloadStatus


class TestDownloadManager:
    @pytest.fixture
    def mgr(self):
        return DownloadManager(max_concurrent=2)

    def test_add_task(self, mgr):
        task = mgr.add_task(
            url="https://youtube.com/watch?v=test",
            video_id="test",
            title="Test Video",
            format_id="22",
        )
        assert task.status == DownloadStatus.WAITING
        assert task.id is not None
        assert len(mgr.list_tasks()) == 1

    def test_add_multiple_tasks(self, mgr):
        for i in range(3):
            mgr.add_task(
                url=f"https://youtube.com/watch?v=v{i}",
                video_id=f"v{i}",
                title=f"Video {i}",
                format_id="22",
            )
        assert len(mgr.list_tasks()) == 3

    def test_get_task(self, mgr):
        task = mgr.add_task(
            url="https://youtube.com/watch?v=test",
            video_id="test",
            title="Test",
            format_id="22",
        )
        found = mgr.get_task(task.id)
        assert found is not None
        assert found.id == task.id

    def test_get_nonexistent_task(self, mgr):
        assert mgr.get_task("nonexistent") is None

    def test_remove_waiting_task(self, mgr):
        task = mgr.add_task(
            url="https://youtube.com/watch?v=test",
            video_id="test",
            title="Test",
            format_id="22",
        )
        result = mgr.remove_task(task.id)
        assert result is True
        assert len(mgr.list_tasks()) == 0

    def test_remove_nonexistent_task(self, mgr):
        assert mgr.remove_task("nonexistent") is False

    def test_cancel_task(self, mgr):
        task = mgr.add_task(
            url="https://youtube.com/watch?v=test",
            video_id="test",
            title="Test",
            format_id="22",
        )
        result = mgr.cancel_task(task.id)
        assert result is True
        updated = mgr.get_task(task.id)
        assert updated.status == DownloadStatus.CANCELLED

    def test_list_tasks_returns_copy(self, mgr):
        mgr.add_task(
            url="https://youtube.com/watch?v=test",
            video_id="test",
            title="Test",
            format_id="22",
        )
        tasks = mgr.list_tasks()
        tasks.clear()
        assert len(mgr.list_tasks()) == 1

    def test_max_concurrent_property(self, mgr):
        assert mgr.max_concurrent == 2
        mgr.max_concurrent = 5
        assert mgr.max_concurrent == 5
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_download_mgr.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/core/download_mgr.py
import uuid
import asyncio
from src.models.download import DownloadTask, DownloadStatus


class DownloadManager:
    def __init__(self, max_concurrent: int = 3):
        self._tasks: dict[str, DownloadTask] = {}
        self._max_concurrent = max_concurrent
        self._active_tasks: set[str] = set()

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
        if not task or task.status != DownloadStatus.DOWNLOADING:
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_download_mgr.py -v`
Expected: PASS (8 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/download_mgr.py backend/tests/test_core/test_download_mgr.py
git commit -m "feat(core): add download manager with queue, concurrency, pause/resume/cancel"
```

---

## Task 10: Progress Tracker + WebSocket Broadcast

**Files:**
- Create: `backend/src/core/progress.py`
- Create: `backend/tests/test_core/test_progress.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_core/test_progress.py
import pytest
import asyncio
from unittest.mock import AsyncMock
from src.core.progress import ProgressTracker
from src.models.download import DownloadProgress


class TestProgressTracker:
    @pytest.fixture
    def tracker(self):
        return ProgressTracker()

    def test_register_listener(self, tracker):
        callback = AsyncMock()
        tracker.register(callback)
        assert callback in tracker._listeners

    def test_unregister_listener(self, tracker):
        callback = AsyncMock()
        tracker.register(callback)
        tracker.unregister(callback)
        assert callback not in tracker._listeners

    @pytest.mark.asyncio
    async def test_broadcast_calls_listeners(self, tracker):
        callback = AsyncMock()
        tracker.register(callback)
        progress = DownloadProgress(
            percent=50.0,
            speed=1_000_000,
            downloaded_bytes=50_000_000,
            total_bytes=100_000_000,
            eta=50,
        )
        await tracker.broadcast("task-001", progress)
        callback.assert_called_once_with("task-001", progress)

    @pytest.mark.asyncio
    async def test_broadcast_to_multiple_listeners(self, tracker):
        cb1 = AsyncMock()
        cb2 = AsyncMock()
        tracker.register(cb1)
        tracker.register(cb2)
        progress = DownloadProgress(
            percent=25.0,
            speed=500_000,
            downloaded_bytes=25_000_000,
            total_bytes=100_000_000,
            eta=150,
        )
        await tracker.broadcast("task-002", progress)
        cb1.assert_called_once()
        cb2.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_handles_listener_error(self, tracker):
        bad_cb = AsyncMock(side_effect=Exception("connection lost"))
        good_cb = AsyncMock()
        tracker.register(bad_cb)
        tracker.register(good_cb)
        progress = DownloadProgress(
            percent=10.0,
            speed=100_000,
            downloaded_bytes=10_000_000,
            total_bytes=100_000_000,
            eta=900,
        )
        await tracker.broadcast("task-003", progress)
        good_cb.assert_called_once()

    def test_create_progress_hook(self, tracker):
        hook = tracker.create_hook("task-001")
        assert callable(hook)

    def test_progress_hook_parses_ytdl_dict(self, tracker):
        hook = tracker.create_hook("task-001")
        # Should not raise
        hook({
            "status": "downloading",
            "downloaded_bytes": 50_000_000,
            "total_bytes": 100_000_000,
            "speed": 1_000_000,
            "eta": 50,
        })
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_progress.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/core/progress.py
import asyncio
from collections.abc import Callable, Awaitable
from src.models.download import DownloadProgress

ProgressCallback = Callable[[str, DownloadProgress], Awaitable[None]]


class ProgressTracker:
    def __init__(self):
        self._listeners: list[ProgressCallback] = []

    def register(self, callback: ProgressCallback) -> None:
        self._listeners.append(callback)

    def unregister(self, callback: ProgressCallback) -> None:
        self._listeners = [cb for cb in self._listeners if cb is not callback]

    async def broadcast(self, task_id: str, progress: DownloadProgress) -> None:
        for cb in self._listeners[:]:
            try:
                await cb(task_id, progress)
            except Exception:
                pass

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
            asyncio.get_event_loop().create_task(self.broadcast(task_id, progress))
        return hook
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_progress.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/progress.py backend/tests/test_core/test_progress.py
git commit -m "feat(core): add progress tracker with WebSocket broadcast and yt-dlp hook"
```

---

## Task 11: Settings Persistence

**Files:**
- Create: `backend/src/config.py`
- Modify: `backend/tests/test_models/test_settings.py`

- [ ] **Step 1: Write failing tests**

Append to `backend/tests/test_models/test_settings.py`:

```python
import os
import json
import tempfile
from src.config import SettingsManager


class TestSettingsManager:
    def test_load_defaults_when_no_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            mgr = SettingsManager(path)
            settings = mgr.load()
            assert settings.default_quality == "best"
            assert settings.max_concurrent_downloads == 3

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            mgr = SettingsManager(path)
            settings = mgr.load()
            settings.download_dir = "/custom/path"
            settings.proxy = "http://127.0.0.1:7890"
            mgr.save(settings)

            loaded = mgr.load()
            assert loaded.download_dir == "/custom/path"
            assert loaded.proxy == "http://127.0.0.1:7890"

    def test_update_settings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "settings.json")
            mgr = SettingsManager(path)
            updated = mgr.update({"default_quality": "1080p", "language": "en"})
            assert updated.default_quality == "1080p"
            assert updated.language == "en"
            # Verify persisted
            loaded = mgr.load()
            assert loaded.default_quality == "1080p"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_models/test_settings.py::TestSettingsManager -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/config.py
import json
import os
from src.models.settings import AppSettings


class SettingsManager:
    def __init__(self, path: str):
        self._path = path

    def load(self) -> AppSettings:
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppSettings(**data)
        return AppSettings()

    def save(self, settings: AppSettings) -> None:
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(settings.model_dump(), f, ensure_ascii=False, indent=2)

    def update(self, data: dict) -> AppSettings:
        settings = self.load()
        updated = settings.model_copy(update=data)
        self.save(updated)
        return updated
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_models/test_settings.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/config.py backend/tests/test_models/test_settings.py
git commit -m "feat(config): add settings manager with JSON persistence"
```

---

## Task 12: FastAPI App + Health Endpoint

**Files:**
- Create: `backend/src/main.py`
- Create: `backend/src/api/router.py`
- Create: `backend/src/api/health.py`
- Create: `backend/tests/test_api/test_health.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_health.py
import pytest


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_includes_version(self, client):
        response = await client.get("/health")
        data = response.json()
        assert "version" in data
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_health.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/api/health.py
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
```

```python
# backend/src/api/router.py
from fastapi import APIRouter
from src.api.health import router as health_router
from src.api.video import router as video_router
from src.api.playlist import router as playlist_router
from src.api.download import router as download_router
from src.api.settings import router as settings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(video_router, prefix="/api/v1")
api_router.include_router(playlist_router, prefix="/api/v1")
api_router.include_router(download_router, prefix="/api/v1")
api_router.include_router(settings_router, prefix="/api/v1")
```

```python
# backend/src/main.py
import sys
import uvicorn
from fastapi import FastAPI
from src.api.router import api_router

app = FastAPI(title="Youtuber Backend", version="0.1.0")
app.include_router(api_router)


def main():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    print(f"PORT={port}", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_health.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/main.py backend/src/api/router.py backend/src/api/health.py backend/tests/test_api/test_health.py
git commit -m "feat(api): add FastAPI app with health endpoint and router setup"
```

---

## Task 13: API — Video Info Endpoint

**Files:**
- Create: `backend/src/api/video.py`
- Create: `backend/tests/test_api/test_video.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_video.py
import pytest
from unittest.mock import patch, MagicMock


class TestVideoInfoEndpoint:
    @pytest.mark.asyncio
    async def test_get_video_info(self, client):
        mock_info = MagicMock()
        mock_info.model_dump.return_value = {
            "id": "test",
            "title": "Test Video",
            "duration": 60,
            "uploader": "User",
            "thumbnail": "https://example.com/t.jpg",
            "webpage_url": "https://youtube.com/watch?v=test",
            "formats": [],
            "subtitles": [],
        }
        with patch("src.api.video._wrapper") as mock_wrapper:
            mock_wrapper.extract_info.return_value = mock_info
            response = await client.post(
                "/api/v1/video/info",
                json={"url": "https://www.youtube.com/watch?v=test"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test"
        assert data["title"] == "Test Video"

    @pytest.mark.asyncio
    async def test_video_info_invalid_url(self, client):
        response = await client.post(
            "/api/v1/video/info",
            json={"url": "https://example.com/not-youtube"},
        )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_video_info_empty_url(self, client):
        response = await client.post(
            "/api/v1/video/info",
            json={"url": ""},
        )
        assert response.status_code == 400
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_video.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_video.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/video.py backend/tests/test_api/test_video.py
git commit -m "feat(api): add POST /api/v1/video/info endpoint"
```

---

## Task 14: API — Playlist Info Endpoint

**Files:**
- Create: `backend/src/api/playlist.py`
- Create: `backend/tests/test_api/test_playlist.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_playlist.py
import pytest
from unittest.mock import patch, MagicMock


class TestPlaylistInfoEndpoint:
    @pytest.mark.asyncio
    async def test_get_playlist_info(self, client):
        mock_info = MagicMock()
        mock_info.model_dump.return_value = {
            "id": "PLtest",
            "title": "Test Playlist",
            "uploader": "User",
            "video_count": 2,
            "videos": [
                {"id": "v1", "title": "V1", "duration": 60, "thumbnail": "", "url": ""},
                {"id": "v2", "title": "V2", "duration": 90, "thumbnail": "", "url": ""},
            ],
            "page": 1,
            "total_pages": 1,
        }
        with patch("src.api.playlist._wrapper") as mock_wrapper:
            mock_wrapper.extract_playlist.return_value = mock_info
            response = await client.post(
                "/api/v1/playlist/info",
                json={"url": "https://www.youtube.com/playlist?list=PLtest"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "PLtest"
        assert data["video_count"] == 2

    @pytest.mark.asyncio
    async def test_playlist_info_with_pagination(self, client):
        mock_info = MagicMock()
        mock_info.model_dump.return_value = {
            "id": "PLbig",
            "title": "Big",
            "uploader": "User",
            "video_count": 100,
            "videos": [],
            "page": 2,
            "total_pages": 4,
        }
        with patch("src.api.playlist._wrapper") as mock_wrapper:
            mock_wrapper.extract_playlist.return_value = mock_info
            response = await client.post(
                "/api/v1/playlist/info",
                json={"url": "https://youtube.com/playlist?list=PLbig", "page": 2, "page_size": 25},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["total_pages"] == 4

    @pytest.mark.asyncio
    async def test_playlist_info_invalid_url(self, client):
        response = await client.post(
            "/api/v1/playlist/info",
            json={"url": "https://example.com/not-playlist"},
        )
        assert response.status_code == 400
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_playlist.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/api/playlist.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.core.url_detector import detect_url_type, UrlType
from src.core.ytdl_wrapper import YtdlWrapper

router = APIRouter()
_wrapper = YtdlWrapper()


class PlaylistInfoRequest(BaseModel):
    url: str
    page: int = 1
    page_size: int = 50


@router.post("/playlist/info")
async def playlist_info(req: PlaylistInfoRequest):
    try:
        result = detect_url_type(req.url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if result.type not in (UrlType.PLAYLIST, UrlType.VIDEO):
        raise HTTPException(status_code=400, detail="URL 不是播放列表或频道")
    try:
        info = _wrapper.extract_playlist(req.url, page=req.page, page_size=req.page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return info.model_dump()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_playlist.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/playlist.py backend/tests/test_api/test_playlist.py
git commit -m "feat(api): add POST /api/v1/playlist/info endpoint with pagination"
```

---

## Task 15: API — Download Endpoints (queue, pause, resume, cancel)

**Files:**
- Create: `backend/src/api/download.py`
- Create: `backend/tests/test_api/test_download.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_download.py
import pytest


class TestDownloadEndpoints:
    @pytest.mark.asyncio
    async def test_start_download(self, client):
        response = await client.post(
            "/api/v1/download",
            json={
                "url": "https://www.youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test Video",
                "format_id": "22",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "waiting"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_get_download_queue(self, client):
        await client.post(
            "/api/v1/download",
            json={
                "url": "https://youtube.com/watch?v=a",
                "video_id": "a",
                "title": "A",
                "format_id": "22",
            },
        )
        response = await client.get("/api/v1/download/queue")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_pause_download(self, client):
        resp = await client.post(
            "/api/v1/download",
            json={
                "url": "https://youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test",
                "format_id": "22",
            },
        )
        task_id = resp.json()["id"]
        response = await client.post(f"/api/v1/download/{task_id}/pause")
        assert response.status_code == 200
        assert response.json()["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_download(self, client):
        resp = await client.post(
            "/api/v1/download",
            json={
                "url": "https://youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test",
                "format_id": "22",
            },
        )
        task_id = resp.json()["id"]
        await client.post(f"/api/v1/download/{task_id}/pause")
        response = await client.post(f"/api/v1/download/{task_id}/resume")
        assert response.status_code == 200
        assert response.json()["status"] == "waiting"

    @pytest.mark.asyncio
    async def test_cancel_download(self, client):
        resp = await client.post(
            "/api/v1/download",
            json={
                "url": "https://youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test",
                "format_id": "22",
            },
        )
        task_id = resp.json()["id"]
        response = await client.post(f"/api/v1/download/{task_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, client):
        response = await client.post("/api/v1/download/nonexistent/cancel")
        assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_download.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_download.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/download.py backend/tests/test_api/test_download.py
git commit -m "feat(api): add download endpoints (start, queue, pause, resume, cancel)"
```

---

## Task 16: API — Settings Endpoint

**Files:**
- Create: `backend/src/api/settings.py`
- Create: `backend/tests/test_api/test_settings.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_settings.py
import pytest
import tempfile
import os


class TestSettingsEndpoints:
    @pytest.mark.asyncio
    async def test_get_settings(self, client):
        response = await client.get("/api/v1/settings")
        assert response.status_code == 200
        data = response.json()
        assert "download_dir" in data
        assert "default_quality" in data
        assert "proxy" in data
        assert "max_concurrent_downloads" in data
        assert "language" in data

    @pytest.mark.asyncio
    async def test_update_settings(self, client):
        response = await client.put(
            "/api/v1/settings",
            json={"default_quality": "1080p", "language": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_quality"] == "1080p"
        assert data["language"] == "en"

    @pytest.mark.asyncio
    async def test_update_settings_partial(self, client):
        # Get current settings
        resp = await client.get("/api/v1/settings")
        original_proxy = resp.json()["proxy"]
        # Update only quality
        response = await client.put(
            "/api/v1/settings",
            json={"default_quality": "720p"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_quality"] == "720p"
        assert data["proxy"] == original_proxy
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_settings.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/api/settings.py
import os
import tempfile
from fastapi import APIRouter
from pydantic import BaseModel
from src.config import SettingsManager

router = APIRouter()

_settings_path = os.path.join(tempfile.gettempdir(), "youtuber_settings.json")
_mgr = SettingsManager(_settings_path)


class SettingsUpdateRequest(BaseModel):
    download_dir: str | None = None
    default_quality: str | None = None
    proxy: str | None = None
    max_concurrent_downloads: int | None = None
    language: str | None = None


@router.get("/settings")
async def get_settings():
    return _mgr.load().model_dump()


@router.put("/settings")
async def update_settings(req: SettingsUpdateRequest):
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = _mgr.update(data)
    return updated.model_dump()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_settings.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/settings.py backend/tests/test_api/test_settings.py
git commit -m "feat(api): add GET/PUT /api/v1/settings endpoints"
```

---

## Task 17: API — WebSocket Endpoint

**Files:**
- Create: `backend/src/api/ws.py`
- Create: `backend/tests/test_api/test_ws.py`

- [ ] **Step 1: Write failing tests**

```python
# backend/tests/test_api/test_ws.py
import pytest
from src.models.download import DownloadProgress


class TestWebSocketEndpoint:
    @pytest.mark.asyncio
    async def test_websocket_connect(self, client):
        async with client.websocket_connect("/ws") as ws:
            # Should connect without error
            assert ws is not None

    @pytest.mark.asyncio
    async def test_websocket_receives_progress(self, client):
        from src.main import app
        from src.core.progress import ProgressTracker

        # Access the progress tracker from the app state
        async with client.websocket_connect("/ws") as ws:
            # Simulate a progress broadcast
            tracker = app.state.progress_tracker
            progress = DownloadProgress(
                percent=50.0,
                speed=1_000_000,
                downloaded_bytes=50_000_000,
                total_bytes=100_000_000,
                eta=50,
            )
            await tracker.broadcast("task-001", progress)
            data = await ws.receive_json()
            assert data["task_id"] == "task-001"
            assert data["progress"]["percent"] == 50.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_api/test_ws.py -v`
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/api/ws.py
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.models.download import DownloadProgress

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
```

Update `backend/src/main.py` to initialize progress tracker:

```python
# backend/src/main.py
import sys
import uvicorn
from fastapi import FastAPI
from src.api.router import api_router
from src.core.progress import ProgressTracker

app = FastAPI(title="Youtuber Backend", version="0.1.0")
app.state.progress_tracker = ProgressTracker()
app.include_router(api_router)


def main():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    print(f"PORT={port}", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_api/test_ws.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/api/ws.py backend/src/main.py backend/tests/test_api/test_ws.py
git commit -m "feat(api): add WebSocket endpoint for real-time progress"
```

---

## Task 18: Integration — Wire Download Manager to yt-dlp + Progress

**Files:**
- Modify: `backend/src/core/download_mgr.py`
- Modify: `backend/src/api/download.py`
- Modify: `backend/tests/test_core/test_download_mgr.py`

- [ ] **Step 1: Write failing tests**

Append to `backend/tests/test_core/test_download_mgr.py`:

```python
class TestDownloadManagerExecution:
    @pytest.mark.asyncio
    async def test_execute_download_calls_ytdl(self, mgr):
        from src.core.progress import ProgressTracker
        tracker = ProgressTracker()
        mgr.set_progress_tracker(tracker)

        with patch("src.core.download_mgr.YtdlWrapper") as MockWrapper:
            mock_instance = MagicMock()
            MockWrapper.return_value = mock_instance

            task = mgr.add_task(
                url="https://youtube.com/watch?v=test",
                video_id="test",
                title="Test",
                format_id="22",
            )
            # Execute should call ytdl download
            await mgr.execute_task(task.id)
            mock_instance.download.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_updates_status_to_completed(self, mgr):
        from src.core.progress import ProgressTracker
        tracker = ProgressTracker()
        mgr.set_progress_tracker(tracker)

        with patch("src.core.download_mgr.YtdlWrapper") as MockWrapper:
            mock_instance = MagicMock()
            mock_instance.download.return_value = "/downloads/test.mp4"
            MockWrapper.return_value = mock_instance

            task = mgr.add_task(
                url="https://youtube.com/watch?v=test",
                video_id="test",
                title="Test",
                format_id="22",
            )
            await mgr.execute_task(task.id)
            updated = mgr.get_task(task.id)
            assert updated.status == DownloadStatus.COMPLETED
            assert updated.filepath == "/downloads/test.mp4"

    @pytest.mark.asyncio
    async def test_execute_handles_failure(self, mgr):
        from src.core.progress import ProgressTracker
        tracker = ProgressTracker()
        mgr.set_progress_tracker(tracker)

        with patch("src.core.download_mgr.YtdlWrapper") as MockWrapper:
            mock_instance = MagicMock()
            mock_instance.download.side_effect = Exception("Network error")
            MockWrapper.return_value = mock_instance

            task = mgr.add_task(
                url="https://youtube.com/watch?v=test",
                video_id="test",
                title="Test",
                format_id="22",
            )
            await mgr.execute_task(task.id)
            updated = mgr.get_task(task.id)
            assert updated.status == DownloadStatus.FAILED
            assert "Network error" in updated.error
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_core/test_download_mgr.py::TestDownloadManagerExecution -v`
Expected: FAIL — `AttributeError: 'DownloadManager' object has no attribute 'set_progress_tracker'`

- [ ] **Step 3: Write minimal implementation**

Add to `backend/src/core/ytdl_wrapper.py`:

```python
    def download(self, url: str, format_id: str, output_dir: str, progress_hook: callable = None) -> str:
        opts = self._base_opts()
        opts["format"] = format_id
        opts["outtmpl"] = os.path.join(output_dir, "%(title)s.%(ext)s")
        if progress_hook:
            opts["progress_hooks"] = [progress_hook]
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename
```

Add `import os` at top of `ytdl_wrapper.py`.

Add to `backend/src/core/download_mgr.py`:

```python
from src.core.ytdl_wrapper import YtdlWrapper
from src.core.progress import ProgressTracker
from src.models.download import DownloadStatus

# Add to DownloadManager class:
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_core/test_download_mgr.py -v`
Expected: PASS (11 tests)

- [ ] **Step 5: Commit**

```bash
git add backend/src/core/download_mgr.py backend/src/core/ytdl_wrapper.py backend/tests/test_core/test_download_mgr.py
git commit -m "feat(core): wire download manager to yt-dlp with progress hooks"
```

---

## Task 19: Full Test Suite Run + Refactoring

**Files:**
- Modify: all backend files as needed

- [ ] **Step 1: Run full test suite**

Run: `cd backend && python -m pytest tests/ -v --tb=short`
Expected: All tests pass

- [ ] **Step 2: Run coverage report**

Run: `cd backend && python -m pytest tests/ --cov=src --cov-report=term-missing`
Expected: Review coverage gaps

- [ ] **Step 3: Refactor — fix any code smells, unused imports, inconsistent naming**

- [ ] **Step 4: Run tests again to verify refactoring didn't break anything**

Run: `cd backend && python -m pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 5: Commit**

```bash
git add backend/
git commit -m "refactor: clean up backend code after full test suite validation"
```

---

## Task 20: Backend Smoke Test — Manual Verification

**Files:**
- No file changes

- [ ] **Step 1: Start the backend server**

Run: `cd backend && python -m src.main`
Expected: `PORT=xxxxx` printed, server starts

- [ ] **Step 2: Test health endpoint**

Run: `curl http://127.0.0.1:{port}/health`
Expected: `{"status":"ok","version":"0.1.0"}`

- [ ] **Step 3: Test video info endpoint with a real YouTube URL**

Run: `curl -X POST http://127.0.0.1:{port}/api/v1/video/info -H "Content-Type: application/json" -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'`
Expected: JSON with video title, formats, subtitles

- [ ] **Step 4: Test settings endpoint**

Run: `curl http://127.0.0.1:{port}/api/v1/settings`
Expected: JSON with settings

- [ ] **Step 5: Stop the server (Ctrl+C)**

- [ ] **Step 6: Commit any fixes**

```bash
git add backend/
git commit -m "fix: address issues found during smoke testing"
```
