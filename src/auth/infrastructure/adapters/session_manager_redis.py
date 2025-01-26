from redis import Redis

from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_manager import SessionManager
from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId
from auth.entrypoint.config import RedisConfig


class SessionManagerRedis(SessionManager):
    def __init__(
        self, client: Redis, config: RedisConfig, request_manager: RequestManager
    ):
        self._client = client
        self._config = config
        self._request_manager = request_manager

    def add(self, session: Session) -> None:
        self._client.set(session.id, str(session.user_id), px=self._config.ttl)

    def prolong_expiration(self, session_id: SessionId) -> None:
        self._client.expire(session_id, self._config.ttl)

    def get_current_session_id(self) -> SessionId | None:
        session_id: SessionId | None = (
            self._request_manager.get_session_id_from_request()
        )

        if session_id is None:
            return None

        return session_id

    def delete_session(self) -> None:
        session_id: SessionId | None = (
            self._request_manager.get_session_id_from_request()
        )

        self._client.delete(session_id)

    def get_user_id(self, session_id: SessionId) -> UserId | None:
        user_id: UserId = self._client.get(session_id)

        if user_id is None:
            return None

        return user_id
