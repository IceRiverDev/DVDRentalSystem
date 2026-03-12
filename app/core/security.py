import time

import httpx
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)

# ── JWKS cache (refreshed every hour) ──────────────────────────────────────
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0
_JWKS_TTL = 3600


async def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at
    if _jwks_cache is None or (time.time() - _jwks_fetched_at) > _JWKS_TTL:
        settings = get_settings()
        async with httpx.AsyncClient() as client:
            resp = await client.get(settings.KEYCLOAK_JWKS_URL, timeout=10)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_fetched_at = time.time()
    return _jwks_cache


async def decode_token(token: str) -> dict:
    settings = get_settings()
    try:
        jwks = await _get_jwks()
        return jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            issuer=settings.KEYCLOAK_ISSUER,
            options={"verify_aud": False},
        )
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid or expired token: {e}")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await decode_token(credentials.credentials)
