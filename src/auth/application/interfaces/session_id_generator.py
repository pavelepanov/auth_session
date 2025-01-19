from auth.domain.entities.session import SessionId
from typing import Protocol


class SessionIdGenerator(Protocol):
    def __call__(self) -> SessionId: ...
