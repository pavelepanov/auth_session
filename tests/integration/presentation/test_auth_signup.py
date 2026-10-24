import pytest
from httpx import AsyncClient

from auth.application.errors import (
    AlreadyAuthenticatedError,
    InvalidPasswordError,
    UserEmailAlreadyExistsError,
)
from tests.conftest import PLAIN_PASSWORD, STATIC_USER_ID
from tests.integration.presentation.conftest import InteractorMocks


class TestSignupEndpoint:
    async def test_signup_returns_user_id(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/signup",
            json={"email": "test@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == 201
        assert response.json() == {"data": {"id": str(STATIC_USER_ID)}}

    @pytest.mark.parametrize(
        ("error", "status", "code"),
        [
            pytest.param(
                AlreadyAuthenticatedError, 409, "ALREADY_AUTHENTICATED", id="logged_in"
            ),
            pytest.param(
                UserEmailAlreadyExistsError,
                409,
                "USER_EMAIL_ALREADY_EXISTS",
                id="duplicate",
            ),
            pytest.param(InvalidPasswordError, 400, "INVALID_PASSWORD", id="password"),
        ],
    )
    async def test_business_errors(
        self,
        client: AsyncClient,
        interactor_mocks: InteractorMocks,
        error: type[Exception],
        status: int,
        code: str,
    ) -> None:
        interactor_mocks.signup.side_effect = error

        response = await client.post(
            "/auth/signup",
            json={"email": "test@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == status
        assert response.json()["error"]["code"] == code
