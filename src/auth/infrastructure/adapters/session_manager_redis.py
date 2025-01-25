from redis import Redis

from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_manager import SessionManager
from auth.domain.entities.session import Session, SessionId
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

    async def is_exists(self, session_id: SessionId) -> bool:
        is_exists = await self._client.exists(session_id)
        if is_exists == 1:
            return True
        return False

    async def get_current_session(self) -> Session | None:
        session_id: SessionId | None = (
            self._request_manager.get_session_id_from_request()
        )

        if session_id is None:
            return None

        session: Session = self._client.get(session_id)

        return session

    def delete_session(self) -> None:
        session_id: SessionId | None = (
            self._request_manager.get_session_id_from_request()
        )

        self._client.delete(session_id)
