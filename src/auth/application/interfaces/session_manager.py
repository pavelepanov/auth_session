from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId


class SessionManager(Protocol):
    @abstractmethod
    def add(self, session: Session) -> None: ...

    @abstractmethod
    def prolong_expiration(self, session_id: SessionId) -> None: ...

    @abstractmethod
    def get_user_id(self, session_id: SessionId) -> UserId | None: ...

    @abstractmethod
    def get_current_session_id(self) -> SessionId | None: ...

    @abstractmethod
    def delete_session(self) -> None: ...
