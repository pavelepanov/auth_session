from dataclasses import dataclass

from auth.domain.entities.user import UserId
from typing import NewType

SessionId = NewType("SessionId", bytes)

@dataclass
class Session:
    id: SessionId
    user_id: UserId
