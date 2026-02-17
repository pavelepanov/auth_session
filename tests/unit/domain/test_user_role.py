from auth.domain.user_role import UserRoleEnum, has_required_role


class TestHasRequiredRole:

    def test_admin_has_admin_access(self):
        result = has_required_role(
            user_role=UserRoleEnum.ADMIN,
            required_role=UserRoleEnum.ADMIN,
        )
        assert result is True

    def test_admin_has_user_access(self):
        result = has_required_role(
            user_role=UserRoleEnum.ADMIN,
            required_role=UserRoleEnum.USER,
        )
        assert result is True

    def test_user_has_user_access(self):
        result = has_required_role(
            user_role=UserRoleEnum.USER,
            required_role=UserRoleEnum.USER,
        )
        assert result is True

    def test_user_has_no_admin_access(self):
        result = has_required_role(
            user_role=UserRoleEnum.USER,
            required_role=UserRoleEnum.ADMIN,
        )
        assert result is False


class TestUserRoleEnum:

    def test_admin_value(self):
        assert UserRoleEnum.ADMIN == "admin"

    def test_user_value(self):
        assert UserRoleEnum.USER == "user"

    def test_role_is_str_enum(self):
        assert isinstance(UserRoleEnum.ADMIN, str)
        assert isinstance(UserRoleEnum.USER, str)
