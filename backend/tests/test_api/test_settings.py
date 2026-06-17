# backend/tests/test_api/test_settings.py
import pytest


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
