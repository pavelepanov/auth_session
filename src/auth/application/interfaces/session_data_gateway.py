from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId


class SessionDataGateway(Protocol):
    @abstractmethod
    async def add(self, session: Session) -> None: ...

    @abstractmethod
    async def get_user_id(self, session_id: SessionId) -> UserId | None: ...

    @abstractmethod
    async def delete_session(self) -> None: ...

    @abstractmethod
    async def prolong_expiration(self, session_id: SessionId) -> None: ...
