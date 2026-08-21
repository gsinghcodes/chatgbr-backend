from fastapi import APIRouter, HTTPException, status, Depends, Cookie
from fastapi.responses import JSONResponse, Response
from typing import Optional

from api.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
)
from api.schemas.common import ReturnJSON
from api.dependencies.auth import get_current_user
from services.auth.auth_service import AuthService
from database.models.user import UserModel

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

auth_service = AuthService()


@router.post(
    "/register",
    response_model=ReturnJSON,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    data = auth_service.register(
        email=request.email,
        password=request.password,
    )

    response = JSONResponse(content=data, status_code=data["status"])

    if data["status"] == 200:
        response.set_cookie(
            key="refresh_token",
            value=data["data"]["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 24 * 60 * 60,
        )

    return response


@router.post(
    "/login",
    response_model=ReturnJSON,
)
def login(request: LoginRequest, response: Response):
    data = auth_service.login(
        email=request.email,
        password=request.password,
    )

    response = JSONResponse(content=data, status_code=data["status"])

    if data["status"] == 200:
        response.set_cookie(
            key="refresh_token",
            value=data["data"]["refresh_token"],
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=15 * 24 * 60 * 60,
        )

    return response


@router.post("/logout")
def logout(
    user: UserModel = Depends(get_current_user),
    refresh_token: Optional[str] = Cookie(default=None),
):
    data = auth_service.logout_user(user_id=user.id, token=refresh_token)

    response = JSONResponse(content=data, status_code=data["status"])

    response.delete_cookie(
        key="refresh_token", httponly=True, secure=False, samesite="lax"
    )

    return response


@router.post("/refresh")
def refresh_access_token(refresh_token: Optional[str] = Cookie(default=None)):
    data = auth_service.refresh_access_token(refresh_token)
    return JSONResponse(content=data, status_code=data["status"])


@router.get(
    "/me",
    response_model=ReturnJSON,
)
def me(
    current_user: UserModel = Depends(get_current_user),
):
    try:
        return ReturnJSON(
            message="Authenticated user fetched successfully.",
            data={
                "id": current_user.id,
                "email": current_user.email,
                "github_username": current_user.github_username,
                "avatar_url": current_user.avatar_url,
            },
            status=200,
        )
    except Exception as e:
        print(e)
