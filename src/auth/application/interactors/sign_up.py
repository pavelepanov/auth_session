from dataclasses import dataclass
from uuid import UUID

from auth.application.errors import AlreadyExists, AuthenticationError, InvalidPassword
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.user import PasswordHash, RawPassword, User, UserId, UserName
from auth.domain.interfaces.password_hasher import PasswordHasher
from auth.domain.services.user import UserService


@dataclass
class SignUpRequest:
    username: str
    raw_password: str


@dataclass
class SignUpResponse:
    id: UUID


class SignUpInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        user_service: UserService,
        transaction_manager: TransactionManager,
        password_hasher: PasswordHasher,
        user_id_generator: UserIdGenerator,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager
        self._password_hasher = password_hasher
        self._user_id_generator = user_id_generator

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        try:
            await self._identity_provider.get_current_user_id()
            raise AuthenticationError("You are already authenticated.")
        except AuthenticationError:
            ...

        user_id: UserId = self._user_id_generator()
        username: UserName = UserName(request_data.username)
        raw_password: RawPassword = RawPassword(request_data.raw_password)
        password_hash: PasswordHash = self._password_hasher.hash(
            raw_password=raw_password
        )

        user: User | None = await self._user_data_gateway.read_by_username(
            username=username
        )

        if user is not None:
            raise AlreadyExists("User with this username already exists.")

        is_valid_raw_password: bool = check_valid_raw_password(raw_password)

        if not is_valid_raw_password:
            raise InvalidPassword(
                "Password should have at least one number, one letter in lowercase,"
                "one letter in uppercase, consists of at least 8 symbols"
            )

        user: User = self._user_service.create_user(
            id=user_id, username=username, password_hash=password_hash
        )

        await self._user_data_gateway.add(user)

        await self._transaction_manager.commit()

        return SignUpResponse(id=user.id)
