from faststream.rabbit import RabbitBroker

from auth.application.interfaces.sender_letter import SenderLetter
from auth.domain.entities.user import UserId
from auth.entrypoint.config import RabbitMQConfig


class EmailSenderLetter(SenderLetter):
    def __init__(self, broker: RabbitBroker, rabbitmq_config: RabbitMQConfig) -> None:
        self._broker = broker
        self._rabbitmq_config = rabbitmq_config

    async def send_letter(self, user_id: UserId):
        email_dto = {"user_id": user_id}
        await self._broker.publish(
            message=email_dto, queue=self._rabbitmq_config.email_sender_queue
        )
