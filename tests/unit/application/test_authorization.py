import pytest

from auth.application.authorization import has_permission
from auth.domain.entities.user import Permission, PermissionEnum, Role, UserRoleEnum


class TestHasPermission:
    @pytest.mark.parametrize(
        ("permissions", "required", "expected"),
        [
            pytest.param([], None, False, id="no_required_permission"),
            pytest.param(
                [], PermissionEnum.USER_HELLO_WORLD_VIEW, False, id="no_access"
            ),
            pytest.param(
                [PermissionEnum.USER_HELLO_WORLD_VIEW],
                PermissionEnum.USER_HELLO_WORLD_VIEW,
                True,
                id="allowed",
            ),
            pytest.param(
                [PermissionEnum.USER_HELLO_WORLD_VIEW],
                PermissionEnum.ADMIN_HELLO_WORLD_VIEW,
                False,
                id="wrong_permission",
            ),
        ],
    )
    def test_access_depends_on_permissions(
        self,
        permissions: list[PermissionEnum],
        required: PermissionEnum | None,
        expected: bool,
    ) -> None:
        roles = [
            Role(UserRoleEnum.USER, permissions=[Permission(p) for p in permissions])
        ]

        result = has_permission(roles, required)

        assert result is expected

    def test_permission_can_belong_to_any_role(self, admin_role: Role) -> None:
        roles = [Role(UserRoleEnum.USER), admin_role]

        result = has_permission(roles, PermissionEnum.ADMIN_HELLO_WORLD_VIEW)

        assert result is True

    def test_user_without_roles_has_no_access(self) -> None:
        assert has_permission([], PermissionEnum.USER_HELLO_WORLD_VIEW) is False
