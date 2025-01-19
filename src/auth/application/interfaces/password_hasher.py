from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import Password


class PasswordHasher(Protocol):
    @abstractmethod
    def hash(self, password: Password): ...
