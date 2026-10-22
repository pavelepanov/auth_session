from typing import Protocol

from auth.domain.entities.session import SessionToken, SessionTokenHash


class SessionTokenHasher(Protocol):
    def hash(self, token: SessionToken) -> SessionTokenHash: ...
