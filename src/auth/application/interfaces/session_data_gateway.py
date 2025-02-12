from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId


class SessionDataGateway(Protocol):
    @abstractmethod
    async def add(self, session: Session) -> None: ...

    @abstractmethod
    async def read_by_id(self, session_id: SessionId) -> Session | None: ...

    @abstractmethod
    async def get_user_id(self, session_id: SessionId) -> UserId | None: ...

    @abstractmethod
    async def delete_session(self, session_id: SessionId) -> None: ...

    @abstractmethod
    async def prolong_expiration(
        self, session_id: SessionId, expiration: datetime
    ) -> None: ...
