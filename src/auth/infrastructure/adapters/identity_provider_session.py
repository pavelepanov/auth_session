from datetime import UTC, datetime, timedelta

from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import Session
from auth.domain.entities.user import User
from auth.entrypoint.config import SessionConfig


class IdentityProviderSession(IdentityProvider):
    def __init__(
        self,
        session_data_gateway: SessionDataGateway,
        client_session_transport: ClientSessionTransport,
        session_token_hasher: SessionTokenHasher,
        session_config: SessionConfig,
        transaction_manager: TransactionManager,
        user_data_gateway: UserDataGateway,
    ):
        self._session_data_gateway = session_data_gateway
        self._client_session_transport = client_session_transport
        self._session_token_hasher = session_token_hasher
        self._session_config = session_config
        self._transaction_manager = transaction_manager
        self._user_data_gateway = user_data_gateway

    async def get_current_user(self) -> User | None:
        token = await self._client_session_transport.get_session()
        if token is None:
            return None

        token_hash = self._session_token_hasher.hash(token)
        session = await self._session_data_gateway.read_by_token_hash(token_hash)
        if session is None:
            await self._client_session_transport.clear_session()
            return None

        if session.expires_at <= datetime.now(UTC):
            await self._discard_session(session)
            return None

        user = await self._user_data_gateway.read_by_id(session.user_id)
        if user is None or not user.is_active:
            await self._discard_session(session)
            return None

        now = datetime.now(UTC)
        expiration_delta = timedelta(minutes=self._session_config.expiration_minutes)
        if session.expires_at - now <= expiration_delta / 2:
            await self._session_data_gateway.prolong(
                session, expires_at=now + expiration_delta
            )
            await self._transaction_manager.commit()
            await self._client_session_transport.set_session(token)

        return user

    async def _discard_session(self, session: Session) -> None:
        await self._session_data_gateway.delete(session)
        await self._transaction_manager.commit()
        await self._client_session_transport.clear_session()
