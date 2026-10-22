from dataclasses import dataclass, field
from enum import StrEnum
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
UserEmail = NewType("UserEmail", str)
PasswordHash = NewType("PasswordHash", str)
RoleId = NewType("RoleId", UUID)
PermissionId = NewType("PermissionId", UUID)

RawPassword = NewType("RawPassword", str)


class UserRoleEnum(StrEnum):
    ADMIN = "admin"
    USER = "user"


class PermissionEnum(StrEnum):
    USER_HELLO_WORLD_VIEW = "user_hello_world.view"
    ADMIN_HELLO_WORLD_VIEW = "admin_hello_world.view"


@dataclass
class Permission:
    value: PermissionEnum
    id: PermissionId | None = None


@dataclass
class Role:
    value: UserRoleEnum
    id: RoleId | None = None
    permissions: list[Permission] = field(default_factory=list)


@dataclass
class User:
    id: UserId
    email: UserEmail
    password_hash: PasswordHash
    is_active: bool
    roles: list[Role] = field(default_factory=list)


def create_user(
    id: UserId,
    email: UserEmail,
    password_hash: PasswordHash,
    roles: list[Role] | None = None,
) -> User:
    return User(
        id=id,
        email=email,
        password_hash=password_hash,
        is_active=True,
        roles=roles or [],
    )
