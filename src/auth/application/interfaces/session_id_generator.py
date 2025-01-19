from typing import Protocol

from auth.domain.entities.session import SessionId


class SessionIdGenerator(Protocol):
    def __call__(self) -> SessionId: ...
