import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# ── Auth override for tests ──────────────────────────────────────────────────
# All data routes depend on get_current_user (Keycloak JWKS verification).
# In tests we replace it with a stub that returns a synthetic user payload,
# so tests run without a live Keycloak instance.

_TEST_USER = {
    "sub": "test-user-id",
    "preferred_username": "testuser",
    "email": "testuser@example.com",
    "realm_access": {"roles": ["admin"]},
}


async def _override_get_current_user() -> dict:
    return _TEST_USER


def _apply_auth_override(app):
    from app.core.security import get_current_user

    app.dependency_overrides[get_current_user] = _override_get_current_user
    return app


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(params=["asyncio"])
def anyio_backend(request):
    return request.param


@pytest_asyncio.fixture(scope="session")
async def client():
    from app.main import app

    _apply_auth_override(app)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c
