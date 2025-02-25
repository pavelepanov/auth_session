from abc import abstractmethod
from typing import Protocol

from auth.domain.entities.user import UserId


class SenderLetter(Protocol):
    @abstractmethod
    async def send_letter(self, user_id: UserId): ...
