from typing import Protocol

from auth.domain.entities.user import UserId


class UserIdGenerator(Protocol):
    def __call__(self) -> UserId: ...
