from auth.domain.entities.user import PermissionEnum, Role


def has_permission(
    user_roles: list[Role],
    required_permission: PermissionEnum | None = None,
) -> bool:
    if required_permission is None:
        return False

    return any(
        permission.value == required_permission
        for role in user_roles
        for permission in role.permissions
    )
