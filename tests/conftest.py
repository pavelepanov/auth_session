"""Shared test data and mocks. Fixtures perform no external I/O."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from auth.application.interfaces.client_session_transport import ClientSessionTransport
from auth.application.interfaces.identity_provider import IdentityProvider
from auth.application.interfaces.password_hasher import PasswordHasher
from auth.application.interfaces.session_data_gateway import SessionDataGateway
from auth.application.interfaces.transaction_manager import TransactionManager
from auth.application.interfaces.user_data_gateway import UserDataGateway
from auth.domain.entities.session import (
    Session,
    SessionId,
    SessionToken,
    SessionTokenHash,
)
from auth.domain.entities.user import (
    PasswordHash,
    Permission,
    PermissionEnum,
    Role,
    User,
    UserEmail,
    UserId,
    UserRoleEnum,
)
from auth.entrypoint.config import SessionConfig

STATIC_USER_ID = UserId(UUID("11111111-1111-1111-1111-111111111111"))
STATIC_SESSION_ID = SessionId(UUID("22222222-2222-2222-2222-222222222222"))
PLAIN_PASSWORD = "test-password-at-least-15-characters"
STATIC_TOKEN = SessionToken("test-session-bearer-token")
STATIC_TOKEN_HASH = SessionTokenHash("a" * 64)
FROZEN_NOW = datetime(2026, 10, 24, 12, tzinfo=UTC)


@dataclass
class CookieState:
    """Outgoing cookie changes recorded by the mock transport."""

    token: SessionToken | None = None
    deleted: bool = False


@pytest.fixture
def session_config() -> SessionConfig:
    return SessionConfig(expiration_minutes=30, token_hash_secret="test-only-secret")


@pytest.fixture
def user_role() -> Role:
    return Role(
        value=UserRoleEnum.USER,
        permissions=[Permission(value=PermissionEnum.USER_HELLO_WORLD_VIEW)],
    )


@pytest.fixture
def admin_role() -> Role:
    return Role(
        value=UserRoleEnum.ADMIN,
        permissions=[Permission(value=value) for value in PermissionEnum],
    )


@pytest.fixture
def password_hash() -> PasswordHash:
    return PasswordHash("test-password-hash")


@pytest.fixture
def sample_user(user_role: Role, password_hash: PasswordHash) -> User:
    return User(
        id=STATIC_USER_ID,
        email=UserEmail("test@example.com"),
        password_hash=password_hash,
        is_active=True,
        roles=[user_role],
    )


@pytest.fixture
def inactive_user(sample_user: User) -> User:
    sample_user.is_active = False
    return sample_user


@pytest.fixture
def admin_user(sample_user: User, admin_role: Role) -> User:
    sample_user.roles = [admin_role]
    return sample_user


@pytest.fixture
def sample_session() -> Session:
    return Session(
        id=STATIC_SESSION_ID,
        token_hash=STATIC_TOKEN_HASH,
        user_id=STATIC_USER_ID,
        expires_at=FROZEN_NOW + timedelta(minutes=30),
        created_at=FROZEN_NOW,
    )


@pytest.fixture
def saved_users() -> list[User]:
    return []


@pytest.fixture
def saved_sessions() -> list[Session]:
    return []


@pytest.fixture
def cookie_state() -> CookieState:
    return CookieState()


@pytest.fixture
def mock_identity_provider() -> AsyncMock:
    mock = AsyncMock(spec=IdentityProvider)
    mock.get_current_user.return_value = None
    return mock


@pytest.fixture
def mock_user_gateway(saved_users: list[User], user_role: Role) -> AsyncMock:
    """Record requested inserts; transaction behavior belongs to DB tests."""
    mock = AsyncMock(spec=UserDataGateway)
    mock.read_by_email.return_value = None
    mock.get_role_by_value.return_value = user_role
    mock.add.side_effect = saved_users.append
    return mock


@pytest.fixture
def mock_session_gateway(saved_sessions: list[Session]) -> AsyncMock:
    mock = AsyncMock(spec=SessionDataGateway)
    mock.add.side_effect = saved_sessions.append
    mock.delete.side_effect = saved_sessions.remove
    mock.read_by_token_hash.return_value = None

    def prolong(session: Session, expires_at: datetime) -> None:
        session.expires_at = expires_at

    mock.prolong.side_effect = prolong
    return mock


@pytest.fixture
def mock_transport(cookie_state: CookieState) -> AsyncMock:
    mock = AsyncMock(spec=ClientSessionTransport)

    def set_session(token: SessionToken) -> None:
        cookie_state.token = token

    def clear_session() -> None:
        cookie_state.token = None
        cookie_state.deleted = True

    mock.get_session.return_value = None
    mock.set_session.side_effect = set_session
    mock.clear_session.side_effect = clear_session
    return mock


@pytest.fixture
def mock_transaction_manager() -> AsyncMock:
    return AsyncMock(spec=TransactionManager)


@pytest.fixture
def mock_password_hasher(password_hash: PasswordHash) -> MagicMock:
    mock = MagicMock(spec=PasswordHasher)
    mock.hash.return_value = password_hash
    mock.is_password_valid.return_value = True
    return mock
