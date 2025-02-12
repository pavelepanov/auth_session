from dataclasses import dataclass
from datetime import datetime
from typing import NewType

from auth.domain.entities.user import UserId

SessionId = NewType("SessionId", str)


@dataclass
class Session:
    id: SessionId
    expiration: datetime
    user_id: UserId


def create_session(
    id: SessionId,
    expiration: datetime,
    user_id: UserId,
) -> Session:
    return Session(
        id=id,
        expiration=expiration,
        user_id=user_id,
    )
