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
