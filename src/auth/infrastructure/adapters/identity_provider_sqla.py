from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.session_manager import SessionManager
from auth.domain.entities.session import Session
from auth.domain.entities.user import UserId


class IdentityProviderSession(IdentityProvider):
    def __init__(
        self,
        session_manager: SessionManager,
    ):
        self._session_manager = session_manager

    async def get_current_user_id(self) -> UserId:
        session: Session = await self._session_manager.get_current_session()

        if session is None:
            raise AuthenticationError("Not authenticated.")

        self._session_manager.prolong_expiration(session)

        return session
