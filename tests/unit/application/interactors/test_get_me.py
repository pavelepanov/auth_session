from unittest.mock import AsyncMock

import pytest

from auth.application.errors import UnauthenticatedError
from auth.application.interactors.get_me import GetMeInteractor
from auth.domain.entities.user import PermissionEnum, Role, User, UserRoleEnum


class TestGetMeInteractor:
    @pytest.fixture
    def interactor(self, mock_identity_provider: AsyncMock) -> GetMeInteractor:
        return GetMeInteractor(mock_identity_provider)

    async def test_returns_profile_with_unique_permissions(
        self,
        interactor: GetMeInteractor,
        mock_identity_provider: AsyncMock,
        sample_user: User,
        admin_role: Role,
    ) -> None:
        sample_user.roles.append(admin_role)
        mock_identity_provider.get_current_user.return_value = sample_user

        response = await interactor()

        assert response.id == sample_user.id
        assert response.email == sample_user.email
        assert response.is_active is True
        assert response.roles == [UserRoleEnum.USER, UserRoleEnum.ADMIN]
        assert len(response.permissions) == 2
        assert set(response.permissions) == {
            PermissionEnum.USER_HELLO_WORLD_VIEW,
            PermissionEnum.ADMIN_HELLO_WORLD_VIEW,
        }

    async def test_user_without_roles_can_read_own_profile(
        self,
        interactor: GetMeInteractor,
        mock_identity_provider: AsyncMock,
        sample_user: User,
    ) -> None:
        sample_user.roles = []
        mock_identity_provider.get_current_user.return_value = sample_user

        response = await interactor()

        assert response.id == sample_user.id
        assert response.roles == []
        assert response.permissions == []

    async def test_anonymous_user_has_no_access(
        self, interactor: GetMeInteractor
    ) -> None:
        with pytest.raises(UnauthenticatedError):
            await interactor()
