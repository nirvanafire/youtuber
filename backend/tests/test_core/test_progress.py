# backend/tests/test_core/test_progress.py
import pytest
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
