from dataclasses import dataclass
from unicodedata import normalize
from uuid import UUID

from auth.application.errors import (
    AlreadyAuthenticatedError,
    InvalidPasswordError,
    UserEmailAlreadyExistsError,
)
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.password_hasher import PasswordHasher
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.application.validators.check_raw_password import check_valid_raw_password
from auth.domain.entities.user import (
    PasswordHash,
    RawPassword,
    User,
    UserEmail,
    UserId,
    UserRoleEnum,
    create_user,
)


@dataclass
class SignUpRequest:
    email: str
    raw_password: str


@dataclass
class SignUpResponse:
    id: UUID


class SignUpInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_data_gateway: UserDataGateway,
        transaction_manager: TransactionManager,
        password_hasher: PasswordHasher,
        user_id_generator: UserIdGenerator,
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._transaction_manager = transaction_manager
        self._password_hasher = password_hasher
        self._user_id_generator = user_id_generator

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        current_user = await self._identity_provider.get_current_user()
        if current_user is not None:
            raise AlreadyAuthenticatedError()

        user_id: UserId = self._user_id_generator()
        email: UserEmail = UserEmail(request_data.email.strip().lower())
        raw_password: RawPassword = RawPassword(
            normalize("NFC", request_data.raw_password)
        )
        existing_user: User | None = await self._user_data_gateway.read_by_email(
            email=email
        )

        if existing_user is not None:
            raise UserEmailAlreadyExistsError()

        is_valid_raw_password: bool = check_valid_raw_password(raw_password)
        if not is_valid_raw_password:
            raise InvalidPasswordError()

        password_hash: PasswordHash = self._password_hasher.hash(
            raw_password=raw_password
        )
        user_role = await self._user_data_gateway.get_role_by_value(UserRoleEnum.USER)
        user: User = create_user(
            id=user_id,
            email=email,
            password_hash=password_hash,
            roles=[user_role],
        )

        await self._user_data_gateway.add(user)
        await self._transaction_manager.commit()

        return SignUpResponse(id=user.id)
