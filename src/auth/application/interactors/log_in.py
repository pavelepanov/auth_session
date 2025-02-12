from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from auth.application.errors import AuthenticationError, DoesNotExists, LogInError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.password_hasher import PasswordHasher
from auth.application.interfaces.request_manager import RequestManager
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import Session, SessionId, create_session
from auth.domain.entities.user import RawPassword, User, UserName
from auth.entrypoint.config import SessionConfig


@dataclass
class LogInRequest:
    username: str
    raw_password: str


class LogInInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        session_data_gateway: SessionDataGateway,
        request_manager: RequestManager,
        session_id_generator: SessionIdGenerator,
        password_hasher: PasswordHasher,
        session_config: SessionConfig,
        transaction_manager: TransactionManager,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._session_data_gateway = session_data_gateway
        self._request_manager = request_manager
        self._session_id_generator = session_id_generator
        self._password_hasher = password_hasher
        self._session_config = session_config
        self._transaction_manager = transaction_manager

    async def __call__(self, request_data: LogInRequest) -> None:
        is_authenticated: bool = await self._identity_provider.is_authenticated()
        if is_authenticated:
            raise LogInError("You are already authenticated.")

        username: UserName = UserName(request_data.username)
        raw_password: RawPassword = RawPassword(request_data.raw_password)

        user: User | None = await self._user_data_gateway.read_by_username(
            username=username
        )
        if user is None:
            raise DoesNotExists("User does not exists by username.")

        if not self._password_hasher.is_password_valid(
            user=user, raw_password=raw_password
        ):
            raise AuthenticationError("Invalid password.")

        if not user.is_active:
            raise AuthenticationError("Your account is not active.")

        session_id: SessionId = self._session_id_generator()
        session_expiration: datetime = datetime.now(timezone.utc) + timedelta(
            minutes=self._session_config.expiration_minutes
        )
        session: Session = create_session(
            id=session_id, expiration=session_expiration, user_id=user.id
        )

        await self._session_data_gateway.add(session)

        self._request_manager.add_session_id_to_request(session_id=session.id)

        await self._transaction_manager.commit()
