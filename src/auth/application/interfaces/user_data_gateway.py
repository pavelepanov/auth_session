from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import User, UserId, UserName
from auth.domain.user_role import UserRoleEnum


class UserDataGateway(Protocol):
    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def read_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    async def read_by_username(self, username: UserName) -> User | None: ...

    @abstractmethod
    async def get_role(self, user_id: UserId) -> UserRoleEnum | None: ...
