from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.models.user import UserModel
from services.auth.auth_service import AuthService
from services.auth.jwt_service import JWTService

security = HTTPBearer()

jwt_service = JWTService()
auth_service = AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserModel:
    try:
        payload = jwt_service.decode_token(
            credentials.credentials,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Access token has expired.")
    except jwt.InvalidTokenError as exc:
        raise HTTPException(401, f"Invalid access token: {exc}")

    try:
        user_id = UUID(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(401, f"Invalid token subject: {exc}")

    user = auth_service.get_current_user(user_id=user_id)

    if user is None:
        raise HTTPException(
            401,
            "User referenced by this token does not exist.",
        )

    return user
