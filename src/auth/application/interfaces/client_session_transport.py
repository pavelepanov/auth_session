from typing import Protocol

from auth.domain.entities.session import SessionToken


class ClientSessionTransport(Protocol):
    async def get_session(self) -> SessionToken | None: ...

    async def set_session(self, session_token: SessionToken) -> None: ...

    async def clear_session(self) -> None: ...
