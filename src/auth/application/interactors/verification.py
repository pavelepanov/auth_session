from dataclasses import dataclass

from auth.application.errors import VerificationError
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.user import User, UserId


@dataclass
class VerificationRequest:
    user_id: UserId


class VerificationInteractor:
    def __init__(
        self,
        session_data_gateway: SessionDataGateway,
        transaction_manager: TransactionManager,
        user_data_gateway: UserDataGateway,
    ) -> None:
        self._session_data_gateway = session_data_gateway
        self._transaction_manager = transaction_manager
        self._user_data_gateway = user_data_gateway

    async def __call__(self, request_data: VerificationRequest) -> None:
        user: User = await self._user_data_gateway.read_by_id(request_data.user_id)

        if not user.is_verified:
            user.is_verified = True

            await self._transaction_manager.commit()

            return

        raise VerificationError("You are already verificated.")
