from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from auth.domain.user_role import UserRoleEnum

UserId = NewType("UserId", UUID)
UserEmail = NewType("UserEmail", str)
PasswordHash = NewType("PasswordHash", str)

RawPassword = NewType("RawPassword", str)


@dataclass
class User:
    id: UserId
    email: UserEmail
    password_hash: PasswordHash
    is_active: bool
    role: UserRoleEnum


def create_user(
    id: UserId,
    email: UserEmail,
    password_hash: PasswordHash,
    role: UserRoleEnum,
) -> User:
    return User(
        id=id,
        email=email,
        password_hash=password_hash,
        is_active=True,
        role=role,
    )
