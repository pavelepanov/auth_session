from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.session import SessionId
from auth.domain.entities.user import UserId


class SessionManager(Protocol):
    @abstractmethod
    async def add(self, user_id: UserId) -> SessionId: ...

    @abstractmethod
    async def prolong_expiration(self, session_id: SessionId) -> None: ...

    @abstractmethod
    async def check_existence(self, session_id: SessionId) -> bool: ...
