from typing import Optional
from fastapi import APIRouter, Cookie, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from core.config import FRONTEND_URL
from api.schemas.common import ReturnJSON

from services.github.github_service import GitHubService
from api.dependencies.auth import get_current_user
from database.models.user import UserModel

router = APIRouter(
    prefix="/github",
    tags=["GitHub Auth"],
)

github_service = GitHubService()


@router.get("/install")
def install_github_app(
    current_user: UserModel = Depends(get_current_user),
):
    url = github_service.get_installation_url(
        user_id=str(current_user.id),
    )

    return {
        "url": url,
    }


@router.get("/callback")
async def github_callback(
    installation_id: int,
    state: str,
):
    url = await github_service.handle_installation_callback(
        installation_id=installation_id,
        state=state,
    )

    return RedirectResponse(url)


@router.get("/repositories")
async def get_github_repositories(
    current_user: UserModel = Depends(
        get_current_user,
    ),
):
    if not current_user.github_access_token:
        return {
            "data": [],
        }

    repositories = await github_service.get_user_repositories(
        access_token=current_user.github_access_token,
    )

    return ReturnJSON(data=repositories, message="Repositories fetched successfully")
