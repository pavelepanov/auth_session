from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import PasswordHash, RawPassword, User


class PasswordHasher(Protocol):
    @abstractmethod
    def hash(self, raw_password: RawPassword) -> PasswordHash: ...

    @abstractmethod
    def verify(
        self, raw_password: RawPassword, password_hash: PasswordHash
    ) -> bool: ...

    @abstractmethod
    def is_password_valid(self, user: User, raw_password: RawPassword): ...
