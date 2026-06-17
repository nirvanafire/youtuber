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
