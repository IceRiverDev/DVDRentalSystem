import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.security import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class CallbackRequest(BaseModel):
    code: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.get("/github/url")
async def github_login_url():
    settings = get_settings()
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri=http://localhost:8080/auth/callback"
        f"&scope=read:user+user:email"
    )
    return {"url": url}


@router.post("/github/callback", response_model=TokenResponse)
async def github_callback(body: CallbackRequest):
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        token_resp = await client.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": body.code,
            },
            headers={"Accept": "application/json"},
            timeout=10,
        )
        token_data = token_resp.json()
        if "access_token" not in token_data:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="GitHub OAuth failed")

        # Get user info
        user_resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token_data['access_token']}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed to get GitHub user info")
        github_user = user_resp.json()

        # Fetch primary email if not public
        email = github_user.get("email")
        if not email:
            email_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {token_data['access_token']}",
                    "Accept": "application/vnd.github+json",
                },
                timeout=10,
            )
            if email_resp.status_code == 200:
                emails = email_resp.json()
                primary = next((e for e in emails if e.get("primary")), None)
                email = primary["email"] if primary else None

    user_info = {
        "github_id": github_user["id"],
        "login": github_user["login"],
        "name": github_user.get("name") or github_user["login"],
        "email": email,
        "avatar_url": github_user.get("avatar_url", ""),
    }
    token = create_access_token(user_info)
    return TokenResponse(access_token=token, user=user_info)


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user
