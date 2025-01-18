from auth.domain.entities.session import SessionId


class StrSessionIdGenerator:
    def __call__(self) -> SessionId: ...
