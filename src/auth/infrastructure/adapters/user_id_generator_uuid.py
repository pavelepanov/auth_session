from uuid import uuid4

from auth.application.interfaces.user_id_generator import UserIdGenerator
from auth.domain.entities.user import UserId


class UserIdGeneratorImpl(UserIdGenerator):
    def __call__(self) -> UserId:
        return UserId(uuid4())
