# backend/tests/test_api/test_video.py
import pytest
from unittest.mock import patch, MagicMock


class TestVideoInfoEndpoint:
    @pytest.mark.asyncio
    async def test_get_video_info(self, client):
        mock_info = MagicMock()
        mock_info.model_dump.return_value = {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "duration": 60,
            "uploader": "User",
            "thumbnail": "https://example.com/t.jpg",
            "webpage_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "formats": [],
            "subtitles": [],
        }
        with patch("src.api.video._wrapper") as mock_wrapper:
            mock_wrapper.extract_info.return_value = mock_info
            response = await client.post(
                "/api/v1/video/info",
                json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "dQw4w9WgXcQ"
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
