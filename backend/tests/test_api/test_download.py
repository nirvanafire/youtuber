# backend/tests/test_api/test_download.py
import pytest


@pytest.fixture(autouse=True)
def _reset_download_manager():
    """Reset the module-level DownloadManager between tests."""
    from src.api.download import _manager, _tracker_initialized
    import src.api.download as mod
    _manager._tasks.clear()
    _manager._active_tasks.clear()
    _manager._interrupt_tasks.clear()
    _manager._auto_schedule = False
    mod._tracker_initialized = False
    yield
    _manager._tasks.clear()
    _manager._active_tasks.clear()
    _manager._interrupt_tasks.clear()
    _manager._auto_schedule = True


class TestDownloadEndpoints:
    @pytest.mark.asyncio
    async def test_start_download(self, client):
        response = await client.post(
            "/api/v1/download",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
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
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
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
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
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
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
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
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
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


class TestSubtitleDownloadEndpoint:
    @pytest.mark.asyncio
    async def test_start_subtitle_download(self, client):
        response = await client.post(
            "/api/v1/download/subtitle",
            json={
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "video_id": "dQw4w9WgXcQ",
                "title": "Test Video",
                "language": "en",
                "ext": "srt",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "waiting"
        assert data["format_id"] == "subtitle:en"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_subtitle_download_appears_in_queue(self, client):
        await client.post(
            "/api/v1/download/subtitle",
            json={
                "url": "https://youtube.com/watch?v=test",
                "video_id": "test",
                "title": "Test",
                "language": "zh",
                "ext": "srt",
            },
        )
        response = await client.get("/api/v1/download/queue")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["format_id"] == "subtitle:zh"
