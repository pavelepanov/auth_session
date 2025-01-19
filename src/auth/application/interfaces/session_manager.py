from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.session import Session, SessionId


class SessionManager(Protocol):
    @abstractmethod
    async def add(self, session: Session) -> None: ...

    @abstractmethod
    async def prolong_expiration(self, session_id: SessionId) -> None: ...

    @abstractmethod
    async def is_exists(self, session_id: SessionId) -> bool: ...

    @abstractmethod
    async def get_current_session(self) -> Session | None: ...

    @abstractmethod
    async def delete_session(self) -> None: ...
