from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import UserId


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user_id(self) -> UserId: ...
