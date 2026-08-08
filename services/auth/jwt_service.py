from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from core.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
)


class JWTService:
    def create_access_token(
        self,
        user_id: UUID,
    ) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": str(user_id),
            "iat": now,
            "exp": now
            + timedelta(
                minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
        }

        return jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM,
        )

    def decode_access_token(
        self,
        token: str,
    ) -> dict:
        return jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
