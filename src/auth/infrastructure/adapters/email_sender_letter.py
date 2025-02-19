from auth.application.interfaces.sender_letter import SenderLetter
from auth.domain.entities.user import UserId


class EmailSenderLetter(SenderLetter):
    async def send_letter(self, user_id: UserId): ...
