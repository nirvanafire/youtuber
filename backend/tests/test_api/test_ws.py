# backend/tests/test_api/test_ws.py
import pytest
from starlette.testclient import TestClient
from src.models.download import DownloadProgress


@pytest.fixture
def ws_client():
    from src.main import app
    client = TestClient(app)
    yield client
    client.close()


class TestWebSocketEndpoint:
    def test_websocket_connect(self, ws_client):
        with ws_client.websocket_connect("/ws") as ws:
            assert ws is not None

    def test_websocket_receives_progress(self, ws_client):
        from src.main import app

        with ws_client.websocket_connect("/ws") as ws:
            tracker = app.state.progress_tracker
            progress = DownloadProgress(
                percent=50.0,
                speed=1_000_000,
                downloaded_bytes=50_000_000,
                total_bytes=100_000_000,
                eta=50,
            )
            tracker.broadcast_sync("task-001", progress)
            data = ws.receive_json()
            assert data["task_id"] == "task-001"
            assert data["progress"]["percent"] == 50.0
