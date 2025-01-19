from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import User, UserId, UserName


class UserDataGateway(Protocol):
    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def read_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def read_by_username(self, username: UserName) -> User | None: ...
