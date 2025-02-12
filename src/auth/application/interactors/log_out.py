from auth.application.errors import LogOutError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.domain.entities.session import SessionId


class LogOutInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        session_data_gateway: SessionDataGateway,
        request_manager: RequestManager,
        transaction_manager: TransactionManager,
    ) -> None:
        self._identity_provider = identity_provider
        self._session_data_gateway = session_data_gateway
        self._request_manager = request_manager
        self._transaction_manager = transaction_manager

    async def __call__(self) -> None:
        is_authenticated: bool = await self._identity_provider.is_authenticated()

        if not is_authenticated:
            raise LogOutError("You are not authenticated.")

        session_id: SessionId = self._request_manager.get_session_id_from_request()

        self._request_manager.delete_session_from_request()

        await self._session_data_gateway.delete_session(session_id=session_id)

        await self._transaction_manager.commit()
