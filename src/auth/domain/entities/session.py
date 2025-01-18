from dataclasses import dataclass
from typing import NewType

from auth.domain.entities.user import UserId

SessionId = NewType("SessionId", str)


@dataclass
class Session:
    id: SessionId
    user_id: UserId
