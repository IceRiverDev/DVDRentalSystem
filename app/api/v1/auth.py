import httpx
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status

from app.core.config import get_settings
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

_COOKIE = "dvd_refresh_token"


async def _keycloak_token(data: dict) -> dict:
    """POST to Keycloak token endpoint; raise 401 on failure."""
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            settings.keycloak_token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=resp.json().get("error_description", "Token request failed"),
        )
    return resp.json()


def _set_refresh_cookie(response: Response, refresh_token: str, max_age: int) -> None:
    response.set_cookie(
        key=_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=False,  # set True in production (HTTPS only)
        samesite="lax",
        max_age=max_age,
        path="/api/v1/auth",
    )


@router.post(
    "/callback", summary="Exchange PKCE code for tokens", include_in_schema=False
)
async def oidc_callback(request: Request, response: Response):
    """
    Receive the PKCE authorization code from the frontend, exchange it with
    Keycloak, store the refresh_token in an HttpOnly cookie, and return the
    access_token to the frontend.
    """
    settings = get_settings()
    body = await request.json()

    token_data = await _keycloak_token(
        {
            "grant_type": "authorization_code",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "code": body["code"],
            "code_verifier": body["code_verifier"],
            "redirect_uri": body["redirect_uri"],
        }
    )

    _set_refresh_cookie(
        response,
        token_data["refresh_token"],
        token_data.get("refresh_expires_in", 604800),
    )
    return {"access_token": token_data["access_token"]}


@router.post(
    "/refresh", summary="Silently refresh access token", include_in_schema=False
)
async def refresh_access_token(
    response: Response,
    dvd_refresh_token: str = Cookie(default=None),
):
    """
    Use the HttpOnly refresh_token cookie to obtain a new access_token.
    Also rotates the refresh_token cookie.
    """
    if not dvd_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token cookie"
        )

    settings = get_settings()
    token_data = await _keycloak_token(
        {
            "grant_type": "refresh_token",
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "refresh_token": dvd_refresh_token,
        }
    )

    _set_refresh_cookie(
        response,
        token_data["refresh_token"],
        token_data.get("refresh_expires_in", 604800),
    )
    return {"access_token": token_data["access_token"]}


@router.post(
    "/logout", summary="Logout and clear refresh token cookie", include_in_schema=False
)
async def logout(response: Response):
    """Clear the HttpOnly refresh_token cookie."""
    response.delete_cookie(key=_COOKIE, path="/api/v1/auth")
    return {"message": "Logged out"}


@router.get("/me", summary="Get current authenticated user")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "sub": current_user.get("sub"),
        "username": current_user.get("preferred_username"),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "roles": current_user.get("realm_access", {}).get("roles", []),
    }


@router.get("/token-info", summary="How to get a token", include_in_schema=True)
async def token_info():
    settings = get_settings()
    return {
        "token_url": f"{settings.KEYCLOAK_ISSUER}/protocol/openid-connect/token",
        "grant_type": "password",
        "example": {
            "client_id": settings.KEYCLOAK_CLIENT_ID,
            "username": "<your username>",
            "password": "<your password>",
            "grant_type": "password",
        },
    }
