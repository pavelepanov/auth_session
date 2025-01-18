from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.session import SessionId


class RequestManager(Protocol):
    @abstractmethod
    def get_session_id_from_request(self) -> SessionId | None: ...

    @abstractmethod
    def add_session_id_to_request(self, session_id: SessionId) -> None: ...

    @abstractmethod
    def delete_session_from_request(self) -> None: ...
