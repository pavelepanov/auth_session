from dataclasses import dataclass
from typing import NewType
from uuid import UUID

UserId = NewType("UserId", UUID)
PasswordHash = NewType("PasswordHash", bytes)


@dataclass
class User:
    id: UserId
    password_hash: PasswordHash
    is_active: bool
