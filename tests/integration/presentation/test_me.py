import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.user import Role, User
from tests.conftest import PLAIN_PASSWORD


class TestMeEndpoint:
    @pytest.mark.parametrize("roles", ["user", "admin", "both", "none"])
    async def test_returns_current_profile(
        self,
        full_client: AsyncClient,
        db_session: AsyncSession,
        sample_user: User,
        user_role: Role,
        admin_role: Role,
        roles: str,
    ) -> None:
        assigned_roles = {
            "user": [user_role],
            "admin": [admin_role],
            "both": [user_role, admin_role],
            "none": [],
        }[roles]
        sample_user.roles = assigned_roles
        db_session.add(sample_user)
        await db_session.commit()
        login = await full_client.post(
            "/auth/login",
            json={"email": sample_user.email, "raw_password": PLAIN_PASSWORD},
        )
        assert login.status_code == 200

        response = await full_client.get("/me")

        expected_roles = {
            "user": ["user"],
            "admin": ["admin"],
            "both": ["admin", "user"],
            "none": [],
        }[roles]
        expected_permissions = {
            "user": ["user_hello_world.view"],
            "admin": ["admin_hello_world.view", "user_hello_world.view"],
            "both": ["admin_hello_world.view", "user_hello_world.view"],
            "none": [],
        }[roles]
        assert response.status_code == 200
        data = response.json()["data"]
        actual_roles = data.pop("roles")
        actual_permissions = data.pop("permissions")
        assert set(actual_roles) == set(expected_roles)
        assert len(actual_roles) == len(expected_roles)
        assert set(actual_permissions) == set(expected_permissions)
        assert len(actual_permissions) == len(expected_permissions)
        assert data == {
            "id": str(sample_user.id),
            "email": sample_user.email,
            "is_active": True,
        }
        assert "set-cookie" not in response.headers

    async def test_anonymous_user_has_no_access(self, full_client: AsyncClient) -> None:
        response = await full_client.get("/me")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHENTICATED"
        assert "set-cookie" not in response.headers
