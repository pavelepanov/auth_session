from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NewType
from uuid import UUID

from auth.domain.entities.user import UserId

SessionId = NewType("SessionId", UUID)
SessionToken = NewType("SessionToken", str)
SessionTokenHash = NewType("SessionTokenHash", str)


@dataclass
class Session:
    id: SessionId
    token_hash: SessionTokenHash
    user_id: UserId
    expires_at: datetime
    created_at: datetime


def create_session(
    id: SessionId,
    token_hash: SessionTokenHash,
    user_id: UserId,
    expires_at: datetime,
) -> Session:
    return Session(
        id=id,
        token_hash=token_hash,
        user_id=user_id,
        expires_at=expires_at,
        created_at=datetime.now(UTC),
    )
