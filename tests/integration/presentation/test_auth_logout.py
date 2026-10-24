from httpx import AsyncClient


class TestLogoutEndpoint:
    async def test_logout_returns_no_content(self, client: AsyncClient) -> None:
        response = await client.delete("/auth/logout")

        assert response.status_code == 204
        assert response.content == b""
