import pytest
from httpx import AsyncClient

from auth.application.errors import PermissionDeniedError, UnauthenticatedError
from tests.integration.presentation.conftest import InteractorMocks


class TestHelloWorldEndpoints:
    @pytest.mark.parametrize("role", ["user", "admin"])
    async def test_success(self, client: AsyncClient, role: str) -> None:
        response = await client.get(f"/hello_world/{role}")

        assert response.status_code == 200
        assert response.json() == {"data": {"hello_world": f"hello world by {role}"}}

    @pytest.mark.parametrize("role", ["user", "admin"])
    @pytest.mark.parametrize(
        ("error", "status"), [(UnauthenticatedError, 401), (PermissionDeniedError, 403)]
    )
    async def test_access_errors(
        self,
        client: AsyncClient,
        interactor_mocks: InteractorMocks,
        role: str,
        error: type[Exception],
        status: int,
    ) -> None:
        getattr(interactor_mocks, role).side_effect = error

        response = await client.get(f"/hello_world/{role}")

        assert response.status_code == status
