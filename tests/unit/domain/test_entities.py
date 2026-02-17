from datetime import datetime, timezone

from tests.conftest import ADMIN_UUID, HASHED_PASSWORD, SESSION_ID_VALUE, USER_UUID

from auth.domain.entities.session import SessionId, create_session
from auth.domain.entities.user import (
    PasswordHash,
    UserId,
    UserName,
    create_user,
)
from auth.domain.user_role import UserRoleEnum


def test_create_user():
    """create_user() корректно создаёт пользователя с is_active=True."""
    user_id = UserId(USER_UUID)
    username = UserName("john_doe")
    role = UserRoleEnum.USER
    is_verified = False

    user = create_user(
        id=user_id,
        username=username,
        password_hash=HASHED_PASSWORD,
        role=role,
        is_verified=is_verified,
    )

    assert user.id == user_id
    assert user.username == username
    assert user.password_hash == HASHED_PASSWORD
    assert user.role == UserRoleEnum.USER
    assert user.is_verified is False
    assert user.is_active is True


def test_create_user_is_always_active():
    """create_user() ВСЕГДА создаёт активного пользователя."""
    user = create_user(
        id=UserId(USER_UUID),
        username=UserName("any_user"),
        password_hash=HASHED_PASSWORD,
        role=UserRoleEnum.USER,
        is_verified=False,
    )

    assert user.is_active is True


def test_create_admin_user():
    """Создание пользователя с ролью ADMIN."""
    user = create_user(
        id=UserId(ADMIN_UUID),
        username=UserName("admin"),
        password_hash=HASHED_PASSWORD,
        role=UserRoleEnum.ADMIN,
        is_verified=True,
    )

    assert user.role == UserRoleEnum.ADMIN
    assert user.is_verified is True


def test_create_session():
    """create_session() корректно создаёт сессию."""
    session_id = SessionId(SESSION_ID_VALUE)
    expiration = datetime(2030, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    user_id = UserId(USER_UUID)

    session = create_session(
        id=session_id,
        expiration=expiration,
        user_id=user_id,
    )

    assert session.id == session_id
    assert session.expiration == expiration
    assert session.user_id == user_id
