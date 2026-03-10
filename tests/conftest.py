import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport


@pytest.fixture(params=["asyncio"])
def anyio_backend(request):
    return request.param


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
