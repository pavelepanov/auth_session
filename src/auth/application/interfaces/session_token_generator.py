from typing import Protocol

from auth.domain.entities.session import SessionToken


class SessionTokenGenerator(Protocol):
    def generate(self) -> SessionToken: ...
