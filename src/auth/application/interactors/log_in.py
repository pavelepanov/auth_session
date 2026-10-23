from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from unicodedata import normalize

from auth.application.errors import AlreadyAuthenticatedError, InvalidCredentialsError
from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.password_hasher import PasswordHasher
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.session_id_generator import SessionIdGenerator
from auth.application.interfaces.session_token_generator import SessionTokenGenerator
from auth.application.interfaces.session_token_hasher import SessionTokenHasher
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.session import create_session
from auth.domain.entities.user import RawPassword, User, UserEmail
from auth.entrypoint.config import SessionConfig


@dataclass
class LogInRequest:
    email: str
    raw_password: str


class LogInInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        session_data_gateway: SessionDataGateway,
        client_session_transport: ClientSessionTransport,
        session_id_generator: SessionIdGenerator,
        session_token_generator: SessionTokenGenerator,
        session_token_hasher: SessionTokenHasher,
        password_hasher: PasswordHasher,
        session_config: SessionConfig,
        transaction_manager: TransactionManager,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._session_data_gateway = session_data_gateway
        self._client_session_transport = client_session_transport
        self._session_id_generator = session_id_generator
        self._session_token_generator = session_token_generator
        self._session_token_hasher = session_token_hasher
        self._password_hasher = password_hasher
        self._session_config = session_config
        self._transaction_manager = transaction_manager

    async def __call__(self, request_data: LogInRequest) -> None:
        current_user = await self._identity_provider.get_current_user()
        if current_user is not None:
            raise AlreadyAuthenticatedError()

        email: UserEmail = UserEmail(request_data.email.strip().lower())
        raw_password: RawPassword = RawPassword(
            normalize("NFC", request_data.raw_password)
        )

        if not check_valid_raw_password(raw_password):
            raise InvalidCredentialsError()

        user: User | None = await self._user_data_gateway.read_by_email(email=email)
        if user is None:
            raise InvalidCredentialsError()

        if not user.is_active:
            raise InvalidCredentialsError()

        if not self._password_hasher.is_password_valid(
            user=user, raw_password=raw_password
        ):
            raise InvalidCredentialsError()

        session_token = self._session_token_generator.generate()
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self._session_config.expiration_minutes
        )
        session = create_session(
            id=self._session_id_generator(),
            token_hash=self._session_token_hasher.hash(session_token),
            user_id=user.id,
            expires_at=expires_at,
        )

        await self._session_data_gateway.add(session)

        await self._transaction_manager.commit()
        await self._client_session_transport.set_session(session_token)
