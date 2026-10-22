from uuid import uuid4

from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.domain.entities.session import SessionId


class SessionIdGeneratorUuid(SessionIdGenerator):
    def __call__(self) -> SessionId:
        return SessionId(uuid4())
