from abc import abstractmethod
from typing import Protocol

from auth.domain.user_role import UserRoleEnum


class IdentityProvider(Protocol):
    @abstractmethod
    async def is_authenticated(self) -> bool: ...

    @abstractmethod
    async def get_role(self) -> UserRoleEnum: ...
