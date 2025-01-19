from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId


class SessionService:
    def create_session(
        self,
        id: SessionId,
        user_id: UserId,
    ) -> Session:
        return Session(
            id=id,
            user_id=user_id,
        )
