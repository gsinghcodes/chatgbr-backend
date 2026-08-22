import secrets
from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from core.config import FRONTEND_URL

from services.github.github_service import GitHubService

router = APIRouter(
    prefix="/auth/github",
    tags=["GitHub Auth"],
)

github_service = GitHubService()


@router.get("")
async def github_login():
    state = secrets.token_urlsafe(32)

    authorization_url = github_service.get_authorization_url(
        state=state,
    )

    response = RedirectResponse(
        url=authorization_url,
        status_code=status.HTTP_302_FOUND,
    )

    response.set_cookie(
        key="github_oauth_state",
        value=state,
        httponly=True,
        secure=True,  # True in production
        samesite="lax",
        max_age=600,
    )

    return response


@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    github_oauth_state: Optional[str] = Cookie(default=None),
):
    if not github_oauth_state:
        raise HTTPException(
            status_code=400,
            detail="GitHub OAuth state cookie is missing.",
        )

    if not secrets.compare_digest(
        state,
        github_oauth_state,
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub OAuth state.",
        )

    auth_result = await github_service.authenticate(code=code)

    response = RedirectResponse(
        url=f"{FRONTEND_URL}/auth/github/callback?access_token={auth_result['access_token']}",
    )

    response.set_cookie(
        key="refresh_token",
        value=auth_result["refresh_token"],
        httponly=True,
        secure=True,  # True in production — match your /login route
        samesite="lax",
        max_age=15 * 24 * 60 * 60,
    )

    response.delete_cookie(key="github_oauth_state")

    return response
