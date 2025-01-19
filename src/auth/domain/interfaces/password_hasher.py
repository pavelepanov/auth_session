from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import PasswordHash, RawPassword


class PasswordHasher(Protocol):
    @abstractmethod
    def hash(self, raw_password: RawPassword) -> PasswordHash: ...

    @abstractmethod
    def verify(
        self, raw_password: RawPassword, password_hash: PasswordHash
    ) -> bool: ...
