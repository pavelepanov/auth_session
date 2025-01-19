from auth.domain.entities.session import SessionId


class SessionIdGenerator:
    def __call__(self) -> SessionId: ...
