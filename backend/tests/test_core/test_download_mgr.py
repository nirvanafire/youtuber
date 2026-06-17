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
