from datetime import datetime, timedelta, timezone

from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import Session, SessionId
from auth.domain.user_role import UserRoleEnum
from auth.entrypoint.config import SessionConfig


class IdentityProviderSession(IdentityProvider):
    """
    Повторение кода оправдано фактом:
    обновление срока истечения жизни сессии зависит от сценария.
    Это не нарушение DRY, это следование бизнес-сценариям.
    """

    def __init__(
        self,
        session_data_gateway: SessionDataGateway,
        request_manager: RequestManager,
        session_config: SessionConfig,
        transaction_manager: TransactionManager,
        user_data_gateway: UserDataGateway,
    ):
        self._session_data_gateway = session_data_gateway
        self._request_manager = request_manager
        self._session_config = session_config
        self._transaction_manager = transaction_manager
        self._user_data_gateway = user_data_gateway

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

    async def get_role(self) -> UserRoleEnum:
        session_id: SessionId = self._request_manager.get_session_id_from_request()

        if session_id is None:
            raise AuthenticationError("You are not authenticated.")

        session: Session | None = await self._session_data_gateway.read_by_id(
            session_id=session_id
        )

        if session is None:
            raise AuthenticationError("You are not authenticated.")

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

        role = await self._user_data_gateway.get_role(user_id=session.user_id)

        await self._transaction_manager.commit()

        return role
