from abc import abstractmethod
from datetime import datetime
from typing import Protocol

from auth.domain.entities.session import Session, SessionTokenHash


class SessionDataGateway(Protocol):
    @abstractmethod
    async def add(self, session: Session) -> None: ...

    @abstractmethod
    async def read_by_token_hash(
        self, token_hash: SessionTokenHash
    ) -> Session | None: ...

    @abstractmethod
    async def delete(self, session: Session) -> None: ...

    @abstractmethod
    async def prolong(self, session: Session, expires_at: datetime) -> None: ...
