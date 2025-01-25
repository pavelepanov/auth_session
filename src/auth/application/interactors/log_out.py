from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_manager import SessionManager
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import Session
from auth.domain.entities.user import UserId


class LogOutInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_mapper: UserDataGateway,
        session_manager: SessionManager,
        transaction_manager: TransactionManager,
        request_manager: RequestManager,
    ) -> None:
        self._identity_provider = identity_provider
        self._user_data_mapper = user_data_mapper
        self._session_manager = session_manager
        self._transaction_manager = transaction_manager
        self._request_manager = request_manager

    async def __call__(self) -> None:
        user_id: UserId = await self._identity_provider.get_current_user_id()

        if user_id is None:
            raise AuthenticationError("Not authenticated.")

        current_session: (
            Session | None
        ) = await self._session_manager.get_current_session()
        if current_session is None:
            raise AuthenticationError("Not authenticated.")

        self._request_manager.delete_session_from_request()

        self._session_manager.delete_session()
