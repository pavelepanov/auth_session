from dataclasses import dataclass

from auth.application.interfaces.identity_provider import IdentityProvider
from auth.domain.errors import AccessControlError
from auth.domain.user_role import UserRoleEnum, has_required_role


@dataclass
class AdminHelloWorldResponse:
    hello_world: str


class AdminHelloWorldInteractor:
    def __init__(
        self,
        identity_provider: IdentityProvider,
    ):
        self._identity_provider = identity_provider

    async def __call__(self) -> AdminHelloWorldResponse:
        user_role: UserRoleEnum = await self._identity_provider.get_role()

        if has_required_role(user_role=user_role, required_role=UserRoleEnum.ADMIN):
            return AdminHelloWorldResponse(hello_world="hello world by admin")

        raise AccessControlError("The required role does not exist.")
