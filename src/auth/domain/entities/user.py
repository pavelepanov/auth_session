from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from auth.domain.user_role import UserRoleEnum

UserId = NewType("UserId", UUID)
UserName = NewType("Username", str)
PasswordHash = NewType("PasswordHash", str)

RawPassword = NewType("RawPassword", str)


@dataclass
class User:
    id: UserId
    username: UserName
    password_hash: PasswordHash
    is_active: bool
    role: UserRoleEnum
    is_verified: bool


def create_user(
    id: UserId,
    username: UserName,
    password_hash: PasswordHash,
    role: UserRoleEnum,
    is_verified: bool,
) -> User:
    return User(
        id=id,
        username=username,
        password_hash=password_hash,
        is_active=True,
        role=role,
        is_verified=is_verified,
    )
