import secrets
from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException, status
from fastapi.responses import RedirectResponse
from core.config import FRONTEND_URL

from services.auth.github_oauth_service import GitHubOAuthService

router = APIRouter(
    prefix="/auth/github",
    tags=["GitHub Auth"],
)

github_oauth_service = GitHubOAuthService()


@router.get("")
async def github_login():
    state = secrets.token_urlsafe(32)

    authorization_url = github_oauth_service.get_authorization_url(
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
        secure=False,  # True in production
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

    access_token = await github_oauth_service.authenticate(code=code)

    return RedirectResponse(
        url=f"{FRONTEND_URL}/auth/github/callback" f"?access_token={access_token}",
    )
