from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.session_manager import SessionManager
from auth.domain.entities.session import SessionId
from auth.domain.entities.user import UserId


class IdentityProviderSession(IdentityProvider):
    def __init__(
        self,
        session_manager: SessionManager,
    ):
        self._session_manager = session_manager

    async def get_current_user_id(self) -> UserId:
        session_id: SessionId = self._session_manager.get_current_session_id()

        if session_id is None:
            raise AuthenticationError("Not authenticated.")

        is_exists_session: bool = await self._session_manager.is_exists(session_id)

        if not is_exists_session:
            await self._session_manager.delete_session()
            raise AuthenticationError("Not authenticated.")

        await self._session_manager.prolong_expiration(session_id)

        user_id: UserId = await self._session_manager.get_user_id(session_id)

        return user_id
