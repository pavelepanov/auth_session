from dataclasses import dataclass

from auth.application.errors import UnauthenticatedError
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.domain.entities.user import PermissionEnum, UserEmail, UserId, UserRoleEnum


@dataclass
class GetMeResponse:
    id: UserId
    email: UserEmail
    is_active: bool
    roles: list[UserRoleEnum]
    permissions: list[PermissionEnum]


class GetMeInteractor:
    def __init__(self, identity_provider: IdentityProvider):
        self._identity_provider = identity_provider

    async def __call__(self) -> GetMeResponse:
        user = await self._identity_provider.get_current_user()
        if user is None:
            raise UnauthenticatedError()

        return GetMeResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            roles=[role.value for role in user.roles],
            permissions=list(
                {
                    permission.value
                    for role in user.roles
                    for permission in role.permissions
                }
            ),
        )
