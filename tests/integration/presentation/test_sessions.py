from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.domain.entities.session import Session, SessionId, SessionToken
from auth.domain.entities.user import User
from auth.entrypoint.config import SessionConfig
from auth.infrastructure.adapters.session_token_hasher_hmac_sha256 import (
    SessionTokenHasherHmacSha256,
)
from auth.infrastructure.adapters.transaction_manager_sqla import TransactionManagerImpl
from tests.conftest import PLAIN_PASSWORD

LOGIN_BODY = {"email": "test@example.com", "raw_password": PLAIN_PASSWORD}


class TestSessionLifecycle:
    @pytest.fixture
    async def stored_user(self, db_session: AsyncSession, sample_user: User) -> User:
        db_session.add(sample_user)
        await db_session.commit()
        return sample_user

    @pytest.fixture
    async def logged_in_client(
        self, full_client: AsyncClient, stored_user: User
    ) -> AsyncClient:
        response = await full_client.post("/auth/login", json=LOGIN_BODY)
        assert response.status_code == 200
        return full_client

    async def test_signup_login_access_logout(
        self,
        full_client: AsyncClient,
        db_session: AsyncSession,
        session_config: SessionConfig,
    ) -> None:
        signup = await full_client.post("/auth/signup", json=LOGIN_BODY)
        assert signup.status_code == 201
        assert "set-cookie" not in signup.headers

        login = await full_client.post("/auth/login", json=LOGIN_BODY)
        assert login.status_code == 200
        token = SessionToken(full_client.cookies["__Host-session"])
        assert len(token) >= 43
        assert set(token) <= set(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        )
        cookie = login.headers["set-cookie"].lower()
        assert "secure" in cookie
        assert "httponly" in cookie
        assert "samesite=lax" in cookie
        assert "path=/" in cookie
        assert "max-age=1800" in cookie
        assert "domain=" not in cookie
        sessions = (await db_session.scalars(select(Session))).all()
        assert len(sessions) == 1
        assert sessions[0].token_hash == SessionTokenHasherHmacSha256(
            session_config
        ).hash(token)
        assert str(sessions[0].token_hash) != str(token)
        await db_session.commit()

        allowed = await full_client.get("/hello_world/user")
        denied = await full_client.get("/hello_world/admin")
        repeated_login = await full_client.post("/auth/login", json=LOGIN_BODY)
        repeated_signup = await full_client.post("/auth/signup", json=LOGIN_BODY)
        assert allowed.status_code == 200
        assert denied.status_code == 403
        assert repeated_login.status_code == 409
        assert repeated_signup.status_code == 409

        logout = await full_client.delete("/auth/logout")
        assert logout.status_code == 204
        assert "__Host-session" not in full_client.cookies
        deleted_cookie = logout.headers["set-cookie"].lower()
        assert "max-age=0" in deleted_cookie
        assert "secure" in deleted_cookie
        assert "httponly" in deleted_cookie
        assert "samesite=lax" in deleted_cookie
        assert (await db_session.scalars(select(Session))).all() == []
        assert (await full_client.get("/hello_world/user")).status_code == 401

    async def test_admin_can_access_both_routes(
        self, full_client: AsyncClient, db_session: AsyncSession, admin_user: User
    ) -> None:
        db_session.add(admin_user)
        await db_session.commit()

        login = await full_client.post("/auth/login", json=LOGIN_BODY)

        assert login.status_code == 200
        assert (await full_client.get("/hello_world/user")).status_code == 200
        assert (await full_client.get("/hello_world/admin")).status_code == 200

    @pytest.mark.parametrize("kind", ["unknown", "expired", "inactive"])
    async def test_invalid_session_revokes_access_and_cookie(
        self,
        logged_in_client: AsyncClient,
        db_session: AsyncSession,
        stored_user: User,
        kind: str,
    ) -> None:
        if kind == "unknown":
            logged_in_client.cookies.clear()
            logged_in_client.cookies.set(
                "__Host-session", "unknown-token", domain="testserver.local", path="/"
            )
        else:
            session = (await db_session.scalars(select(Session))).one()
            if kind == "expired":
                session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
            else:
                stored_user.is_active = False
            await db_session.commit()

        response = await logged_in_client.get("/hello_world/user")

        assert response.status_code == 401
        assert "max-age=0" in response.headers["set-cookie"].lower()
        if kind != "unknown":
            assert (await db_session.scalars(select(Session))).all() == []

    async def test_renewal_extends_same_session_and_refreshes_cookie(
        self, logged_in_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        token = logged_in_client.cookies["__Host-session"]
        session = (await db_session.scalars(select(Session))).one()
        session.expires_at = datetime.now(UTC) + timedelta(minutes=1)
        old_expiration = session.expires_at
        session_id = session.id
        await db_session.commit()

        response = await logged_in_client.get("/hello_world/user")
        await db_session.refresh(session)

        assert response.status_code == 200
        assert "max-age=1800" in response.headers["set-cookie"].lower()
        assert logged_in_client.cookies["__Host-session"] == token
        assert session.id == session_id
        assert session.expires_at > old_expiration + timedelta(minutes=28)
        assert len((await db_session.scalars(select(Session))).all()) == 1

    async def test_fresh_session_does_not_refresh_cookie(
        self, logged_in_client: AsyncClient
    ) -> None:
        response = await logged_in_client.get("/hello_world/user")

        assert response.status_code == 200
        assert "set-cookie" not in response.headers

    async def test_failed_commit_rolls_back_session_and_issues_no_cookie(
        self, full_client: AsyncClient, db_session: AsyncSession, stored_user: User
    ) -> None:
        inserted_sessions: list[SessionId] = []

        async def fail_after_insert(manager: TransactionManagerImpl) -> None:
            await manager._session.flush()
            inserted_sessions.extend(
                session.id
                for session in (await manager._session.scalars(select(Session))).all()
            )
            raise RuntimeError("test commit failure after INSERT")

        with patch.object(TransactionManagerImpl, "commit", new=fail_after_insert):
            response = await full_client.post("/auth/login", json=LOGIN_BODY)

        assert response.status_code == 500
        assert len(inserted_sessions) == 1
        assert "set-cookie" not in response.headers
        assert "__Host-session" not in full_client.cookies
        assert (await db_session.scalars(select(Session))).all() == []

    async def test_failed_signup_rolls_back_user_and_issues_no_cookie(
        self, full_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        inserted_users: list[User] = []

        async def fail_after_insert(manager: TransactionManagerImpl) -> None:
            await manager._session.flush()
            inserted_users.extend((await manager._session.scalars(select(User))).all())
            raise RuntimeError("test commit failure after INSERT")

        with patch.object(TransactionManagerImpl, "commit", new=fail_after_insert):
            response = await full_client.post("/auth/signup", json=LOGIN_BODY)

        assert response.status_code == 500
        assert len(inserted_users) == 1
        assert "set-cookie" not in response.headers
        assert (await db_session.scalars(select(User))).all() == []

    async def test_failed_logout_preserves_session_and_client_cookie(
        self, logged_in_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        token = logged_in_client.cookies["__Host-session"]
        sessions_after_delete: list[int] = []

        async def fail_after_delete(manager: TransactionManagerImpl) -> None:
            await manager._session.flush()
            sessions_after_delete.append(
                len((await manager._session.scalars(select(Session))).all())
            )
            raise RuntimeError("test commit failure after DELETE")

        with patch.object(TransactionManagerImpl, "commit", new=fail_after_delete):
            response = await logged_in_client.delete("/auth/logout")

        assert sessions_after_delete == [0]
        assert response.status_code == 500
        assert "set-cookie" not in response.headers
        assert logged_in_client.cookies["__Host-session"] == token
        assert len((await db_session.scalars(select(Session))).all()) == 1

    async def test_logout_is_idempotent_for_anonymous_client(
        self, full_client: AsyncClient
    ) -> None:
        first = await full_client.delete("/auth/logout")
        second = await full_client.delete("/auth/logout")

        assert first.status_code == second.status_code == 204
        assert "max-age=0" in second.headers["set-cookie"].lower()

    async def test_logout_preserves_other_browser_session(
        self, logged_in_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        first_token = logged_in_client.cookies["__Host-session"]
        logged_in_client.cookies.clear()
        login = await logged_in_client.post("/auth/login", json=LOGIN_BODY)
        assert login.status_code == 200

        logout = await logged_in_client.delete("/auth/logout")
        logged_in_client.cookies.set("__Host-session", first_token)
        response = await logged_in_client.get("/hello_world/user")

        assert logout.status_code == 204
        assert response.status_code == 200
        assert len((await db_session.scalars(select(Session))).all()) == 1

    async def test_expired_cookie_is_replaced_by_new_login_session(
        self, logged_in_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        old_token = logged_in_client.cookies["__Host-session"]
        old_session = (await db_session.scalars(select(Session))).one()
        old_id = old_session.id
        old_session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await db_session.commit()
        db_session.expunge_all()

        response = await logged_in_client.post("/auth/login", json=LOGIN_BODY)
        sessions = (await db_session.scalars(select(Session))).all()

        assert response.status_code == 200
        assert logged_in_client.cookies["__Host-session"] != old_token
        assert "max-age=1800" in response.headers["set-cookie"].lower()
        assert len(response.headers.get_list("set-cookie")) == 1
        assert len(sessions) == 1
        assert sessions[0].id != old_id

    async def test_expired_session_cleanup_preserves_new_signup(
        self, logged_in_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        session = (await db_session.scalars(select(Session))).one()
        session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        await db_session.commit()

        response = await logged_in_client.post(
            "/auth/signup",
            json={"email": "new@example.com", "raw_password": PLAIN_PASSWORD},
        )

        assert response.status_code == 201
        assert (await db_session.scalars(select(Session))).all() == []
        users = (await db_session.scalars(select(User))).all()
        assert {user.email for user in users} == {"test@example.com", "new@example.com"}

    async def test_empty_cookie_is_anonymous(self, full_client: AsyncClient) -> None:
        full_client.cookies.set("__Host-session", "")

        response = await full_client.get("/hello_world/user")

        assert response.status_code == 401
        assert "set-cookie" not in response.headers
