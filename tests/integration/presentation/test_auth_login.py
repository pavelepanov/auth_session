import pytest
from httpx import AsyncClient

from auth.application.errors import AlreadyAuthenticatedError, InvalidCredentialsError
from tests.conftest import PLAIN_PASSWORD
from tests.integration.presentation.conftest import InteractorMocks


class TestLoginEndpoint:
    async def test_success_returns_empty_data(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == 200
        assert response.json() == {"data": None}

    @pytest.mark.parametrize(
        ("error", "status", "code"),
        [
            pytest.param(
                InvalidCredentialsError, 401, "INVALID_CREDENTIALS", id="invalid"
            ),
            pytest.param(
                AlreadyAuthenticatedError, 409, "ALREADY_AUTHENTICATED", id="logged_in"
            ),
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
        interactor_mocks.login.side_effect = error

        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == status
        assert response.json()["error"]["code"] == code
        assert "set-cookie" not in response.headers

    @pytest.mark.parametrize(
        ("body", "field", "code"),
        [
            pytest.param({}, "email", "REQUIRED_FIELD", id="missing_email"),
            pytest.param(
                {"email": "a@b.com"},
                "raw_password",
                "REQUIRED_FIELD",
                id="missing_password",
            ),
            pytest.param(
                {"email": "bad", "raw_password": "secret"},
                "email",
                "INVALID_EMAIL",
                id="bad_email",
            ),
            pytest.param(
                {"email": "a@b.com", "raw_password": 123},
                "raw_password",
                "INVALID_TYPE",
                id="password_type",
            ),
        ],
    )
    async def test_validation_does_not_expose_input(
        self, client: AsyncClient, body: dict[str, object], field: str, code: str
    ) -> None:
        response = await client.post("/auth/login", json=body)

        assert response.status_code == 422
        error = response.json()["error"]
        assert error["code"] == "REQUEST_VALIDATION_ERROR"
        assert any(d["field"] == field and d["code"] == code for d in error["details"])
        assert "secret" not in response.text
        assert "input" not in response.text
        assert "ctx" not in response.text

    async def test_invalid_json(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/login",
            content='{"raw_password":"secret",',
            headers={"content-type": "application/json"},
        )

        assert response.status_code == 422
        assert response.json()["error"]["details"][0]["code"] == "INVALID_JSON"
        assert "secret" not in response.text

    async def test_unexpected_error_is_sanitized(
        self, client: AsyncClient, interactor_mocks: InteractorMocks
    ) -> None:
        interactor_mocks.login.side_effect = RuntimeError("database-password-and-token")

        response = await client.post(
            "/auth/login",
            json={"email": "test@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == 500
        assert response.json()["error"]["code"] == "INTERNAL_ERROR"
        assert "database-password-and-token" not in response.text
