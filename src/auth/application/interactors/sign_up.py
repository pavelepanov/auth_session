from dataclasses import dataclass
from uuid import UUID

from auth.application.errors import AuthenticationError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.user import PasswordHash, RawPassword, User, UserName
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
    ):
        self._identity_provider = identity_provider
        self._user_data_gateway = user_data_gateway
        self._user_service = user_service
        self._transaction_manager = transaction_manager
        self._password_hasher = password_hasher

    async def __call__(self, request_data: SignUpRequest) -> SignUpResponse:
        try:
            await self._identity_provider.get_current_user_id()
            raise AuthenticationError("You are already authenticated.")
        except AuthenticationError:
            ...

        username: UserName = UserName(request_data.username)
        raw_password: RawPassword = RawPassword(request_data.raw_password)
        password_hash: PasswordHash = self._password_hasher.hash(
            raw_password=raw_password
        )

        user: User = self._user_service.create_user(
            username=username, password_hash=password_hash
        )

        await self._user_data_gateway.add(user)

        await self._transaction_manager.commit()

        return SignUpResponse(id=user.id)
