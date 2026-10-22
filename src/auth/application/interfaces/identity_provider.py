from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import User


class IdentityProvider(Protocol):
    @abstractmethod
    async def get_current_user(self) -> User | None:
        """Вызывать до бизнес-изменений: обновление или удаление сессии
        может вызвать commit общей транзакции.
        """
        ...
