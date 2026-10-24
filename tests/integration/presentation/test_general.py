from httpx import AsyncClient


class TestGeneralEndpoints:
    async def test_health_does_not_require_database(self, client: AsyncClient) -> None:
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert "set-cookie" not in response.headers

    async def test_root_redirects_to_docs(self, client: AsyncClient) -> None:
        response = await client.get("/")

        assert response.status_code == 307
        assert response.headers["location"] == "docs/"

    async def test_unknown_route_has_structured_error(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/missing")

        assert response.status_code == 404
        assert response.json()["error"]["code"] == "NOT_FOUND"

    async def test_wrong_method_has_structured_error(self, client: AsyncClient) -> None:
        response = await client.get("/auth/login")

        assert response.status_code == 405
        assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"

    async def test_openapi_documents_business_errors(self, client: AsyncClient) -> None:
        response = await client.get("/openapi.json")

        assert response.status_code == 200
        paths = response.json()["paths"]
        assert set(paths["/auth/login"]["post"]["responses"]) >= {
            "200",
            "401",
            "409",
            "422",
            "500",
        }
        examples = paths["/auth/signup"]["post"]["responses"]["409"]["content"][
            "application/json"
        ]["examples"]
        assert set(examples) == {"ALREADY_AUTHENTICATED", "USER_EMAIL_ALREADY_EXISTS"}
