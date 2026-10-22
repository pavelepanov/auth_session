from dataclasses import dataclass

from auth.application.authorization import has_permission
from auth.application.errors import AuthenticationError, PermissionDenied
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.domain.entities.user import PermissionEnum


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
        user = await self._identity_provider.get_current_user()
        if user is None:
            raise AuthenticationError("You are not authenticated.")

        if not has_permission(
            user_roles=user.roles,
            required_permission=PermissionEnum.ADMIN_HELLO_WORLD_VIEW,
        ):
            raise PermissionDenied("You do not have the required permission.")

        return AdminHelloWorldResponse(hello_world="hello world by admin")
