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
