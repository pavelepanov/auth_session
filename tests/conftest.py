from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from auth.domain.entities.session import Session, SessionId
from auth.domain.entities.user import PasswordHash, User, UserId, UserName
from auth.domain.user_role import UserRoleEnum

HASHED_PASSWORD = PasswordHash(
    "$2b$12$8mjSL2sL8qauE3o2cNTgyeSwUlVa0LufWdZd2WrBaGgQQ3fPMIJoy"
) # RawPassword: TestPassword1

USER_UUID = UUID("00000000-0000-0000-0000-000000000001")
ADMIN_UUID = UUID("00000000-0000-0000-0000-000000000002")
INACTIVE_UUID = UUID("00000000-0000-0000-0000-000000000003")
SESSION_ID_VALUE = "test-session-id-abc123"


@pytest.fixture
def user_id() -> UserId:
    return UserId(USER_UUID)


@pytest.fixture
def sample_user(user_id: UserId) -> User:
    return User(
        id=user_id,
        username=UserName("testuser"),
        password_hash=HASHED_PASSWORD,
        is_active=True,
        role=UserRoleEnum.USER,
        is_verified=False,
    )


@pytest.fixture
def verified_user(user_id: UserId) -> User:
    return User(
        id=user_id,
        username=UserName("verified_user"),
        password_hash=HASHED_PASSWORD,
        is_active=True,
        role=UserRoleEnum.USER,
        is_verified=True,
    )


@pytest.fixture
def admin_user() -> User:
    return User(
        id=UserId(ADMIN_UUID),
        username=UserName("admin_user"),
        password_hash=HASHED_PASSWORD,
        is_active=True,
        role=UserRoleEnum.ADMIN,
        is_verified=True,
    )


@pytest.fixture
def inactive_user() -> User:
    return User(
        id=UserId(INACTIVE_UUID),
        username=UserName("inactive_user"),
        password_hash=HASHED_PASSWORD,
        is_active=False,
        role=UserRoleEnum.USER,
        is_verified=True,
    )


@pytest.fixture
def session_id() -> SessionId:
    return SessionId(SESSION_ID_VALUE)


@pytest.fixture
def sample_session(session_id: SessionId, user_id: UserId) -> Session:
    return Session(
        id=session_id,
        expiration=datetime(2030, 1, 1, tzinfo=timezone.utc),
        user_id=user_id,
    )


@pytest.fixture
def mock_identity_provider() -> AsyncMock:
    mock = AsyncMock()
    mock.is_authenticated.return_value = False
    mock.get_role.return_value = UserRoleEnum.USER
    return mock


@pytest.fixture
def mock_user_data_gateway() -> AsyncMock:
    mock = AsyncMock()
    mock.read_by_username.return_value = None
    mock.read_by_id.return_value = None
    mock.add.return_value = None
    return mock


@pytest.fixture
def mock_session_data_gateway() -> AsyncMock:
    mock = AsyncMock()
    mock.add.return_value = None
    mock.delete_session.return_value = None
    return mock


@pytest.fixture
def mock_transaction_manager() -> AsyncMock:
    mock = AsyncMock()
    mock.commit.return_value = None
    return mock


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    mock = MagicMock()
    mock.hash.return_value = HASHED_PASSWORD
    mock.verify.return_value = True
    mock.is_password_valid.return_value = True
    return mock


@pytest.fixture
def mock_user_id_generator(user_id: UserId) -> MagicMock:
    mock = MagicMock()
    mock.return_value = user_id
    return mock


@pytest.fixture
def mock_session_id_generator(session_id: SessionId) -> MagicMock:
    mock = MagicMock()
    mock.return_value = session_id
    return mock


@pytest.fixture
def mock_request_manager(session_id: SessionId) -> MagicMock:
    mock = MagicMock()
    mock.get_session_id_from_request.return_value = session_id
    return mock


@pytest.fixture
def mock_sender_letter() -> AsyncMock:
    mock = AsyncMock()
    mock.send_letter.return_value = None
    return mock


@pytest.fixture
def session_config() -> MagicMock:
    mock = MagicMock()
    mock.expiration_minutes = 5
    return mock
