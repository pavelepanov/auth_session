from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_manager import SessionManager


class LogOutInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        session_manager: SessionManager,
        request_manager: RequestManager,
    ) -> None:
        self._identity_provider = identity_provider
        self._session_manager = session_manager
        self._request_manager = request_manager

    async def __call__(self) -> None:
        await self._identity_provider.get_current_user_id()

        self._request_manager.delete_session_from_request()

        await self._session_manager.delete_session()
