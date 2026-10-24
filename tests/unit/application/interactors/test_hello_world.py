from unittest.mock import AsyncMock

import pytest

from auth.application.errors import PermissionDeniedError, UnauthenticatedError
from auth.application.interactors.admin_hello_world import AdminHelloWorldInteractor
from auth.application.interactors.user_hello_world import UserHelloWorldInteractor
from auth.domain.entities.user import User


class TestHelloWorldInteractors:
    @pytest.fixture(params=["user", "admin"])
    def interactor(
        self, request: pytest.FixtureRequest, mock_identity_provider: AsyncMock
    ) -> UserHelloWorldInteractor | AdminHelloWorldInteractor:
        if request.param == "user":
            return UserHelloWorldInteractor(mock_identity_provider)
        return AdminHelloWorldInteractor(mock_identity_provider)

    async def test_admin_can_access_both_routes(
        self,
        interactor: UserHelloWorldInteractor | AdminHelloWorldInteractor,
        mock_identity_provider: AsyncMock,
        admin_user: User,
    ) -> None:
        mock_identity_provider.get_current_user.return_value = admin_user

        response = await interactor()

        expected_role = (
            "user" if isinstance(interactor, UserHelloWorldInteractor) else "admin"
        )
        assert response.hello_world == f"hello world by {expected_role}"

    async def test_anonymous_user_has_no_access(
        self, interactor: UserHelloWorldInteractor | AdminHelloWorldInteractor
    ) -> None:
        with pytest.raises(UnauthenticatedError):
            await interactor()

    async def test_missing_permissions_deny_access(
        self,
        interactor: UserHelloWorldInteractor | AdminHelloWorldInteractor,
        mock_identity_provider: AsyncMock,
        sample_user: User,
    ) -> None:
        sample_user.roles = []
        mock_identity_provider.get_current_user.return_value = sample_user

        with pytest.raises(PermissionDeniedError):
            await interactor()

    async def test_regular_user_cannot_access_admin_route(
        self, mock_identity_provider: AsyncMock, sample_user: User
    ) -> None:
        mock_identity_provider.get_current_user.return_value = sample_user
        interactor = AdminHelloWorldInteractor(mock_identity_provider)

        with pytest.raises(PermissionDeniedError):
            await interactor()
