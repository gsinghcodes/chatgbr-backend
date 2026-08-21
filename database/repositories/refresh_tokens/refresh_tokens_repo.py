from database.models.refresh_tokens import RefreshTokenModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID
from datetime import datetime, timezone


class RefreshTokensRepository:
    def create(self, instance: RefreshTokenModel, session: Session):
        session.add(instance)
        session.flush()

        return instance

    def get_by_token_hash(self, token_hash: str, session: Session):
        statement = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        )

        return session.execute(statement=statement).scalar_one_or_none()

    def get_active_by_token_hash(self, token_hash: str, session: Session):
        now = datetime.now(timezone.utc)
        statement = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.expires_at > now,
            RefreshTokenModel.revoked_at.is_(None),
        )
        return session.execute(statement=statement).scalar_one_or_none()

    def revoke_token_by_user(self, user_id: UUID, session: Session):
        now = datetime.now(timezone.utc)
        statement = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None)
        )
        tokens = session.execute(statement).scalars().all()
        if not tokens:
            return False
        for token in tokens:
            token.revoked_at = now
        return True

    def revoke_token_by_hash(self, user_id: UUID, token_hash: str, session: Session):
        now = datetime.now(timezone.utc)
        statement = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id,
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.revoked_at.is_(None),
        )
        token = session.execute(statement).scalar_one_or_none()
        if token:
            token.revoked_at = now
            return True
        return False
