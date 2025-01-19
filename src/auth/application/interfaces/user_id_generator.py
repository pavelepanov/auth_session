from auth.domain.entities.user import UserId
from typing import Protocol

class UserIdGenerator(Protocol):
    def __call__(self) -> UserId: ...
