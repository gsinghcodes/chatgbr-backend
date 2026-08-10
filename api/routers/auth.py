from fastapi import APIRouter, HTTPException, status, Depends

from api.schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
)
from api.schemas.common import ReturnJSON
from api.dependencies.auth import get_current_user
from services.auth.auth_service import AuthService
from database.models.user import UserModel

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

auth_service = AuthService()


@router.post(
    "/register",
    response_model=ReturnJSON,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    try:
        access_token = auth_service.register(
            email=request.email,
            password=request.password,
        )

        return ReturnJSON(
            message="User registered successfully.",
            data={
                "access_token": access_token,
                "token_type": "Bearer",
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=ReturnJSON,
)
def login(request: LoginRequest):
    try:
        access_token = auth_service.login(
            email=request.email,
            password=request.password,
        )

        return ReturnJSON(
            message="Login successful.",
            data={
                "access_token": access_token,
                "token_type": "Bearer",
            },
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )


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
        )
    except Exception as e:
        print(e)
