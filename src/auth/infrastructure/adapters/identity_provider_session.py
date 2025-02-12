from datetime import datetime, timedelta, timezone

from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import UserId
from auth.entrypoint.config import SessionConfig


class IdentityProviderSession(IdentityProvider):
    def __init__(
        self,
        session_data_gateway: SessionDataGateway,
        request_manager: RequestManager,
        session_config: SessionConfig,
        transaction_manager: TransactionManager,
    ):
        self._session_data_gateway = session_data_gateway
        self._request_manager = request_manager
        self._session_config = session_config
        self._transaction_manager = transaction_manager

    async def get_current_user_id(self) -> UserId:
        session_id: SessionId = self._session_data_gateway.get_current_session_id()

        if session_id is None:
            raise AuthenticationError("Not authenticated.")

        is_exists_session: bool = await self._session_data_gateway.is_exists(session_id)

        if not is_exists_session:
            await self._session_data_gateway.delete_session()
            self._request_manager.delete_session_from_request()
            raise AuthenticationError("Not authenticated.")

        await self._session_data_gateway.prolong_expiration(session_id)

        user_id: UserId = await self._session_data_gateway.get_user_id(session_id)

        return user_id

    async def is_authenticated(self) -> bool:
        session_id: SessionId = self._request_manager.get_session_id_from_request()

        if session_id is None:
            return False

        session: Session | None = await self._session_data_gateway.read_by_id(
            session_id=session_id
        )

        if session is None:
            return False

        if session.expiration < datetime.now(timezone.utc):
            await self._session_data_gateway.delete_session(session.id)
            self._request_manager.delete_session_from_request()

            await self._transaction_manager.commit()

            return False

        new_expiration: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=self._session_config.expiration_minutes
        )

        await self._session_data_gateway.prolong_expiration(
            session_id=session_id, expiration=new_expiration
        )

        await self._transaction_manager.commit()

        return True
