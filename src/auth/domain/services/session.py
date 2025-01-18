from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId
from auth.domain.interfaces.str_session_id_generator import StrSessionIdGenerator


class SessionService:
    def __init__(
        self,
        session_id_generator: StrSessionIdGenerator,
    ):
        self.session_id_generator = session_id_generator

    def create_session(
        self,
        user_id: UserId,
    ):
        session_id: SessionId = self.session_id_generator()

        return Session(
            id=session_id,
            user_id=user_id,
        )
