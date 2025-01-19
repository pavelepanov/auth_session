from dataclasses import dataclass
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
UserName = NewType("Username", str)
PasswordHash = NewType("PasswordHash", bytes)

RawPassword = NewType("RawPassword", str)


@dataclass
class User:
    id: UserId
    username: UserName
    password_hash: PasswordHash
    is_active: bool
