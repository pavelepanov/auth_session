from dataclasses import dataclass

from auth.application.errors import AuthenticationError, DoesNotExists
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_manager import SessionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import Session
from auth.domain.entities.user import RawPassword, User, UserName
from auth.domain.services.session import SessionService
from auth.domain.services.user import UserService


@dataclass
class LogInRequest:
    username: str
    raw_password: str


class LogInInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        session_manager: SessionManager,
        session_service: SessionService,
        user_service: UserService,
        request_manager: RequestManager,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._session_manager = session_manager
        self._session_service = session_service
        self._user_service = user_service
        self._request_manager = request_manager

    async def __call__(self, request_data: LogInRequest) -> None:
        try:
            await self._identity_provider.get_current_user_id()
            raise AuthenticationError("You are already authenticated.")
        except AuthenticationError:
            ...

        username: UserName = UserName(request_data.username)
        raw_password: RawPassword = RawPassword(request_data.raw_password)

        user: User | None = await self._user_data_gateway.read_by_username(
            username=username
        )
        if user is None:
            raise DoesNotExists("User does not exists by username.")

        if not self._user_service.is_password_valid(
            user=user, raw_password=raw_password
        ):
            raise AuthenticationError("Invalid password.")

        if not user.is_active:
            raise AuthenticationError("Your account is not active.")

        session: Session = self._session_service.create_session(user_id=user.id)

        if self._session_manager.is_exists(session.id):
            raise AuthenticationError("Already authenticated.")

        await self._session_manager.add(session=session)

        await self._request_manager.add_session_id_to_request(session_id=session.id)
